# Criptonautas — kit de marca

[ENGLISH](README.md) | **ESPAÑOL**

Todo lo necesario para diseñar para la comunidad: logo, color, tipografía, imágenes, voz, splash y plantillas. Las reglas de uso están en la página pública, **https://criptonautas.co/kit**; este repositorio es la fuente de la que sale todo.

## Estructura

```
src/        el código que genera cada archivo
  simbolo.py      el símbolo, construido geométricamente (GUTTER = espacio entre figuras)
  nombre.py       el nombre "Criptonautas", reconstruido del PNG de 2023 (src/fuente/)
  horizontal.py   símbolo + nombre
  splash.py       animación de carga para Discourse
  kit.py          arma dist/, el ZIP y la página; también los textos de cada sitio (SITES)
  pagina.py       el HTML de la página
  discourse.json  esquema de color del tema de Discourse
  portada.py      portadas 1200×630 para artículos y posts (CLI y HTTP para n8n)
fonts-src/  Inter Tight y Lora con su licencia OFL
dist/       archivos listos para usar (generados)
discourse/  imágenes para los settings de Discourse (logos, íconos, splash, push)
ghost/      imágenes para Design & branding y Newsletter de Ghost (ícono, logos, portada, social)
docs/       la página que se publica en criptonautas.co/kit (generada)
```

## Regenerar

```
pip install cairosvg numpy pillow scikit-image fonttools brotli
make
```

`make` primero verifica (simetría del símbolo, fidelidad del nombre respecto del original, animación sin SMIL) y después regenera `dist/` y `docs/`. Si una verificación falla, no se genera nada. Ningún archivo generado lleva metadatos.

**Para actualizar el logo:** cambiar `src/simbolo.py` o `src/nombre.py`, correr `make` y revisar `docs/index.html`. Todos los archivos, el ZIP y la página se actualizan juntos.

## Splash en Discourse

1. Activar la imagen de splash en `/admin/config/upcoming-changes`.
2. Subir `dist/splash/criptonautas-splash.svg` en el ajuste `splash screen image`.
3. Revisar en modo claro y oscuro: los colores salen del tema.

## Nombre y descripción de los sitios

`dist/voz/sitios.json` (se edita en `SITES`, dentro de `src/kit.py`) tiene el título y la descripción de criptonautas.co y comunidad.criptonautas.co, y en qué campo de Ghost y de Discourse va cada uno. `make` falla si un título pasa de 60 caracteres o una descripción de 155.

## Portadas automáticas

`src/portada.py` arma la portada 1200×630 sobre la plantilla del kit: categoría, título en Inter Tight (hasta 3 líneas, corta solo y avisa si no entra) e ilustración opcional en el hueco de la derecha. Sale en PNG y WebP, sin metadatos.

```
python3 src/portada.py --categoria "Curso" --titulo "Qué es una wallet" --imagen ilus.png
# → portadas/tct_que-es-una-wallet_portada_v1.png y .webp
```

Necesita Inter Tight instalada en el sistema (las de `fonts-src/`).

**Con n8n:** correr el servicio en Docker en la misma red que n8n.

```
make
docker build -f Dockerfile.portada -t criptonautas-portada .
docker run -d --name portada --network <red-de-n8n> -e PORTADA_TOKEN=<token> criptonautas-portada
```

En n8n, un nodo **HTTP Request**:

- Method `POST`, URL `http://portada:8787/portada`
- Authentication: Header Auth → `Authorization: Bearer <token>`
- Body JSON: `{"categoria": "{{ $json.categoria }}", "titulo": "{{ $json.titulo }}", "formato": "webp"}`. Para mandar ilustración, agregar `"imagen"` con el binario en base64.
- Response → Response Format: **File**. El nodo siguiente recibe la portada como binario y la sube a Ghost o Discourse.

Errores: `422` con el motivo en texto (título largo, imagen inválida), `401` sin token, `413` cuerpo demasiado grande. `GET /salud` responde `ok`.

## Publicar con nginx

```nginx
location = /kit { return 301 /kit/; }
location /kit/ {
    alias /srv/brand-kit/docs/;
    index index.html;
    location ~* \.(svg|png|woff2|zip)$ { expires 7d; add_header Cache-Control "public"; }
}
```

Las rutas de la página son relativas: funciona en `/kit/` o en cualquier otra carpeta.

## Contribuir

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para los cambios al kit y la [guía de la organización](https://github.com/somos-criptonautas/.github/blob/main/CONTRIBUTING.md) para las convenciones generales.

## Licencia

Código MIT; plantillas y textos CC BY-NC-SA 4.0; logo y nombre de uso abierto con reglas; tipografías OFL. Detalle en [`LICENSE.md`](LICENSE.md).

Texto de este README bajo [CC BY-NC-SA 4.0](CC-BY-NC-SA-4.0.txt).
