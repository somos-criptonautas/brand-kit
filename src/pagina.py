"""HTML of criptonautas.co/kit. Bilingual: every text exists in ES and EN, CSS shows one."""
import simbolo
import splash as splash_mod

HEAD = 2 * simbolo.r / (2 * (simbolo.R + simbolo.r))      # head diameter / symbol height
D = 'descargas'


def t(es, en):
    return f'<span lang="es">{es}</span><span lang="en">{en}</span>'


def blk(es, en, tag='p'):
    return f'<{tag} lang="es">{es}</{tag}><{tag} lang="en">{en}</{tag}>'


VAR_NAMES = {'color': ('Color', 'Colour'), 'oscuro': ('Oscuro', 'Dark'),
             'una-tinta': ('Una tinta', 'One ink'), 'negativo': ('Negativo', 'Reverse')}
VAR_BG = {'color': '#E8E6E1', 'oscuro': '#181719', 'una-tinta': '#FFFFFF', 'negativo': '#14110F'}
VAR_USE = {'color': ('Uso principal, sobre fondos claros.', 'Main use, on light grounds.'),
           'oscuro': ('Sobre fondos en modo oscuro.', 'On grounds in dark mode.'),
           'una-tinta': ('Impresión a una tinta, sellos, grabado.', 'One-ink print, stamps, engraving.'),
           'negativo': ('Sobre fotos o fondos de color, tinta clara.', 'On photos or colour, light ink.')}


def dl(path, label):
    return f'<a class="dl" href="{D}/{path}" download>{label}</a>'


def logo_cards(variants, kind, ratio):
    out = []
    for v in variants:
        es, en = VAR_NAMES[v]
        ues, uen = VAR_USE[v]
        base = f'logo/{kind}/criptonautas-{kind}-{v}'
        out.append(
            f'<figure class="card"><div class="plate {kind}" style="background:{VAR_BG[v]}">'
            f'<img src="{D}/{base}.svg" alt="Criptonautas — {es} / {en}" loading="lazy" style="aspect-ratio:{ratio}"></div>'
            f'<figcaption><strong>{t(es, en)}</strong><span class="muted">{t(ues, uen)}</span>'
            f'<span class="dls">{dl(base + ".svg", "SVG")}{dl(base + ".png", "PNG")}</span></figcaption></figure>')
    return ''.join(out)


def clear_space():
    x = HEAD * 1550
    W, H = 7800, 1550
    m = x
    return (f'<svg class="diagram" viewBox="{-m - 40} {-m - 40} {W + 2 * m + 80} {H + 2 * m + 80}" role="img" '
            f'aria-label="Espacio libre / Clear space">'
            f'<rect x="{-m}" y="{-m}" width="{W + 2 * m}" height="{H + 2 * m}" fill="none" stroke="#7E7973" '
            f'stroke-width="14" stroke-dasharray="60 40"/>'
            f'<image href="{D}/logo/horizontal/criptonautas-horizontal-color.svg" width="{W}" height="{H}"/>'
            f'<rect width="{W}" height="{H}" fill="none" stroke="#E6211E" stroke-width="10" stroke-dasharray="30 30"/>'
            + ''.join(f'<circle cx="{cx}" cy="{cy}" r="{x / 2}" fill="none" stroke="#E6211E" stroke-width="12"/>'
                      for cx, cy in ((-m / 2, H / 2), (W + m / 2, H / 2), (W / 2, -m / 2), (W / 2, H + m / 2)))
            + '</svg>')


MISUSE = [
    ('No deformar.', 'Do not stretch.', 'style="transform:scaleX(1.45)"', '#E8E6E1', 'color'),
    ('No rotar.', 'Do not rotate.', 'style="transform:rotate(-14deg)"', '#E8E6E1', 'color'),
    ('No cambiar los colores.', 'Do not recolour.', 'style="filter:hue-rotate(110deg) saturate(1.6)"', '#E8E6E1', 'color'),
    ('Sin sombras, brillos ni degradados.', 'No shadows, glows or gradients.',
     'style="filter:drop-shadow(0 0 10px #ff00ff) drop-shadow(6px 6px 2px #000a)"', '#E8E6E1', 'color'),
    ('No usar sobre fondos sin contraste.', 'Do not place on low-contrast grounds.', '', '#5814EA', 'color'),
    ('No separar ni cambiar la tipografía del nombre.', 'Do not split it or retype the name.', None, '#E8E6E1', None),
]


def misuse():
    out = []
    for es, en, style, bg, v in MISUSE:
        if style is None:      # retyped name in another face, symbol moved to the right
            art = (f'<span class="retyped">Criptonautas</span>'
                   f'<img src="{D}/logo/simbolo/criptonautas-simbolo-color.svg" alt="" class="retyped-sym">')
        else:
            art = f'<img src="{D}/logo/horizontal/criptonautas-horizontal-{v}.svg" alt="" {style}>'
        out.append(f'<figure class="card bad"><div class="plate misuse" style="background:{bg}">{art}</div>'
                   f'<figcaption><span class="x" aria-hidden="true">✕</span>{t(es, en)}</figcaption></figure>')
    return ''.join(out)


def swatch(name, hexv, role_es, role_en, contrast, on, on_label, rgb, graphics=False):
    c = contrast(hexv, on)
    use_es, use_en = (('solo gráficos', 'graphics only') if graphics or name == 'Halftone' else ('texto', 'text') if c >= 4.5 else ('texto grande y gráficos', 'large text & graphics')
                      if c >= 3 else ('solo gráficos', 'graphics only'))
    ink = '#14110F' if contrast(hexv, '#14110F') > contrast(hexv, '#FFFFFF') else '#FFFFFF'
    return (f'<figure class="swatch"><div class="chip" style="background:{hexv};color:{ink}">'
            f'<span class="hex">{hexv}</span></div><figcaption><strong>{name}</strong>'
            f'<span class="mono">RGB {rgb(hexv)}</span>'
            f'<span class="mono">{c:.2f}:1 {on_label} · {t(use_es, use_en)}</span>'
            f'<span class="muted">{t(role_es, role_en)}</span></figcaption></figure>')


VOICE = [
    ('En Criptonautas el curso es abierto.', '¡Nuestro increíble curso te va a hacer ganar!',
     'At Criptonautas the course is open.', 'Our amazing course will make you win!'),
    ('Cuando perdí mi primera posición, aprendí a respetar el stop.', 'Te enseñamos a ganar siempre.',
     'When I lost my first position, I learned to respect the stop.', 'We teach you how to always win.'),
    ('Qué evaluar según el momento del mercado.', 'Señal de compra: entrá ya.',
     'What to assess given the market moment.', 'Buy signal: get in now.'),
    ('La comunidad responde en comunidad.criptonautas.co.', 'Preguntá en el foro.',
     'The community answers at comunidad.criptonautas.co.', 'Ask on the forum.'),
]

TEMPLATE_NAMES = {
    'portada-1200x630': ('Portada de artículo / vista previa de enlace', 'Article cover / link preview'),
    'avatar-512-claro': ('Avatar, claro', 'Avatar, light'), 'avatar-512-oscuro': ('Avatar, oscuro', 'Avatar, dark'),
    'banner-1500x500-claro': ('Banner, claro', 'Banner, light'), 'banner-1500x500-oscuro': ('Banner, oscuro', 'Banner, dark'),
}

CSS = """
@font-face{font-family:"Inter Tight";src:url(fuentes/inter-tight.woff2) format("woff2");font-weight:100 900;font-display:swap}
@font-face{font-family:"Inter Tight";src:url(fuentes/inter-tight-italic.woff2) format("woff2");font-weight:100 900;font-style:italic;font-display:swap}
@font-face{font-family:Lora;src:url(fuentes/lora.woff2) format("woff2");font-weight:400 700;font-display:swap}
:root{--bg:#F8F8F8;--surface:#FFFFFF;--line:#DEDBD6;--text:#1A1A1A;--muted:#5C5852;--accent:#5814EA;--accent-text:#FFFFFF;
--warn:#E6211E;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--bg:#181719;--surface:#222024;--line:#3B393E;--text:#F1F1F1;--muted:#B5B0AA;
--accent:#C89DFF;--accent-text:#181719;--warn:#F98E76}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
html[data-lang=es] [lang=en]:not(html),html[data-lang=en] [lang=es]:not(html){display:none}
html{font-size:22px}
body{margin:0;background:var(--bg);color:var(--text);font:400 1rem/1.6 "Inter Tight","Helvetica Neue",Arial,sans-serif}
a{color:var(--accent)}
h1,h2,h3{font-family:"Inter Tight",sans-serif;font-weight:800;letter-spacing:-.02em;line-height:1.15;margin:0 0 .5em}
h1{font-size:clamp(2rem,5vw,3.2rem)}
h2{font-size:clamp(1.6rem,3.5vw,2.2rem);margin-top:0}
h3{font-size:1.4rem;margin-top:1.6em}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header.top{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;gap:16px;min-height:64px}
header.top .brand{display:block;line-height:0;flex:none}header.top img{height:28px;width:auto}
nav.sections{display:flex;gap:16px;overflow-x:auto;flex:1;scrollbar-width:none;font-size:1rem}
nav.sections a{color:var(--text);text-decoration:none;white-space:nowrap;opacity:.8}
nav.sections a:hover{opacity:1;text-decoration:underline}
.lang{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden;flex:none}
.lang button{font:700 1rem "Inter Tight",sans-serif;padding:6px 10px;border:0;background:transparent;color:var(--text);cursor:pointer}
.lang button[aria-pressed=true]{background:var(--accent);color:var(--accent-text)}
.only-light{display:block}.only-dark{display:none}
@media (prefers-color-scheme:dark){.only-light{display:none}.only-dark{display:block}}
.hero{padding:64px 0 40px}
.hero p{font-size:1.3rem;max-width:44em;color:var(--muted)}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:6px;font-weight:700;text-decoration:none;
background:var(--accent);color:var(--accent-text)}
.btn.ghost{background:transparent;color:var(--accent);border:1.5px solid var(--accent)}
section{scroll-margin-top:64px;padding:56px 0;border-top:1px solid var(--line)}
section>.wrap>p.lead,section>.wrap>p[lang]{max-width:46em}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin:24px 0}
.grid.wide{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.card{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.plate{display:grid;place-items:center;padding:28px;min-height:150px}
.plate img{max-width:100%;height:auto}
.plate.simbolo img{width:110px}
.plate.horizontal img{width:100%;max-width:300px}
.card figcaption{padding:14px 16px 16px;display:flex;flex-direction:column;gap:4px;font-size:1rem}
.muted{color:var(--muted)}
.dls{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
a.dl{font-size:1rem;font-weight:700;padding:4px 10px;border:1px solid var(--line);border-radius:4px;text-decoration:none;color:var(--text)}
a.dl:hover{border-color:var(--accent);color:var(--accent)}
.rules{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));margin:24px 0}
.rule{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:20px}
.rule h3{margin-top:0}
.diagram{width:100%;height:auto;background:#E8E6E1;border-radius:6px;padding:8px}
.misuse{min-height:130px;overflow:hidden}
.misuse img{max-width:220px;width:80%}
.bad figcaption{flex-direction:row;align-items:baseline;gap:8px}
.x{color:var(--warn);font-weight:700}
.retyped{font:400 1.35rem Lora,serif;color:#14110F}
.misuse .retyped-sym{width:38px;margin-left:10px}
.misuse:has(.retyped){display:flex;align-items:center;justify-content:center}
.swatch{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.chip{height:110px;display:flex;align-items:flex-end;padding:12px}
.hex{font:700 1rem ui-monospace,Menlo,Consolas,monospace}
.swatch figcaption{padding:12px 14px 14px;display:flex;flex-direction:column;gap:3px;font-size:1rem}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.95rem}
ul.tight{padding-left:1.2em}ul.tight li{margin:.3em 0}
.type{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:22px}
.type .sample{font-size:2rem;line-height:1.2;margin:.2em 0 .4em}.type .sample.body{font-size:1rem;line-height:1.6}
.voice td{overflow-wrap:anywhere}.voice{table-layout:fixed;width:100%;border-collapse:collapse;margin:20px 0;font-size:1rem}
.voice th,.voice td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}
.voice th{font-weight:800}
.yes{color:var(--text)}.no{color:var(--muted);text-decoration:line-through;text-decoration-color:var(--warn)}
.splash{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin:24px 0}
.splash div{display:grid;place-items:center;height:220px;border-radius:8px}
.splash svg{width:120px;height:120px}
ol.steps li{margin:.4em 0}
code{font:.88em ui-monospace,Menlo,Consolas,monospace;background:var(--surface);border:1px solid var(--line);padding:1px 5px;border-radius:4px}
.tpl-grid{align-items:start}
.tpl .plate{padding:0;min-height:0;background:var(--line)}
.tpl .plate img{width:100%;display:block}
footer{padding:40px 0 64px;border-top:1px solid var(--line);color:var(--muted);font-size:1rem}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media (max-width:640px){header.top img{height:22px}nav.sections{display:none}.hero{padding:40px 0 24px}}
"""

JS = """
(function(){var d=document.documentElement,b=[].slice.call(document.querySelectorAll('[data-set-lang]'));
function set(l){d.setAttribute('data-lang',l);d.lang=l;b.forEach(function(x){x.setAttribute('aria-pressed',String(x.dataset.setLang===l))});
try{localStorage.setItem('cn-lang',l)}catch(e){}}
var q=null,s=null;try{q=new URLSearchParams(location.search).get('lang')}catch(e){}try{s=localStorage.getItem('cn-lang')}catch(e){}
set(q==='en'||q==='es'?q:(s||((navigator.language||'es').slice(0,2)==='en'?'en':'es')));
b.forEach(function(x){x.addEventListener('click',function(){set(x.dataset.setLang)})});})();
"""


def render(version, fecha, repo, brand, shape_dk, neutral, semantic, ui, contrast, rgb, templates, variants, zip_kb):
    P, DK = '#E8E6E1', '#181719'
    SPLASH = splash_mod.splash().replace('<svg ', '<svg aria-hidden="true" ', 1)
    sw_brand = ''.join(swatch(n, l, es, en, contrast, P, 'Paper', rgb) for s, n, l, d, es, en in brand)
    sw_dark = ''.join(swatch(f'{n} · {t("oscuro", "dark")}', d, es, en, contrast, DK, '#181719', rgb)
                      for s, n, l, d, es, en in brand) + swatch(shape_dk[1] + f' · {t("oscuro", "dark")}', shape_dk[2], shape_dk[3],
                                                                 shape_dk[4], contrast, DK, '#181719', rgb, graphics=True)
    sw_neutral = ''.join(swatch(n, v, es, en, contrast, P if s != 'paper' else '#14110F',
                                'Paper' if s != 'paper' else 'Ink', rgb) for s, n, v, es, en in neutral)
    sw_sem = ''.join(swatch(n, l, es, en, contrast, P, 'Paper', rgb) + swatch(f'{n} · {t("oscuro", "dark")}', d, es, en, contrast, DK, '#181719', rgb)
                     for s, n, l, d, es, en in semantic)

    voice_rows = ''.join(f'<tr><td class="yes">{t(ye, ya)}</td><td class="no">{t(ne, na)}</td></tr>'
                         for ye, ne, ya, na in VOICE)
    tpl_cards = ''.join(
        f'<figure class="card tpl"><div class="plate"><img src="{D}/plantillas/{n}.png" alt="{TEMPLATE_NAMES[n][0]}" loading="lazy"></div>'
        f'<figcaption><strong>{t(*TEMPLATE_NAMES[n])}</strong><span class="dls">{dl(f"plantillas/{n}.svg", "SVG")}'
        f'{dl(f"plantillas/{n}.png", "PNG")}</span></figcaption></figure>' for n in templates)
    contrib = blk('El kit es de la comunidad: cualquiera puede proponer cambios al logo, los colores o las plantillas, '
                  f'con un pull request en el <a href="{repo}">repositorio</a> o en '
                  '<a href="https://comunidad.criptonautas.co">comunidad.criptonautas.co</a> con una imagen del antes y el después.',
                  'The kit belongs to the community: anyone can propose changes to the logo, colours or templates, '
                  f'with a pull request on the <a href="{repo}">repository</a> or at '
                  '<a href="https://comunidad.criptonautas.co">comunidad.criptonautas.co</a> with a before/after image.')
    repo_btn = (f'<a class="btn ghost" href="{repo}">{t("Repositorio", "Repository")}</a>' if repo else '')
    nav = [('logo', 'Logo', 'Logo'), ('color', 'Color', 'Colour'), ('tipografia', 'Tipografía', 'Type'),
           ('imagenes', 'Imágenes', 'Imagery'), ('voz', 'Voz', 'Voice'), ('splash', 'Splash', 'Splash'),
           ('plantillas', 'Plantillas', 'Templates'), ('licencia', 'Licencia', 'Licence')]
    nav_html = ''.join(f'<a href="#{i}">{t(es, en)}</a>' for i, es, en in nav)

    return f"""<!doctype html>
<html lang="es" data-lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Criptonautas · Kit de marca / Brand kit</title>
<meta name="description" content="Logo, color, tipografía, imágenes, voz y plantillas para diseñar para la comunidad Criptonautas.">
<meta property="og:title" content="Criptonautas · Kit de marca">
<meta property="og:image" content="{D}/plantillas/portada-1200x630.png">
<link rel="icon" href="{D}/logo/simbolo/criptonautas-simbolo-color.svg" type="image/svg+xml">
<link rel="preload" href="fuentes/inter-tight.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="#" aria-label="Criptonautas">
<img class="only-light" src="{D}/logo/horizontal/criptonautas-horizontal-color.svg" alt="Criptonautas">
<img class="only-dark" src="{D}/logo/horizontal/criptonautas-horizontal-oscuro.svg" alt="Criptonautas"></a>
<nav class="sections" aria-label="Secciones / Sections">{nav_html}</nav>
<div class="lang" role="group" aria-label="Idioma / Language">
<button type="button" data-set-lang="es" aria-pressed="true">ES</button><button type="button" data-set-lang="en" aria-pressed="false">EN</button></div>
</div></header>

<main>
<div class="hero"><div class="wrap">
<h1>{t('Kit de marca', 'Brand kit')}</h1>
{blk('Trading y cripto peer-to-peer. Curso abierto, revisado en comunidad: sin gurús, señales ni hype. '
     'Este kit permite diseñar desde nuestra voz visual.',
     'Peer-to-peer trading and crypto. An open course, reviewed in community: no gurus, signals or hype. '
     'This kit lets anyone design in our visual voice.')}
<div class="actions"><a class="btn" href="{D}/criptonautas-kit.zip" download>{t('Descargar todo', 'Download everything')} · ZIP {zip_kb / 1024:.1f} MB</a>{repo_btn}</div>
</div></div>

<section id="logo"><div class="wrap">
<h2>Logo</h2>
{blk('Seis humanos en ronda. Nadie en el centro ni por encima del resto. '
     'Logo en dos versiones: horizontal (símbolo y nombre) y solo símbolo.',
     'Six humans in a ring. No one at the centre or above the rest. '
     'The logo in two versions: horizontal (symbol and name) and symbol only.')}
<h3>{t('Horizontal', 'Horizontal')}</h3>
<div class="grid">{logo_cards(variants, 'horizontal', '780/155')}</div>
<h3>{t('Solo símbolo', 'Symbol only')}</h3>
{blk('Para avatares, íconos y lugares donde el nombre ya aparece cerca.',
     'For avatars, icons and places where the name already appears nearby.')}
<div class="grid">{logo_cards(variants, 'simbolo', '1/1')}</div>

<div class="rules">
<div class="rule"><h3>{t('Espacio libre', 'Clear space')}</h3>
{blk('Alrededor del logo queda libre, como mínimo, el diámetro de una cabeza del símbolo. '
     'Ningún texto, borde ni imagen entra en esa zona.',
     'Keep at least the diameter of one of the symbol’s heads clear around the logo. '
     'No text, edge or image enters that zone.')}
{clear_space()}</div>
<div class="rule"><h3>{t('Tamaño mínimo', 'Minimum size')}</h3>
<ul class="tight">
<li>{t('Símbolo: <strong>24 px</strong> en pantalla, <strong>8 mm</strong> impreso.',
       'Symbol: <strong>24 px</strong> on screen, <strong>8 mm</strong> in print.')}</li>
<li>{t('Horizontal: <strong>120 px</strong> de ancho en pantalla, <strong>30 mm</strong> impreso.',
       'Horizontal: <strong>120 px</strong> wide on screen, <strong>30 mm</strong> in print.')}</li>
</ul>
{blk('Más chico, las figuras se funden y el nombre deja de leerse.',
     'Any smaller and the figures merge and the name stops reading.')}</div>
</div>

<h3>{t('Usos incorrectos', 'Incorrect use')}</h3>
<div class="grid">{misuse()}</div>
</div></section>

<section id="color"><div class="wrap">
<h2>{t('Color', 'Colour')}</h2>
{blk('Los acentos salen del logo, con su intensidad de pantalla: presentes, sin brillar. '
     'Cada valor indica su contraste y en qué se usa en la comunidad.',
     'The accents come from the logo, at its screen intensity: present, never glowing. '
     'Each value lists its contrast and where the community uses it.')}
<h3>{t('Acentos', 'Accents')}</h3><div class="grid">{sw_brand}</div>
<h3>{t('Acentos en modo oscuro', 'Accents in dark mode')}</h3><div class="grid">{sw_dark}</div>
<h3>{t('Neutros', 'Neutrals')}</h3><div class="grid">{sw_neutral}</div>
<h3>{t('Estados', 'States')}</h3><div class="grid">{sw_sem}</div>
<h3>{t('Reglas', 'Rules')}</h3>
<ul class="tight">
<li>{t('No se inventan tonos: todo color sale de esta paleta.', 'No invented hues: every colour comes from this palette.')}</li>
<li>{t('Violeta Tinta puede ir en texto. Rojo Óxido solo en formas, gráficos y texto grande.',
       'Violeta Tinta may set text. Rojo Óxido is for shapes, graphics and large type only.')}</li>
<li>{t('Sin degradados, brillos ni neón.', 'No gradients, glows or neon.')}</li>
<li>{t('Los errores llevan ícono o texto, nunca solo color.', 'Errors carry an icon or label, never colour alone.')}</li>
<li>{t('Todo diseño tiene que entenderse también en escala de grises.', 'Every design must also read in greyscale.')}</li>
</ul>
<div class="dls">{dl('color/paleta.css', 'paleta.css')}{dl('color/tokens.json', 'tokens.json')}{dl('color/paleta.gpl', 'paleta.gpl (GIMP · Inkscape)')}{dl('color/discourse.json', 'discourse.json')}</div>
</div></section>

<section id="tipografia"><div class="wrap">
<h2>{t('Tipografía', 'Type')}</h2>
{blk('Dos familias, cada una con un lugar. Las dos son libres (licencia OFL) y vienen en el ZIP.',
     'Two families, each with its place. Both are free (OFL licence) and included in the ZIP.')}
<div class="grid wide">
<div class="type"><h3>Inter Tight</h3><p class="sample" style="font-family:'Inter Tight';font-weight:800;letter-spacing:-.02em">{t('Aprender en comunidad', 'Learning together')}</p>
<p class="sample" style="font-family:'Inter Tight'">{t('Una pregunta, varias respuestas.', 'One question, many answers.')}</p>
{blk('Titulares en todas las superficies, en 800 con la interletra cerrada (-0,02 em). Texto e interfaz en la comunidad, en 400.',
     'Headings on every surface, at 800 with tracking tightened (-0.02 em). Text and interface in the community, at 400.')}</div>
<div class="type"><h3>Lora</h3><p class="sample body" style="font-family:Lora">{t('El curso se lee con tiempo. Cada capítulo propone un criterio, lo explica con un caso real y deja la discusión abierta en la comunidad, donde se revisa y se mejora entre todos.', 'The course is read at length. Each chapter puts forward a criterion, explains it with a real case and leaves the discussion open in the community, where it is reviewed and improved together.')}</p>
{blk('Lectura larga en el blog: artículos, ensayos y capítulos del curso. Cuerpo en 400, con interlineado amplio y líneas de 60 a 75 caracteres. Los titulares siguen en Inter Tight.', 'Long-form reading on the blog: articles, essays and course chapters. Body at 400, with generous leading and lines of 60 to 75 characters. Headings stay in Inter Tight.')}</div>
</div>
{blk('El nombre del logo es un lettering propio: no se escribe con ninguna de estas tipografías.',
     'The name in the logo is custom lettering: it is never typeset in any of these faces.')}
</div></section>

<section id="imagenes"><div class="wrap">
<h2>{t('Imágenes', 'Imagery')}</h2>
{blk('<strong>Se ilustran situaciones, no individuos.</strong> Siluetas, manos, multitudes, objetos y símbolos. '
     'Nunca una figura de autoridad ni un rostro reconocible: es la regla que más distingue a la comunidad.',
     '<strong>Situations are illustrated, not individuals.</strong> Silhouettes, hands, crowds, objects and symbols. '
     'Never an authority figure or a recognisable face: this is the rule that most sets the community apart.')}
<div class="rules">
<div class="rule"><h3>{t('1 · Tinta y trama', '1 · Ink & halftone')}</h3>{blk('Portadas y artículos. Línea de tinta imperfecta, sombreado con trama, un solo acento.', 'Covers and articles. Imperfect ink line, halftone shading, one accent.')}</div>
<div class="rule"><h3>{t('2 · Retícula apagada', '2 · Muted grid')}</h3>{blk('Infografías y datos. Geometría que estructura: la retícula es el eje. Debe leerse sin color.', 'Infographics and data. Geometry that does the structuring: the grid is the axis. Must read without colour.')}</div>
<div class="rule"><h3>{t('3 · Secuencia', '3 · Sequence')}</h3>{blk('Procesos y pasos. Boceto suelto, 3 a 5 cuadros numerados.', 'Processes and steps. Loose sketch, 3 to 5 numbered frames.')}</div>
</div>
<div class="rules">
<div class="rule"><h3>{t('Siempre', 'Always')}</h3><ul class="tight">
<li>{t('Ink sobre Paper, con los acentos de la paleta.', 'Ink on Paper, with the palette’s accents.')}</li>
<li>{t('El texto lo agrega un humano, en Inter Tight, sobre una placa Paper.', 'Text is added by a human, in Inter Tight, on a Paper plate.')}</li>
<li>{t('Capturas y gráficos: Violeta Tinta marca lo importante, Rojo Óxido el contraejemplo. Rectángulos redondeados y flechas rectas.',
       'Screenshots and charts: Violeta Tinta marks what matters, Rojo Óxido the counter-example. Rounded rectangles and straight arrows.')}</li>
<li>{t('Los datos reales se dibujan o se capturan, nunca se generan con IA.', 'Real data is drawn or captured, never AI-generated.')}</li>
</ul></div>
<div class="rule"><h3>{t('Nunca', 'Never')}</h3><ul class="tight">
<li>{t('Neón, brillos, cromados, 3D o fotorrealismo.', 'Neon, glow, chrome, 3D or photorealism.')}</li>
<li>{t('Cohetes, lunas, autos de lujo, toros y osos, robots.', 'Rockets, moons, supercars, bulls and bears, robots.')}</li>
<li>{t('Texto escrito por un generador de imágenes.', 'Text written by an image generator.')}</li>
<li>{t('Alguien que pueda leerse como "el experto".', 'Anyone who could read as "the expert".')}</li>
</ul></div>
</div>
</div></section>

<section id="voz"><div class="wrap">
<h2>{t('Voz', 'Voice')}</h2>
<ul class="tight">
<li>{t('En la marca se nombra a la comunidad: "En Criptonautas…".', 'The brand names the community: "At Criptonautas…".')}</li>
<li>{t('La primera persona se usa para contar una experiencia directa.', 'First person is for telling a direct experience.')}</li>
<li>{t('Neutral y con autoridad: frases cortas, sin adjetivos de venta, sin promesas de ganancia.', 'Neutral and authoritative: short sentences, no sales adjectives, no promise of gains.')}</li>
<li>{t('Nunca "señales": se habla de criterios y de qué evaluar.', 'Never "signals": talk about criteria and what to assess.')}</li>
<li>{t('Es "la comunidad", no "el foro". Publicamos historias, no temas ni tópicos; respuestas, en vez de posteos. Y somos humanos, más que personas o usuarios.', 'It is "the community", not "the forum". We publish stories, not topics; replies, rather than posts. And we are humans, more than people or users.')}</li>
</ul>
<table class="voice"><thead><tr><th>{t('Así', 'Like this')}</th><th>{t('Así no', 'Not like this')}</th></tr></thead>
<tbody>{voice_rows}</tbody></table>
</div></section>

<section id="splash"><div class="wrap">
<h2>{t('Splash de carga', 'Loading splash')}</h2>
{blk('El anillo gira de a un paso y se ilumina la figura que llega arriba: toma la palabra y la cede. '
     'Con "reducir movimiento" activado se muestra el logo quieto.',
     'The ring turns one step at a time and the figure reaching the top lights up: it takes the floor and passes it on. '
     'With "reduce motion" on, the logo stays still.')}
<div class="splash"><div style="background:#F8F8F8;--tertiary:#5814EA;--quaternary:#E6211E">{SPLASH}</div>
<div style="background:#181719;--tertiary:#C89DFF;--quaternary:#F98E76">{SPLASH}</div></div>
<div class="dls">{dl('splash/criptonautas-splash.svg', 'criptonautas-splash.svg')}</div>
</div></section>

<section id="plantillas"><div class="wrap">
<h2>{t('Plantillas', 'Templates')}</h2>
{blk('Los SVG tienen el texto editable: se abren en Inkscape, Figma o Penpot con Inter Tight instalada.',
     'SVG text stays editable: open them in Inkscape, Figma or Penpot with Inter Tight installed.')}
<div class="grid wide tpl-grid">{tpl_cards}</div>
</div></section>

<section id="licencia"><div class="wrap">
<h2>{t('Licencia', 'Licence')}</h2>
<ul class="tight">
<li>{t('<strong>Logo, símbolo y nombre:</strong> se usan libremente para referirse a la comunidad o diseñar para ella, '
       'sin modificarlos y sin dar a entender que Criptonautas respalda algo que no organiza.',
       '<strong>Logo, symbol and name:</strong> free to use to refer to or design for the community, '
       'unmodified, and without implying Criptonautas endorses something it does not organise.')}</li>
<li>{t('<strong>Plantillas y textos:</strong> CC BY-NC-SA 4.0, sin uso comercial.', '<strong>Templates and copy:</strong> CC BY-NC-SA 4.0, no commercial use.')}</li>
<li>{t('<strong>Código:</strong> MIT. <strong>Tipografías:</strong> OFL, de sus autores.', '<strong>Code:</strong> MIT. <strong>Typefaces:</strong> OFL, by their authors.')}</li>
</ul>
<div class="dls">{dl('LICENSE.md', 'LICENSE.md')}</div>
<h3>{t('Contribuir', 'Contributing')}</h3>
{contrib}
</div></section>
</main>

<footer><div class="wrap">Criptonautas · {t('Kit de marca', 'Brand kit')} v{version} · {fecha} · <a href="https://criptonautas.co">criptonautas.co</a></div></footer>
<script>{JS}</script>
</body>
</html>
"""
