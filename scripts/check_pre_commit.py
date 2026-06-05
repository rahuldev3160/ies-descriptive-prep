#!/usr/bin/env python3
"""
Auto-discovers pre-commit checks from .knowledge/bugs/*.md frontmatter.

To add a new auto-check: open the bug record and add hook_* fields.
This script finds them, runs the checks, and blocks commits that violate them.
No manual hook editing needed.

Hook fields (all optional except hook_pattern):
  hook_pattern  — Python re pattern to match bad code
  hook_exclude  — Python re pattern for lines that are safe (e.g. .method() calls)
  hook_scope    — glob matching filenames to check (default: *.html)
  hook_message  — one-line description shown when blocked
  hook_ref      — where to read more (CLAUDE.md entry, bug record)
"""

import fnmatch
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(r.stdout.strip())


def staged_files() -> list[str]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True,
    )
    return r.stdout.splitlines()


def parse_hook(md_path: Path) -> dict | None:
    """Return hook config from a bug record's frontmatter, or None if absent."""
    try:
        text = md_path.read_text()
    except OSError:
        return None

    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None

    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            fields[k.strip()] = v.strip()

    if "hook_pattern" not in fields:
        return None

    return {
        "name":    fields.get("name", md_path.stem),
        "pattern": fields["hook_pattern"],
        "exclude": fields.get("hook_exclude", ""),
        "scope":   fields.get("hook_scope", "*.html"),
        "message": fields.get("hook_message", ""),
        "ref":     fields.get("hook_ref", ""),
    }


def discover_checks(root: Path) -> list[dict]:
    bugs_dir = root / ".knowledge" / "bugs"
    if not bugs_dir.exists():
        return []
    checks = []
    for md in sorted(bugs_dir.glob("*.md")):
        hook = parse_hook(md)
        if hook:
            checks.append(hook)
    return checks


def check_file(path: Path, pattern: str, exclude: str) -> list[tuple[int, str]]:
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return []
    hits = []
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            if exclude and re.search(exclude, line):
                continue
            hits.append((i, line.strip()))
    return hits


def main() -> None:
    root = repo_root()
    staged = staged_files()
    if not staged:
        sys.exit(0)

    checks = discover_checks(root)
    if not checks:
        sys.exit(0)

    fail = False
    for check in checks:
        targets = [
            f for f in staged
            if fnmatch.fnmatch(Path(f).name, check["scope"])
        ]
        if not targets:
            continue

        hits_by_file: dict[str, list[tuple[int, str]]] = {}
        for rel in targets:
            hits = check_file(root / rel, check["pattern"], check["exclude"])
            if hits:
                hits_by_file[rel] = hits

        if not hits_by_file:
            continue

        print(f"\nBLOCKED  {check['name']}: {check['message']}")
        for rel, hits in hits_by_file.items():
            print(f"  {rel}")
            for lineno, line in hits[:5]:
                print(f"    line {lineno}: {line}")
        if check["ref"]:
            print(f"  See: {check['ref']}")
        fail = True

    if fail:
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
