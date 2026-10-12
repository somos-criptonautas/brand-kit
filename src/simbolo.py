#!/usr/bin/env python3
"""Criptonautas mark, rebuilt analytically.

Six figures on a 60 deg ring. One figure is constructed once in local
coords (u = outward along its axis, v = lateral) and instanced by rotation,
so the six-fold symmetry is exact rather than traced.

Figure geometry, before the gutter inset:
  head    disc at (R, 0), radius r
  sector  |angle| <= 30 deg around +u, apex at the mark centre
  shoulders  two lines through the head centre at 30 deg to the lateral
             axis, keeping the side toward the centre
  neck    the sector is cut back off the head disc
A uniform inset of D on every edge opens the gutters, the central star and
the neck gap in one operation, so one number controls all the spacing.
"""
import math

GUTTER = 21.5      # half the gap between figures; matches the 2023 mark
R = 400.0          # head centre, distance from mark centre
r = 81.5           # head radius
C = 500.0          # viewBox centre
VB = 1000

S3 = math.sqrt(3) / 2   # cos 30
H = 0.5                 # sin 30


def line_x(n, c):
    """Line {P : P.n = c} as (nu, nv, c)."""
    return (n[0], n[1], c)


def isect(l1, l2):
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = a1 * b2 - a2 * b1
    return ((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det)


def line_circle(l, ctr, rad, pick):
    """Intersections of line with circle; pick=-1/+1 selects along the line dir."""
    a, b, c = l
    # closest point on line to ctr
    t = c - (a * ctr[0] + b * ctr[1])
    foot = (ctr[0] + a * t, ctr[1] + b * t)
    h2 = rad * rad - t * t
    if h2 < 0:
        raise ValueError("line misses circle")
    h = math.sqrt(h2)
    dirv = (-b, a)
    return (foot[0] + pick * h * dirv[0], foot[1] + pick * h * dirv[1])


# Flat cut across each body's inner end, measured from the mark centre.
# The original mark truncates the apex rather than letting six points meet;
# that chamfer is what opens the six-pointed void at the centre.
TRUNC = 66.0


def figure(D, T=TRUNC):
    """Return the body vertices and neck radius in local (u, v)."""
    gap = r + 2 * D          # inner radius of the neck arc
    # sector edges, normals pointing into the sector
    edge_L = line_x((H, S3), D)      # left  (v < 0 side)
    edge_R = line_x((H, -S3), D)     # right (v > 0 side)
    # shoulder cuts through the head centre, normals pointing toward the centre
    sh_L = line_x((-S3, H), D - S3 * R)
    sh_R = line_x((-S3, -H), D - S3 * R)

    apex = isect(edge_L, edge_R)             # where the two edges would meet
    T = max(T, apex[0])                      # never cut past the apex
    w = (0.5 * T - D) / S3                   # half-width of the flat at u = T
    cutL, cutR = (T, w), (T, -w)             # cutL on the right edge, then across
    tipL = isect(edge_L, sh_L)               # left arm tip
    tipR = isect(edge_R, sh_R)
    # where each shoulder cut runs back onto the neck arc
    bL = line_circle(sh_L, (R, 0.0), gap, +1)
    bR = line_circle(sh_R, (R, 0.0), gap, -1)
    return cutL, cutR, tipL, bL, bR, tipR, gap


def to_xy(p):
    """local (u, v) -> SVG (x, y); u outward is up."""
    return (C + p[1], C - p[0])


def fmt(p):
    x, y = to_xy(p)
    return f"{x:.2f} {y:.2f}"


def body_path(D, T=TRUNC):
    cutL, cutR, tipL, bL, bR, tipR, gap = figure(D, T)
    return (
        f"M {fmt(cutL)} L {fmt(cutR)} L {fmt(tipL)} L {fmt(bL)} "
        f"A {gap:.2f} {gap:.2f} 0 0 0 {fmt(bR)} "
        f"L {fmt(tipR)} Z"
    )


VIOLET = "#5814EA"
RUST = "#E6211E"
VIOLET_DK = "#7C36FF"   # dark-surface variants, color-system-v02 §3
RUST_DK = "#F98E76"
INK = "#14110F"
PAPER = "#E8E6E1"


def svg(D=GUTTER, mono=None, title="Criptonautas", pair=(VIOLET, RUST), T=TRUNC):
    head_y = C - R
    body = body_path(D, T)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}" '
        f'width="{VB}" height="{VB}" role="img" aria-label="{title}">',
        f"  <title>{title}</title>",
        "  <defs>",
        '    <g id="cn-figure">',
        f'      <circle cx="{C:.0f}" cy="{head_y:.2f}" r="{r:.2f}"/>',
        f'      <path d="{body}"/>',
        "    </g>",
        "  </defs>",
    ]
    for i in range(6):
        fill = mono if mono else pair[i % 2]
        rot = f' transform="rotate({i * 60} {C:.0f} {C:.0f})"' if i else ""
        out.append(f'  <use href="#cn-figure" fill="{fill}"{rot}/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def svg_flat(D=GUTTER, mono=None, title="Criptonautas", pair=(VIOLET, RUST), T=TRUNC):
    """Same mark with the instances baked into literal paths."""
    head_y = C - R
    body = body_path(D, T)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}" '
        f'width="{VB}" height="{VB}" role="img" aria-label="{title}">',
        f"  <title>{title}</title>",
    ]
    for i in range(6):
        fill = mono if mono else pair[i % 2]
        rot = f' transform="rotate({i * 60} {C:.0f} {C:.0f})"' if i else ""
        out.append(f'  <g fill="{fill}"{rot}>')
        out.append(f'    <circle cx="{C:.0f}" cy="{head_y:.2f}" r="{r:.2f}"/>')
        out.append(f'    <path d="{body}"/>')
        out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def demo():
    """One runnable check: symmetry, closure and gutter width."""
    D = 21.5
    cutL, cutR, tipL, bL, bR, tipR, gap = figure(D)
    assert abs(cutL[1] + cutR[1]) < 1e-9 and cutL[0] == cutR[0] == TRUNC
    assert cutL[1] > 0 and cutL[0] > 2 * D       # flat sits short of the apex
    assert abs(tipL[1] + tipR[1]) < 1e-9 and abs(tipL[0] - tipR[0]) < 1e-9
    assert abs(bL[1] + bR[1]) < 1e-9 and abs(bL[0] - bR[0]) < 1e-9
    for p in (bL, bR):
        assert abs(math.hypot(p[0] - R, p[1]) - gap) < 1e-6
    # arm tips must sit outside the neck arc, or the arm has no point
    assert math.hypot(tipL[0] - R, tipL[1]) > gap
    # the flat's ends must land exactly on the two sector edges
    assert abs(H * cutL[0] - S3 * cutL[1] - D) < 1e-9   # on the right edge
    assert abs(H * cutR[0] + S3 * cutR[1] - D) < 1e-9   # on the left edge
    # no-truncation case degenerates to the sharp apex
    a = figure(D, 0.0)
    assert abs(a[0][1]) < 1e-9 and abs(a[0][0] - 2 * D) < 1e-9
    print("demo ok  flat half-width", round(cutL[1], 2),
          " neck radius", round(gap, 2))


if __name__ == "__main__":
    demo()
