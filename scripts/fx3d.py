"""Extra 3D layers for the profile section cards: perspective floors, orbit rings with moons,
and more rotating solids. Wraps profile_sections so the base layouts stay untouched.

All motion is SMIL, so it plays inside <img> on GitHub. (GitHub renders README images as
plain images, so pointer/hover interaction is not possible there.)
"""
import profile_sections as ps
from build_profile_svgs import THEMES, shade, bob
from poly3d import solid

GLOW_END = 'fill="url(#glow)"/>'
BORDER_START = '<rect x=".5" y=".5"'


def _inject(svg, back="", front=""):
    """back: drawn just above the background glow (behind content); front: above all content."""
    if back:
        svg = svg.replace(GLOW_END, GLOW_END + back, 1)
    if front:
        i = svg.rfind(BORDER_START)
        svg = svg[:i] + front + svg[i:]
    return svg


def floor(uid, x0, x1, top, bottom, color, op=.5, rows=7, cols=13, dur=4.0):
    """Synthwave-style perspective floor: lines converge on a vanishing point and
    horizontal rails scroll toward the viewer."""
    w = x1 - x0
    vx, vy = x0 + w / 2, top - (bottom - top) * .9   # vanishing point above the horizon
    o = [f'<defs><linearGradient id="{uid}f" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".45" stop-color="#fff" stop-opacity=".8"/>'
         f'<stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
         f'<radialGradient id="{uid}h" cx=".5" cy="1" r=".75"><stop offset="0" stop-color="#fff"/>'
         f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
         f'<mask id="{uid}m"><rect x="{x0}" y="{top}" width="{w}" height="{bottom - top}" fill="url(#{uid}f)"/>'
         f'<rect x="{x0}" y="{top}" width="{w}" height="{bottom - top}" fill="url(#{uid}h)" opacity=".0"/></mask></defs>',
         f'<g mask="url(#{uid}m)" stroke="{color}" stroke-opacity="{op}" stroke-width="1" fill="none">']
    # converging verticals
    for c in range(cols + 1):
        bx = x0 - w * .35 + (w * 1.7) * c / cols
        t = (top - vy) / (bottom - vy)
        tx = vx + (bx - vx) * t
        o.append(f'<line x1="{tx:.1f}" y1="{top}" x2="{bx:.1f}" y2="{bottom}"/>')
    # scrolling rails (perspective spacing via ease-in spline)
    for r in range(rows):
        beg = -dur * r / rows
        o.append(f'<line x1="{x0}" x2="{x1}" y1="{top}" y2="{top}">'
                 f'<animate attributeName="y1" values="{top};{bottom}" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".55 0 1 .6"/>'
                 f'<animate attributeName="y2" values="{top};{bottom}" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".55 0 1 .6"/>'
                 f'</line>')
    o.append(f'<line x1="{x0}" x2="{x1}" y1="{top}" y2="{top}" stroke-opacity="{min(1, op * 1.6):.2f}"/>')
    o.append('</g>')
    return "".join(o)


def ring(uid, cx, cy, rx, ry, color, dur=7.0, moon=5.5, begin=0.0, op=.55):
    """Tilted orbit ring around a solid. Returns (back, front) layers so the ring and its
    moon pass behind the solid on the far side and in front on the near side."""
    back_arc = f"M{cx - rx},{cy} A{rx},{ry} 0 0,1 {cx + rx},{cy}"     # far (upper) half
    front_arc = f"M{cx + rx},{cy} A{rx},{ry} 0 0,1 {cx - rx},{cy}"    # near (lower) half
    grad = (f'<defs><radialGradient id="{uid}mo" cx=".35" cy=".35" r=".7">'
            f'<stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="{shade(color, 1.4)}"/>'
            f'<stop offset="1" stop-color="{shade(color, .45)}"/></radialGradient></defs>')

    def body(scale):
        return f'<circle r="{moon * scale:.1f}" fill="url(#{uid}mo)"/>'

    # clockwise path from right-most point: first half = near/front (bottom), second = far/back (top)
    path = f"M{cx + rx},{cy} A{rx},{ry} 0 1,1 {cx - rx},{cy} A{rx},{ry} 0 1,1 {cx + rx},{cy}"

    def moon_layer(front):
        vis = "1;0" if front else "0;1"
        sc = 1.0 if front else .72
        return (f'<g opacity="{vis[0]}">{body(sc)}'
                f'<animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{vis}" keyTimes="0;.5" calcMode="discrete" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')

    stroke = f'fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round"'
    back = (grad + f'<path d="{back_arc}" {stroke} stroke-opacity="{op * .55:.2f}" stroke-dasharray="3 5">'
            f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="1.6s" repeatCount="indefinite"/></path>'
            + moon_layer(False))
    front = (f'<path d="{front_arc}" {stroke} stroke-opacity="{op:.2f}" stroke-dasharray="3 5">'
             f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="1.6s" repeatCount="indefinite"/></path>'
             + moon_layer(True))
    return back, front


def cluster(items):
    return "".join(f'<g>{bob(5, 5, i * .6)}' + solid(shp, x, y, r, shade(c, 1.5), shade(c, .55), 48, d, phase=i) + '</g>'
                   for i, (x, y, r, c, shp, d) in enumerate(items))


# ------------------------------------------------------------------ enhanced sections
_project, _header, _cta, _stack, _about = ps.project, ps.header, ps.cta, ps.stack, ps.about


def project(theme, p):
    t = THEMES[theme]
    dark = theme == "dark"
    a = p["accent"]
    rb, rf = ring("pr", 72, 74, 50, 13, shade(a, 1.3) if dark else shade(a, .8), dur=6.5, op=.75 if dark else .6)
    back = floor("pf", 300, 600, 214, 320, a, op=.22 if dark else .2, rows=6, cols=12, dur=3.6) + rb
    return _inject(_project(theme, p), back, rf)


def header(theme, kicker, title, sub):
    t = THEMES[theme]
    dark = theme == "dark"
    rb, rf = ring("hr", 1070, 86, 64, 16, t["accent"], dur=8, moon=6, op=.7 if dark else .55)
    back = floor("hf", 860, 1200, 118, 170, t["accent2"], op=.35 if dark else .28, rows=5, dur=3.2) + rb
    front = rf + cluster([(900, 56, 12, "#a78bfa", "dodeca", 10)])
    return _inject(_header(theme, kicker, title, sub), back, front)


def cta(theme):
    t = THEMES[theme]
    dark = theme == "dark"
    rb, rf = ring("cr", 1010, 108, 92, 22, "#818cf8", dur=9, moon=7, op=.7 if dark else .55)
    rb2, rf2 = ring("cs", 1010, 108, 120, 30, t["accent"], dur=13, moon=4.5, begin=-4, op=.45 if dark else .35)
    back = floor("cf", 780, 1200, 150, 220, t["accent2"], op=.35 if dark else .28, rows=6, dur=3.6) + rb2 + rb
    return _inject(_cta(theme), back, rf + rf2)


def stack(theme):
    svg = _stack(theme)
    front = cluster([(1090, 74, 30, "#22d3ee", "ico", 13), (1148, 104, 15, "#f59e0b", "cube", 8),
                     (1028, 100, 14, "#fb7185", "octa", 10)])
    rb, rf = ring("sr", 1090, 78, 50, 12, "#818cf8", dur=7, moon=4.5, op=.6)
    return _inject(svg, rb, rf + front)


def about(theme):
    t = THEMES[theme]
    dark = theme == "dark"
    back = floor("af", 0, 640, 395, 470, t["accent"], op=.28 if dark else .22, rows=6, dur=4)
    return _inject(_about(theme), back)


def build_all(out_dir):
    ps.project, ps.header, ps.cta, ps.stack, ps.about = project, header, cta, stack, about
    ps.build_all(out_dir)
