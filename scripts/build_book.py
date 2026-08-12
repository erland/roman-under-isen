#!/usr/bin/env python3
"""Bygg EPUB och PDF från Under isens kanoniska Markdown-kapitel.

Kräver Pandoc. PDF-bygget kräver XeLaTeX och TeX Gyre Pagella.
Kapitelnoteringar exporteras inte.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

PANDOC_VERSION = "3.1.11.1"
CHAPTER_RE = re.compile(r"kapitel-(\d{2,})\.md$")
H1_RE = re.compile(r"^#\s+Kapitel\s+(\d+)\s+[–-]\s+(.+?)\s*$", re.MULTILINE)


def simple_metadata(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "book"


def run(cmd: list[str], cwd: Path) -> None:
    print("+ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def pandoc_version() -> str:
    result = subprocess.run(["pandoc", "--version"], text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("Pandoc finns inte i PATH.")
    first = result.stdout.splitlines()[0]
    match = re.search(r"pandoc\s+([0-9][^\s]*)", first)
    return match.group(1) if match else first


def strip_notes(text: str) -> str:
    return re.split(r"\n---\s*\n\s*Kort kapitelnotering:", text, maxsplit=1)[0].rstrip() + "\n"


def normalize_chapter_heading(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return f"# {match.group(1)}. {match.group(2)}"
    return H1_RE.sub(repl, text, count=1)


def title_page(title: str, author: str) -> str:
    return f"""# {title} {{.unnumbered .title-page}}

::: {{.title-page}}
<p class="book-title">{title}</p>
<p class="author">{author}</p>
:::
"""


def read_front_matter(root: Path, title: str, author: str) -> str:
    parts: list[str] = []
    parts.append(title_page(title, author))
    om_boken = root / "om-boken.md"
    if om_boken.exists():
        text = om_boken.read_text(encoding="utf-8").strip()
        if not text.startswith("#"):
            text = "# Om boken {.unnumbered}\n\n" + text
        else:
            text = re.sub(r"^#\s+(.+)$", r"# \1 {.unnumbered}", text, count=1, flags=re.MULTILINE)
        parts.append(text + "\n")
    return "\n\n\\newpage\n\n".join(parts)


def combined_markdown(root: Path, metadata: dict[str, str]) -> str:
    title = metadata.get("title", "Under isen")
    author = metadata.get("author", "Erland Lindmark")
    header = [
        "---",
        f'title: "{title}"',
        f'author: "{author}"',
        f'lang: "{metadata.get("language", "sv-SE")}"',
        "---",
        "",
    ]
    parts: list[str] = ["\n".join(header), read_front_matter(root, title, author)]

    chapters = sorted(
        (int(m.group(1)), path)
        for path in (root / "kapitel").glob("kapitel-*.md")
        if (m := CHAPTER_RE.match(path.name))
    )
    for number, path in chapters:
        text = strip_notes(path.read_text(encoding="utf-8"))
        text = normalize_chapter_heading(text)
        parts.append(text)
    return "\n\n\\newpage\n\n".join(parts) + "\n"


def find_pdf_font_dir() -> str | None:
    candidates = [
        Path("/usr/share/texmf"),
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
    ]
    for base in candidates:
        if not base.exists():
            continue
        for font in base.rglob("texgyrepagella-regular.otf"):
            needed = [
                font.parent / "texgyrepagella-regular.otf",
                font.parent / "texgyrepagella-bold.otf",
                font.parent / "texgyrepagella-italic.otf",
                font.parent / "texgyrepagella-bolditalic.otf",
            ]
            if all(p.exists() for p in needed):
                return str(font.parent) + "/"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Projektrot")
    parser.add_argument("--output-dir", default="dist", help="Utdatamapp")
    parser.add_argument("--skip-pdf", action="store_true", help="Bygg endast EPUB")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    outdir = Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    version = pandoc_version()
    if version != PANDOC_VERSION:
        raise RuntimeError(f"Fel Pandoc-version: {version}. Förväntade {PANDOC_VERSION}.")

    metadata_path = root / "publishing" / "metadata.yaml"
    metadata = simple_metadata(metadata_path)
    title = metadata.get("title", "Under isen")
    slug = slugify(title)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        manuscript = tmp / "under-isen-export.md"
        manuscript.write_text(combined_markdown(root, metadata), encoding="utf-8")

        epub = outdir / f"{slug}.epub"
        epub_cmd = [
            "pandoc",
            str(manuscript),
            "--from=markdown+implicit_figures+fenced_divs",
            "--to=epub3",
            "--standalone",
            "--toc",
            "--toc-depth=1",
            "--metadata-file", str(metadata_path),
            "--css", str(root / "publishing" / "epub.css"),
            "--output", str(epub),
        ]
        run(epub_cmd, cwd=root)

        fixer = root / "publishing" / "fix-epub-after-pandoc.py"
        if fixer.exists():
            run([sys.executable, str(fixer), str(epub)], cwd=root)

        if not args.skip_pdf:
            pdf = outdir / f"{slug}.pdf"
            pdf_cmd = [
                "pandoc",
                str(manuscript),
                "--from=markdown+implicit_figures+fenced_divs",
                "--standalone",
                "--toc",
                "--toc-depth=1",
                "--metadata-file", str(metadata_path),
                "--pdf-engine=xelatex",
                "--template", str(root / "publishing" / "pdf-template.tex"),
                "--lua-filter", str(root / "publishing" / "pdf-filter.lua"),
            ]
            font_dir = find_pdf_font_dir()
            if font_dir:
                pdf_cmd.extend(["--metadata", f"pdf-font-dir={font_dir}"])
            pdf_cmd.extend(["--output", str(pdf)])
            run(pdf_cmd, cwd=root)

    print(f"Byggt till: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
