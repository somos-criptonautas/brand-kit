#!/usr/bin/env python3
"""Wordmark + horizontal lockup SVGs, placed exactly where the original lockup has them."""
import simbolo as symbol
import nombre as fit

S = 10                      # 1 source px = 10 units
LEFT, TOP = 25, 21          # original lockup's top-left edge, source px
SYM_C, SYM_H = (94.0, 98.5), 155.0   # original symbol centre and height, source px
X0, Y0 = 185, 60            # wordmark crop origin inside the source image
W, H = (805 - LEFT) * S, (176 - TOP) * S

INK, PAPER = '#14110F', '#E8E6E1'
VIOLET, RUST = '#5814EA', '#E6211E'
VIOLET_DK, RUST_DK = '#7C36FF', '#F98E76'


def wordmark_d(ox, oy):
    loops, _, y0 = fit.build()
    assert y0 == Y0, y0
    return fit.to_d(loops, scale=S, ox=ox, oy=oy, nd=1)


def symbol_group(fills):
    k = SYM_H * S / (2 * (symbol.R + symbol.r))
    cx, cy = (SYM_C[0] - LEFT) * S, (SYM_C[1] - TOP) * S
    body = symbol.body_path(symbol.GUTTER)
    figs = []
    for i in range(6):
        rot = f' transform="rotate({i * 60} 500 500)"' if i else ''
        figs.append(f'<g fill="{fills[i % 2]}"{rot}><circle cx="500" cy="100" r="81.5"/><path d="{body}"/></g>')
    return (f'<g transform="translate({cx - 500 * k:.2f} {cy - 500 * k:.2f}) scale({k:.6f})">'
            + ''.join(figs) + '</g>')


def lockup(sym_fills, text_fill, d):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
            f'{symbol_group(sym_fills)}'
            f'<path fill="{text_fill}" fill-rule="evenodd" d="{d}"/></svg>\n')


def variants():
    """The four horizontal lockups, keyed by variant slug."""
    d = wordmark_d(ox=LEFT - X0, oy=TOP - Y0)
    return {
        'color': lockup((VIOLET, RUST), INK, d),
        'oscuro': lockup((VIOLET_DK, RUST_DK), PAPER, d),
        'una-tinta': lockup((INK, INK), INK, d),
        'negativo': lockup((PAPER, PAPER), PAPER, d),
    }


if __name__ == '__main__':
    v = variants()
    assert len(v) == 4 and all(s.startswith('<svg') for s in v.values())
    print('ok', {k: len(s) for k, s in v.items()})
