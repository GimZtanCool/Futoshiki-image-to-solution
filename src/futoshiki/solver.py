from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import Puzzle


@dataclass(frozen=True)
class SolveResult:
    status: Literal["unique", "multiple", "unsatisfiable", "unavailable"]
    solution: list[list[int]] | None

    @property
    def status_message(self) -> str:
        return {
            "unique": "Unique solution found.",
            "multiple": "A valid solution was found, but the puzzle is not unique.",
            "unsatisfiable": "The extracted constraints are inconsistent.",
            "unavailable": "OR-Tools is not installed. Install requirements.txt to solve puzzles.",
        }[self.status]


def solve(puzzle: Puzzle) -> SolveResult:
    """Solve a parameterized Futoshiki satisfaction problem and test uniqueness."""
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return SolveResult("unavailable", None)

    model = cp_model.CpModel()
    board = [[model.NewIntVar(1, puzzle.size, f"x_{row}_{col}") for col in range(puzzle.size)] for row in range(puzzle.size)]
    for row in range(puzzle.size):
        model.AddAllDifferent(board[row])
    for col in range(puzzle.size):
        model.AddAllDifferent([board[row][col] for row in range(puzzle.size)])
    for given in puzzle.givens:
        model.Add(board[given.row][given.col] == given.value)
    for relation in puzzle.inequalities:
        left = board[relation.first.row][relation.first.col]
        right = board[relation.second.row][relation.second.col]
        model.Add(left < right if relation.relation == "<" else left > right)

    class FirstTwoSolutions(cp_model.CpSolverSolutionCallback):
        def __init__(self) -> None:
            super().__init__()
            self.solutions: list[list[list[int]]] = []

        def on_solution_callback(self) -> None:
            self.solutions.append([[self.Value(board[row][col]) for col in range(puzzle.size)] for row in range(puzzle.size)])
            if len(self.solutions) == 2:
                self.StopSearch()

    # Futoshiki is a satisfaction problem: enumerate only enough solutions to
    # distinguish a uniquely solvable board from an ambiguous one.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    callback = FirstTwoSolutions()
    status = solver.SearchForAllSolutions(model, callback)
    if not callback.solutions:
        return SolveResult("unsatisfiable", None)
    return SolveResult("multiple" if len(callback.solutions) > 1 else "unique", callback.solutions[0])
