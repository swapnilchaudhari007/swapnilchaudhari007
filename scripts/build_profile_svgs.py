#!/usr/bin/env python3
"""Builds the 3D hero banner and 3D contribution card for the GitHub profile README.

Usage:
  GITHUB_TOKEN=... python3 scripts/build_profile_svgs.py            # fetch live data
  python3 scripts/build_profile_svgs.py --data contributions.json   # offline: [["YYYY-MM-DD", n], ...]
"""
import datetime as dt
import json
import math
import os
import sys
import urllib.request

USER = os.environ.get("PROFILE_USER", "swapnilchaudhari007")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, Inter, Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    "dark": dict(
        bg0="#070b16", bg1="#0d1424", card="#0b1220", border="#1e293b",
        fg="#f1f5f9", muted="#94a3b8", faint="#64748b", chip="#111a2e", chipb="#23314d",
        accent="#22d3ee", accent2="#818cf8",
        levels=["#1a2335", "#1d6f8a", "#0ea5c6", "#22d3ee", "#a5f3fc"],
        glow=0.55, shadow="#000000",
    ),
    "light": dict(
        bg0="#f8fafc", bg1="#eef2ff", card="#ffffff", border="#e2e8f0",
        fg="#0f172a", muted="#475569", faint="#94a3b8", chip="#ffffff", chipb="#dbe3f0",
        accent="#0891b2", accent2="#4f46e5",
        levels=["#e6ebf3", "#bae6fd", "#38bdf8", "#0284c7", "#075985"],
        glow=0.30, shadow="#334155",
    ),
}


def shade(hexc, f):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x * f))) for x in (r, g, b))


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ data
def fetch_live():
    token = os.environ["GITHUB_TOKEN"]
    q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
         "variables": {"u": USER}}
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps(q).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def load():
    if "--data" in sys.argv:
        return json.load(open(sys.argv[sys.argv.index("--data") + 1]))
    return fetch_live()


def stats(days):
    days = sorted((dt.date.fromisoformat(d), c) for d, c in days)
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    best_d, best_c = max(days, key=lambda x: x[1])
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:  # today not yet counted shouldn't break streak
        seq = seq[:-1]
    for _, c in reversed(seq):
        if not c:
            break
        cur += 1
    return days, dict(total=total, active=active, best_d=best_d, best_c=best_c, longest=longest, current=cur)


# ------------------------------------------------------------------ hero
def iso_slab(cx, cy, a, t, top, left, right, edge, extra="", cls=""):
    b = a / 2
    T = [(cx, cy - b), (cx + a, cy), (cx, cy + b), (cx - a, cy)]
    L = [(cx - a, cy), (cx, cy + b), (cx, cy + b + t), (cx - a, cy + t)]
    R = [(cx, cy + b), (cx + a, cy), (cx + a, cy + t), (cx, cy + b + t)]
    return (f'<g class="{cls}">'
            f'<polygon points="{pts(L)}" fill="{left}"/>'
            f'<polygon points="{pts(R)}" fill="{right}"/>'
            f'<polygon points="{pts(T)}" fill="{top}" stroke="{edge}" stroke-width="1"/>'
            f'{extra}</g>')


def iso_box(x, y, s, h, color):
    """Small cube whose base's top corner sits at (x, y)."""
    b = s / 2
    T = [(x, y - h), (x + s, y + b - h), (x, y + s - h), (x - s, y + b - h)]
    L = [(x - s, y + b - h), (x, y + s - h), (x, y + s), (x - s, y + b)]
    R = [(x, y + s - h), (x + s, y + b - h), (x + s, y + b), (x, y + s)]
    return (f'<polygon points="{pts(L)}" fill="{shade(color, .72)}"/>'
            f'<polygon points="{pts(R)}" fill="{shade(color, .52)}"/>'
            f'<polygon points="{pts(T)}" fill="{color}"/>')


def hero(theme):
    t = THEMES[theme]
    W, H = 1200, 380
    dark = theme == "dark"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Swapnil Chaudhari — Senior Software Developer">',
         "<defs>",
         f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>',
         f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{t["accent2"]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></radialGradient>',
         f'<radialGradient id="glow2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"] * .7:.2f}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>',
         '<linearGradient id="topA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a5b4fc"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>',
         '<linearGradient id="topB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#818cf8"/><stop offset="1" stop-color="#06b6d4"/></linearGradient>',
         '<linearGradient id="topC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6366f1"/><stop offset="1" stop-color="#0891b2"/></linearGradient>',
         f'<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["fg"]}"/><stop offset="1" stop-color="{"#c7d2fe" if dark else "#3730a3"}"/></linearGradient>',
         f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.2" fill="{t["faint"]}" fill-opacity="{.35 if dark else .45}"/></pattern>',
         '<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".55" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>',
         '<mask id="m"><rect width="100%" height="100%" fill="url(#fade)"/></mask>',
         f'<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>',
         '<clipPath id="r"><rect width="1200" height="380" rx="20"/></clipPath>',
         "</defs>",
         "<style>"
         ".f1{animation:fl 6s ease-in-out infinite}.f2{animation:fl 6s ease-in-out .6s infinite}.f3{animation:fl 6s ease-in-out 1.2s infinite}"
         "@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}"
         ".pulse{animation:p 2.4s ease-in-out infinite}@keyframes p{0%,100%{opacity:1}50%{opacity:.35}}"
         "</style>",
         '<g clip-path="url(#r)">',
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#m)"/>',
         '<circle cx="930" cy="190" r="260" fill="url(#glow)"/>',
         '<circle cx="1080" cy="320" r="180" fill="url(#glow2)"/>',
         ]
    # --- 3D stack (decorative architecture)
    cx, a, th = 930, 150, 16
    edge = "rgba(255,255,255,0.45)" if dark else "rgba(255,255,255,0.9)"
    o.append(f'<ellipse cx="{cx}" cy="335" rx="190" ry="26" fill="{t["shadow"]}" opacity="{.55 if dark else .18}" filter="url(#soft)"/>')
    o.append(iso_slab(cx, 262, a, th, "url(#topC)", "#312e81", "#164e63", edge, cls="f3"))
    o.append(iso_slab(cx, 196, a, th, "url(#topB)", "#3730a3", "#155e75", edge, cls="f2"))
    # skyline of small cubes on top slab
    cubes = []
    s = 22
    heights = [[18, 34, 22], [44, 62, 30], [26, 40, 54]]
    cols = ["#e0e7ff", "#a5f3fc", "#c7d2fe"]
    for i in range(3):
        for j in range(3):
            # grid on the top face: i along +x/+y, j along -x/+y
            gx = cx + (i - j) * s * 1.25
            gy = 130 - a / 2 + 30 + (i + j) * s * 0.62
            cubes.append((gy, gx, heights[i][j], cols[(i + j) % 3]))
    sky = "".join(iso_box(gx, gy - 4, 16, h, c) for gy, gx, h, c in sorted(cubes))
    o.append(iso_slab(cx, 130, a, th, "url(#topA)", "#4338ca", "#0e7490", edge, extra=sky, cls="f1"))
    # connector beams
    # --- text block
    x = 64
    o += [
        f'<g class="in"><rect x="{x}" y="70" width="318" height="30" rx="15" fill="{t["chip"]}" stroke="{t["chipb"]}"/>'
        f'<circle class="pulse" cx="{x + 18}" cy="85" r="4.5" fill="#22c55e"/>'
        f'<text x="{x + 32}" y="90" font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="1.4" fill="{t["muted"]}">SENIOR SOFTWARE DEVELOPER</text></g>',
        f'<text class="in d1" x="{x - 3}" y="168" font-family="{FONT}" font-size="60" font-weight="800" letter-spacing="-1.5" fill="url(#name)">Swapnil Chaudhari</text>',
        f'<text class="in d2" x="{x}" y="212" font-family="{FONT}" font-size="22" fill="{t["muted"]}">Backend engineer shipping <tspan fill="{t["accent"]}" font-weight="600">AI</tspan> &amp; <tspan fill="{t["accent2"]}" font-weight="600">cloud</tspan> products.</text>',
    ]
    chips = ["C# / .NET", "SQL", "Python", "AWS", "LLMs · MCP"]
    cxp = x
    g = ['<g class="in d3">']
    for c in chips:
        w = 18 + len(c) * 8.6
        g.append(f'<rect x="{cxp}" y="246" width="{w:.0f}" height="34" rx="9" fill="{t["chip"]}" stroke="{t["chipb"]}"/>'
                 f'<text x="{cxp + w / 2:.1f}" y="268" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{t["fg"]}">{esc(c)}</text>')
        cxp += w + 10
    g.append("</g>")
    o += g
    o.append(f'<text class="in d4" x="{x}" y="318" font-family="{FONT}" font-size="15" fill="{t["faint"]}">Thane, India  ·  Bajaj Group  ·  Open to backend / AI engineering roles</text>')
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{t["border"]}"/>')
    o.append("</g></svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ contribution card
def contrib(theme, days, st):
    t = THEMES[theme]
    dark = theme == "dark"
    W, H = 1200, 520
    mx = max(1, st["best_c"])

    def level(c):
        if c == 0:
            return 0
        r = c / mx
        return 1 if r <= .15 else 2 if r <= .35 else 3 if r <= .65 else 4

    start = days[0][0]
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday
    first, last = days[0][0], days[-1][0]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="3D contribution graph: {st["total"]} contributions in the last year">',
         "<defs>",
         f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>',
         f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"] * .6:.2f}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>',
         '<clipPath id="r"><rect width="1200" height="520" rx="20"/></clipPath>',
         "</defs>",
         "<style>.b{animation:sh 4s ease-in-out infinite}@keyframes sh{0%,100%{opacity:1}50%{opacity:.82}}</style>",
         '<g clip-path="url(#r)">',
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
         '<circle cx="860" cy="300" r="320" fill="url(#glow)"/>',
         ]
    # header
    x = 48
    o += [
        f'<text x="{x}" y="66" font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="1.6" fill="{t["accent"]}">CONTRIBUTION ACTIVITY</text>',
        f'<text x="{x}" y="104" font-family="{FONT}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">Last 12 months</text>',
        f'<text x="{x}" y="132" font-family="{FONT}" font-size="15" fill="{t["muted"]}">{first:%b %d, %Y} – {last:%b %d, %Y}</text>',
    ]
    tiles = [
        ("Total contributions", f'{st["total"]}', ""),
        ("Active days", f'{st["active"]}', ""),
        ("Current streak", f'{st["current"]}', "days"),
        ("Longest streak", f'{st["longest"]}', "days"),
        ("Best day", f'{st["best_c"]}', f'{st["best_d"]:%b %d}'),
    ]
    ty = 162
    for i, (label, val, unit) in enumerate(tiles):
        col, row = i % 2, i // 2
        w = 148 if i < 4 else 306
        tx, yy = x + col * 158, ty + row * 92
        o.append(f'<g class="in" style="animation-delay:{.1 * i:.1f}s"><rect x="{tx}" y="{yy}" width="{w}" height="80" rx="14" fill="{t["card"]}" fill-opacity="{.7 if dark else .9}" stroke="{t["border"]}"/>'
                 f'<text x="{tx + 16}" y="{yy + 28}" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{label}</text>'
                 f'<text x="{tx + 16}" y="{yy + 62}" font-family="{FONT}" font-size="28" font-weight="700" fill="{t["fg"]}">{val}'
                 + (f'<tspan font-size="14" font-weight="500" fill="{t["faint"]}" dx="6">{unit}</tspan>' if unit else "") + "</text></g>")
    # legend
    ly = 470
    o.append(f'<text x="{x}" y="{ly + 12}" font-family="{FONT}" font-size="13" fill="{t["faint"]}">Less</text>')
    for i, c in enumerate(t["levels"]):
        o.append(f'<rect x="{x + 38 + i * 20}" y="{ly}" width="14" height="14" rx="3" fill="{c}"/>')
    o.append(f'<text x="{x + 38 + 5 * 20 + 6}" y="{ly + 12}" font-family="{FONT}" font-size="13" fill="{t["faint"]}">More</text>')

    # isometric skyline: weeks rise to the right, weekdays run down-right
    s = 11.2
    W_v, D_v = (s, -s / 2), (s, s / 2)
    ox, oy = 400, 425
    cells = []
    for d, c in days:
        wk = (d - start).days // 7
        dow = (d.weekday() + 1) % 7
        cells.append((dow - wk, wk, dow, c, d))
    cells.sort()
    gap = 1.1
    for _, wk, dow, c, d in cells:
        bx = ox + wk * W_v[0] + dow * D_v[0]
        by = oy + wk * W_v[1] + dow * D_v[1]
        p0 = (bx + gap, by)
        pw = (bx + W_v[0], by + W_v[1] + gap * .5)
        pd = (bx + D_v[0], by + D_v[1] - gap * .5)
        pwd = (bx + W_v[0] + D_v[0] - gap, by + W_v[1] + D_v[1])
        h = 3.0 if c == 0 else 8 + 84 * math.sqrt(c / mx)
        up = lambda p: (p[0], p[1] - h)
        col = t["levels"][level(c)]
        top = [up(p0), up(pw), up(pwd), up(pd)]
        left = [up(p0), up(pd), pd, p0]
        right = [up(pd), up(pwd), pwd, pd]
        lf, rf = (.78, .58) if dark else (.86, .70)
        if c:
            o.append(f'<g class="b" style="transform-origin:{pd[0]:.1f}px {pd[1]:.1f}px;animation-delay:{.25 + wk * .012:.2f}s">'
                     f'<title>{c} contribution{"s" if c != 1 else ""} on {d:%b %d, %Y}</title>')
        else:
            o.append("<g>")
        o.append(f'<polygon points="{pts(left)}" fill="{shade(col, lf)}"/>'
                 f'<polygon points="{pts(right)}" fill="{shade(col, rf)}"/>'
                 f'<polygon points="{pts(top)}" fill="{col}"/></g>')
    # month labels along the front edge (dow = 6)
    seen = set()
    for d, _ in days:
        if d.day <= 7 and d.weekday() == 6 and (d.year, d.month) not in seen:
            seen.add((d.year, d.month))
            wk = (d - start).days // 7
            lx = ox + wk * W_v[0] + 7 * D_v[0] + 6
            lyy = oy + wk * W_v[1] + 7 * D_v[1] + 16
            o.append(f'<text x="{lx:.1f}" y="{lyy:.1f}" font-family="{FONT}" font-size="11" fill="{t["faint"]}" transform="rotate(-26.6 {lx:.1f} {lyy:.1f})">{d:%b}</text>')
    o.append(f'<text x="{W - 40}" y="{H - 28}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["faint"]}">github.com/{USER}</text>')
    o.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{t["border"]}"/>')
    o.append("</g></svg>")
    return "\n".join(o)


def main():
    os.makedirs(OUT, exist_ok=True)
    days, st = stats(load())
    for th in THEMES:
        open(os.path.join(OUT, f"hero-{th}.svg"), "w").write(hero(th))
        open(os.path.join(OUT, f"contrib-3d-{th}.svg"), "w").write(contrib(th, days, st))
    print(json.dumps({k: str(v) for k, v in st.items()}))


if __name__ == "__main__":
    main()
