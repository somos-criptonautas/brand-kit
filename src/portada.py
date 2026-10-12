#!/usr/bin/env python3
"""Portada 1200×630 para artículos y posts: la plantilla del kit con categoría, título e ilustración.

    python3 src/portada.py --categoria Curso --titulo "Qué es una wallet" [--imagen ilus.png] [--slug wallet]
    python3 src/portada.py --servir [--puerto 8787]      # HTTP para n8n
    python3 src/portada.py --probar                      # autocomprobación

HTTP (para el nodo HTTP Request de n8n):
    POST /portada   JSON {"categoria", "titulo", "imagen": base64 opcional, "formato": "png" | "webp"}
                    → la imagen (Content-Type image/png o image/webp)
    GET  /salud     → "ok"
    Si PORTADA_TOKEN está definido, cada POST debe traer "Authorization: Bearer <token>".

Necesita cairosvg y Pillow, y las fuentes de fonts-src/ instaladas en el sistema (Inter Tight).
Las salidas no llevan metadatos.
"""
import argparse, base64, binascii, html, io, json, os, re, sys, unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cairosvg
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / 'fonts-src'
LOCKUP = ROOT / 'dist' / 'logo' / 'horizontal' / 'criptonautas-horizontal-color.svg'

# Misma geometría que la plantilla portada-1200x630 de kit.py.
W, H, SLOT = 1200, 630, 760
INK, PAPER, HALFTONE, VIOLET = '#14110F', '#E8E6E1', '#7E7973', '#5814EA'
TITLE_X, TITLE_Y0, TITLE_STEP, TITLE_SIZE, MAX_LINES = 64, 196, 66, 56, 3
# Pillow mide el avance sin el letter-spacing negativo, así que sobreestima: lo que entra acá entra en cairo.
TITLE_MAX_W = SLOT - TITLE_X - 64
MAX_TITLE, MAX_CAT, MAX_IMAGE = 140, 30, 10 * 1024 * 1024
PNG_KEEP = {b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND'}


class Invalida(ValueError):
    """Entrada rechazada; el mensaje va tal cual al que llamó."""


def _font():
    f = ImageFont.truetype(str(FONTS / 'InterTight.ttf'), TITLE_SIZE)
    f.set_variation_by_axes([800])
    return f


def lineas(titulo, font=None):
    """Corta el título en líneas que entran en el ancho; falla si hacen falta más de MAX_LINES."""
    font = font or _font()
    out = []
    for palabra in titulo.split():
        prueba = f'{out[-1]} {palabra}' if out else palabra
        if out and font.getlength(prueba) <= TITLE_MAX_W:
            out[-1] = prueba
        elif font.getlength(palabra) > TITLE_MAX_W:
            raise Invalida(f'la palabra «{palabra}» no entra en una línea')
        else:
            out.append(palabra)
    if len(out) > MAX_LINES:
        raise Invalida(f'el título ocupa {len(out)} líneas; el máximo es {MAX_LINES}. Acortalo.')
    return out


def _inner(svg):
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    body = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip())
    return vb, re.sub(r'<title>.*?</title>', '', body)


def _ilustracion(data):
    """Reabre la imagen y la vuelve a codificar como PNG: valida el formato y descarta sus metadatos."""
    if len(data) > MAX_IMAGE:
        raise Invalida('la ilustración pesa más de 10 MB')
    try:
        im = Image.open(io.BytesIO(data))
        if im.format not in ('PNG', 'JPEG', 'WEBP'):
            raise Invalida('la ilustración tiene que ser PNG, JPEG o WebP')
        im = im.convert('RGB')
    except Invalida:
        raise
    except Exception:
        raise Invalida('la ilustración no es una imagen válida')
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return base64.b64encode(buf.getvalue()).decode()


def svg(categoria, titulo, imagen=None):
    categoria, titulo = ' '.join(categoria.split()), ' '.join(titulo.split())
    if not titulo or not categoria:
        raise Invalida('faltan la categoría o el título')
    if len(titulo) > MAX_TITLE or len(categoria) > MAX_CAT:
        raise Invalida(f'máximo {MAX_CAT} caracteres de categoría y {MAX_TITLE} de título')
    tspans = ''.join(f'<tspan x="{TITLE_X}" y="{TITLE_Y0 + i * TITLE_STEP}">{html.escape(l)}</tspan>'
                     for i, l in enumerate(lineas(titulo)))
    if imagen:
        slot = (f'<image x="{SLOT}" y="0" width="{W - SLOT}" height="{H}" preserveAspectRatio="xMidYMid slice" '
                f'href="data:image/png;base64,{_ilustracion(imagen)}"/>')
    else:   # sin ilustración queda la trama de la plantilla, sin el rótulo
        hatch = ''.join(f'<line x1="{x}" y1="0" x2="{x - H}" y2="{H}"/>' for x in range(SLOT, W + H, 16))
        slot = f'<g stroke="{HALFTONE}" stroke-width="1.2">{hatch}</g>'
    vb, lockup = _inner(LOCKUP.read_text())
    lh = 48
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
            f'<clipPath id="s"><rect x="{SLOT}" width="{W - SLOT}" height="{H}"/></clipPath>'
            f'<g clip-path="url(#s)">{slot}</g>'
            f'<text x="{TITLE_X}" y="112" font-family="Inter Tight" font-weight="700" font-size="22" letter-spacing="2.5" '
            f'fill="{VIOLET}">{html.escape(categoria.upper())}</text>'
            f'<text font-family="Inter Tight" font-weight="800" letter-spacing="-1.1" font-size="{TITLE_SIZE}" fill="{INK}">{tspans}</text>'
            f'<svg x="{TITLE_X}" y="{H - 64 - lh}" width="{lh * 7800 / 1550}" height="{lh}" viewBox="{vb}">{lockup}</svg>'
            f'</svg>')


def _sin_meta_png(data):
    out, i = [data[:8]], 8
    while i < len(data):
        n = int.from_bytes(data[i:i + 4], 'big')
        if data[i + 4:i + 8] in PNG_KEEP:
            out.append(data[i:i + 12 + n])
        i += 12 + n
    return b''.join(out)


def render(categoria, titulo, imagen=None, formato='png'):
    if formato not in ('png', 'webp'):
        raise Invalida('formato: png o webp')
    png = _sin_meta_png(cairosvg.svg2png(bytestring=svg(categoria, titulo, imagen).encode(), output_width=W))
    if formato == 'png':
        return png
    buf = io.BytesIO()
    Image.open(io.BytesIO(png)).convert('RGB').save(buf, 'WEBP', quality=90, method=6)   # Pillow no escribe EXIF ni ICC
    return buf.getvalue()


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:60] or 'portada'


# ---------------------------------------------------------------- HTTP para n8n
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, b'ok') if self.path == '/salud' else self._send(404, b'no existe')

    def do_POST(self):
        if self.path != '/portada':
            return self._send(404, b'no existe')
        token = os.environ.get('PORTADA_TOKEN')
        if token and self.headers.get('Authorization') != f'Bearer {token}':
            return self._send(401, b'token incorrecto')
        n = int(self.headers.get('Content-Length') or 0)
        if not 0 < n <= MAX_IMAGE * 4 // 3 + 4096:      # base64 de 10 MB + el resto del JSON
            return self._send(413, b'cuerpo vacio o demasiado grande')
        try:
            req = json.loads(self.rfile.read(n))
            if not isinstance(req, dict):
                raise Invalida('se espera un objeto JSON')
            img = req.get('imagen')
            try:
                img = base64.b64decode(img, validate=True) if img else None
            except (binascii.Error, TypeError):
                raise Invalida('imagen: base64 inválido')
            fmt = req.get('formato', 'png')
            out = render(str(req.get('categoria', '')), str(req.get('titulo', '')), img, fmt)
        except (Invalida, json.JSONDecodeError) as e:
            return self._send(422, str(e).encode())
        self._send(200, out, f'image/{fmt}')

    def log_message(self, fmt, *args):      # sin registrar títulos ni IPs
        pass


# ---------------------------------------------------------------- autocomprobación
def probar():
    assert lineas('Qué es una wallet') == ['Qué es una wallet']
    assert len(lineas('Cómo leer el volumen sin confundirlo con la tendencia')) == 3
    for malo in ('x' * 141, 'palabra ' * 40):
        try:
            render('Curso', malo); raise AssertionError('debía rechazar el título')
        except Invalida:
            pass
    png = render('Análisis técnico', 'Soportes & <resistencias> en marcos cortos')
    im = Image.open(io.BytesIO(png))
    assert im.size == (W, H)
    assert _chunks(png) <= PNG_KEEP
    # el texto no invade la ilustración: columna 700–759 vacía (solo fondo)
    rgb = im.convert('RGB')
    assert all(rgb.getpixel((x, y)) == (232, 230, 225) for x in range(700, 760) for y in range(140, 360))
    ilus = io.BytesIO(); Image.new('RGB', (800, 800), '#5814EA').save(ilus, 'JPEG')
    webp = render('Curso', 'Con ilustración', ilus.getvalue(), 'webp')
    assert Image.open(io.BytesIO(webp)).getpixel((1000, 300))[2] > 150
    try:
        render('Curso', 'Imagen falsa', b'<svg onload=1>'); raise AssertionError('debía rechazar la imagen')
    except Invalida:
        pass
    print('portada ok')


def _chunks(data):
    i, kinds = 8, set()
    while i < len(data):
        n = int.from_bytes(data[i:i + 4], 'big'); kinds.add(data[i + 4:i + 8]); i += 12 + n
    return kinds


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--categoria'); ap.add_argument('--titulo'); ap.add_argument('--imagen', type=Path)
    ap.add_argument('--slug'); ap.add_argument('--salida', type=Path, default=ROOT / 'portadas')
    ap.add_argument('--servir', action='store_true'); ap.add_argument('--puerto', type=int, default=8787)
    ap.add_argument('--host', default=os.environ.get('PORTADA_HOST', '127.0.0.1'))
    ap.add_argument('--probar', action='store_true')
    a = ap.parse_args()
    if a.probar:
        probar()
    elif a.servir:
        print(f'portada escuchando en http://{a.host}:{a.puerto}')
        ThreadingHTTPServer((a.host, a.puerto), Handler).serve_forever()
    elif a.categoria and a.titulo:
        a.salida.mkdir(parents=True, exist_ok=True)
        base = a.salida / f'tct_{a.slug or slugify(a.titulo)}_portada_v1'
        try:
            img = a.imagen.read_bytes() if a.imagen else None
            for fmt in ('png', 'webp'):
                Path(f'{base}.{fmt}').write_bytes(render(a.categoria, a.titulo, img, fmt))
        except Invalida as e:
            sys.exit(f'portada: {e}')
        print(f'{base}.png\n{base}.webp')
    else:
        ap.print_help()
