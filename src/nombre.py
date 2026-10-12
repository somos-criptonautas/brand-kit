#!/usr/bin/env python3
"""Rebuild the Criptonautas wordmark from the anti-aliased source as clean outlines.

Not a pixel trace: the anti-aliased edge is read to sub-pixel precision, the
1px sampling ripple is smoothed out, and each outline is refitted the way a
type designer draws it -- sharp corners kept, straight runs as true lines
(snapped vertical/horizontal), curves as few cubic Beziers with nodes on the
x/y extrema and axis-aligned handles there.
"""
import numpy as np
from PIL import Image
from skimage import measure
from fuente_png import coverage

UP = 8            # bicubic oversampling used only to locate the 50% edge
STEP = 0.08       # resampling step along the outline, source px
SMOOTH = 0.45     # gaussian sigma along the outline, source px (kills 1px ripple)
CORNER = 32       # degrees of turning within +-WIN to call a corner
WIN = 0.55        # source px
LINE_TOL = 0.10   # max deviation for a run to be a straight line, source px
CURVE_TOL = 0.2  # max Bezier deviation, source px (edge noise is ~0.06 px rms)
SNAP_DEG = 2.5    # lines within this of vertical/horizontal are snapped


# ---------- outline extraction ----------
def outlines():
    c, _ = coverage()
    ys = np.nonzero(c.max(1) > 0.02)[0]
    y0 = ys.min() - 3
    c = c[y0:ys.max() + 4]
    big = np.array(Image.fromarray((c * 255).astype('uint8'))
                   .resize((c.shape[1] * UP, c.shape[0] * UP), Image.BICUBIC)) / 255.0
    big = np.pad(big, 2)
    out = []
    for ct in measure.find_contours(big, 0.5):
        pts = (ct[:, ::-1] - 2 + 0.5) / UP - 0.5 / UP    # (x, y) in source px
        if len(pts) < 20:
            continue
        out.append(resample(pts))
    return out, c, y0


def resample(p):
    p = p[:-1] if np.allclose(p[0], p[-1]) else p
    q = np.vstack([p, p[:1]])
    seg = np.hypot(*np.diff(q, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(s[-1] / STEP), 8)
    t = np.linspace(0, s[-1], n, endpoint=False)
    return np.column_stack([np.interp(t, s, q[:, 0]), np.interp(t, s, q[:, 1])])


def gsmooth(p, sigma, closed=True):
    k = int(3 * sigma / STEP) + 1
    w = np.exp(-0.5 * (np.arange(-k, k + 1) * STEP / sigma) ** 2)
    w /= w.sum()
    if closed:
        ext = np.vstack([p[-k:], p, p[:k]])
    else:
        ext = np.vstack([2 * p[0] - p[k:0:-1], p, 2 * p[-1] - p[-2:-k - 2:-1]])
    return np.column_stack([np.convolve(ext[:, i], w, 'valid') for i in range(2)])


def heading(p):
    d = np.roll(p, -1, 0) - np.roll(p, 1, 0)
    return np.arctan2(d[:, 1], d[:, 0])


def corners(p):
    sm = gsmooth(p, 0.2)
    h = np.unwrap(heading(sm))
    k = int(WIN / STEP)
    n = len(p)
    hh = np.concatenate([h - (h[-1] - h[0] + (h[1] - h[0])) * 0, h])  # placeholder for clarity
    turn = np.degrees(np.abs(np.angle(np.exp(1j * (np.roll(h, -k) - np.roll(h, k))))))
    idx = []
    for i in range(n):
        if turn[i] >= CORNER and turn[i] == max(turn[(i + j) % n] for j in range(-k, k + 1)):
            if not idx or (i - idx[-1]) > k:
                idx.append(i)
    if len(idx) > 1 and (idx[0] + n - idx[-1]) <= k:
        idx.pop()
    return idx


# ---------- fitting ----------
def bez(ctrl, t):
    t = t[:, None]
    a, b, c, d = ctrl
    return (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d


def chord_params(p):
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
    return s / s[-1]


def fit_cubic(p, t0, t1):
    """Least-squares cubic with fixed end points and end tangent directions."""
    u = chord_params(p)
    for _ in range(4):
        b0, b1, b2, b3 = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
        A1, A2 = np.outer(b1, t0), np.outer(b2, t1)
        r = p - np.outer(b0 + b1, p[0]) - np.outer(b2 + b3, p[-1])
        C = np.array([[np.sum(A1 * A1), np.sum(A1 * A2)], [np.sum(A1 * A2), np.sum(A2 * A2)]])
        X = np.array([np.sum(A1 * r), np.sum(A2 * r)])
        try:
            a1, a2 = np.linalg.solve(C, X)
        except np.linalg.LinAlgError:
            a1 = a2 = -1
        L = np.hypot(*(p[-1] - p[0]))
        if a1 < 1e-3 * L or a2 < 1e-3 * L or a1 > L or a2 > L:
            a1 = a2 = L / 3
        ctrl = np.array([p[0], p[0] + a1 * t0, p[-1] + a2 * t1, p[-1]])
        u = reparam(ctrl, p, u)
    err = np.hypot(*(bez(ctrl, u) - p).T)
    return ctrl, err


def reparam(ctrl, p, u):
    a, b, c, d = ctrl
    for _ in range(2):
        t = u[:, None]
        q = bez(ctrl, u)
        q1 = 3 * ((1 - t) ** 2 * (b - a) + 2 * (1 - t) * t * (c - b) + t ** 2 * (d - c))
        q2 = 6 * ((1 - t) * (c - 2 * b + a) + t * (d - 2 * c + b))
        num = np.sum((q - p) * q1, 1)
        den = np.sum(q1 * q1, 1) + np.sum((q - p) * q2, 1)
        u = np.clip(u - np.where(np.abs(den) > 1e-12, num / den, 0), 0, 1)
        u[0], u[-1] = 0, 1
        u = np.maximum.accumulate(u)
    return u


def unit(v):
    n = np.hypot(*v)
    return v / n if n > 1e-12 else v


def tangent_at(p, i, back):
    k = max(2, int(0.35 / STEP))
    j = max(0, i - k) if back else min(len(p) - 1, i + k)
    return unit(p[j] - p[i])


def axis_snap(v):
    ang = np.degrees(np.arctan2(v[1], v[0])) % 90
    if min(ang, 90 - ang) < 12:
        return np.array([np.sign(v[0]), 0.0]) if abs(v[0]) > abs(v[1]) else np.array([0.0, np.sign(v[1])])
    return v


def fit_span(p, t0, t1, depth=0):
    if len(p) < 4:
        return [('L', p[0], p[-1])]
    ctrl, err = fit_cubic(p, t0, t1)
    if err.max() <= CURVE_TOL or depth > 8:
        return [('C',) + tuple(ctrl)]
    i = int(np.argmax(err))
    i = min(max(i, 3), len(p) - 4)
    tm = unit(p[min(i + 3, len(p) - 1)] - p[max(i - 3, 0)])
    return fit_span(p[:i + 1], t0, -tm, depth + 1) + fit_span(p[i:], tm, t1, depth + 1)


def is_line(p):
    a, b = p[0], p[-1]
    d = b - a
    L = np.hypot(*d)
    if L < 0.4:
        return False
    dev = np.abs((p[:, 0] - a[0]) * d[1] - (p[:, 1] - a[1]) * d[0]) / L
    return dev.max() <= LINE_TOL


def extrema(p):
    """Indices where the outline is horizontal or vertical (node positions).
    Found on a heavily smoothed copy so residual ripple cannot fake an extremum."""
    if len(p) < 10:
        return []
    q = gsmooth(p, 1.2, closed=False)
    d = np.diff(q, axis=0)
    m = int(2.5 / STEP)
    out = []
    for ax in (0, 1):
        s = np.sign(d[:, ax])
        for i in range(1, len(s)):
            if s[i] != s[i - 1] and s[i] != 0 and s[i - 1] != 0:
                out.append(i)
    out = sorted(i for i in set(out) if m <= i <= len(p) - 1 - m)
    keep = []
    for i in out:
        if not keep or i - keep[-1] > m:
            keep.append(i)
    return keep


def fit_curve_run(p):
    """Split a smooth run at its extrema, give those nodes axis-aligned handles."""
    cuts = [0] + extrema(p) + [len(p) - 1]
    segs = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        q = p[a:b + 1]
        t0 = tangent_at(p, a, back=False)
        t1 = tangent_at(p, b, back=True)
        if a != 0:
            t0 = axis_snap(t0)
        if b != len(p) - 1:
            t1 = axis_snap(t1)
        segs += fit_span(q, t0, t1)
    return segs


def fit_outline(raw):
    cidx = corners(raw)
    n = len(raw)
    if not cidx:                                   # fully smooth loop: start at the top extremum
        i0 = int(np.argmin(raw[:, 1]))
        raw = np.roll(raw, -i0, 0)
        p = gsmooth(raw, SMOOTH)
        p = np.vstack([p, p[:1]])
        t = np.array([1.0 if p[1, 0] > p[0, 0] else -1.0, 0.0])
        cuts = [0] + extrema(p) + [len(p) - 1]
        segs = []
        for a, b in zip(cuts[:-1], cuts[1:]):
            t0 = axis_snap(tangent_at(p, a, False)) if a else t
            t1 = axis_snap(tangent_at(p, b, True)) if b != len(p) - 1 else -t
            segs += fit_span(p[a:b + 1], t0, t1)
        return segs
    raw = np.roll(raw, -cidx[0], 0)
    cidx = [(c - cidx[0]) % n for c in cidx] + [n]
    loop = np.vstack([raw, raw[:1]])
    segs = []
    for a, b in zip(cidx[:-1], cidx[1:]):
        run = loop[a:b + 1]
        if is_line(run):
            segs.append(('L', run[0], run[-1]))
            continue
        sm = gsmooth(run, SMOOTH, closed=False)
        sm[0], sm[-1] = run[0], run[-1]            # corners stay where the edge says
        # a run may still hold straight sub-runs (e.g. a stem flowing into a curve)
        segs += split_lines_and_curves(sm)
    return segs


MINLINE = 6.0       # shortest straight run kept as a line inside a curved run, source px
STEM_MIN = 10.0     # px
INLINE_TOL = 0.06   # stricter straightness inside curved runs


def straight_intervals(p):
    m = int(MINLINE / STEP)
    out, i, n = [], 0, len(p)
    while i + m < n:
        j = i + m
        if dev(p[i:j + 1]) <= INLINE_TOL:
            while j + 1 < n and dev(p[i:j + 2]) <= INLINE_TOL:
                j += 1
            v = p[j] - p[i]
            ang = np.degrees(np.arctan2(v[1], v[0])) % 90
            # inside a smooth run only stems/bars count as straight: long and axis-aligned
            if np.hypot(*v) >= STEM_MIN and min(ang, 90 - ang) < 3:
                out.append((i, j))
            i = j + 1
        else:
            i += max(1, m // 6)
    return out


def dev(p):
    a, b = p[0], p[-1]
    d = b - a
    L = np.hypot(*d)
    if L < 1e-9:
        return 1e9
    return (np.abs((p[:, 0] - a[0]) * d[1] - (p[:, 1] - a[1]) * d[0]) / L).max()


def split_lines_and_curves(p):
    """Keep genuinely straight sub-runs (a stem flowing into a bowl) as lines; fit the rest as curves."""
    iv = straight_intervals(p)
    out, k = [], 0
    for i, j in iv:
        if i - k >= 4:
            out += fit_curve_run(p[k:i + 1])
        elif i > k:
            out.append(('L', p[k], p[i]))
        out.append(('L', p[i], p[j]))
        k = j
    if len(p) - 1 - k >= 4:
        out += fit_curve_run(p[k:])
    elif len(p) - 1 > k:
        out.append(('L', p[k], p[-1]))
    return out


def tidy(segs, eps=0.15):
    """Drop sliver segments left at corners, joining their neighbours."""
    out = []
    for s in segs:
        a, b = s[1], (s[2] if s[0] == 'L' else s[4])
        if np.hypot(*(b - a)) < eps and out:
            prev = out[-1]
            out[-1] = shift_end(prev, b - (prev[2] if prev[0] == 'L' else prev[4]))
            continue
        out.append(s)
    # merge consecutive collinear lines
    merged = []
    for s in out:
        if merged and s[0] == 'L' and merged[-1][0] == 'L':
            a, m, b = merged[-1][1], merged[-1][2], s[2]
            if dev(np.array([a, m, b])) < 0.04:
                merged[-1] = ('L', a, b)
                continue
        merged.append(s)
    return merged


# ---------- regularisation ----------
def snap_lines(loops):
    """Make near-vertical/horizontal lines exact, carrying the moved node into neighbours."""
    for segs in loops:
        n = len(segs)
        for i, s in enumerate(segs):
            if s[0] != 'L':
                continue
            a, b = s[1], s[2]
            ang = np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0])) % 180
            if min(ang, 180 - ang) < SNAP_DEG:
                y = (a[1] + b[1]) / 2
                move(segs, i, a.copy(), np.array([a[0], y]), b.copy(), np.array([b[0], y]))
            elif abs(ang - 90) < SNAP_DEG:
                x = (a[0] + b[0]) / 2
                move(segs, i, a.copy(), np.array([x, a[1]]), b.copy(), np.array([x, b[1]]))
    return loops


def move(segs, i, a0, a1, b0, b1):
    n = len(segs)
    segs[i] = ('L', a1, b1)
    pi, ni = (i - 1) % n, (i + 1) % n
    segs[pi] = shift_end(segs[pi], a1 - a0)
    segs[ni] = shift_start(segs[ni], b1 - b0)


def shift_end(s, d):
    if s[0] == 'L':
        return ('L', s[1], s[2] + d)
    return ('C', s[1], s[2], s[3] + d, s[4] + d)


def shift_start(s, d):
    if s[0] == 'L':
        return ('L', s[1] + d, s[2])
    return ('C', s[1] + d, s[2] + d, s[3], s[4])


def chord(s):
    return np.hypot(*((s[2] if s[0] == 'L' else s[4]) - s[1]))


def flat_axis(s, sag=0.45, deg=3):
    """A barely-bent curve running along an axis is a straight edge blurred by the raster."""
    a, b = s[1], s[4]
    if chord(s) < 3:
        return False
    ang = np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0])) % 90
    return min(ang, 90 - ang) < deg and dev(np.array([a, s[2], s[3], b])) < sag


def regularise(loops):
    """Type-design clean-up: no slivers at corners, one node per straight edge,
    and shared horizontals (baseline, x-height, cap, descender) on one exact value."""
    for k, segs in enumerate(loops):
        segs = [('L', s[1], s[4]) if s[0] == 'C' and (chord(s) < 0.7 or flat_axis(s)) else s for s in segs]
        loops[k] = segs
    snap_lines(loops)
    for k, segs in enumerate(loops):
        merged = []
        for s in segs:
            if merged and s[0] == 'L' and merged[-1][0] == 'L' and \
                    dev(np.array([merged[-1][1], merged[-1][2], s[2]])) < 0.03:
                merged[-1] = ('L', merged[-1][1], s[2])
            else:
                merged.append(s)
        if len(merged) > 2 and merged[0][0] == 'L' and merged[-1][0] == 'L' and \
                dev(np.array([merged[-1][1], merged[0][1], merged[0][2]])) < 0.03:
            merged[0] = ('L', merged[-1][1], merged[0][2])
            merged.pop()
        loops[k] = merged
    # horizontal metric lines
    ys = sorted(s[1][1] for l in loops for s in l if s[0] == 'L' and abs(s[1][1] - s[2][1]) < 1e-9)
    clusters = []
    for y in ys:
        if clusters and y - clusters[-1][-1] < 0.4:
            clusters[-1].append(y)
        else:
            clusters.append([y])
    target = {y: float(np.mean(c)) for c in clusters for y in c}
    for segs in loops:
        for i, s in enumerate(segs):
            if s[0] == 'L' and abs(s[1][1] - s[2][1]) < 1e-9:
                t = target[s[1][1]]
                move(segs, i, s[1].copy(), np.array([s[1][0], t]), s[2].copy(), np.array([s[2][0], t]))
    return loops, [round(float(np.mean(c)), 2) for c in clusters if len(c) > 2]


def end_dir(s):
    if s[0] == 'L':
        return s[2] - s[1]
    v = s[4] - s[3]
    return v if np.hypot(*v) > 1e-6 else s[4] - s[2]


def start_dir(s):
    if s[0] == 'L':
        return s[2] - s[1]
    v = s[2] - s[1]
    return v if np.hypot(*v) > 1e-6 else s[3] - s[1]


def sharpen(loops, short=1.3, span=2.6, min_turn=30):
    """Corners: the ~1px bevel left by the anti-aliased edge is replaced by the
    true corner, i.e. the meeting point of the two edges' tangents."""
    for k, segs in enumerate(loops):
        changed = True
        while changed:
            changed = False
            n = len(segs)
            for i in range(n):
                if chord(segs[i]) >= short:
                    continue
                j = i                                  # extend cluster forward
                while chord(segs[(j + 1) % n]) < short and (j - i) < n - 3:
                    j += 1
                if chord(segs[(i - 1) % n]) < short:
                    continue                           # handled from the cluster's first member
                cl = [segs[(q) % n] for q in range(i, j + 1)]
                if sum(chord(c) for c in cl) > span:
                    continue
                P, N = segs[(i - 1) % n], segs[(j + 1) % n]
                if chord(P) < 2 or chord(N) < 2:
                    continue
                dp, dn = end_dir(P), start_dir(N)
                cosang = np.dot(dp, dn) / (np.hypot(*dp) * np.hypot(*dn))
                if np.degrees(np.arccos(np.clip(cosang, -1, 1))) < min_turn:
                    continue
                p0 = P[2] if P[0] == 'L' else P[4]
                q0 = N[1]
                den = dp[0] * dn[1] - dp[1] * dn[0]
                if abs(den) < 1e-9:
                    continue
                t = ((q0[0] - p0[0]) * dn[1] - (q0[1] - p0[1]) * dn[0]) / den
                X = p0 + t * dp
                mid = (cl[0][1] + (cl[-1][2] if cl[-1][0] == 'L' else cl[-1][4])) / 2
                if np.hypot(*(X - mid)) > span:
                    continue
                newP = shift_end(P, X - p0)
                newN = shift_start(N, X - q0)
                idx = sorted({(q) % n for q in range(i, j + 1)})
                segs[(i - 1) % n] = newP
                segs[(j + 1) % n] = newN
                for q in reversed(idx):
                    del segs[q]
                changed = True
                break
        loops[k] = segs
    return loops


def smooth_joins(loops, max_deg=22):
    """Nodes that are meant to be smooth get collinear handles (G1): no kinks."""
    for segs in loops:
        n = len(segs)
        for i in range(n):
            a, b = segs[i], segs[(i + 1) % n]
            da, db = end_dir(a), start_dir(b)
            la, lb = np.hypot(*da), np.hypot(*db)
            if la < 1e-9 or lb < 1e-9:
                continue
            ang = np.degrees(np.arccos(np.clip(np.dot(da, db) / (la * lb), -1, 1)))
            if ang < 0.05 or ang > max_deg:
                continue
            if a[0] == 'L' and b[0] == 'L':
                continue
            if a[0] == 'L':
                u = da / la
            elif b[0] == 'L':
                u = db / lb
            else:
                u = da / la + db / lb
                u /= np.hypot(*u)
            node = a[2] if a[0] == 'L' else a[4]
            if a[0] == 'C':
                h = np.hypot(*(a[4] - a[3]))
                segs[i] = ('C', a[1], a[2], node - u * h, node)
            if b[0] == 'C':
                h = np.hypot(*(b[2] - b[1]))
                segs[(i + 1) % n] = ('C', node, node + u * h, b[3], b[4])
    return loops


def to_d(loops, scale=1.0, ox=0.0, oy=0.0, nd=2):
    f = lambda z: f"{(z[0] - ox) * scale:.{nd}f} {(z[1] - oy) * scale:.{nd}f}"
    out = []
    for segs in loops:
        out.append('M ' + f(segs[0][1]))
        for s in segs:
            out.append(('L ' + f(s[2])) if s[0] == 'L' else ('C ' + ' '.join(f(q) for q in s[2:])))
        out.append('Z')
    return ' '.join(out)


def build():
    raws, c, y0 = outlines()
    loops = [tidy(fit_outline(r)) for r in raws]
    loops = snap_lines(loops)
    loops, metrics = regularise(loops)
    loops = sharpen(loops)
    # smooth_joins: tried, rotating handles cost more fidelity than it saved
    build.metrics = metrics
    return loops, c, y0


def fidelity(loops, c):
    import io, cairosvg
    H, W = c.shape
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<path fill="#000" fill-rule="evenodd" d="{to_d(loops)}"/></svg>')
    r = np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA'))[..., 3] / 255
    return ((r > .5) & (c > .5)).sum() / ((r > .5) | (c > .5)).sum()


if __name__ == '__main__':
    loops, c, y0 = build()
    iou = fidelity(loops, c)
    n = sum(len(l) for l in loops)
    print(f'outlines {len(loops)}  segments {n}  IoU vs source {iou:.4f}')
    assert len(loops) == 17 and iou > 0.99, 'rebuild drifted from the source lettering'
