# Brand kit — agent guide

Rules for anyone changing this repo, people and AI agents alike. Org-wide
conventions (README, licenses, commits) are in the [contributing guide](https://github.com/somos-criptonautas/.github/blob/main/CONTRIBUTING.md).

## Checks

```bash
pip install cairosvg numpy pillow scikit-image fonttools brotli
make          # symbol, name, splash and lockup checks, then dist/ and docs/
```

`make` needs Inter Tight installed system-wide (`fonts-src/`); without them
cairo falls back to another face and the templates come out wrong without failing.

## What a change is reviewed against

- `dist/` and `docs/` are generated. Edit `src/` and run `make`; never edit them by hand.
- No metadata in any output: no `<title>`, `aria-label`, `<metadata>` or comments in
  SVGs, no `tEXt`/`tIME`/`pHYs`/`caBX` chunks in PNGs. `kit.py` asserts it for `dist/`;
  `discourse/` and `ghost/` are not rebuilt by `make`, so check them by hand when replaced.
- Colours come from `BRAND`, `NEUTRAL` and `SEMANTIC` in `src/kit.py`. Light-mode accents
  stay at L* ≤ 60; a new value needs its contrast against Paper and `#181719` recalculated.
- Logo changes follow the acceptance rules in `CONTRIBUTING.md`.

## Things that are easy to get wrong

- The name is lettering rebuilt from `src/fuente/logo-original-2023.png`, not a font.
  Don't re-set it in a typeface.
- The splash animates with CSS transform/opacity only: Discourse strips SMIL.
- The automatic covers service ([criptonautas-featured-ghost-cover](https://github.com/somos-criptonautas/criptonautas-featured-ghost-cover))
  copies the `portada-1200x630` geometry and the horizontal lockup. If either changes, update it there too.
- The ZIP uses a fixed date so rebuilding without changes gives the same bytes.
