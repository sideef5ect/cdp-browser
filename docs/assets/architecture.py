#!/usr/bin/env python3
"""cdp-browser architecture, blueprint style (cyanotype): one CDP endpoint, two browser backends.

Usage: python3 architecture.py   (writes architecture.svg beside this file)
Stdlib only. Adapted from the obsidian-note skill's examples/blueprint-architecture.py;
the helpers above DIAGRAM are the style (docs/styles/blueprint.md).
"""

from pathlib import Path

W, H = 1380, 1020
MINOR, MAJOR = 20, 100  # grid 5:1
OUTER, INNER = 24, 34  # frame insets
THICK, THIN = 1.8, 0.9  # 2:1 line weights

P = dict(
    ground="#17457c",
    line="#ffffff",
    text="#ffffff",
    soft="#cfe0f5",
    accent="#ffc94d",
    fill="#1a4c86",
    grid=(0.05, 0.13),
    vignette=("#1d5491", "#11365f"),
)

COND = "'Avenir Next Condensed', 'DIN Condensed', 'Barlow Condensed', 'Arial Narrow', sans-serif"
SANS = "'Avenir Next', Inter, 'Helvetica Neue', 'Segoe UI', Arial, sans-serif"
MONO = "Menlo, 'SF Mono', 'IBM Plex Mono', Consolas, 'DejaVu Sans Mono', monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    out = []
    add = out.append
    acc = P["accent"]

    def text(x, y, s, size, fill, family=SANS, weight=400, anchor="start", ls=0, extra=""):
        add(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{esc(s)}</text>'
        )

    def label(x, y, s, size=13, fill=None, anchor="start", weight=600):
        """Uppercase mono drawing label, widely tracked."""
        text(x, y, s.upper(), size, fill or P["line"], MONO, weight, anchor, ls=round(size * 0.12, 2))

    def code(x, y, s, size=13, fill=None, anchor="start", weight=400):
        """Case-sensitive mono (paths, flags, functions)."""
        text(x, y, s, size, fill or P["soft"], MONO, weight, anchor)

    def line(x1, y1, x2, y2, w=THIN, color=None, extra=""):
        add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or P["line"]}" stroke-width="{w}" {extra}/>')

    def path(pts, w=1.4, color=None, dashed=False, arrow="ar"):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        mk = f' marker-end="url(#{arrow})"' if arrow else ""
        add(f'<path d="{d}" fill="none" stroke="{color or P["line"]}" stroke-width="{w}"{dash}{mk}/>')

    def box(x, y, w, h, name, subs, mono_subs=False, outline=THICK):
        """Square-cornered part: mono caps name, short sub-labels."""
        add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{P["fill"]}" stroke="{P["line"]}" '
            f'stroke-width="{outline}"/>'
        )
        text(x + 14, y + 27, name.upper(), 15, P["text"], MONO, 700, ls=1)
        for i, s in enumerate(subs):
            if mono_subs:
                code(x + 14, y + 49 + i * 20, s, 13)
            else:
                text(x + 14, y + 49 + i * 20, s, 14, P["soft"], SANS)

    def volume(x, y, w, h, name, sub):
        """Cylinder glyph for a mounted volume."""
        ry = 9
        add(
            f'<path d="M{x},{y + ry} L{x},{y + h - ry} A{w / 2},{ry} 0 0 0 {x + w},{y + h - ry} '
            f'L{x + w},{y + ry} A{w / 2},{ry} 0 0 0 {x},{y + ry} Z" fill="{P["fill"]}" stroke="{P["line"]}" '
            f'stroke-width="{THICK}"/>'
        )
        add(
            f'<path d="M{x},{y + ry} A{w / 2},{ry} 0 0 0 {x + w},{y + ry}" fill="none" stroke="{P["line"]}" '
            f'stroke-width="{THIN}"/>'
        )
        code(x + 12, y + 42, name, 13, P["text"], weight=700)
        text(x + 12, y + 62, sub, 14, P["soft"], SANS)

    def hdim(x1, x2, y, s, ext_to=None):
        """Horizontal dimension: extension lines, arrowheads both ends, value knocked out of the line."""
        if ext_to is not None:
            line(x1, ext_to, x1, y + 6, 0.7, extra='opacity="0.7"')
            line(x2, ext_to, x2, y + 6, 0.7, extra='opacity="0.7"')
        line(x1, y, x2, y, THIN, extra='marker-start="url(#ar)" marker-end="url(#ar)"')
        w = len(s) * 12 * 0.62 + 16
        add(f'<rect x="{(x1 + x2) / 2 - w / 2}" y="{y - 9}" width="{w}" height="18" fill="{P["ground"]}"/>')
        label((x1 + x2) / 2, y + 4, s, 12, anchor="middle")

    def tag(x, y, s, color=None, anchor="start"):
        """Short connector label on a ground knockout."""
        size = 12
        w = len(s) * size * 0.62 + len(s) * 1.44 + 8
        x0 = x - 4 if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w + 4)
        add(f'<rect x="{x0}" y="{y - 12}" width="{w}" height="17" fill="{P["ground"]}"/>')
        label(x, y, s, size, color, anchor)

    # ---- sheet: ground, vignette, grid, frame, zones
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    add("<title>cdp-browser architecture</title>")
    add(
        "<defs>"
        f'<marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" '
        f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5" fill="none" '
        f'stroke="{P["line"]}" stroke-width="1.4"/></marker>'
        f'<marker id="am" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" '
        f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5" fill="none" '
        f'stroke="{acc}" stroke-width="1.6"/></marker>'
    )
    a, b = P["vignette"]
    add(
        f'<radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/></radialGradient>'
    )
    add("</defs>")
    add(f'<rect width="{W}" height="{H}" fill="{P["ground"]}"/>')  # solid background, always
    add(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    gmin, gmaj = P["grid"]
    for x in range(0, W + 1, MINOR):
        line(x, 0, x, H, 1, extra=f'opacity="{gmaj if x % MAJOR == 0 else gmin}"')
    for y in range(0, H + 1, MINOR):
        line(0, y, W, y, 1, extra=f'opacity="{gmaj if y % MAJOR == 0 else gmin}"')
    add(
        f'<rect x="{OUTER}" y="{OUTER}" width="{W - 2 * OUTER}" height="{H - 2 * OUTER}" fill="none" '
        f'stroke="{P["line"]}" stroke-width="2.5"/>'
    )
    add(
        f'<rect x="{INNER}" y="{INNER}" width="{W - 2 * INNER}" height="{H - 2 * INNER}" fill="none" '
        f'stroke="{P["line"]}" stroke-width="0.8" opacity="0.7"/>'
    )
    zw = (W - 2 * INNER) / 6
    for i in range(6):
        x = INNER + zw * (i + 0.5)
        for y in (OUTER + 8, H - OUTER - 2):
            text(x, y, str(i + 1), 9, P["line"], MONO, anchor="middle", extra='opacity="0.7"')
    zh = (H - 2 * INNER) / 4
    for i, z in enumerate("ABCD"):
        y = INNER + zh * (i + 0.5) + 3
        for x in (OUTER + 5, W - OUTER - 5):
            text(x, y, z, 9, P["line"], MONO, anchor="middle", extra='opacity="0.7"')

    # ---- DIAGRAM
    label(80, 92, "FIG. 1  ·  cdp-browser  ·  architecture", 13, P["soft"])
    text(80, 134, "ONE CDP API, TWO BROWSERS", 36, P["text"], COND, 600, ls=1)

    BH = 80
    LX, LW = 80, 200  # agent column
    TRUNK = 330  # fork trunk x
    CX0, CX1, CY0, CY1 = 400, 1300, 220, 700  # container frame
    CW = 180
    COL = [430, 650, 870, 1090]  # container columns (gap 40)
    R1, R2, R3 = 300, 440, 580  # container rows
    RA_SKILL, RA_AGENT, RA_SCRIPT = 300, 440, 580  # agent column rows
    HY = 820  # host chrome row

    # agent side
    box(LX, RA_SKILL, LW, BH, "SKILL.md", ["skills/browser/"], mono_subs=True)
    box(LX, RA_AGENT, LW, BH, "Coding agent", ["Claude Code, Codex"])
    box(LX, RA_SCRIPT, LW, BH, "Playwright script", ["connect_over_cdp()", "background_tab()"], mono_subs=True)
    mx = LX + LW / 2
    path([(mx, RA_AGENT), (mx, RA_SKILL + BH)])
    tag(mx + 12, (RA_SKILL + BH + RA_AGENT) / 2 + 5, "reads")
    path([(mx, RA_AGENT + BH), (mx, RA_SCRIPT)])
    tag(mx + 12, (RA_AGENT + BH + RA_SCRIPT) / 2 + 5, "runs")

    # backend A: container frame
    add(
        f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="none" stroke="{P["line"]}" '
        f'stroke-width="{THICK}"/>'
    )
    label(CX0 + 20, CY0 + 30, "Backend A  ·  Docker container", 13, P["soft"])
    code(CX0 + 20, CY0 + 52, "ghcr.io/sideef5ect/cdp-browser", 14, P["text"], weight=700)

    box(COL[0], R1, CW, BH, "socat", ["0.0.0.0:19222", "to 127.0.0.1:19223"], mono_subs=True)
    box(COL[1], R1, CW, BH, "Chromium", ["Playwright, headed", "CDP on :19223"])
    box(COL[3], R1, CW, BH, "x11vnc :15900", ["mirrors display"])
    volume(COL[1], R2, CW, BH, "/app/chrome_profile", "logins persist")
    box(COL[2], R2, CW, BH, "Xvfb :99", ["virtual display", "+ fluxbox WM"])
    box(COL[2], R3, CW, BH, "WebKit", ["no CDP, docker exec", "H.264 on ARM64"])
    volume(COL[3], R3, CW, BH, "/app/webkit_profile", "logins persist")

    # entrypoint note: thin outline, folded corner
    nx, ny, nw, nh = COL[0], R3, CW + 40 + CW, BH
    f = 14
    add(
        f'<path d="M{nx},{ny} L{nx + nw - f},{ny} L{nx + nw},{ny + f} L{nx + nw},{ny + nh} L{nx},{ny + nh} Z" '
        f'fill="{P["fill"]}" stroke="{P["line"]}" stroke-width="{THIN}"/>'
    )
    add(
        f'<path d="M{nx + nw - f},{ny} L{nx + nw - f},{ny + f} L{nx + nw},{ny + f}" fill="none" '
        f'stroke="{P["line"]}" stroke-width="{THIN}"/>'
    )
    code(nx + 14, ny + 27, "entrypoint.sh", 14, P["text"], weight=700)
    text(nx + 14, ny + 49, "starts Xvfb, fluxbox, VNC, Chromium, socat", 14, P["soft"])
    text(nx + 14, ny + 69, "clears stale profile locks", 14, P["soft"])

    # container wiring
    y1 = R1 + BH / 2
    path([(COL[0] + CW, y1), (COL[1], y1)], 1.8, acc, arrow="am")  # socat -> chromium (CDP)
    cx2 = COL[2] + CW / 2
    path([(COL[1] + CW, y1), (cx2, y1), (cx2, R2)])  # chromium -> Xvfb
    tag(COL[1] + CW + 12, y1 - 8, "renders")
    cx3 = COL[3] + CW / 2
    y2 = R2 + BH / 2
    path([(COL[2] + CW, y2), (cx3, y2), (cx3, R1 + BH)])  # Xvfb -> x11vnc
    tag(COL[2] + CW + 12, y2 - 8, "reads")
    cx1 = COL[1] + CW / 2
    path([(cx1, R1 + BH), (cx1, R2)], 1.2, dashed=True, arrow=None)  # chromium profile mount
    path([(COL[2] + CW, R3 + BH / 2), (COL[3], R3 + BH / 2)], 1.2, dashed=True, arrow=None)  # webkit mount
    hdim(COL[2], COL[2] + CW, R2 + BH + 26, "1920 x 1080", ext_to=R2 + BH + 4)  # display size

    # VNC viewer outside the container, above x11vnc
    VY = 110
    box(COL[3], VY, CW, 64, "VNC viewer", ["your desktop"])
    path([(cx3, VY + 64), (cx3, R1)], 1.8, acc, arrow="am")
    tag(cx3 - 12, (VY + 64 + CY0) / 2 + 5, "watch, log in by hand", anchor="end")
    tag(cx3 + 12, (CY0 + R1) / 2 + 5, ":15900", acc)

    # backend B: host chrome
    HX, HW = 400, 440
    label(HX, HY - 14, "Backend B", 13, P["soft"])
    box(
        HX,
        HY,
        HW,
        BH,
        "Host Chrome",
        ["--remote-debugging-port=9222", "--user-data-dir ~/.cache/chrome-cdp"],
        mono_subs=True,
    )
    ay = HY + 24
    add(f'<circle cx="{HX + HW}" cy="{ay}" r="3" fill="{P["line"]}"/>')
    path([(HX + HW, ay), (HX + HW + 40, ay)], THIN, arrow=None)
    code(HX + HW + 50, ay + 5, "background_tab()", 13, P["text"], weight=700)
    text(HX + HW + 50, ay + 25, "never steals focus", 14, P["soft"])

    # the fork: one URL, two backends (the accent path)
    sy = RA_SCRIPT + BH / 2
    hy = HY + BH / 2
    path([(LX + LW, sy), (TRUNK, sy)], 1.8, acc, arrow=None)
    path([(TRUNK, sy), (TRUNK, y1), (COL[0], y1)], 1.8, acc, arrow="am")
    path([(TRUNK, sy), (TRUNK, hy), (HX, hy)], 1.8, acc, arrow="am")
    add(f'<circle cx="{TRUNK}" cy="{sy}" r="4.5" fill="{acc}"/>')
    tag(TRUNK + 12, y1 - 9, ":19222", acc)
    tag(TRUNK + 12, hy - 9, ":9222", acc)
    # headline callout on the junction
    add(f'<circle cx="{TRUNK}" cy="{730}" r="3" fill="{acc}"/>')
    path([(TRUNK, 730), (TRUNK + 30, 730)], THIN, acc, arrow=None)
    label(TRUNK + 40, 735, "one CDP API, two backends", 13, acc, weight=700)
    for i, (k, url) in enumerate([("container", "http://localhost:19222"), ("host", "http://localhost:9222")]):
        code(TRUNK + 40, 756 + i * 20, k, 13)
        code(TRUNK + 130, 756 + i * 20, url, 13, P["text"])

    # socat note: headed Chromium binds loopback only
    sx = COL[0] + 24
    add(f'<circle cx="{sx}" cy="{R1 + BH}" r="3" fill="{P["line"]}"/>')
    path([(sx, R1 + BH), (sx, R1 + BH + 40), (sx + 14, R1 + BH + 40)], THIN, arrow=None)
    text(sx + 22, R1 + BH + 45, "Chromium binds", 14, P["soft"])
    text(sx + 22, R1 + BH + 65, "loopback only", 14, P["soft"])

    # legend
    lx, ly = 80, 690
    label(lx, ly, "legend", 11)
    for i, (kind, s) in enumerate(
        [
            ("accent", "open port (CDP, VNC)"),
            ("solid", "call, data flow"),
            ("dashed", "volume mount"),
            ("dim", "measured size"),
        ]
    ):
        y = ly + 26 + i * 24
        if kind == "solid":
            line(lx, y, lx + 56, y, 1.4)
        elif kind == "dashed":
            line(lx, y, lx + 56, y, 1.2, extra='stroke-dasharray="6 4"')
        elif kind == "dim":
            line(lx, y, lx + 56, y, THIN, extra='marker-start="url(#ar)" marker-end="url(#ar)"')
        else:
            line(lx, y, lx + 56, y, 1.8, acc)
        text(lx + 68, y + 5, s, 14, P["soft"])

    # title block, lower right
    bw, bh = 420, 100
    bx, by = W - INNER - bw, H - INNER - bh
    add(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{P["fill"]}" stroke="{P["line"]}" '
        f'stroke-width="{THICK}"/>'
    )
    line(bx, by + 44, bx + bw, by + 44)
    line(bx + 170, by + 44, bx + 170, by + bh)
    line(bx + 350, by + 44, bx + 350, by + bh)
    label(bx + 12, by + 17, "title", 9, P["soft"])
    text(bx + 12, by + 37, "CDP-BROWSER", 20, P["text"], COND, 600, ls=1.5)
    for x, k, v in [
        (bx + 12, "image", "amd64 + arm64"),
        (bx + 182, "built by", "GH Actions, GHCR"),
        (bx + 362, "rev", "A"),
    ]:
        label(x, by + 62, k, 9, P["soft"])
        label(x, by + 84, v, 12, P["text"], weight=700)

    add("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    dest = Path(__file__).with_name("architecture.svg")
    dest.write_text(build())
    print(f"wrote {dest}")
