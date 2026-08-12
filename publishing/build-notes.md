# Build notes – Under isen

Markdown är kanonisk källa. Kapitelnoteringar exporteras inte.

## GitHub Actions-publicering

Projektet är förberett för tre arbetsflöden:

1. `Validate` – snabb projekt- och manusvalidering.
2. `Build Preview` – manuell byggning av EPUB och PDF som ett gemensamt artifact.
3. `Release` – byggning av EPUB och PDF vid `v*`-taggar och uppladdning som release assets.

Pandoc-versionen är låst till `3.1.11.1`. PDF byggs med XeLaTeX och TeX Gyre Pagella.
