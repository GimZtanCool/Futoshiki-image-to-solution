# TB1 — Futoshiki image-to-solution pipeline

This project reads a 4×4 or 5×5 Futoshiki puzzle image, extracts the givens and inequality relations, solves it with Constraint Programming, and renders the result.

## Install

Python 3.11–3.13 is recommended (some scientific dependencies may not yet publish wheels for newer Python releases).

Installation has two parts: Python dependencies and the Tesseract OCR engine. `requirements.txt` includes `pytesseract`, the Python wrapper that calls Tesseract. It does **not** install the separate Tesseract executable or its language data. Both are needed to recognize digits from uploaded images. See the [pytesseract installation instructions](https://github.com/madmaze/pytesseract#installation) and [Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html).

### Windows (PowerShell)

Run these commands from the repository root to install the Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install Tesseract with Windows Package Manager:

```powershell
winget install --id UB-Mannheim.TesseractOCR --exact --source winget
```

Alternatively, download the Windows installer linked by the [official Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html#windows). Include English language data (`eng`), which the current OCR code uses by default.

Open a new PowerShell terminal and verify that the engine and its language data are available:

```powershell
tesseract --version
tesseract --list-langs
```

If `tesseract` is not recognized, add its installation directory (normally `C:\Program Files\Tesseract-OCR`) to your user `Path` environment variable, then restart the terminal. You can also enable that directory for the current PowerShell session before launching the app:

```powershell
$env:Path = "C:\Program Files\Tesseract-OCR;$env:Path"
tesseract --version
```

If you chose another installation directory, use that path instead.

The app also detects Tesseract installations registered by Windows installers and checks common installation folders. For a custom path, you can explicitly configure the executable without editing Python files:

```powershell
$env:TESSERACT_CMD = 'C:\path\to\Tesseract-OCR\tesseract.exe'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Use the full executable path, including `tesseract.exe`. Stop an already-running Streamlit process with Ctrl+C before relaunching with changed environment variables. Installing another Python package named `tesseract` does not replace the separate OCR engine required by `pytesseract`.

Launch the app with the same virtual environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install the OCR engine separately using the appropriate system package manager:

```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr tesseract-ocr-eng

# macOS with Homebrew
brew install tesseract
```

Verify the installation with `tesseract --version` and `tesseract --list-langs`. The bundled JSON example works without Tesseract, but uploading puzzle images requires the OCR engine.

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

The repository includes 10 image/JSON pairs covering 4×4 and 5×5 boards, digital inputs, simulated perspective, contrast and lighting changes, JPEG compression, and slight blur. See [`data/dataset/README.md`](data/dataset/README.md) for the inventory and validation details. Upload the PNG/JPG files through **Puzzle image** to demonstrate the OCR pipeline. Their JSON companions are expected labels for evaluation. These examples are synthetic images adapted to the current extractor and were validated through image extraction and solving.
