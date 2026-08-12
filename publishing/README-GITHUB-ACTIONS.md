# GitHub Actions-publicering

Den här katalogen är införd enligt konceptet i det bifogade Romanskaparen-publiceringskitet.

## Struktur

`.github/` ligger i projektroten, på samma nivå som `README.md`.

```text
.github/
  workflows/
    01-validate.yml
    02-build-preview.yml
    03-release.yml
scripts/
  validate_project.py
  build_book.py
publishing/
  metadata.yaml
  epub.css
  fix-epub-after-pandoc.py
  pdf-template.tex
  pdf-filter.lua
```

## Arbetsflöden

- `01-validate.yml` kör snabb validering vid push/pull request mot `main`.
- `02-build-preview.yml` startas manuellt och bygger EPUB + PDF till artifact `under-isen-preview`.
- `03-release.yml` körs på taggar `v*` och publicerar EPUB + PDF som separata release assets.

## Byggkommandon

```bash
python3 scripts/validate_project.py .
python3 scripts/build_book.py --output-dir dist
```

Pandoc-versionen är låst till `3.1.11.1`.
