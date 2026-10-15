#!/usr/bin/env python3
"""Builds the whole Criptonautas brand kit from src/ into dist/ and docs/.

    python3 src/kit.py

Change the mark in simbolo.py (or the name in nombre.py), run this again,
and every file, the ZIP and the web page follow.
"""
import io, json, re, shutil, subprocess, zipfile
from datetime import date
from pathlib import Path

import cairosvg

import horizontal
import simbolo
import splash

ROOT = Path(__file__).resolve().parent.parent
DIST, DOCS = ROOT / 'dist', ROOT / 'docs'
FONTS = ROOT / 'fonts-src'
VERSION = '1.3'
REPO_URL = 'https://github.com/somos-criptonautas/brand-kit'

# ---------------------------------------------------------------- colour
# One table feeds the swatches, the CSS, the JSON tokens and the GIMP palette.
BRAND = [
    # slug, name, light, dark, role es, role en
    ('violeta-tinta', 'Violeta Tinta', '#5814EA', '#C89DFF',
     'Acento principal. Enlaces, botones y texto destacado.',
     'Primary accent. Links, buttons and emphasised text.'),
    ('rojo-oxido', 'Rojo Óxido', '#E5500A', '#F3936A',
     'Acento secundario. Formas, gráficos y texto grande; nunca texto corrido.',
     'Secondary accent. Shapes, graphics and large type; never body text.'),
]
# The symbol's violet on dark grounds: #C89DFF would sit 2 L* from #F3936A and the ring would go flat in greyscale.
SHAPE_DK = ('violeta-tinta-formas', 'Violeta Tinta · formas', simbolo.VIOLET_DK,
            'Solo formas y el símbolo en modo oscuro: separa del Rojo Óxido en escala de grises. Nunca texto.',
            'Shapes and the symbol in dark mode only: it separates from Rojo Óxido in greyscale. Never text.')
# Primary-button fill in dark mode. Violeta Tinta's #C89DFF under white text is 2.16:1;
# this is 4.54:1. Buttons only: as text on #181719 it is 3.94:1, so links keep #C89DFF.
BUTTON_DK = ('violeta-boton', 'Violeta Tinta · botones', '#8E4CFF',
             'Fondo de botones primarios en modo oscuro, con texto blanco. No para texto.',
             'Primary-button fill in dark mode, under white text. Not for text.')
NEUTRAL = [
    ('ink', 'Ink', '#14110F', 'Todo el texto. Nunca negro puro.', 'All text. Never pure black.'),
    ('paper', 'Paper', '#E8E6E1', 'Fondo. Blanco neutro, ni crema ni sepia.', 'Ground. Neutral off-white, never cream or sepia.'),
    ('halftone', 'Halftone', '#7E7973', 'Tramas y sombreado. No para texto.', 'Halftone and shading. Not for text.'),
]
SEMANTIC = [
    ('error', 'Error', '#9E1B27', '#FF8DA5', 'Siempre con ícono o texto: comparte familia con Rojo Óxido.',
     'Always with an icon or label: it shares a hue family with Rojo Óxido.'),
    ('exito', 'Éxito', '#1F7A5C', '#6DC08F', 'Confirmaciones.', 'Confirmations.'),
]
UI = {'light': {'bg': '#F8F8F8', 'text': '#1A1A1A'}, 'dark': {'bg': '#181719', 'text': '#F1F1F1'}}
INK, PAPER, DARK_BG = '#14110F', '#E8E6E1', '#181719'


def lum(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb(h):
    return ', '.join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def colour_files(out):
    out.mkdir(parents=True, exist_ok=True)
    tokens = {s: {'name': n, 'light': l, 'dark': d} for s, n, l, d, *_ in BRAND + SEMANTIC}
    tokens.update({s: {'name': n, 'value': v} for s, n, v, *_ in NEUTRAL})
    tokens[SHAPE_DK[0]] = {'name': SHAPE_DK[1], 'light': simbolo.VIOLET, 'dark': SHAPE_DK[2]}
    tokens[BUTTON_DK[0]] = {'name': BUTTON_DK[1], 'dark': BUTTON_DK[2]}
    (out / 'tokens.json').write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + '\n')
    css = [':root {']
    css += [f'  --cn-{s}: {l};' for s, n, l, d, *_ in BRAND + SEMANTIC]
    css += [f'  --cn-{s}: {v};' for s, n, v, *_ in NEUTRAL] + [f'  --cn-{SHAPE_DK[0]}: {simbolo.VIOLET};']
    css += ['}', '@media (prefers-color-scheme: dark) {', '  :root {']
    css += [f'    --cn-{s}: {d};' for s, n, l, d, *_ in BRAND + SEMANTIC] + [f'    --cn-{SHAPE_DK[0]}: {SHAPE_DK[2]};',
                                                                       f'    --cn-{BUTTON_DK[0]}: {BUTTON_DK[2]};']
    css += ['  }', '}']
    (out / 'paleta.css').write_text('\n'.join(css) + '\n')
    gpl = ['GIMP Palette', 'Name: Criptonautas', 'Columns: 4', '#']
    for s, n, v, *_ in [(s, n, l) for s, n, l, *_ in BRAND] + [(s, f'{n} (oscuro)', d) for s, n, l, d, *_ in BRAND] + [(SHAPE_DK[0], f'{SHAPE_DK[1]} (oscuro)', SHAPE_DK[2]),
                                                                                                                        (BUTTON_DK[0], f'{BUTTON_DK[1]} (oscuro)', BUTTON_DK[2])] \
            + [(s, n, v) for s, n, v, *_ in NEUTRAL]:
        r, g, b = (int(v[i:i + 2], 16) for i in (1, 3, 5))
        gpl.append(f'{r:3d} {g:3d} {b:3d}\t{n}')
    (out / 'paleta.gpl').write_text('\n'.join(gpl) + '\n')
    shutil.copy(ROOT / 'src' / 'discourse.json', out / 'discourse.json')


# ---------------------------------------------------------------- logo
VARIANTS = {   # slug: (symbol fills, background used for previews)
    'color': ((simbolo.VIOLET, simbolo.RUST), PAPER),
    'oscuro': ((simbolo.VIOLET_DK, simbolo.RUST_DK), DARK_BG),
    'una-tinta': ((INK, INK), '#FFFFFF'),
    'negativo': ((PAPER, PAPER), INK),
}


PNG_KEEP = {b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND'}


def sin_meta(svg):
    """Delivered files carry no metadata: no <title>, aria-label or role. The web page keeps them inline."""
    svg = re.sub(r'\s*<title>.*?</title>', '', svg)
    return re.sub(r' role="img"| aria-label="[^"]*"', '', svg)


def png(svg, path, width):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(path), output_width=width)
    data, i, out = path.read_bytes(), 8, []        # keep only the chunks that draw the image
    out.append(data[:8])
    while i < len(data):
        n = int.from_bytes(data[i:i + 4], 'big')
        if data[i + 4:i + 8] in PNG_KEEP:
            out.append(data[i:i + 12 + n])
        i += 12 + n
    path.write_bytes(b''.join(out))


def logo_files(out):
    hz = horizontal.variants()
    for v, (fills, _) in VARIANTS.items():
        for kind, svg, w in (('simbolo', simbolo.svg_flat(pair=fills) if fills[0] != fills[1]
                              else simbolo.svg_flat(mono=fills[0]), 1024),
                             ('horizontal', hz[v], 2400)):
            d = out / 'logo' / kind
            d.mkdir(parents=True, exist_ok=True)
            name = f'criptonautas-{kind}-{v}'
            (d / f'{name}.svg').write_text(sin_meta(svg))
            png(svg, d / f'{name}.png', w)


def inner(svg):
    """Root viewBox and inner markup of an SVG string, for nesting it in another SVG."""
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    body = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', svg.strip())
    body = re.sub(r'<title>.*?</title>', '', body)
    return vb, body


def place(svg, x, y, w, h):
    vb, body = inner(svg)
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}">{body}</svg>'


# ---------------------------------------------------------------- templates
def templates(out):
    out.mkdir(parents=True, exist_ok=True)
    hz = horizontal.variants()
    hz_ratio = 7800 / 1550
    files = {}

    # post cover / link preview: title on the left, illustration slot on the right
    W, H, slot = 1200, 630, 760
    hatch = ''.join(f'<line x1="{x}" y1="0" x2="{x - H}" y2="{H}"/>' for x in range(slot, W + H, 16))
    files['portada-1200x630'] = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
        f'<clipPath id="s"><rect x="{slot}" width="{W - slot}" height="{H}"/></clipPath>'
        f'<g clip-path="url(#s)" stroke="#7E7973" stroke-width="1.2">{hatch}</g>'
        f'<rect x="{slot + 70}" y="{H / 2 - 24}" width="{W - slot - 140}" height="48" fill="{PAPER}"/>'
        f'<text x="{(slot + W) / 2}" y="{H / 2 + 7}" text-anchor="middle" font-family="Inter Tight" font-size="20" fill="{INK}">'
        f'Ilustración · {W - slot} × {H}</text>'
        f'<text x="64" y="112" font-family="Inter Tight" font-weight="700" font-size="22" letter-spacing="2.5" '
        f'fill="{simbolo.VIOLET}">CATEGORÍA</text>'
        f'<text font-family="Inter Tight" font-weight="800" letter-spacing="-1.1" font-size="56" fill="{INK}">'
        f'<tspan x="64" y="196">Título del artículo</tspan><tspan x="64" y="262">en dos o tres líneas</tspan></text>'
        f'{place(hz["color"], 64, H - 64 - 48, 48 * hz_ratio, 48)}</svg>\n')

    modes = (('claro', (simbolo.VIOLET, simbolo.RUST), PAPER, 'color', INK),
             ('oscuro', (simbolo.VIOLET_DK, simbolo.RUST_DK), DARK_BG, 'oscuro', PAPER))
    for mode, fills, bg, lock, txt in modes:     # banners before avatars: similar heights share a row
        lw = 760
        files[f'banner-1500x500-{mode}'] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 500" width="1500" height="500">'
            f'<rect width="1500" height="500" fill="{bg}"/>'
            f'{place(hz[lock], (1500 - lw) / 2, 160, lw, lw / hz_ratio)}'
            f'<text x="750" y="380" text-anchor="middle" font-family="Inter Tight" font-size="28" fill="{txt}">'
            f'comunidad.criptonautas.co</text></svg>\n')
    for mode, fills, bg, lock, txt in modes:
        s = 400                                    # leaves more than one head of clear space
        files[f'avatar-512-{mode}'] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            f'<rect width="512" height="512" fill="{bg}"/>{place(simbolo.svg_flat(pair=fills), 56, 56, s, s)}</svg>\n')

    for name, svg in files.items():
        (out / f'{name}.svg').write_text(sin_meta(svg))
        w = int(re.search(r'width="(\d+)"', svg).group(1))
        png(svg, out / f'{name}.png', w)
    return list(files)


# ---------------------------------------------------------------- fonts
LATIN = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,'
         'U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD')
FONT_FILES = {   # web name: source file
    'inter-tight': 'InterTight.ttf', 'inter-tight-italic': 'InterTight-Italic.ttf',
    'lora': 'Lora.ttf', 'lato-400': 'Lato-Regular.ttf', 'lato-700': 'Lato-Bold.ttf',
    'lato-400i': 'Lato-Italic.ttf',
}


def fonts(kit_dir, web_dir):
    kit_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)
    for f in FONTS.glob('*'):
        if f.suffix == '.ttf':   # still installable TTF, cut to the Latin set the kit uses
            subprocess.run(['pyftsubset', str(f), f'--unicodes={LATIN}', '--layout-features=*',
                            f'--output-file={kit_dir / f.name}'], check=True)
        else:
            shutil.copy(f, kit_dir / f.name)
    for web, src in FONT_FILES.items():
        subprocess.run(['pyftsubset', str(FONTS / src), f'--unicodes={LATIN}', '--flavor=woff2',
                        '--layout-features=*', f'--output-file={web_dir / (web + ".woff2")}'], check=True)


# ---------------------------------------------------------------- build
def build():
    for d in (DIST, DOCS):
        shutil.rmtree(d, ignore_errors=True)
    logo_files(DIST)
    (DIST / 'splash').mkdir(parents=True)
    (DIST / 'splash' / 'criptonautas-splash.svg').write_text(sin_meta(splash.splash()))
    colour_files(DIST / 'color')
    tpl = templates(DIST / 'plantillas')
    fonts(DIST / 'tipografia', DOCS / 'fuentes')
    for f in ('LICENSE.md', 'CC-BY-NC-SA-4.0.txt', 'README.md', 'README.es.md'):
        shutil.copy(ROOT / f, DIST / f)

    zpath = DIST / 'criptonautas-kit.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(DIST.rglob('*')):
            if f.is_file() and f != zpath:
                info = zipfile.ZipInfo(str(Path('criptonautas-kit') / f.relative_to(DIST)), (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED   # fixed date: no build time inside the ZIP
                z.writestr(info, f.read_bytes())

    shutil.copytree(DIST, DOCS / 'descargas', dirs_exist_ok=True)
    import pagina
    (DOCS / 'index.html').write_text(pagina.render(
        version=VERSION, fecha=date.today().isoformat(), repo=REPO_URL,
        brand=BRAND, shape_dk=SHAPE_DK, button_dk=BUTTON_DK, neutral=NEUTRAL, semantic=SEMANTIC, ui=UI,
        contrast=contrast, rgb=rgb, templates=tpl, variants=list(VARIANTS),
        zip_kb=zpath.stat().st_size // 1024))
    return zpath


if __name__ == '__main__':
    z = build()
    files = [f for f in DIST.rglob('*') if f.is_file()]
    assert (DOCS / 'index.html').exists() and z.exists()
    assert len(list((DIST / 'logo').rglob('*.svg'))) == 8
    for f in DIST.rglob('*.svg'):
        assert not re.search(r'<title|aria-label|<metadata|<!--', f.read_text()), f
    print(f'kit {VERSION}: {len(files)} files in dist/, zip {z.stat().st_size // 1024} KB, page docs/index.html')
