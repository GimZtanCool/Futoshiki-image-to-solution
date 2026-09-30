from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


class PuzzleValidationError(ValueError):
    """Raised when extracted puzzle data cannot be represented safely."""


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        try:
            return cls(row=int(data["row"]), col=int(data["col"]))
        except (KeyError, TypeError, ValueError) as error:
            raise PuzzleValidationError("Positions require integer row and col values") from error

    def to_dict(self) -> dict[str, int]:
        return {"row": self.row, "col": self.col}


@dataclass(frozen=True)
class Given:
    row: int
    col: int
    value: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Given":
        try:
            return cls(int(data["row"]), int(data["col"]), int(data["value"]))
        except (KeyError, TypeError, ValueError) as error:
            raise PuzzleValidationError("Givens require integer row, col, and value") from error

    def to_dict(self) -> dict[str, int]:
        return {"row": self.row, "col": self.col, "value": self.value}


@dataclass(frozen=True)
class Inequality:
    first: Position
    relation: Literal["<", ">"]
    second: Position

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Inequality":
        relation = data.get("relation")
        if relation not in {"<", ">"}:
            raise PuzzleValidationError("Inequality relation must be '<' or '>'")
        return cls(Position.from_dict(data["first"]), relation, Position.from_dict(data["second"]))

    def to_dict(self) -> dict[str, Any]:
        return {"first": self.first.to_dict(), "relation": self.relation, "second": self.second.to_dict()}


@dataclass(frozen=True)
class Puzzle:
    size: int
    givens: tuple[Given, ...]
    inequalities: tuple[Inequality, ...]

    def __post_init__(self) -> None:
        if self.size < 2:
            raise PuzzleValidationError("Puzzle size must be at least 2")
        cells: set[tuple[int, int]] = set()
        for given in self.givens:
            self._validate_position(Position(given.row, given.col))
            if not 1 <= given.value <= self.size:
                raise PuzzleValidationError(f"Given {given.value} is outside domain 1..{self.size}")
            key = (given.row, given.col)
            if key in cells:
                raise PuzzleValidationError(f"Duplicate given at {key}")
            cells.add(key)
        seen_relations: set[tuple[Position, str, Position]] = set()
        for inequality in self.inequalities:
            self._validate_position(inequality.first)
            self._validate_position(inequality.second)
            distance = abs(inequality.first.row - inequality.second.row) + abs(inequality.first.col - inequality.second.col)
            if distance != 1:
                raise PuzzleValidationError("Inequalities must connect adjacent cells")
            key = (inequality.first, inequality.relation, inequality.second)
            if key in seen_relations:
                raise PuzzleValidationError("Duplicate inequality")
            seen_relations.add(key)

    def _validate_position(self, position: Position) -> None:
        if not (0 <= position.row < self.size and 0 <= position.col < self.size):
            raise PuzzleValidationError(f"Position {position} is outside the board")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Puzzle":
        try:
            return cls(
                size=int(data["size"]),
                givens=tuple(Given.from_dict(item) for item in data.get("givens", [])),
                inequalities=tuple(Inequality.from_dict(item) for item in data.get("inequalities", [])),
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, PuzzleValidationError):
                raise
            raise PuzzleValidationError("Puzzle requires an integer size") from error

    def to_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "givens": [given.to_dict() for given in self.givens],
            "inequalities": [item.to_dict() for item in self.inequalities],
        }
