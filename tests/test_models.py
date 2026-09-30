import pytest

from src.futoshiki.models import Puzzle, PuzzleValidationError


def test_round_trip_preserves_semantic_relation() -> None:
    source = {
        "size": 4,
        "givens": [{"row": 0, "col": 0, "value": 1}],
        "inequalities": [{"first": {"row": 0, "col": 0}, "relation": "<", "second": {"row": 1, "col": 0}}],
    }
    assert Puzzle.from_dict(source).to_dict() == source


@pytest.mark.parametrize(
    "data",
    [
        {"size": 4, "givens": [{"row": 4, "col": 0, "value": 1}]},
        {"size": 4, "givens": [{"row": 0, "col": 0, "value": 5}]},
        {"size": 4, "inequalities": [{"first": {"row": 0, "col": 0}, "relation": "<", "second": {"row": 2, "col": 0}}]},
    ],
)
def test_invalid_data_is_rejected(data: dict) -> None:
    with pytest.raises(PuzzleValidationError):
        Puzzle.from_dict(data)
