#!/usr/bin/env python3
"""Build analysis/index.json from the markdown files in analysis/.

The manifest is the single source of truth the frontend uses to list matches.
Running this script after adding or editing a markdown file keeps the site in
sync. CI verifies the committed manifest matches the output of this script.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"
MANIFEST_PATH = ANALYSIS_DIR / "index.json"

VIDEO_ID_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([^&\s)]+)")
LABEL_LINE_RE = re.compile(r"^(?P<key>[A-Za-z]+)\s*:\s*(?P<value>.*)$")


def _split_labels(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _first_match(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    v = value.strip().lower()
    if v in {"yes", "true"}:
        return True
    if v in {"no", "false"}:
        return False
    return None


def parse_match(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")

    # Derive title/event/year from the filename so we have a stable default.
    stem = path.stem
    if "_" in stem:
        match_part, event_part = stem.split("_", 1)
    else:
        match_part, event_part = stem, ""
    title = match_part.replace("-", " ")
    event = event_part.replace("-", " ").strip()

    year_match = re.search(r"(19|20)\d{2}", event)
    year = int(year_match.group(0)) if year_match else None

    video_url = _first_match(r"\*\*Video URL\*\*:\s*(\S+)", content) or ""
    video_id_match = VIDEO_ID_RE.search(video_url)
    video_id = video_id_match.group(1) if video_id_match else ""

    winner = _first_match(r"\*\*Winner\*\*:\s*(.+)", content)
    submission_type = _first_match(r"\*\*Submission Type\*\*:\s*(.+)", content)
    submission_finish = _parse_bool(
        _first_match(r"\*\*Submission Finish\*\*:\s*(.+)", content)
    )
    if submission_type and submission_type.strip().upper() == "N/A":
        submission_type = None

    # Label list block sits between "## Label List" and the next header.
    label_block_match = re.search(
        r"## Label List\s*\n(?P<body>[\s\S]*?)(?=\n##|\Z)", content
    )
    positions: list[str] = []
    techniques: list[str] = []
    submissions: list[str] = []
    transitions: list[str] = []
    if label_block_match:
        for raw_line in label_block_match.group("body").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            m = LABEL_LINE_RE.match(line)
            if not m:
                continue
            key = m.group("key").lower()
            values = _split_labels(m.group("value"))
            if key.startswith("position"):
                positions = values
            elif key.startswith("technique"):
                techniques = values
            elif key.startswith("submission"):
                submissions = values
            elif key.startswith("transition"):
                transitions = values

    return {
        "file": path.name,
        "title": title,
        "event": event,
        "year": year,
        "videoUrl": video_url,
        "videoId": video_id,
        "winner": winner,
        "submissionType": submission_type,
        "submissionFinish": submission_finish,
        "labels": {
            "positions": positions,
            "techniques": techniques,
            "submissions": submissions,
            "transitions": transitions,
        },
    }


def build_manifest() -> dict[str, Any]:
    md_files = sorted(
        p for p in ANALYSIS_DIR.glob("*.md") if p.name.lower() != "readme.md"
    )
    matches = [parse_match(p) for p in md_files]
    return {
        "version": 1,
        "count": len(matches),
        "matches": matches,
    }


def serialize(manifest: dict[str, Any]) -> str:
    # Deterministic output: sorted keys, 2-space indent, trailing newline.
    return json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    manifest = build_manifest()
    serialized = serialize(manifest)

    check = "--check" in sys.argv
    if check:
        current = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else ""
        if current != serialized:
            sys.stderr.write(
                f"{MANIFEST_PATH.relative_to(REPO_ROOT)} is out of date. "
                "Run `python scripts/build_manifest.py` and commit the result.\n"
            )
            return 1
        print(f"{MANIFEST_PATH.relative_to(REPO_ROOT)} is up to date ({manifest['count']} matches).")
        return 0

    MANIFEST_PATH.write_text(serialized, encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(REPO_ROOT)} with {manifest['count']} matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
