#!/usr/bin/env python3
"""Fail when a SKILL.md contains a broken relative Markdown link."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK = re.compile(r"]\(([^)\n]+)\)")
REPOSITORY_BLOB_PREFIX = (
    "https://github.com/jsj9346/agent-skills/blob/main/"
)


def local_target(
    raw_destination: str, *, repo_root: Path, skill_file: Path
) -> Path | None:
    destination = raw_destination.strip()
    if destination.startswith("<") and ">" in destination:
        destination = destination[1 : destination.index(">")]
    else:
        destination = destination.split(maxsplit=1)[0]

    if not destination or destination.startswith(("#", "//")):
        return None

    if destination.startswith(REPOSITORY_BLOB_PREFIX):
        repository_path = destination.removeprefix(REPOSITORY_BLOB_PREFIX)
        return repo_root / unquote(repository_path.split("#", maxsplit=1)[0])

    parsed = urlsplit(destination)
    if parsed.scheme or not parsed.path:
        return None

    return skill_file.parent / unquote(parsed.path)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    skill_files = sorted(repo_root.rglob("SKILL.md"))
    failures: list[str] = []
    checked_links = 0

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = local_target(
                match.group(1), repo_root=repo_root, skill_file=skill_file
            )
            if target is None:
                continue

            checked_links += 1
            if not target.exists():
                line = text.count("\n", 0, match.start()) + 1
                relative_skill = skill_file.relative_to(repo_root)
                try:
                    missing_target = target.relative_to(repo_root)
                except ValueError:
                    missing_target = target
                failures.append(
                    f"{relative_skill}:{line}: missing {missing_target}"
                )

    if failures:
        print("Broken relative links in SKILL.md files:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Validated {checked_links} local skill links across "
        f"{len(skill_files)} SKILL.md files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
