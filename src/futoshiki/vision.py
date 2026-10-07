from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any

import cv2
import numpy as np

from .models import Given, Inequality, Position, Puzzle, PuzzleValidationError


class ExtractionError(RuntimeError):
    """Raised when an image cannot be converted into a trustworthy puzzle."""


def _order_corners(points: np.ndarray) -> np.ndarray:
    points = points.reshape(4, 2).astype(np.float32)
    ordered = np.zeros((4, 2), dtype=np.float32)
    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).reshape(-1)
    ordered[0] = points[np.argmin(sums)]
    ordered[2] = points[np.argmax(sums)]
    ordered[1] = points[np.argmin(diffs)]
    ordered[3] = points[np.argmax(diffs)]
    return ordered


def _find_board_corners(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    minimum_area = image.shape[0] * image.shape[1] * 0.10
    candidates: list[tuple[float, np.ndarray]] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < minimum_area:
            continue
        polygon = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(polygon) == 4:
            candidates.append((area, polygon))
    if candidates:
        return _order_corners(max(candidates, key=lambda item: item[0])[1])
    # Digital screenshots sometimes have no outer contour. In that case, use
    # the complete image only when it is reasonably square.
    ratio = image.shape[1] / image.shape[0]
    if not 0.7 <= ratio <= 1.3:
        raise ExtractionError("Could not locate a four-corner puzzle board")
    height, width = image.shape[:2]
    return np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)


def _warp_board(image: np.ndarray, corners: np.ndarray, side: int = 800) -> np.ndarray:
    target = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(corners, target)
    return cv2.warpPerspective(image, matrix, (side, side))


def _infer_size(warped: np.ndarray) -> int:
    """Choose the 4×4 or 5×5 lattice with the strongest dark boundary signal."""
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    ink = 255 - cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # `ink` above is bright where text is absent; invert again for projection.
    ink = 255 - ink
    horizontal = ink.mean(axis=1)
    vertical = ink.mean(axis=0)
    scores: dict[int, float] = {}
    for size in (4, 5):
        boundaries = [round(index * (len(horizontal) - 1) / size) for index in range(size + 1)]
        score = sum(horizontal[max(0, point - 4): point + 5].max() for point in boundaries)
        score += sum(vertical[max(0, point - 4): point + 5].max() for point in boundaries)
        scores[size] = float(score)
    return max(scores, key=scores.get)


def _find_tesseract(configured_command: str = "tesseract") -> str | None:
    """Find the OCR engine without requiring Windows installers to update PATH."""
    override = os.environ.get("TESSERACT_CMD")
    if override:
        return override
    command = shutil.which(configured_command)
    if command:
        return command
    if Path(configured_command).is_file():
        return configured_command
    if os.name == "nt":
        import winreg

        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\Tesseract-OCR") as key:
                    for value_name in ("InstallDir", "Path"):
                        try:
                            directory, _ = winreg.QueryValueEx(key, value_name)
                        except OSError:
                            continue
                        executable = Path(directory) / "tesseract.exe"
                        if executable.is_file():
                            return str(executable)
            except OSError:
                continue
        for variable in ("ProgramFiles", "LOCALAPPDATA"):
            directory = os.environ.get(variable)
            if directory:
                relative = "Tesseract-OCR" if variable == "ProgramFiles" else "Programs/Tesseract-OCR"
                executable = Path(directory) / relative / "tesseract.exe"
                if executable.is_file():
                    return str(executable)
    return None


def _ocr_digit(cell: np.ndarray, size: int) -> tuple[int | None, float]:
    try:
        import pytesseract
    except ImportError as error:
        raise ExtractionError("The Python OCR wrapper is missing. Install requirements.txt with pip.") from error
    command = _find_tesseract(pytesseract.pytesseract.tesseract_cmd)
    if command:
        pytesseract.pytesseract.tesseract_cmd = command
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 8)
    config = f"--psm 10 -c tessedit_char_whitelist={''.join(str(n) for n in range(1, size + 1))}"
    try:
        info = pytesseract.image_to_data(thresholded, config=config, output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError as error:
        raise ExtractionError(
            "Tesseract OCR was not found. On Windows, install it with "
            "'winget install --id UB-Mannheim.TesseractOCR --exact --source winget', "
            "then restart the app. For a custom installation, set TESSERACT_CMD "
            "to the full path of tesseract.exe. See the README installation section."
        ) from error
    except pytesseract.TesseractError as error:
        raise ExtractionError(
            f"Tesseract OCR could not read the image: {error}. "
            "Check that English (eng) language data is installed and TESSDATA_PREFIX, if set, is correct."
        ) from error
    for text, confidence in zip(info["text"], info["conf"]):
        try:
            value = int(text.strip())
            score = float(confidence)
        except (ValueError, TypeError):
            continue
        if 1 <= value <= size:
            return value, score
    return None, 0.0


def _classify_gap(gap: np.ndarray, horizontal_gap: bool) -> str | None:
    """Classify a simple two-stroke inequality by locating its narrow vertex.

    Horizontal gaps produce `<`/`>` directly. For vertical gaps, the same
    vertex rule is normalized as top-cell `<`/`>` bottom-cell. This deliberately
    rejects uncertain contours instead of inventing a constraint.
    """
    gray = cv2.cvtColor(gap, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    points = np.column_stack(np.where(binary > 0))
    if len(points) < 18:
        return None
    axis = 1 if horizontal_gap else 0  # x for horizontal gap, y for vertical gap
    along = points[:, axis]
    counts = np.bincount(along, minlength=binary.shape[1] if horizontal_gap else binary.shape[0])
    active = np.flatnonzero(counts)
    if len(active) < 6:
        return None
    # The vertex has fewer ink pixels than the two open ends. Ignore the outer
    # 15% where cell borders or digits may leak into the crop.
    start, end = active[0], active[-1]
    interior = np.arange(start + max(1, (end - start) // 7), end - max(1, (end - start) // 7) + 1)
    if len(interior) == 0:
        return None
    vertex = interior[np.argmin(counts[interior])]
    midpoint = (start + end) / 2
    if abs(vertex - midpoint) < max(2, (end - start) * 0.08):
        return None
    if horizontal_gap:
        return "<" if vertex < midpoint else ">"
    return "<" if vertex < midpoint else ">"


def extract_puzzle(payload: bytes) -> tuple[Puzzle, np.ndarray, dict[str, Any]]:
    """Extract a Futoshiki board from encoded JPEG/PNG bytes.

    The function never accepts user corrections: it either produces validated
    semantic data or raises `ExtractionError` for the UI to report.
    """
    image = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ExtractionError("The uploaded file is not a readable image")
    corners = _find_board_corners(image)
    warped = _warp_board(image, corners)
    size = _infer_size(warped)
    side = warped.shape[0]
    cell = side / size
    givens: list[Given] = []
    inequalities: list[Inequality] = []
    confidence: list[float] = []
    for row in range(size):
        for col in range(size):
            pad = int(cell * 0.20)
            top, bottom = int(row * cell) + pad, int((row + 1) * cell) - pad
            left, right = int(col * cell) + pad, int((col + 1) * cell) - pad
            value, score = _ocr_digit(warped[top:bottom, left:right], size)
            if value is not None:
                givens.append(Given(row, col, value))
                confidence.append(score)
    gap = max(12, int(cell * 0.19))
    for row in range(size):
        for col in range(size - 1):
            x = int((col + 1) * cell)
            y1, y2 = int(row * cell + cell * 0.28), int((row + 1) * cell - cell * 0.28)
            relation = _classify_gap(warped[y1:y2, x - gap:x + gap], horizontal_gap=True)
            if relation:
                inequalities.append(Inequality(Position(row, col), relation, Position(row, col + 1)))
    for row in range(size - 1):
        for col in range(size):
            y = int((row + 1) * cell)
            x1, x2 = int(col * cell + cell * 0.28), int((col + 1) * cell - cell * 0.28)
            relation = _classify_gap(warped[y - gap:y + gap, x1:x2], horizontal_gap=False)
            if relation:
                inequalities.append(Inequality(Position(row, col), relation, Position(row + 1, col)))
    try:
        puzzle = Puzzle(size=size, givens=tuple(givens), inequalities=tuple(inequalities))
    except PuzzleValidationError as error:
        raise ExtractionError(str(error)) from error
    return puzzle, image, {"warped": warped, "corners": corners, "size": size, "mean_ocr_confidence": float(np.mean(confidence)) if confidence else 0.0}
