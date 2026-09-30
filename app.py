from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.futoshiki.models import Puzzle
from src.futoshiki.render import draw_clean_solution, overlay_solution
from src.futoshiki.solver import solve
from src.futoshiki.vision import ExtractionError, extract_puzzle


ROOT = Path(__file__).parent


def load_example() -> Puzzle:
    with (ROOT / "data" / "examples" / "futoshiki_4x4.json").open() as handle:
        return Puzzle.from_dict(json.load(handle))


st.set_page_config(page_title="Futoshiki Solver", layout="wide")
st.title("Futoshiki: image → constraints → solution")
st.caption("Upload a 4×4 or 5×5 board. No manual transcription is used in the image pipeline.")

uploaded = st.file_uploader("Puzzle image", type=["png", "jpg", "jpeg"])
use_example = st.checkbox("Load bundled example", value=uploaded is None)

puzzle: Puzzle | None = None
source_image = None
debug = None

try:
    if uploaded is not None:
        payload = uploaded.getvalue()
        puzzle, source_image, debug = extract_puzzle(payload)
    elif use_example:
        puzzle = load_example()
except ExtractionError as error:
    st.error(f"Could not extract a valid puzzle: {error}")

if puzzle is not None:
    left, right = st.columns(2)
    with left:
        st.subheader("Extracted puzzle")
        st.json(puzzle.to_dict())
        if debug:
            st.caption(f"Detected {debug['size']}×{debug['size']} board")
            st.image(debug["warped"], caption="Perspective-corrected board", channels="BGR")

    result = solve(puzzle)
    with right:
        st.subheader("Solver result")
        st.write(result.status_message)
        if result.solution:
            clean = draw_clean_solution(puzzle, result.solution)
            st.image(clean, caption="Solved board", channels="BGR")
            if source_image is not None:
                st.image(
                    overlay_solution(source_image, puzzle, result.solution, debug["corners"]),
                    caption="Solution over the original image",
                    channels="BGR",
                )
        elif result.status == "multiple":
            st.info("The extracted instance has more than one solution.")
