"""Static 3D-styled section cards for the profile README (About, Projects, Tech stack, CTA, buttons).

Shares the design tokens of build_profile_svgs.py so every section looks like one system.
"""
from build_profile_svgs import THEMES, FONT, MONO, shade, pts, esc, bob, enter, shine_gradient

# ------------------------------------------------------------------ content
ABOUT = dict(
    title="Backend roots. AI & cloud ambitions.",
    body=("Software engineer from Thane, India with a strong backend foundation in C#, ASP.NET, "
          "C/C++ and SQL — now shipping AI and cloud-native products, from voice assistants on AWS "
          "to computer-vision safety systems and mixed-reality apps."),
    facts=[("5", "projects shipped in 2026"), ("2+ yrs", "on GitHub"), ("Thane", "India · IST")],
    points=[
        ("#22d3ee", "Building", "Production-style hackathon projects across AI, AWS, mobile and XR"),
        ("#818cf8", "Exploring", "LLMs, MCP servers, computer vision and serverless architectures"),
        ("#34d399", "Day to day", "APIs, databases, Linux and clean, maintainable backend code"),
        ("#f59e0b", "Open to", "Backend, full-stack and AI engineering opportunities"),
    ],
)

PROJECTS = [
    dict(slug="carecircle", repo="carecircle-mcp", name="CareCircle", accent="#fb7185", tag="Amazon Developer Hackathon",
         desc="Alexa+ MCP server for elder medication care — voice dose logging, double-dose guard, family alerts and multilingual digests.",
         stack=["TypeScript", "Bedrock", "Lambda", "DynamoDB", "SNS"]),
    dict(slug="safetyeye", repo="safetyeye", name="SafetyEye", accent="#f59e0b", tag="INDUX 5.0 · AI",
         desc="AI PPE & hazard monitor for worksites — helmet/vest detection, restricted zones, fall detection and multilingual alerts.",
         stack=["Python", "YOLO11", "FastAPI"]),
    dict(slug="pinchplan", repo="pinchplan", name="PinchPlan", accent="#a78bfa", tag="Meta VR Start 2026",
         desc="Hands-first mixed-reality focus desk for Meta Quest, built for the web with WebXR.",
         stack=["WebXR", "JavaScript"]),
    dict(slug="questlog", repo="questlog", name="QuestLog", accent="#34d399", tag="RevenueCat Shipaton",
         desc="Your gaming bucket list, gamified — with in-app subscriptions powered by RevenueCat.",
         stack=["TypeScript", "Expo", "RevenueCat"]),
    dict(slug="societymitra", repo="societymitra", name="SocietyMitra", accent="#38bdf8", tag="Nebius × NVIDIA AI",
         desc="AI co-secretary for housing societies — an agent built on NVIDIA Nemotron via Nebius Token Factory.",
         stack=["Python", "Nemotron", "Nebius", "Tavily"]),
]

STACK = [
    ("Languages", [("C", "#00599C"), ("C++", "#00599C"), ("C#", "#512BD4"), ("Python", "#3776AB"),
                   ("TypeScript", "#3178C6"), ("JavaScript", "#F7DF1E"), ("PHP", "#777BB4"), ("Dart", "#0175C2")]),
    ("Backend", [("ASP.NET", "#512BD4"), ("FastAPI", "#009688"), ("Node.js", "#339933"), ("WordPress", "#21759B")]),
    ("Frontend & Mobile", [("HTML5", "#E34F26"), ("CSS3", "#1572B6"), ("Flutter", "#02569B"), ("Expo", "#8b95a7"), ("WebXR", "#a78bfa")]),
    ("Data & Cloud", [("MS SQL", "#CC2927"), ("MySQL", "#4479A1"), ("Firebase", "#FFCA28"), ("AWS", "#FF9900"), ("DynamoDB", "#4053D6")]),
    ("AI & Tools", [("YOLO11", "#6366f1"), ("Bedrock", "#FF9900"), ("Linux", "#FCC624"), ("Git", "#F05032"), ("VS Code", "#007ACC")]),
]


# ------------------------------------------------------------------ helpers
def text_w(s, size, weight=400, mono=False):
    """Deterministic width estimate (same result locally and in CI)."""
    if mono:
        return len(s) * size * 0.6
    f = 0.545 if weight < 600 else 0.58
    narrow = sum(1 for ch in s if ch in "iljtfrI.,:;'|!· ")
    wide = sum(1 for ch in s if ch in "mwMW—")
    return size * (f * len(s) - 0.25 * narrow + 0.3 * wide)


def wrap(s, size, width, weight=400):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if text_w(trial, size, weight) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def frame(theme, W, H, glow_xy=(0.8, 0.4), body="", label=""):
    t = THEMES[theme]
    dark = theme == "dark"
    gx, gy = glow_xy
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>',
        f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["accent2"]}" stop-opacity="{t["glow"] * .7:.2f}"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.2" fill="{t["faint"]}" fill-opacity="{.28 if dark else .38}"/></pattern>',
        f'<clipPath id="r"><rect width="{W}" height="{H}" rx="20"/></clipPath>',
        "</defs>",
        '<g clip-path="url(#r)">',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<circle cx="{W * gx:.0f}" cy="{H * gy:.0f}" r="{max(W, H) * .32:.0f}" fill="url(#glow)"/>',
        body,
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{t["border"]}"/>',
        "</g></svg>",
    ])


def cube(x, y, s, color, h=None):
    """Isometric cube; (x, y) = top vertex of the top face."""
    h = s if h is None else h
    b = s / 2
    T = [(x, y), (x + s, y + b), (x, y + s), (x - s, y + b)]
    L = [(x - s, y + b), (x, y + s), (x, y + s + h), (x - s, y + b + h)]
    R = [(x, y + s), (x + s, y + b), (x + s, y + b + h), (x, y + s + h)]
    return (f'<polygon points="{pts(L)}" fill="{shade(color, .72)}"/>'
            f'<polygon points="{pts(R)}" fill="{shade(color, .52)}"/>'
            f'<polygon points="{pts(T)}" fill="{color}" stroke="rgba(255,255,255,.35)" stroke-width=".8"/>')


def eyebrow(theme, x, y, s):
    t = THEMES[theme]
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="14" font-weight="700" letter-spacing="1.8" fill="{t["accent"]}">{esc(s.upper())}</text>'


def keycap(t, x, y, label, dot=None, size=16, pad=18, h=42, mono=False, dark=True, press=None):
    """3D keyboard-key chip. Returns (svg, width)."""
    tw = text_w(label, size, 600, mono)
    w = tw + pad * 2 + (18 if dot else 0)
    depth = 6
    face0 = t["chip"]
    edge = shade(t["chipb"], .75 if dark else .82)
    anim = ""
    if press:  # (offset seconds, cycle seconds): key goes down and springs back once per cycle
        off, cyc = press
        a = off / cyc
        e = .022
        anim = (f'<animateTransform attributeName="transform" type="translate" additive="sum" '
                f'values="0 0;0 0;0 {depth - 1};0 0;0 0" keyTimes="0;{a:.3f};{a + e:.3f};{a + 2.4 * e:.3f};1" '
                f'dur="{cyc}s" repeatCount="indefinite"/>')
    s = [f'<rect x="{x}" y="{y + depth}" width="{w:.0f}" height="{h}" rx="10" fill="{edge}"/>',
         f'<g>{anim}',
         f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="10" fill="{face0}" stroke="{t["chipb"]}"/>',
         f'<rect x="{x + 6}" y="{y + 3}" width="{w - 12:.0f}" height="2" rx="1" fill="#ffffff" fill-opacity="{.08 if dark else .9}"/>']
    tx = x + pad
    if dot:
        s.append(f'<circle cx="{x + pad + 5}" cy="{y + h / 2}" r="5" fill="{dot}"/>')
        tx += 18
    s.append(f'<text x="{tx:.1f}" y="{y + h / 2 + size * .36:.1f}" font-family="{MONO if mono else FONT}" font-size="{size}" font-weight="600" fill="{t["fg"]}">{esc(label)}</text></g>')
    return "".join(s), w


# ------------------------------------------------------------------ sections
def about(theme):
    t = THEMES[theme]
    dark = theme == "dark"
    W, H = 1200, 470
    x = 56
    o = [eyebrow(theme, x, 72, "About me"),
         f'<text x="{x}" y="118" font-family="{FONT}" font-size="34" font-weight="800" letter-spacing="-.6" fill="{t["fg"]}">{esc(ABOUT["title"])}</text>']
    for i, line in enumerate(wrap(ABOUT["body"], 18, 540)):
        o.append(f'<text x="{x}" y="{168 + i * 30}" font-family="{FONT}" font-size="18" fill="{t["muted"]}">{esc(line)}</text>')
    # fact tiles
    fx = x
    for big, small in ABOUT["facts"]:
        w = max(text_w(big, 26, 700), text_w(small, 13)) + 36
        o.append(f'<rect x="{fx}" y="330" width="{w:.0f}" height="84" rx="14" fill="{t["card"]}" fill-opacity="{.7 if dark else .9}" stroke="{t["border"]}"/>'
                 f'<text x="{fx + 18}" y="370" font-family="{FONT}" font-size="26" font-weight="700" fill="{t["fg"]}">{esc(big)}</text>'
                 f'<text x="{fx + 18}" y="396" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{esc(small)}</text>')
        fx += w + 12
    # right column: 3D bullet list
    rx = 680
    o.append(f'<rect x="{rx - 24}" y="44" width="500" height="382" rx="18" fill="{t["card"]}" fill-opacity="{.55 if dark else .75}" stroke="{t["border"]}"/>')
    for i, (col, label, desc) in enumerate(ABOUT["points"]):
        y = 76 + i * 88
        o.append(f'<g>{bob(5, 5, i * .5)}{cube(rx + 16, y, 16, col)}</g>')
        o.append(f'<g>{enter(.2 + i * .15, 10)}<text x="{rx + 52}" y="{y + 16}" font-family="{FONT}" font-size="18" font-weight="700" fill="{t["fg"]}">{esc(label)}</text>')
        for j, line in enumerate(wrap(desc, 16, 390)):
            o.append(f'<text x="{rx + 52}" y="{y + 42 + j * 22}" font-family="{FONT}" font-size="16" fill="{t["muted"]}">{esc(line)}</text>')
        o.append('</g>')
    return frame(theme, W, H, (0.78, 0.5), "\n".join(o), "About Swapnil Chaudhari")


def project(theme, p):
    t = THEMES[theme]
    dark = theme == "dark"
    W, H = 600, 320
    a = p["accent"]
    o = [f'<defs>{shine_gradient("bar", 4, 0.5, .8)}</defs>',
         f'<rect x="0" y="0" width="{W}" height="5" fill="{a}"/>',
         f'<rect x="0" y="0" width="{W}" height="5" fill="url(#bar)"/>']
    # 3D icon: big cube + small floating cube
    o.append(f'<ellipse cx="68" cy="112" rx="34" ry="9" fill="#000" opacity="{.35 if dark else .12}"/>')
    o.append(f'<g>{bob(3, 6, 0)}{cube(68, 40, 30, a, 30)}</g>')
    o.append(f'<g>{bob(5, 3.2, .4)}{cube(104, 30, 11, shade(a, 1.15) if dark else a)}</g>')
    o.append(f'<text x="132" y="78" font-family="{FONT}" font-size="30" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">{esc(p["name"])}</text>')
    tag = p["tag"].upper()
    tw = text_w(tag, 12, 700) + 22
    o.append(f'<rect x="132" y="92" width="{tw:.0f}" height="24" rx="12" fill="{a}" fill-opacity="{.16 if dark else .12}" stroke="{a}" stroke-opacity=".45"/>'
             f'<text x="143" y="108" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="1" fill="{a if dark else shade(a, .7)}">{esc(tag)}</text>')
    # arrow
    o.append(f'<g stroke="{t["muted"]}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
             '<animateTransform attributeName="transform" type="translate" values="0 0;0 0;4 -4;0 0" keyTimes="0;.6;.8;1" dur="2.6s" repeatCount="indefinite"/>'
             '<path d="M548 44 L566 26"/><path d="M552 26 H566 V40"/></g>')
    for i, line in enumerate(wrap(p["desc"], 18, 520)[:3]):
        o.append(f'<text x="40" y="{158 + i * 27}" font-family="{FONT}" font-size="18" fill="{t["muted"]}">{esc(line)}</text>')
    x = 40
    for s in p["stack"]:
        k, w = keycap(t, x, 256, s, size=14, pad=12, h=32, mono=True, dark=dark)
        o.append(k)
        x += w + 8
    return frame(theme, W, H, (0.95, 0.1), "\n".join(o), f'{p["name"]} — {p["desc"]}')


def stack(theme):
    t = THEMES[theme]
    dark = theme == "dark"
    W = 1200
    x0, xl = 56, 270
    o = [eyebrow(theme, x0, 72, "Tech stack"),
         f'<text x="{x0}" y="116" font-family="{FONT}" font-size="34" font-weight="800" letter-spacing="-.6" fill="{t["fg"]}">Tools I build with</text>']
    y = 156
    kidx = 0
    for gi, (group, items) in enumerate(STACK):
        o.append(f'<text x="{x0}" y="{y + 27}" font-family="{FONT}" font-size="16" font-weight="700" fill="{t["muted"]}">{esc(group)}</text>')
        x = xl
        for label, col in items:
            _, w = keycap(t, 0, 0, label, dot=col, dark=dark)
            if x + w > W - 50:
                x = xl
                y += 62
            k, w = keycap(t, x, y, label, dot=col, dark=dark, press=(1.0 + kidx * .16, 8))
            kidx += 1
            o.append(k)
            x += w + 12
        y += 62
        if gi < len(STACK) - 1:
            o.append(f'<line x1="{x0}" x2="{W - 56}" y1="{y - 9}" y2="{y - 9}" stroke="{t["border"]}"/>')
            y += 8
    H = y + 34
    return frame(theme, W, H, (0.9, 0.15), "\n".join(o), "Tech stack")


def cta(theme):
    t = THEMES[theme]
    W, H = 1200, 220
    o = [eyebrow(theme, 56, 76, "Get in touch"),
         f'<text x="56" y="124" font-family="{FONT}" font-size="36" font-weight="800" letter-spacing="-.6" fill="{t["fg"]}">Let’s build something together.</text>',
         f'<text x="56" y="162" font-family="{FONT}" font-size="18" fill="{t["muted"]}">Open to backend, full-stack and AI engineering roles · Thane, India (IST)</text>']
    # decorative cube cluster
    for i, (dx, dy, s, c) in enumerate([(1000, 60, 34, "#6366f1"), (1068, 96, 24, "#22d3ee"), (946, 112, 20, "#a78bfa")]):
        o.append(f'<g>{bob(5, 5, i * .7)}{cube(dx, dy, s, c)}</g>')
    return frame(theme, W, H, (0.85, 0.5), "\n".join(o), "Let's build something together")


def button(theme, label, color):
    t = THEMES[theme]
    dark = theme == "dark"
    W, H = 240, 64
    depth = 7
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">',
         f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{shade(color, 1.12)}"/><stop offset="1" stop-color="{color}"/></linearGradient>',
         f'<rect x="2" y="{depth + 1}" width="{W - 4}" height="{H - depth - 3}" rx="14" fill="{shade(color, .55)}"/>',
         f'<rect x="2" y="2" width="{W - 4}" height="{H - depth - 3}" rx="14" fill="url(#g)"/>',
         f'<rect x="12" y="5" width="{W - 24}" height="2" rx="1" fill="#fff" fill-opacity=".35"/>',
         shine_gradient("s", 3.5, 0.8 if "Link" in label else 1.2, .45),
         f'<rect x="2" y="2" width="{W - 4}" height="{H - depth - 3}" rx="14" fill="url(#s)"/>',
         f'<text x="{W / 2 - 8}" y="{(H - depth) / 2 + 7}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="#ffffff">{esc(label)}</text>',
         f'<g stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate({W / 2 + text_w(label, 19, 700) / 2 + 2},{(H - depth) / 2 - 8})"><path d="M0 12 L10 2"/><path d="M2 2 H10 V10"/></g>',
         "</svg>"]
    return "\n".join(o)


def header(theme, kicker, title, sub):
    t = THEMES[theme]
    W, H = 1200, 170
    o = [eyebrow(theme, 56, 66, kicker),
         f'<text x="56" y="112" font-family="{FONT}" font-size="34" font-weight="800" letter-spacing="-.6" fill="{t["fg"]}">{esc(title)}</text>',
         f'<text x="56" y="144" font-family="{FONT}" font-size="17" fill="{t["muted"]}">{esc(sub)}</text>']
    for i, (dx, dy, s, c) in enumerate([(1060, 50, 26, "#fb7185"), (1110, 76, 18, "#f59e0b"), (1012, 82, 16, "#34d399")]):
        o.append(f'<g>{bob(5, 5, i * .6)}{cube(dx, dy, s, c)}</g>')
    return frame(theme, W, H, (0.9, 0.5), "\n".join(o), title)


def build_all(out_dir):
    import os
    for th in THEMES:
        files = {
            f"about-{th}.svg": about(th),
            f"stack-{th}.svg": stack(th),
            f"cta-{th}.svg": cta(th),
            f"projects-header-{th}.svg": header(th, "Featured projects", "Things I've shipped", "Five production-style builds from 2026 hackathons — tap a card to open the repo."),
            f"btn-linkedin-{th}.svg": button(th, "LinkedIn", "#0A66C2"),
            f"btn-email-{th}.svg": button(th, "Email", "#4f46e5"),
        }
        for p in PROJECTS:
            files[f'project-{p["slug"]}-{th}.svg'] = project(th, p)
        for name, svg in files.items():
            with open(os.path.join(out_dir, name), "w") as f:
                f.write(svg)
