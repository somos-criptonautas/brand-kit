# Criptonautas — brand kit

**ENGLISH** | [ESPAÑOL](README.es.md)

Everything needed to design for the community: logo, colour, type, imagery, voice, splash and templates. The usage rules live on the public page, **https://criptonautas.co/kit**; this repository is the source everything is built from.

## Structure

```
src/        the code that builds every file
  simbolo.py      the symbol, built geometrically (GUTTER = gap between figures)
  nombre.py       the name "Criptonautas", rebuilt from the 2023 PNG (src/fuente/)
  horizontal.py   symbol + name
  splash.py       loading animation for Discourse
  kit.py          builds dist/, the ZIP and the page
  pagina.py       the page's HTML
  discourse.json  Discourse theme colour scheme
fonts-src/  Inter Tight, Lora and Lato with their OFL licence
dist/       ready-to-use files (generated)
discourse/  images for Discourse's settings (logos, icons, splash, push)
  tema/           the theme component's colour code (dark-mode button violet), for reference
ghost/      images for Ghost's Design & branding and Newsletter (icon, logos, cover, social)
docs/       the page published at criptonautas.co/kit (generated)
```

## Rebuild

```
pip install cairosvg numpy pillow scikit-image fonttools brotli
make
```

`make` checks first (symbol symmetry, fidelity of the name to the original lettering, no SMIL in the splash), then rebuilds `dist/` and `docs/`. If a check fails, nothing is built. No generated file carries metadata.

**To update the logo:** edit `src/simbolo.py` or `src/nombre.py`, run `make`, review `docs/index.html`. Every file, the ZIP and the page update together.

## What changed in v1.3

- **Rojo Óxido** is `#E5500A` (light) and `#F3936A` (dark), formerly `#E6211E` and `#F98E76`. Names stay the same (`rojo-oxido`, `--cn-rojo-oxido`, the `tokens.json` keys), so nothing that uses them breaks. The light red is 3.07:1 on Paper: large text and graphics only, as before.
- **Violeta Tinta · botones** `#8E4CFF`, a dark-mode-only token (`--cn-violeta-boton`): primary-button fill under white text, 4.54:1. Links keep `#C89DFF`, because `#8E4CFF` as text on `#181719` is only 3.94:1. The Discourse code that applies it is in `discourse/tema/`.
- **Lato** joins the type: text and interface on the forum. Inter Tight keeps headings everywhere, Lora long reading on the blog.
- The ZIP's TTFs are cut to the Latin set the kit uses (still installable, variable axes kept): the ZIP drops to about 1 MB. `fonts-src/` keeps the full files.
- **Splash** beat slowed from 0.55 s to 0.9 s in `src/splash.py` (`discourse/splash.svg` already ran at 0.9 s).
- `discourse/` and `ghost/` aren't rebuilt by `make`: their red was swapped in place. Images already uploaded to Discourse or Ghost have to be uploaded again, and the forum's colour palette needs `quaternary` updated by hand.

## Splash on Discourse

1. Enable the splash image in `/admin/config/upcoming-changes`.
2. Upload `dist/splash/criptonautas-splash.svg` in the `splash screen image` setting.
3. Check light and dark mode: colours come from the theme.

## Automatic covers

Automatic covers for Ghost posts without a featured image, and for Discourse wiki, course and glossary topics, are made by [criptonautas-featured-cover](https://github.com/somos-criptonautas/criptonautas-featured-cover), on this kit's 1200×630 template.

## Publishing with nginx

```nginx
location = /kit { return 301 /kit/; }
location /kit/ {
    alias /srv/brand-kit/docs/;
    index index.html;
    location ~* \.(svg|png|woff2|zip)$ { expires 7d; add_header Cache-Control "public"; }
}
```

Page paths are relative: it works under `/kit/` or any other folder.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for changes to the kit and the [organisation guide](https://github.com/somos-criptonautas/.github/blob/main/CONTRIBUTING.md) for general conventions.

## Licence

Code MIT; templates and copy CC BY-NC-SA 4.0; logo and name open use with rules; typefaces OFL. Details in [`LICENSE.md`](LICENSE.md).

Text of this README under [CC BY-NC-SA 4.0](CC-BY-NC-SA-4.0.txt).
