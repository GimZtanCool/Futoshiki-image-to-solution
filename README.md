# TB1 — Futoshiki image-to-solution pipeline

This project reads a 4×4 or 5×5 Futoshiki puzzle image, extracts the givens and inequality relations, solves it with Constraint Programming, and renders the result.

## Install

Python 3.11–3.13 is recommended (some scientific dependencies may not yet publish wheels for newer Python releases).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For digit OCR, install the system binary `tesseract-ocr` as well. The app still works with the included JSON example when Tesseract is unavailable.

## Run

```bash
streamlit run app.py
```

Upload a puzzle image, or select **Load bundled example**. The app shows the extracted semantic data, solves it automatically, and presents a clean solution plus an overlay.

## Test

```bash
pytest
```

## Input contract

The extractor passes this JSON-compatible structure to the solver:

```json
{
  "size": 4,
  "givens": [{"row": 0, "col": 0, "value": 1}],
  "inequalities": [{
    "first": {"row": 0, "col": 0},
    "relation": "<",
    "second": {"row": 0, "col": 1}
  }]
}
```

Coordinates are zero-based. Every relation is semantic (`first < second` or `first > second`), so horizontal and vertical symbols share the same solver interface.

## Project layout

- `src/futoshiki/models.py`: validation and shared data model.
- `src/futoshiki/solver.py`: generic OR-Tools CP-SAT model.
- `src/futoshiki/vision.py`: perspective correction, grid discovery, OCR, and inequality detection.
- `src/futoshiki/render.py`: clean-grid and image-overlay rendering.
- `tests/`: unit and integration-ready tests.

## Dataset protocol

Place an image and a same-named JSON ground-truth file in `data/dataset/`, for example `photo_01.jpg` and `photo_01.json`. Run `python -m scripts.evaluate_dataset data/dataset` from the repository root to report grid-size, given-digit, inequality, exact-extraction, and end-to-end solve metrics.

The repository includes 10 image/JSON pairs covering 4×4 and 5×5 boards, digital inputs, simulated perspective, contrast and lighting changes, JPEG compression, and slight blur. See [`data/dataset/README.md`](data/dataset/README.md) for the inventory and validation details. These examples are synthetic and were adapted to the current extractor. Real photographs of printed boards still need to be added to cover the assignment's printed-image requirement and assess robustness on independent inputs.
