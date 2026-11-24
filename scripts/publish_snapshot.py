"""Merge a collection snapshot with the current repository snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def merge_snapshot_payloads(remote: dict[str, Any], collected: dict[str, Any]) -> dict[str, Any]:
    """Merge rows by ID, preserving the newest collectedAt value per ID."""
    merged: dict[str, dict[str, Any]] = {}
    for payload in (remote, collected):
        for row in payload.get("observations", []):
            row_id = row.get("id")
            if not row_id:
                continue
            current = merged.get(str(row_id))
            if current is None or str(row.get("collectedAt", "")) >= str(current.get("collectedAt", "")):
                merged[str(row_id)] = row

    observations = sorted(
        merged.values(),
        key=lambda row: (str(row.get("collectedAt", "")), str(row.get("id", ""))),
    )
    generated_at = max(
        str(remote.get("generatedAt", "")),
        str(collected.get("generatedAt", "")),
    ) or None
    return {"generatedAt": generated_at, "observations": observations}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collected", type=Path, required=True, help="Collected snapshot JSON")
    parser.add_argument("--target", type=Path, required=True, help="Remote snapshot to update")
    args = parser.parse_args()

    collected = json.loads(args.collected.read_text(encoding="utf-8"))
    remote = json.loads(args.target.read_text(encoding="utf-8")) if args.target.exists() else {}
    merged = merge_snapshot_payloads(remote, collected)
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
