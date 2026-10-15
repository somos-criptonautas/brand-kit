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
  portada.py      1200×630 covers for articles and posts (CLI and HTTP for n8n)
fonts-src/  Inter Tight and Lora with their OFL licence
dist/       ready-to-use files (generated)
discourse/  images for Discourse's settings (logos, icons, splash, push)
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

## Splash on Discourse

1. Enable the splash image in `/admin/config/upcoming-changes`.
2. Upload `dist/splash/criptonautas-splash.svg` in the `splash screen image` setting.
3. Check light and dark mode: colours come from the theme.

## Automatic covers

`src/portada.py` builds the 1200×630 cover on the kit's template: category, title in Inter Tight (up to 3 lines, wrapped automatically, with an error if it doesn't fit) and an optional illustration in the right-hand slot. Output is PNG and WebP, without metadata.

```
python3 src/portada.py --categoria "Curso" --titulo "Qué es una wallet" --imagen ilus.png
# → portadas/tct_que-es-una-wallet_portada_v1.png and .webp
```

Needs Inter Tight installed system-wide (the ones in `fonts-src/`).

**With n8n:** run the service in Docker on the same network as n8n.

```
make
docker build -f Dockerfile.portada -t criptonautas-portada .
umask 077; printf 'PORTADA_TOKEN=%s\n' "$(openssl rand -hex 32)" > portada.env
docker run -d --name portada --restart unless-stopped --network <n8n-network> --env-file portada.env \
  --read-only --tmpfs /tmp:size=16m --cap-drop ALL --security-opt no-new-privileges \
  --memory 256m --pids-limit 64 criptonautas-portada
```

In n8n, an **HTTP Request** node:

- Method `POST`, URL `http://portada:8787/portada`
- Authentication: Header Auth → `Authorization: Bearer <token>`
- Body JSON: `{"categoria": "{{ $json.categoria }}", "titulo": "{{ $json.titulo }}", "formato": "webp"}`. The illustration is CLI-only: the server never decodes images from outside.
- Response → Response Format: **File**. The next node receives the cover as binary and uploads it to Ghost or Discourse.

The service refuses to start without a `PORTADA_TOKEN` of 32+ characters and publishes no port: only n8n reaches it, over the internal network. Errors: `422` with the reason as text (title too long, invalid JSON), `401` wrong token, `400` no `Content-Length`, `413` body over 4 KB. `GET /salud` answers `ok`.

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
