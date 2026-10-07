import json
from pathlib import Path
import sys

import numpy as np
import pytest
import pytesseract

from src.futoshiki import vision
from src.futoshiki.models import Puzzle


def test_explicit_engine_path_takes_priority(monkeypatch, tmp_path) -> None:
    executable = tmp_path / "OCR engine" / "tesseract.exe"
    monkeypatch.setenv("TESSERACT_CMD", str(executable))
    assert vision._find_tesseract() == str(executable)


def test_engine_can_be_found_on_path(monkeypatch) -> None:
    monkeypatch.delenv("TESSERACT_CMD", raising=False)
    monkeypatch.setattr(vision.shutil, "which", lambda command: "/opt/ocr/tesseract")
    assert vision._find_tesseract() == "/opt/ocr/tesseract"


def test_missing_engine_reports_actionable_extraction_error(monkeypatch) -> None:
    monkeypatch.setattr(vision, "_find_tesseract", lambda command: None)

    def missing_engine(*args, **kwargs):
        raise pytesseract.TesseractNotFoundError()

    monkeypatch.setattr(pytesseract, "image_to_data", missing_engine)
    with pytest.raises(vision.ExtractionError, match="TESSERACT_CMD"):
        vision._ocr_digit(np.full((120, 120, 3), 255, dtype=np.uint8), 4)


def test_missing_language_data_reports_extraction_error(monkeypatch) -> None:
    monkeypatch.setattr(vision, "_find_tesseract", lambda command: None)

    def missing_language(*args, **kwargs):
        raise pytesseract.TesseractError(1, "Error opening data file eng.traineddata")

    monkeypatch.setattr(pytesseract, "image_to_data", missing_language)
    with pytest.raises(vision.ExtractionError, match="English"):
        vision._ocr_digit(np.full((120, 120, 3), 255, dtype=np.uint8), 4)


def test_missing_python_wrapper_is_not_silently_treated_as_empty(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    with pytest.raises(vision.ExtractionError, match="requirements.txt"):
        vision._ocr_digit(np.full((120, 120, 3), 255, dtype=np.uint8), 4)


@pytest.mark.skipif(vision._find_tesseract() is None, reason="Tesseract engine is not installed")
def test_dataset_image_is_recognized_with_real_ocr() -> None:
    directory = Path(__file__).resolve().parents[1] / "data" / "dataset"
    expected = Puzzle.from_dict(json.loads((directory / "01_4x4_digital.json").read_text()))
    actual, _, _ = vision.extract_puzzle((directory / "01_4x4_digital.png").read_bytes())
    assert actual.size == expected.size
    assert set(actual.givens) == set(expected.givens)
    assert set(actual.inequalities) == set(expected.inequalities)
