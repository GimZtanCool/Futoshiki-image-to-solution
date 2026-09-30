from __future__ import annotations

import cv2
import numpy as np

from .models import Puzzle


def draw_clean_solution(puzzle: Puzzle, solution: list[list[int]], cell_size: int = 110) -> np.ndarray:
    """Return a presentation-ready BGR grid; original givens are blue, solved cells green."""
    margin = 35
    side = puzzle.size * cell_size
    canvas = np.full((side + 2 * margin, side + 2 * margin, 3), 255, dtype=np.uint8)
    given_cells = {(given.row, given.col) for given in puzzle.givens}
    for index in range(puzzle.size + 1):
        offset = margin + index * cell_size
        cv2.line(canvas, (margin, offset), (margin + side, offset), (30, 30, 30), 2)
        cv2.line(canvas, (offset, margin), (offset, margin + side), (30, 30, 30), 2)
    for row in range(puzzle.size):
        for col in range(puzzle.size):
            color = (190, 70, 20) if (row, col) in given_cells else (25, 135, 25)
            text = str(solution[row][col])
            origin = (margin + col * cell_size + 42, margin + row * cell_size + 72)
            cv2.putText(canvas, text, origin, cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3, cv2.LINE_AA)
    for relation in puzzle.inequalities:
        a, b = relation.first, relation.second
        x1, y1 = margin + a.col * cell_size + cell_size // 2, margin + a.row * cell_size + cell_size // 2
        x2, y2 = margin + b.col * cell_size + cell_size // 2, margin + b.row * cell_size + cell_size // 2
        symbol = relation.relation
        x, y = (x1 + x2) // 2 - 12, (y1 + y2) // 2 + 10
        cv2.putText(canvas, symbol, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (60, 60, 60), 2, cv2.LINE_AA)
    return canvas


def overlay_solution(image: np.ndarray, puzzle: Puzzle, solution: list[list[int]], corners: np.ndarray) -> np.ndarray:
    """Project non-given values onto the detected board quadrilateral."""
    output = image.copy()
    given_cells = {(given.row, given.col) for given in puzzle.givens}
    board_side = 800
    layer = np.zeros((board_side, board_side, 4), dtype=np.uint8)
    cell = board_side / puzzle.size
    for row in range(puzzle.size):
        for col in range(puzzle.size):
            if (row, col) in given_cells:
                continue
            cv2.putText(layer, str(solution[row][col]), (int((col + 0.38) * cell), int((row + 0.68) * cell)), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (20, 160, 20, 255), 3, cv2.LINE_AA)
    destination = np.array(corners, dtype=np.float32)
    source = np.array([[0, 0], [board_side - 1, 0], [board_side - 1, board_side - 1], [0, board_side - 1]], dtype=np.float32)
    transform = cv2.getPerspectiveTransform(source, destination)
    warped = cv2.warpPerspective(layer, transform, (image.shape[1], image.shape[0]))
    alpha = warped[:, :, 3:4] / 255.0
    output[:] = (output * (1 - alpha) + warped[:, :, :3] * alpha).astype(np.uint8)
    return output
