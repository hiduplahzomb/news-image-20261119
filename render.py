#!/usr/bin/env python3
"""Render the news-image-20261119 entry: a four-story illustrated news
digest for Thursday 19 November 2026. Runs at build time with Pillow;
the submitted program (main.py) just copies the rendered entry.png.

Layout (1024x1024, sol's playbook): date in a top title band, one
full-width lead story (~half the height), three illustrated briefs
below. Every illustration is event-specific: the visuals must carry
the page, with captions covered.

Stories (all verified against live reporting, 19 Nov 2026):
  LEAD  Anthropic shares begin trading on Nasdaq as ANT after the
        record $81.3B IPO priced at $83 (18 Nov pricing, 19 Nov debut).
  BRIEF Trump, Xi and Putin meet in Shenzhen at the APEC summit.
  BRIEF Grand Theft Auto VI launches worldwide; gamers enter Vice City.
  BRIEF Severe Cyclone Akvan nears India's Andhra-Odisha coast.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette --
PAPER = (247, 243, 235)
INK = (26, 26, 26)
NAVY = (15, 27, 45)
WHITE = (255, 255, 255)
MUTED = (107, 103, 94)
RULE = (208, 201, 184)
RED = (180, 35, 24)
GREEN = (74, 222, 128)      # lead chart / ticker
GREEN_DK = (20, 83, 45)
LEAD_BG = (10, 31, 20)      # dark trading-screen panel
LEAD_GRID = (28, 58, 40)
GOLD = (212, 175, 55)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = word if not line else line + " " + word
            if draw.textlength(trial, font=fnt) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line or not lines:
            lines.append(line)
    return lines


def fit_size(draw, text, start, max_width, bold=True, min_size=16):
    """Largest size <= start at which text fits max_width on one line."""
    size = start
    while size > min_size:
        if draw.textlength(text, font=font(bold, size)) <= max_width:
            return size
        size -= 1
    return size


def text(draw, xy, s, size, color, bold=False):
    draw.text(xy, s, font=font(bold, size), fill=color)


def text_centered(draw, cx, y, s, size, color, bold=False):
    fnt = font(bold, size)
    draw.text((cx - draw.textlength(s, font=fnt) / 2, y), s, font=fnt,
              fill=color)


# -------------------------------------------------------------- lead art --

def draw_chart(d, x0, y0, x1, y1):
    """Rising stock chart: grid, area fill, green line, arrow, labels.

    The line is a stylised illustration of a rising debut, NOT a plot
    of real trades: only the verified $83 IPO price is labelled, and
    the panel is marked "Illustration" (Hydrogen review, criterion 4).
    """
    # Grid.
    for gy in range(y0 + 30, y1, 40):
        d.line([(x0, gy), (x1, gy)], fill=LEAD_GRID, width=1)
    # Area under the line (slightly lighter than the panel).
    pts = [(x0 + 10, y1 - 18), (x0 + 130, y1 - 30), (x0 + 250, y1 - 22),
           (x0 + 370, y1 - 62), (x0 + 490, y1 - 88), (x0 + 610, y1 - 118),
           (x0 + 730, y1 - 150), (x0 + 850, y1 - 178)]
    fill = pts + [(x0 + 850, y1 - 4), (x0 + 10, y1 - 4)]
    d.polygon(fill, fill=(16, 48, 30))
    # The line.
    d.line(pts, fill=GREEN, width=7, joint="curve")
    # Arrowhead at the end.
    ex, ey = pts[-1]
    d.polygon([(ex + 22, ey - 16), (ex + 2, ey - 2), (ex + 16, ey + 12)],
              fill=GREEN)
    # Price label: only the verified $83 IPO price (no invented axis).
    text(d, (x0 + 780, y1 - 218), "$83", 30, GREEN, bold=True)
    # Honest label: this is an illustration, not trade data. Bottom
    # right of the chart area, clear of the rising line.
    text(d, (x1 - 130, y1 - 24), "Illustration", 18, (148, 163, 150))


def draw_lead(d):
    x0, y0, x1, y1 = 24, 112, 1000, 556
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=LEAD_BG)
    # Kicker.
    text(d, (x0 + 26, y0 + 20), "BUSINESS  \u2022  NEW YORK", 24,
         GREEN, bold=True)
    # Ticker box, top right.
    bx0, by0, bx1, by1 = x1 - 218, y0 + 16, x1 - 26, y0 + 64
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=8,
                        outline=GREEN, width=3)
    text_centered(d, (bx0 + bx1) // 2, by0 + 8, "ANT  $83", 28, WHITE,
                  bold=True)
    # Headline, two lines.
    text(d, (x0 + 26, y0 + 62), "ANTHROPIC DEBUTS ON NASDAQ", 50, WHITE,
         bold=True)
    text(d, (x0 + 26, y0 + 122), "AFTER RECORD $81 BILLION IPO", 46,
         GREEN, bold=True)
    # Sub-line.
    text(d, (x0 + 26, y0 + 184),
         "Shares begin trading today after pricing above range", 24,
         (200, 210, 202))
    # Chart fills the bottom of the panel.
    draw_chart(d, x0 + 26, y0 + 224, x1 - 26, y1 - 18)


# ------------------------------------------------------------ brief art ---

def draw_flag_us(d, x, y, w, h):
    """Simplified US flag: stripes + blue canton with star dots."""
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    stripe = h / 13
    for i in range(0, 13, 2):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=(178, 34, 52))
    cw, ch = w * 0.4, h * 7 / 13
    d.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            sx = x + 6 + c * (cw - 10) / 3
            sy = y + 5 + r * (ch - 8) / 2
            d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5],
                      fill=WHITE)


def draw_star(d, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def draw_flag_cn(d, x, y, w, h):
    """Simplified China flag: red + one big yellow star, four small."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw_star(d, x + w * 0.28, y + h * 0.3, h * 0.22, (255, 222, 0))
    for sx, sy in ((0.55, 0.15), (0.68, 0.28), (0.68, 0.48), (0.55, 0.6)):
        draw_star(d, x + w * sx, y + h * sy, h * 0.09, (255, 222, 0))


def draw_flag_ru(d, x, y, w, h):
    """Russia tricolour: white / blue / red horizontal bands."""
    d.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3],
                fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def draw_summit(d, x0, y0, w, h):
    """Three flags on poles above a round summit table."""
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10,
                        fill=(232, 222, 196))
    fw, fh = 84, 56
    gap = (w - 3 * fw) // 4
    pole_top = y0 + 22
    pole_bot = y0 + h - 78
    for i, fn in enumerate((draw_flag_us, draw_flag_cn, draw_flag_ru)):
        fx = x0 + gap + i * (fw + gap)
        fy = pole_top + 4
        d.line([(fx + fw // 2, pole_top), (fx + fw // 2, pole_bot)],
               fill=(120, 110, 90), width=4)
        fn(d, fx, fy, fw, fh)
        d.ellipse([fx + fw // 2 - 4, pole_top - 4, fx + fw // 2 + 4,
                   pole_top + 4], fill=GOLD)
    # Table: a rectangular top with two legs, reading as a meeting table.
    ty = y0 + h - 52
    d.rounded_rectangle([x0 + 30, ty, x0 + w - 30, ty + 16], radius=5,
                        fill=(122, 72, 32))
    d.rectangle([x0 + 30, ty, x0 + w - 30, ty + 6], fill=(146, 90, 42))
    for lx in (x0 + 56, x0 + w - 64):
        d.rectangle([lx, ty + 16, lx + 8, y0 + h - 6],
                    fill=(90, 60, 30))


def draw_vice_city(d, x0, y0, w, h):
    """Neon Vice City sunset: gradient sky, sun, palms, skyline, water."""
    # Sky gradient: deep purple -> pink -> orange.
    top = (45, 27, 78)
    mid = (193, 53, 132)
    bot = (255, 126, 61)
    for yy in range(h):
        t = yy / max(1, h - 1)
        if t < 0.55:
            s = t / 0.55
            col = tuple(int(top[i] + (mid[i] - top[i]) * s)
                        for i in range(3))
        else:
            s = (t - 0.55) / 0.45
            col = tuple(int(mid[i] + (bot[i] - mid[i]) * s)
                        for i in range(3))
        d.line([(x0, y0 + yy), (x0 + w, y0 + yy)], fill=col)
    # Sun, low over the skyline, clear of the tallest buildings.
    sx, sy, sr = x0 + 62, y0 + int(h * 0.44), 30
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 209, 102))
    # Skyline silhouette.
    base = y0 + int(h * 0.78)
    heights = [52, 78, 44, 96, 62, 110, 70, 48, 88, 58]
    bw = w / len(heights)
    for i, bh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 1, base - bh, bx + bw - 1, base],
                    fill=(20, 10, 30))
        # A few lit windows.
        for wy in range(int(base - bh) + 8, base - 6, 14):
            if (i * 7 + wy) % 3 == 0:
                d.rectangle([bx + bw / 2 - 2, wy, bx + bw / 2 + 2,
                             wy + 4], fill=(255, 209, 102))
    # Palm silhouettes, left and right: tall curved trunks with long
    # drooping fronds (crown -> rise -> droop), silhouetted on the sky.
    for px, flip in ((x0 + 40, 1), (x0 + w - 40, -1)):
        py = base
        pts = []
        for t in range(9):
            tt = t / 8
            pts.append((px + flip * 16 * tt * tt,
                        py - 88 * tt))
        d.line(pts, fill=(20, 10, 30), width=6)
        tx, ty = pts[-1]
        for ang in (-170, -130, -90, -50, -10):
            a = math.radians(ang)
            ex = tx + 48 * math.cos(a)
            ey = ty + 48 * math.sin(a) * 0.55 + 16
            mx = tx + 24 * math.cos(a)
            my = ty + 24 * math.sin(a) * 0.55 - 8
            d.line([(tx, ty), (mx, my), (ex, ey)], fill=(20, 10, 30),
                   width=5)
    # Water strip with a sun reflection.
    d.rectangle([x0, base, x0 + w, y0 + h], fill=(30, 16, 54))
    for i in range(6):
        rw = 46 - i * 6
        ry = base + 6 + i * 6
        d.line([(sx - rw // 2, ry), (sx + rw // 2, ry)],
               fill=(255, 170, 90), width=3)
    # "VI" in the sky, top right, clear of the skyline (Hydrogen
    # review: the old 58px letters overlapped the buildings and would
    # smear at 300px). 44px at y0+6 ends at ~y0+50, above the tallest
    # nearby building top (y0+60).
    fnt = font(True, 44)
    d.text((x0 + w - 76, y0 + 6), "VI", font=fnt, fill=WHITE,
           stroke_width=2, stroke_fill=(255, 110, 180))


def draw_cyclone(d, x0, y0, w, h):
    """Spiral cyclone over the Bay of Bengal beside India's east coast."""
    # Sea gradient.
    top = (18, 63, 107)
    bot = (10, 42, 74)
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(x0, y0 + yy), (x0 + w, y0 + yy)], fill=col)
    # Landmass (India's east coast) on the right.
    land = [(x0 + w, y0), (x0 + w * 0.78, y0),
            (x0 + w * 0.72, y0 + h * 0.3), (x0 + w * 0.8, y0 + h * 0.55),
            (x0 + w * 0.74, y0 + h * 0.8), (x0 + w * 0.82, y0 + h),
            (x0 + w, y0 + h)]
    d.polygon(land, fill=(201, 177, 140))
    d.line(land[:-1], fill=(160, 135, 95), width=3)
    # Rain streaks over the land.
    for i in range(12):
        rx = x0 + w * 0.82 + (i % 4) * 12
        ry = y0 + 14 + (i // 4) * 48 + (i % 3) * 8
        d.line([(rx, ry), (rx - 7, ry + 16)], fill=(220, 235, 245),
               width=2)
    # Spiral: concentric arcs, rotating start angles, white bands.
    cx, cy = x0 + int(w * 0.42), y0 + int(h * 0.52)
    for r, start, width in ((78, 20, 12), (62, 110, 11), (47, 200, 10),
                            (33, 290, 9), (20, 40, 8)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=start,
              end=start + 250, fill=WHITE, width=width)
    # Eye.
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(10, 42, 74))
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=WHITE,
              width=2)


# --------------------------------------------------------------- layout ---

BRIEFS = [
    {
        "art": draw_summit,
        "kicker": "DIPLOMACY  \u2022  SHENZHEN",
        "color": (15, 118, 110),
        "headline": "TRUMP, XI AND PUTIN MEET",
        "sub": "First trilateral summit at APEC",
    },
    {
        "art": draw_vice_city,
        "kicker": "CULTURE  \u2022  WORLDWIDE",
        "color": (193, 53, 132),
        "headline": "GTA VI LAUNCHES",
        "sub": "Gamers flood Vice City after 13 years",
    },
    {
        "art": draw_cyclone,
        "kicker": "WEATHER  \u2022  INDIA",
        "color": (3, 105, 161),
        "headline": "CYCLONE AKVAN NEARS INDIA",
        "sub": "Red alert; coastal evacuations under way",
    },
]

FOOTER = "News of Thursday, 19 November 2026."


def draw_brief(d, x0, brief):
    w = 320
    y_art, h_art = 572, 190
    brief["art"](d, x0, y_art, w, h_art)
    text(d, (x0, 780), brief["kicker"], 20, brief["color"], bold=True)
    lines = wrap(d, brief["headline"], font(True, 29), w)
    ly = 812
    for line in lines[:2]:
        text(d, (x0, ly), line, 29, INK, bold=True)
        ly += 36
    sub_lines = wrap(d, brief["sub"], font(False, 22), w)
    ly = 890
    for line in sub_lines[:2]:
        text(d, (x0, ly), line, 22, MUTED)
        ly += 28


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Title band.
    d.rectangle([0, 0, W, 96], fill=NAVY)
    text_centered(d, W // 2, 24, "THURSDAY, 19 NOVEMBER 2026", 50,
                  WHITE, bold=True)
    d.rectangle([0, 96, W, 100], fill=GOLD)
    # Lead + briefs + footer.
    draw_lead(d)
    for i, brief in enumerate(BRIEFS):
        draw_brief(d, 24 + i * 328, brief)
    text_centered(d, W // 2, 992, FOOTER, 18, MUTED)
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img = build()
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
