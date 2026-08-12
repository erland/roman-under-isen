# Projektstatus

## Nuvarande fas

Komplett första utkast. Romanen **Under isen** omfattar 28 kapitel och är färdigskriven som första version.

## Senast godkända kapitel eller del

- Senast godkända: Kapitel 28 – Under isen
- Senast ändrad: Kapitel 28, godkänt och sparat i projektpaketet
- EPUB-exportmetadata tillagd: titel, författare, försättssida och Om boken

## Slutläge i berättelsen

Mats Holm är gripen, men det juridiska och personliga efterspelet fortsätter. Eriks röda pärm visar att han 2019 varnade för operativ användning av kartmaterialet. Maja-pärmen är separat förseglad och ska inte användas som personalakt eller allmän bilaga. Erik, Karin och Maja får en bitterljuv slutpunkt på isen i Luleå: allt under ytan finns kvar, men Erik står inte längre ensam med Mats version.

## EPUB-export

Projektet innehåller nu filer som gör EPUB-exporten reproducerbar:

- `epub-metadata.md`
- `forsattssida.md`
- `om-boken.md`

Dessa anger att EPUB-versionen ska ha:

- Titel: **Under isen**
- Författare: **Erland Lindmark**
- Språk: `sv`
- Titelsida/försättssida
- Om boken-sida med baksidestext
- Kapitel 1–28 i nummerordning

## Nästa rekommenderade steg

Nästa arbetsfas bör vara revision snarare än fler kapitel. Rekommenderad ordning:

1. Grovrevision av hela romanens struktur.
2. Kontroll av kontinuitet, särskilt röstkedjan, pärmarna och tidslinjen.
3. Fördjupning av Mats Holm/Daniella/Rebecka om mer tydlighet behövs.
4. Språklig putsning kapitel för kapitel.
5. Beslut om läsarversion: behålla eller ta bort kapitelnoteringar.
6. Ny EPUB-export enligt `epub-metadata.md`.

## GitHub Actions-publicering

Projektet har kompletterats med GitHub Actions för reproducerbar validering och publicering:

- `.github/workflows/01-validate.yml`
- `.github/workflows/02-build-preview.yml`
- `.github/workflows/03-release.yml`
- `scripts/validate_project.py`
- `scripts/build_book.py`
- `publishing/metadata.yaml`
- `publishing/epub.css`
- `publishing/fix-epub-after-pandoc.py`
- `publishing/pdf-template.tex`
- `publishing/pdf-filter.lua`
- `publishing/build-notes.md`

`.github` ligger i projektroten på samma nivå som `README.md`.

