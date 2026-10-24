"""Real-time-looking 3D for static SVG: convex polyhedra rotated in true 3D, projected per frame,
and animated with SMIL (points / fill / opacity). Works inside <img> on GitHub.

Base attributes always hold frame 0, so renderers without SMIL still show a solid shape.
"""
import math

PHI = (1 + 5 ** .5) / 2


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, t):
    A, B = _hex(a), _hex(b)
    return "#%02x%02x%02x" % tuple(round(A[i] + (B[i] - A[i]) * t) for i in range(3))


def _lit(c, f):
    r, g, b = _hex(c)
    if f <= 1:
        return "#%02x%02x%02x" % tuple(max(0, round(x * f)) for x in (r, g, b))
    k = min(1, f - 1)  # blend toward white for highlights
    return "#%02x%02x%02x" % tuple(round(x + (255 - x) * k) for x in (r, g, b))


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(v):
    L = math.sqrt(_dot(v, v)) or 1
    return (v[0] / L, v[1] / L, v[2] / L)


def _hull_faces(V):
    """Faces of a convex polyhedron from its vertices (brute-force planes; fine for <=20 verts)."""
    n, faces, seen = len(V), [], set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                nrm = _cross(_sub(V[j], V[i]), _sub(V[k], V[i]))
                if _dot(nrm, nrm) < 1e-9:
                    continue
                nrm = _norm(nrm)
                d = _dot(nrm, V[i])
                side = [_dot(nrm, v) - d for v in V]
                if all(s <= 1e-6 for s in side) or all(s >= -1e-6 for s in side):
                    if all(s >= -1e-6 for s in side):
                        nrm, d = (-nrm[0], -nrm[1], -nrm[2]), -d
                    on = tuple(sorted(m for m in range(n) if abs(_dot(nrm, V[m]) - d) < 1e-6))
                    if on in seen:
                        continue
                    seen.add(on)
                    c = tuple(sum(V[m][a] for m in on) / len(on) for a in range(3))
                    # order the face's vertices counter-clockwise around the outward normal
                    u = _norm(_sub(V[on[0]], c))
                    w = _cross(nrm, u)
                    ring = sorted(on, key=lambda m: math.atan2(_dot(_sub(V[m], c), w), _dot(_sub(V[m], c), u)))
                    faces.append(ring)
    return faces


def shape(name):
    if name == "cube":
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    elif name == "octa":
        V = [(1.35, 0, 0), (-1.35, 0, 0), (0, 1.35, 0), (0, -1.35, 0), (0, 0, 1.35), (0, 0, -1.35)]
    elif name == "ico":
        V = [p for a in (-1, 1) for b in (-PHI, PHI) for p in ((0, a, b), (a, b, 0), (b, 0, a))]
    elif name == "dodeca":
        V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        ip = 1 / PHI
        V += [p for a in (-ip, ip) for b in (-PHI, PHI) for p in ((0, a, b), (a, b, 0), (b, 0, a))]
    elif name == "hexprism":
        V = [(math.cos(k * math.pi / 3) * 1.25, h, math.sin(k * math.pi / 3) * 1.25) for k in range(6) for h in (-.8, .8)]
    elif name == "gem":  # brilliant-ish: octagon girdle + crown table + pointed pavilion
        V = [(math.cos(k * math.pi / 4) * 1.3, .15, math.sin(k * math.pi / 4) * 1.3) for k in range(8)]
        V += [(math.cos(k * math.pi / 4 + math.pi / 8) * .75, .75, math.sin(k * math.pi / 4 + math.pi / 8) * .75) for k in range(8)]
        V += [(0, -1.5, 0)]
    else:
        raise ValueError(name)
    R = max(math.sqrt(_dot(v, v)) for v in V)
    V = [(v[0] / R, v[1] / R, v[2] / R) for v in V]
    return V, _hull_faces(V)


def _rot(v, ax, ay, az):
    x, y, z = v
    c, s = math.cos(az), math.sin(az); x, y = x * c - y * s, x * s + y * c
    c, s = math.cos(ay), math.sin(ay); x, z = x * c + z * s, -x * s + z * c
    c, s = math.cos(ax), math.sin(ax); y, z = y * c - z * s, y * s + z * c
    return (x, y, z)


def solid(name, cx, cy, r, c1, c2, frames=48, dur=12, tilt=-0.42, wobble=0.35, phase=0.0,
          edge="#ffffff", edge_op=.35, persp=3.2, light=(-.5, -.75, .9), spin=1):
    """Rotating convex solid centred at (cx, cy) with radius r. c1→c2 = colour ramp by face direction."""
    V, F = shape(name)
    L = _norm(light)
    per = [[] for _ in F]
    for f in range(frames):
        th = spin * 2 * math.pi * f / frames + phase
        P3 = [_rot(_rot(v, 0, th, 0), tilt + wobble * math.sin(th) * .4, 0, wobble * math.cos(th) * .5) for v in V]
        P2 = [(cx + p[0] * r * persp / (persp - p[2]), cy - p[1] * r * persp / (persp - p[2])) for p in P3]
        for i, face in enumerate(F):
            q = [P2[m] for m in face]
            area = sum(q[k][0] * q[(k + 1) % len(q)][1] - q[(k + 1) % len(q)][0] * q[k][1] for k in range(len(q)))
            n3 = _norm(_cross(_sub(P3[face[1]], P3[face[0]]), _sub(P3[face[2]], P3[face[0]])))
            lam = max(0, _dot(n3, L))
            spec = max(0, _dot(n3, _norm((L[0], L[1], L[2] + 1)))) ** 18
            col = _lit(_mix(c2, c1, (n3[1] + 1) / 2), .42 + .78 * lam + .55 * spec)
            per[i].append((" ".join(f"{x:.1f},{y:.1f}" for x, y in q), col, area < 0))
    out = []
    for i, fr in enumerate(per):
        loop = fr + fr[:1]
        pv = ";".join(p for p, _, _ in loop)
        cv = ";".join(c for _, c, _ in loop)
        ov = ";".join("1" if v else "0" for _, _, v in loop)
        out.append(f'<polygon points="{fr[0][0]}" fill="{fr[0][1]}" opacity="{1 if fr[0][2] else 0}" '
                   f'stroke="{edge}" stroke-opacity="{edge_op}" stroke-width="1" stroke-linejoin="round">'
                   f'<animate attributeName="points" values="{pv}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="fill" values="{cv}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="{ov}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>'
                   f'</polygon>')
    return "<g>" + "".join(out) + "</g>"


def orbit(cx, cy, rx, ry, dur, begin, body, half):
    """A body travelling an elliptical orbit. half='back' draws only while behind, 'front' only in front.
    Path starts at the right-most point and goes clockwise (down = front)."""
    path = f"M{cx + rx},{cy} A{rx},{ry} 0 1,1 {cx - rx},{cy} A{rx},{ry} 0 1,1 {cx + rx},{cy}"
    vis = "1;0" if half == "front" else "0;1"
    return (f'<g opacity="{vis[0]}">{body}'
            f'<animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{vis}" keyTimes="0;.5" calcMode="discrete" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')
