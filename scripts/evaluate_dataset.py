"""Evaluate image extraction against same-named JSON ground-truth files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from src.futoshiki.models import Puzzle
from src.futoshiki.solver import solve
from src.futoshiki.vision import ExtractionError, extract_puzzle


def score(expected: Puzzle, actual: Puzzle) -> dict[str, int]:
    expected_givens = {(item.row, item.col, item.value) for item in expected.givens}
    actual_givens = {(item.row, item.col, item.value) for item in actual.givens}
    expected_relations = {(item.first, item.relation, item.second) for item in expected.inequalities}
    actual_relations = {(item.first, item.relation, item.second) for item in actual.inequalities}
    return {
        "size": int(expected.size == actual.size),
        "givens_correct": len(expected_givens & actual_givens),
        "givens_total": len(expected_givens),
        "relations_correct": len(expected_relations & actual_relations),
        "relations_total": len(expected_relations),
        "exact": int(
            expected.size == actual.size
            and expected_givens == actual_givens
            and expected_relations == actual_relations
        ),
    }


def percentage(correct: int, total: int) -> str:
    return "n/a" if total == 0 else f"{correct / total:.1%}"


def main(directory: Path) -> int:
    images = [path for path in directory.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    if not images:
        print("No dataset images found. Add image/JSON pairs to data/dataset/.")
        return 1
    totals = {key: 0 for key in ("size", "givens_correct", "givens_total", "relations_correct", "relations_total", "exact", "solved")}
    processed = 0
    for image_path in sorted(images):
        truth_path = image_path.with_suffix(".json")
        if not truth_path.exists():
            print(f"SKIP {image_path.name}: missing {truth_path.name}")
            continue
        processed += 1
        expected = Puzzle.from_dict(json.loads(truth_path.read_text()))
        try:
            actual, _, _ = extract_puzzle(image_path.read_bytes())
            row = score(expected, actual)
            row["solved"] = int(solve(actual).status in {"unique", "multiple"})
            print(f"{image_path.name}: exact={bool(row['exact'])}, solve={bool(row['solved'])}")
        except ExtractionError as error:
            print(f"{image_path.name}: extraction failed ({error})")
            row = {key: 0 for key in totals if key != "solved"}
            row["solved"] = 0
        for key, value in row.items():
            totals[key] += value
    if processed == 0:
        print("No image has a matching JSON ground-truth file.")
        return 1
    count = processed
    print(f"Grid size: {percentage(totals['size'], count)}")
    print(f"Given digits: {percentage(totals['givens_correct'], totals['givens_total'])}")
    print(f"Inequalities: {percentage(totals['relations_correct'], totals['relations_total'])}")
    print(f"Exact boards: {percentage(totals['exact'], count)}")
    print(f"End-to-end solved: {percentage(totals['solved'], count)}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("data/dataset")
    raise SystemExit(main(target))
