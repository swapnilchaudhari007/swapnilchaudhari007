"""3D-styled contribution snake: a glossy snake slithers across the contribution grid and eats
every day with activity, then the board resets. Pure SMIL, so it animates inside <img> on GitHub.

Usage (also called from fx3d.build_all during the daily workflow):
  python3 scripts/snake.py --data contributions.json   # [["YYYY-MM-DD", n], ...]
"""
import datetime as dt
import json
import os
import sys

from build_profile_svgs import THEMES, shade
import profile_sections as ps

CELL, GAP = 16, 4
STEP = CELL + GAP
X0, Y0 = 70, 132
SEG = 7            # snake length in cells
DT = 0.09          # seconds per cell moved


def _grid(days):
    days = sorted((dt.date.fromisoformat(d) if isinstance(d, str) else d, c) for d, c in days)
    start = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7)  # Sunday on/before first day
    cells = {}
    for d, c in days:
        k = (d - start).days
        cells[(k // 7, k % 7)] = c
    weeks = max(w for w, _ in cells) + 1
    return cells, weeks


def _level(c, mx):
    if c <= 0:
        return 0
    q = c / max(mx, 1)
    return 1 if q <= .25 else 2 if q <= .5 else 3 if q <= .75 else 4


def _route(targets):
    """Greedy nearest-neighbour tour over the food cells, walked one grid step at a time."""
    pos = (-1, 0)
    path = [(-SEG - 1, 0), pos]
    left = set(targets)
    eat = {}
    while left:
        nxt = min(left, key=lambda p: (abs(p[0] - pos[0]) + abs(p[1] - pos[1]), p))
        left.remove(nxt)
        x, y = pos
        while x != nxt[0]:
            x += 1 if nxt[0] > x else -1
            path.append((x, y))
        while y != nxt[1]:
            y += 1 if nxt[1] > y else -1
            path.append((x, y))
        pos = (x, y)
        eat[nxt] = len(path) - 1
    # leave to the right, off the board
    x, y = pos
    for _ in range(SEG + 2):
        x += 1
        path.append((x, y))
    return path, eat


def _xy(p):
    return X0 + p[0] * STEP + CELL / 2, Y0 + p[1] * STEP + CELL / 2


def snake(theme, days):
    t = THEMES[theme]
    dark = theme == "dark"
    lv = t["levels"]
    cells, weeks = _grid(days)
    mx = max(cells.values())
    food = [p for p, c in cells.items() if c > 0]
    path, eat = _route(food)
    steps = len(path) - 1
    pause = 1.6
    T = steps * DT + pause
    W = 1200
    H = Y0 + 7 * STEP + 52

    o = [ps.eyebrow(theme, 56, 66, "Contribution snake"),
         f'<text x="56" y="106" font-family="{ps.FONT}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">Eating my commits, one day at a time</text>']

    # board: empty cells as a pattern (tiny), active days drawn on top
    o.append(f'<defs><pattern id="cell" x="{X0}" y="{Y0}" width="{STEP}" height="{STEP}" patternUnits="userSpaceOnUse">'
             f'<rect width="{CELL}" height="{CELL}" rx="4" fill="{lv[0]}"/>'
             f'<rect width="{CELL}" height="2" rx="1" y="0" fill="#fff" fill-opacity="{.05 if dark else .5}"/></pattern>'
             f'<radialGradient id="ball" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#ffffff"/>'
             f'<stop offset=".35" stop-color="{shade(t["accent"], 1.25)}"/><stop offset="1" stop-color="{shade(t["accent2"], .7)}"/></radialGradient>'
             f'<radialGradient id="head" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#ffffff"/>'
             f'<stop offset=".35" stop-color="{shade(t["accent2"], 1.3)}"/><stop offset="1" stop-color="{shade(t["accent2"], .55)}"/></radialGradient>'
             f'<filter id="sg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter></defs>')
    o.append(f'<rect x="{X0}" y="{Y0}" width="{weeks * STEP - GAP}" height="{7 * STEP - GAP}" fill="url(#cell)"/>')

    for p in sorted(food):
        c = cells[p]
        col = lv[_level(c, mx)]
        k = eat[p] * DT / T
        x, y = X0 + p[0] * STEP, Y0 + p[1] * STEP
        o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{col}">'
                 f'<animate attributeName="fill" values="{col};{lv[0]};{lv[0]};{col}" keyTimes="0;{k:.4f};.985;1" '
                 f'calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/></rect>')
        # little pop when eaten
        cx, cy = x + CELL / 2, y + CELL / 2
        o.append(f'<circle cx="{cx}" cy="{cy}" r="0" fill="none" stroke="{t["accent"]}" stroke-width="2" opacity="0">'
                 f'<animate attributeName="r" values="0;0;14;14" keyTimes="0;{k:.4f};{min(.999, k + .03):.4f};1" dur="{T:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;.9;0;0" keyTimes="0;{k:.4f};{min(.999, k + .03):.4f};1" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/></circle>')

    # snake: segments follow the same polyline, each a step behind the one in front
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in map(_xy, path))
    d = "M" + pts.replace(" ", " L")
    move_end = steps * DT / T
    for i in reversed(range(SEG)):
        r = CELL / 2 + 1 - i * .55
        lag = i * DT
        grad = "head" if i == 0 else "ball"
        body = (f'<ellipse cy="{r * .9:.1f}" rx="{r:.1f}" ry="{r * .45:.1f}" fill="#000" opacity="{.35 if dark else .18}" filter="url(#sg)"/>'
                f'<circle r="{r:.1f}" fill="url(#{grad})"/>')
        if i == 0:  # eyes
            body += '<circle cx="2.5" cy="-3" r="2" fill="#fff"/><circle cx="3" cy="-3" r="1" fill="#0b1220"/>'
        o.append(f'<g>{body}<animateMotion path="{d}" dur="{T:.2f}s" repeatCount="indefinite" calcMode="linear" '
                 f'keyPoints="0;0;1;1" keyTimes="0;{lag / T:.4f};{min(.999, move_end + lag / T):.4f};1" rotate="auto"/></g>')

    total = sum(cells.values())
    o.append(f'<text x="{W - 56}" y="{H - 22}" text-anchor="end" font-family="{ps.MONO}" font-size="12" fill="{t["faint"]}">'
             f'{total} contributions · {len(food)} active days in the last year</text>')
    return ps.frame(theme, W, H, (0.85, 0.2), "\n".join(o), "Contribution snake eating the activity graph")


def stats_card(theme, days):
    """Activity stats: four 3D tiles (total, current streak, longest streak, best day) and an
    isometric bar chart of the last 16 weeks."""
    from build_profile_svgs import stats, esc
    t = THEMES[theme]
    dark = theme == "dark"
    days, st = stats(days)
    W, H = 1200, 300
    o = [ps.eyebrow(theme, 56, 66, "GitHub activity"),
         f'<text x="56" y="106" font-family="{ps.FONT}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">Shipping streak</text>']
    tiles = [(f'{st["total"]}', "total contributions", t["accent"]),
             (f'{st["current"]} days', "current streak", "#f59e0b"),
             (f'{st["longest"]} days', "longest streak", "#a78bfa"),
             (f'{st["best_c"]}', f'best day · {st["best_d"]:%b %d}', "#34d399")]
    x = 56
    for i, (big, small, col) in enumerate(tiles):
        w, h, dep = 156, 112, 8
        y = 136
        o.append(f'<g>{ps.enter(.15 + i * .12, 12)}'
                 f'<rect x="{x}" y="{y + dep}" width="{w}" height="{h}" rx="16" fill="{shade(col, .45 if dark else .8)}" fill-opacity="{.55 if dark else .5}"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{col}" stroke-opacity=".55"/>'
                 f'<rect x="{x + 14}" y="{y + 4}" width="{w - 28}" height="2" rx="1" fill="#fff" fill-opacity="{.1 if dark else .9}"/>'
                 f'<circle cx="{x + 24}" cy="{y + 28}" r="6" fill="{col}"/>'
                 f'<text x="{x + 18}" y="{y + 72}" font-family="{ps.FONT}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">{esc(big)}</text>'
                 f'<text x="{x + 18}" y="{y + 96}" font-family="{ps.FONT}" font-size="13" fill="{t["muted"]}">{esc(small)}</text></g>')
        x += w + 14
    # isometric weekly bars (last 16 weeks)
    weeks = []
    for k in range(16):
        end = days[-1][0] - dt.timedelta(days=7 * (15 - k))
        weeks.append(sum(c for d, c in days if end - dt.timedelta(days=6) <= d <= end))
    mx = max(weeks) or 1
    bx, base = 772, 252
    o.append(f'<text x="{bx - 20}" y="66" font-family="{ps.FONT}" font-size="13" font-weight="700" letter-spacing="1.2" fill="{t["faint"]}">LAST 16 WEEKS</text>')
    for k, v in enumerate(weeks):
        hgt = 4 + 120 * v / mx
        cx = bx + k * 24
        cy = base - k * 4 - hgt - 12
        lv = t["levels"][0 if v == 0 else min(4, 1 + int(3.99 * v / mx))]
        o.append(f'<g>{ps.enter(.3 + k * .05, 20)}' + ps.cube(cx, cy, 12, lv, hgt) + '</g>')
    o.append(f'<text x="{W - 56}" y="{H - 22}" text-anchor="end" font-family="{ps.MONO}" font-size="12" fill="{t["faint"]}">refreshed daily · {days[-1][0]:%d %b %Y}</text>')
    return ps.frame(theme, W, H, (0.8, 0.3), "\n".join(o), "GitHub activity stats")


def build(days, out_dir):
    for th in THEMES:
        with open(os.path.join(out_dir, f"snake-{th}.svg"), "w") as f:
            f.write(snake(th, days))
        with open(os.path.join(out_dir, f"stats-{th}.svg"), "w") as f:
            f.write(stats_card(th, days))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build_profile_svgs import load, OUT
    build(load(), OUT)
