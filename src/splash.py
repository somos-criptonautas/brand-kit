#!/usr/bin/env python3
"""Discourse splash: ring turns 60 deg per beat, the light belongs to the top slot.

Discourse rules: CSS keyframes only (no SMIL), animate transform/opacity only,
prefixed keyframe names, theme colours via var(--tertiary) / var(--quaternary).
"""
import simbolo as build

STEP = 0.55            # one beat
TURN = 0.35            # rotation inside the beat; the rest is the pause
DIM = 0.35             # opacity of figures not at the top
CYCLE = 6 * STEP
EASE = "cubic-bezier(.55,0,.15,1)"


def pct(t):
    return f"{t / CYCLE * 100:.3f}%"


def turn_keyframes():
    out = []
    for k in range(6):
        t0 = k * STEP
        out.append(f"{pct(t0)}{{transform:rotate({k * 60}deg)}}")
        out.append(f"{pct(t0 + TURN)}{{transform:rotate({(k + 1) * 60}deg)}}")
    out.append(f"100%{{transform:rotate(360deg)}}")
    return "".join(out)


def lit_keyframes():
    # Figure 0's opacity: lit at the top, leaves in beat 1, returns in beat 6.
    # Figure i runs the same curve i beats earlier (negative delay).
    back = 5 * STEP
    return (f"0%{{opacity:1}}{pct(TURN)}{{opacity:{DIM}}}"
            f"{pct(back)}{{opacity:{DIM}}}{pct(back + TURN)}{{opacity:1}}"
            f"100%{{opacity:1}}")


def splash():
    body = build.body_path(build.GUTTER)
    head_y = build.C - build.R
    m = 500 - (build.R + build.r)            # ring radius 481.5: no clipping mid-turn
    css = (
        ".cn-v{fill:var(--tertiary,#5814EA)}.cn-r{fill:var(--quaternary,#E6211E)}"
        f".cn-ring{{transform-box:fill-box;transform-origin:50% 50%;"
        f"animation:cn-turn {CYCLE:.2f}s {EASE} infinite}}"
        f".cn-f{{animation:cn-lit {CYCLE:.2f}s {EASE} infinite}}"
        f"@keyframes cn-turn{{{turn_keyframes()}}}"
        f"@keyframes cn-lit{{{lit_keyframes()}}}"
        "@media (prefers-reduced-motion:reduce){.cn-ring,.cn-f{animation:none}}"
    )
    figs = []
    for i in range(6):
        cls = "cn-v" if i % 2 == 0 else "cn-r"
        rot = f' transform="rotate({i * 60} 500 500)"' if i else ""
        delay = f' style="animation-delay:-{i * STEP:.2f}s"' if i else ""
        figs.append(
            f'<g class="cn-f {cls}"{delay}><g{rot}>'
            f'<circle cx="500" cy="{head_y:.0f}" r="{build.r}"/><path d="{body}"/></g></g>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m:g} {m:g} {1000 - 2 * m:g} {1000 - 2 * m:g}">'
        f'<style>{css}</style>'
        f'<g class="cn-ring">{"".join(figs)}</g></svg>\n'
    )


def demo():
    s = splash()
    assert "<animate" not in s                      # no SMIL
    assert "@keyframes cn-turn" in s and "@keyframes cn-lit" in s
    # figure i must be fully lit exactly when it reaches the top:
    # it arrives at the end of the turn of beat (6 - i)
    for i in range(1, 6):
        arrive = (6 - i - 1) * STEP + TURN          # absolute time
        template = (arrive + i * STEP) % CYCLE      # where the delay puts it in figure 0's curve
        assert abs(template - (5 * STEP + TURN)) < 1e-9, (i, template)
    print("demo ok", len(s.encode()), "bytes")


if __name__ == "__main__":
    demo()
