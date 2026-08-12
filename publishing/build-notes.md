# Build notes – Under isen

Markdown är kanonisk källa. Kapitelnoteringar exporteras inte.

## GitHub Actions-publicering

Projektet är förberett för tre arbetsflöden:

1. `Validate` – snabb projekt- och manusvalidering.
2. `Build Preview` – manuell byggning av EPUB och PDF som ett gemensamt artifact.
3. `Release` – byggning av EPUB och PDF vid `v*`-taggar och uppladdning som release assets.

Pandoc-versionen är låst till `3.1.11.1`. PDF byggs med XeLaTeX och TeX Gyre Pagella.

## 2026-08-12 – PDF-mallfix för GitHub Actions

Preview-actionen kunde tidigare bygga EPUB men föll i PDF-steget med:

```text
Undefined control sequence
\tightlist
```

Orsak: Pandoc kan generera `\tightlist` för kompakta Markdown-listor, men den anpassade LaTeX-mallen definierade inte kommandot.

Åtgärd:
- `publishing/pdf-template.tex` definierar nu `\tightlist`.
- Mallen har dessutom en robust font-fallback: TeX Gyre Pagella om den finns, annars Noto Serif eller generell serif.
- Lokal testkörning av `python3 scripts/validate_project.py` gick igenom.
- Lokal testkörning av `python3 scripts/build_book.py --output-dir /mnt/data/book-dist-test-v32c` byggde EPUB och PDF.
