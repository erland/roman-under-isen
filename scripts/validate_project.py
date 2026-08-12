#!/usr/bin/env python3
"""Snabb deterministisk validering för Romanskaparen-projektet Under isen.

Avsedd för både lokal körning och GitHub Actions. Använder endast Python-
standardbiblioteket.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

CHAPTER_RE = re.compile(r"kapitel-(\d{2,})\.md$")
CHAPTER_H1_RE = re.compile(r"^#\s+Kapitel\s+(\d+)\s+[–-]\s+(.+?)\s*$")
MARKERS = ("TODO", "FIXME", "[PLACEHOLDER]")

REQUIRED_PATHS = (
    "README.md",
    "roman-bibel.md",
    "synopsis.md",
    "kapitelplan.md",
    "projektstatus.md",
    "epub-metadata.md",
    "forsattssida.md",
    "om-boken.md",
    "kapitel",
    "publishing/metadata.yaml",
    "publishing/epub.css",
    "publishing/fix-epub-after-pandoc.py",
    "publishing/pdf-template.tex",
    "publishing/pdf-filter.lua",
    "scripts/build_book.py",
    "scripts/validate_project.py",
)

REQUIRED_METADATA_KEYS = ("title", "author", "language")


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"ERROR: {message}", file=sys.stderr)


def parse_simple_yaml_scalars(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or key.startswith("-"):
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def validate_markdown_links(root: Path, errors: list[str]) -> None:
    link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for md in sorted(root.rglob("*.md")):
        if any(part in {".git"} for part in md.relative_to(root).parts):
            continue
        text = md.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            target = target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if " " in target and not target.startswith(("./", "../")):
                target = target.split(" ", 1)[0]
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                continue
            if not candidate.exists():
                add_error(errors, f"Trasig intern Markdown-länk i {md.relative_to(root)}: {target}")


def validate_chapters(root: Path, errors: list[str]) -> None:
    chapter_dir = root / "kapitel"
    chapters = sorted(
        (int(m.group(1)), path)
        for path in chapter_dir.glob("kapitel-*.md")
        if (m := CHAPTER_RE.match(path.name))
    )
    if not chapters:
        add_error(errors, "Inga kapitel hittades i kapitel/ med mönstret kapitel-XX.md.")
        return

    numbers = [n for n, _ in chapters]
    expected = list(range(1, max(numbers) + 1))
    if numbers != expected:
        add_error(errors, f"Kapitelserien har luckor eller fel ordning: {numbers}")

    if len(chapters) != 28:
        add_error(errors, f"Förväntade 28 kapitel, hittade {len(chapters)}.")

    for number, path in chapters:
        text = path.read_text(encoding="utf-8").strip()
        rel = path.relative_to(root)
        if not text:
            add_error(errors, f"Tomt kapitel: {rel}")
            continue
        first = text.splitlines()[0].strip()
        match = CHAPTER_H1_RE.match(first)
        if not match:
            add_error(errors, f"Fel H1-format i {rel}: {first!r}")
            continue
        h1_number = int(match.group(1))
        if h1_number != number:
            add_error(errors, f"Kapitelnummer i rubrik matchar inte filnamn i {rel}: {h1_number} != {number}")
        body_without_notes = re.split(r"\n---\s*\n\s*Kort kapitelnotering:", text, maxsplit=1)[0].strip()
        if len(body_without_notes.split()) < 200:
            add_error(errors, f"Kapitlet verkar mycket kort före kapitelnotering: {rel}")

        for marker in MARKERS:
            if marker in text:
                add_error(errors, f"Arbetsmarkör {marker!r} finns kvar i {rel}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Projektrot")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    errors: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            add_error(errors, f"Obligatorisk sökväg saknas: {rel}")

    metadata_path = root / "publishing" / "metadata.yaml"
    if metadata_path.exists():
        metadata = parse_simple_yaml_scalars(metadata_path)
        for key in REQUIRED_METADATA_KEYS:
            if not metadata.get(key):
                add_error(errors, f"Metadata saknar värde för: {key}")
        if metadata.get("title") != "Under isen":
            add_error(errors, "publishing/metadata.yaml ska ha title: Under isen")
        if metadata.get("author") != "Erland Lindmark":
            add_error(errors, "publishing/metadata.yaml ska ha author: Erland Lindmark")

    validate_chapters(root, errors)
    validate_markdown_links(root, errors)

    if errors:
        print(f"\nValidering misslyckades med {len(errors)} fel.", file=sys.stderr)
        return 1
    print("Validering OK: projektstruktur, metadata och kapitelserie ser konsekventa ut.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
