import importlib.util

import pytest

from src.futoshiki.models import Given, Puzzle
from src.futoshiki.solver import solve


pytestmark = pytest.mark.skipif(importlib.util.find_spec("ortools") is None, reason="OR-Tools not installed")


def test_complete_valid_board_is_unique() -> None:
    values = [[1, 2, 3, 4], [2, 3, 4, 1], [3, 4, 1, 2], [4, 1, 2, 3]]
    puzzle = Puzzle(4, tuple(Given(row, col, values[row][col]) for row in range(4) for col in range(4)), ())
    result = solve(puzzle)
    assert result.status == "unique"
    assert result.solution == values


def test_conflicting_givens_are_unsatisfiable() -> None:
    puzzle = Puzzle(4, (Given(0, 0, 1), Given(0, 1, 1)), ())
    assert solve(puzzle).status == "unsatisfiable"


def test_empty_board_has_multiple_solutions() -> None:
    assert solve(Puzzle(4, (), ())).status == "multiple"
