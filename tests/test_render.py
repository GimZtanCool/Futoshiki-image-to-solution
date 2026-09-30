import numpy as np

from src.futoshiki.models import Given, Puzzle
from src.futoshiki.render import draw_clean_solution


def test_clean_render_has_expected_canvas_shape() -> None:
    image = draw_clean_solution(Puzzle(4, (Given(0, 0, 1),), ()), [[1, 2, 3, 4], [2, 3, 4, 1], [3, 4, 1, 2], [4, 1, 2, 3]])
    assert image.shape == (510, 510, 3)
    assert image.dtype == np.uint8
