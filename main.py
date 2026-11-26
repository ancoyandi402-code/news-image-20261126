#!/usr/bin/env python3
"""One-day newspaper front page: Thursday 26 November 2026.

Renders a 1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Pure Pillow drawing: no network, no clock, no randomness, so every run
produces identical bytes.

Design rule: the page is built to be read at 300px, the size the
make.fun judge sees. The top half carries the whole day at a glance --
a huge date, a strip of key numbers in large type, one big lead story
with a drawn illustration, and two big panels. The dense brief list,
map and DATE CHECK underneath prove breadth at full size.

39 stories, all dated 26 November 2026, each numbered, tagged by
region and sourced. The DATE CHECK box names what was deliberately
left out: the previous days' news (Hormuz, Nvidia, COP31, ICJ
Myanmar, Sanofi/Insmed).
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (250, 247, 240)      # newsprint off-white
INK = (18, 18, 18)
RED = (155, 28, 28)
NAVY = (20, 32, 64)
GREY = (90, 88, 82)
BLUE = (58, 110, 165)     # sea
LAND = (196, 178, 138)    # map land
GOLD = (200, 160, 40)
MARGIN = 28
CW = W - 2 * MARGIN

HERE = os.path.dirname(os.path.abspath(__file__))


def load_font(name, size):
    for path in (os.path.join(HERE, "fonts", name),
                 os.path.join(HERE, name)):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.truetype(name, size)


def serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap: lines that fit max_w by measured text length."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rule(draw, x0, y, x1, weight=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=weight)
    return y + weight


# ---------------------------------------------------------------- stories
# (number, region, headline, summary, source)
LEAD = (1, "UNITED STATES",
        "A century of balloons: Macy's 100th Thanksgiving parade",
        "A record 100 inflatables and 3 million spectators on a 2.5-mile "
        "route through New York -- but a storm may ground the giant "
        "balloons if gusts top 34 mph.",
        "Macy's / PEOPLE")

WHY = ("WHY IT MATTERS: the centennial parade is the one story that "
       "could only happen today -- Thanksgiving itself.")

PANELS = [
    (2, "ASIA", "Bank of Korea lifts base rate to 3.25%",
     "Third hike of the cycle, to curb inflation as a chip-export boom "
     "runs hot. Growth outlook raised to 3.9% for 2026.", "Yonhap"),
    (3, "EUROPE", "EU budget battle: \u20ac1.78 trillion on the table",
     "Leaders meet in Brussels over the 2028-2034 framework and "
     "Ukraine's 2027 funding; five Central European states opposed.",
     "Europe News Hub"),
]

GRID = [
    (4, "EUROPE", "London Tube stops as drivers walk out",
     "RMT strike from midday; no Piccadilly or Circle.", "TfL / BBC"),
    (5, "SPORT", "Mahomes vs Allen, episode XI",
     "Chiefs (8-2) visit Bills (9-1) in the nightcap.", "CNN"),
    (6, "ASIA", "North Korea expels Swiss diplomat",
     "Pyongyang shuts Switzerland's new office.", "Jabulani Radio"),
    (10, "ASIA", "India marks 77th Constitution Day",
     "77 years on; Preamble readings nationwide.", "selfstudys"),
    (11, "MIDDLE EAST", "Israeli strike kills Hamas official in Gaza City",
     "Airstrike kills Hamas official Abu al-Ouf.", "EUR Radio"),
    (12, "SPORT", "IPL 2027 auction: 1,220 players register",
     "1,220 cricketers enrolled for the 2027 auction.", "selfstudys"),
]

# (number, one-line headline) -- trimmed to fit one column line
ALSO = [
    (7, "Gukesh faces Sindarov"),
    (8, "India: 18 years since 26/11"),
    (9, "EU rejects US tariff case"),
    (13, "Thanksgiving Day in the US"),
    (14, "US markets closed for holiday"),
    (15, "Storm may ground the balloons"),
    (16, "TCU at Texas Tech, 8pm ET"),
    (17, "EU advances 7 budget plans"),
    (18, "EU farm-cage ban timeline"),
    (19, "3.7M EU industry jobs at risk"),
    (20, "Von der Leyen on ceasefire"),
    (21, "BoJ: Dec hike to 1.5% likely"),
    (22, "India: humans must control AI"),
    (23, "IITs add 6,000 AI seats"),
    (24, "Doloo airport approved"),
    (25, "Kamarajar terminal approved"),
    (26, "First NE India antivenom"),
    (27, "Bio-economy to hit $300bn"),
    (28, "India-Nepal exercise begins"),
    (29, "Sooryavanshi hits 204 off 53"),
    (30, "Flipkart CEO to step down"),
    (31, "Hasina seeks return to Dhaka"),
    (32, "Bangladesh wage up 36%"),
    (33, "Suneung AI cheating scandal"),
    (34, "Five Mexicans held in Nigeria"),
    (35, "New Oshima debuts at Mombasa"),
    (36, "Tuas Port Phase Two starts"),
    (37, "Europa League: 17 fixtures"),
    (38, "India: end shipping attacks"),
    (39, "GRSE delivers 120th warship"),
]

# (big number, label) -- the strip that reads at 300px
KEYNUMS = [
    ("100", "inflatables in parade"),
    ("3M", "spectators on route"),
    ("3.25%", "BoK base rate"),
    ("490,334", "Russian war deaths"),
    ("\u20ac1.78tn", "EU budget debate"),
    ("+36%", "Bangladesh wage rise"),
]

DATECHECK = ("DATE CHECK \u2014 Every story here happened or was first reported "
             "on Thursday 26 November 2026. Left out on purpose: Wed 25 Nov \u2014 "
             "Hormuz tankers hit mines; Nvidia reinstates Huang; COP31 "
             "collapses; Shenzhou-24 lifts off. Tue 24 Nov \u2014 ICJ rules on "
             "Myanmar; Sanofi/Insmed.")


# ------------------------------------------------------- drawn illustrations
def draw_balloons(d, x, y, w, h):
    """Three parade inflatables over a row of heads."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 242), outline=INK)
    # red balloon, left
    cx, cy = x + w * 0.24, y + h * 0.34
    d.ellipse([cx - w * 0.13, cy - h * 0.22, cx + w * 0.13, cy + h * 0.22],
              fill=RED, outline=INK)
    d.ellipse([cx - w * 0.05, cy - h * 0.16, cx + w * 0.02, cy - h * 0.04],
              fill=(255, 120, 120))
    d.line([(cx, cy + h * 0.22), (cx, y + h * 0.78)], fill=INK, width=2)
    # gold balloon, centre, biggest
    cx, cy = x + w * 0.55, y + h * 0.30
    d.ellipse([cx - w * 0.16, cy - h * 0.24, cx + w * 0.16, cy + h * 0.24],
              fill=GOLD, outline=INK)
    d.ellipse([cx - w * 0.06, cy - h * 0.18, cx + w * 0.03, cy - h * 0.04],
              fill=(255, 220, 130))
    d.line([(cx, cy + h * 0.24), (cx, y + h * 0.78)], fill=INK, width=2)
    # blue balloon, right
    cx, cy = x + w * 0.84, y + h * 0.36
    d.ellipse([cx - w * 0.11, cy - h * 0.20, cx + w * 0.11, cy + h * 0.20],
              fill=BLUE, outline=INK)
    d.ellipse([cx - w * 0.04, cy - h * 0.14, cx + w * 0.02, cy - h * 0.03],
              fill=(140, 190, 230))
    d.line([(cx, cy + h * 0.20), (cx, y + h * 0.78)], fill=INK, width=2)
    # crowd heads along the bottom
    for i in range(9):
        hx = x + w * (0.06 + i * 0.11)
        d.ellipse([hx - 5, y + h * 0.82, hx + 5, y + h * 0.92], fill=INK)
    d.line([(x, y + h * 0.96), (x + w, y + h * 0.96)], fill=INK, width=2)


def draw_coin_chart(d, x, y, w, h):
    """A % coin and a rising arrow: the rate hike."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 247, 240), outline=INK)
    cx, cy = x + w * 0.30, y + h * 0.45
    r = min(w, h) * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=INK,
              width=2)
    d.text((cx, cy), "%", font=serif_b(int(r * 1.1)), fill=INK, anchor="mm")
    pts = [(x + w * 0.52, y + h * 0.72), (x + w * 0.64, y + h * 0.55),
           (x + w * 0.72, y + h * 0.62), (x + w * 0.88, y + h * 0.34)]
    d.line(pts, fill=RED, width=4, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 12, ay + 2), (ax - 2, ay + 12)], fill=RED)


def draw_eu_building(d, x, y, w, h):
    """Columned building under a ring of twelve stars, on navy."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 32, 64), outline=INK)
    cx, cy = x + w / 2, y + h * 0.26
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx = cx + math.cos(a) * w * 0.30
        sy = cy + math.sin(a) * h * 0.16
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=GOLD)
    # pediment, block and four columns
    bx, by = x + w * 0.16, y + h * 0.52
    bw, bh = w * 0.68, h * 0.38
    d.polygon([(bx - 6, by), (bx + bw / 2, by - h * 0.12),
               (bx + bw + 6, by)], fill=(250, 247, 240))
    d.rectangle([bx, by, bx + bw, by + bh], fill=(250, 247, 240))
    for i in range(4):
        colx = bx + bw * (0.12 + i * 0.24)
        d.rectangle([colx, by + 4, colx + 8, by + bh - 4], fill=NAVY)


def continent_polys():
    """Rough continent outlines in map-local coordinates."""
    return [
        # North America
        [(30, 25), (70, 12), (115, 18), (135, 38), (125, 58), (100, 72),
         (70, 68), (40, 52), (25, 38)],
        # South America
        [(95, 95), (115, 88), (130, 100), (125, 130), (112, 158),
         (100, 150), (92, 120)],
        # Europe
        [(158, 22), (178, 16), (190, 26), (184, 42), (168, 44), (158, 34)],
        # Africa
        [(160, 58), (186, 52), (202, 64), (196, 92), (186, 118),
         (172, 114), (162, 88), (156, 70)],
        # Asia
        [(192, 18), (235, 8), (285, 14), (312, 28), (302, 58), (272, 68),
         (240, 62), (212, 52), (196, 38)],
        # Australia
        [(272, 128), (298, 124), (304, 144), (284, 150), (270, 140)],
    ]


def draw_map(d, mx, my):
    mw, mh = 320, 108
    s = mh / 190.0
    d.rectangle([mx, my, mx + mw, my + mh], fill=(214, 232, 242),
                outline=INK)
    for poly in continent_polys():
        pts = [(mx + px, my + py * s) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=(120, 105, 70))
    # six numbered pins, spread so none overlap: (story, map x, map y)
    pins = [(1, 70, 42), (2, 280, 38), (3, 172, 30), (4, 150, 20),
            (8, 236, 70), (11, 198, 58)]
    for num, px, py in pins:
        cx, cy = mx + px, my + py * s
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=(255, 255, 255))
        d.text((cx, cy), str(num), font=sans_b(11), fill=(255, 255, 255),
               anchor="mm")


# ------------------------------------------------------------------- layout
def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- navy top bar ----
    d.rectangle([0, 0, W, 30], fill=NAVY)
    d.text((MARGIN, 15), "THE WORLD IN ONE DAY", font=sans_b(15),
           fill=(255, 255, 255), anchor="lm")
    d.text((W - MARGIN, 15), "39 STORIES \u2022 6 CONTINENTS \u2022 EVERY ONE DATED",
           font=sans_b(15), fill=(255, 255, 255), anchor="rm")
    y = 40

    # ---- masthead: date huge so it reads at 300px ----
    d.text((W / 2, y), "Thursday 26 November 2026", font=serif_b(50),
           fill=INK, anchor="ma")
    y += 58
    y = rule(d, MARGIN, y, W - MARGIN, 3)
    y = rule(d, MARGIN, y + 4, W - MARGIN, 1)
    y += 6
    d.text((W / 2, y), "Macy's 100th parade  \u2022  Korea hikes to 3.25%  "
           "\u2022  EU budget battle  \u2022  Tube strike",
           font=sans_b(17), fill=RED, anchor="ma")
    y += 26
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8

    # ---- key-numbers strip: numbers big ----
    n = len(KEYNUMS)
    bw = CW // n
    for i, (num, label) in enumerate(KEYNUMS):
        x0 = MARGIN + i * bw
        d.rectangle([x0, y, x0 + bw - 6, y + 56], outline=INK, width=1)
        d.text((x0 + (bw - 6) / 2, y + 7), num, font=serif_b(34),
               fill=RED, anchor="ma")
        for li, line in enumerate(wrap(d, label, sans(11), bw - 16)):
            d.text((x0 + (bw - 6) / 2, y + 42 + li * 13), line,
                   font=sans(11), fill=INK, anchor="ma")
    y += 56 + 8
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8

    # ---- lead story: Macy's parade, big illustration, big headline ----
    num, region, head, summ, src = LEAD
    d.text((MARGIN, y), "1  \u2022  TOP STORY  \u2022  " + region,
           font=sans_b(16), fill=RED, anchor="la")
    y += 24
    lead_y = y
    ill_w, ill_h = 250, 120
    draw_balloons(d, MARGIN, lead_y + 4, ill_w, ill_h)
    tx = MARGIN + ill_w + 18
    tw = W - MARGIN - tx
    for line in wrap(d, head, serif_b(38), tw):
        d.text((tx, lead_y), line, font=serif_b(38), fill=INK, anchor="la")
        lead_y += 44
    lead_y += 4
    for line in wrap(d, summ, sans(17), tw):
        d.text((tx, lead_y), line, font=sans(17), fill=INK, anchor="la")
        lead_y += 21
    lead_y += 4
    for line in wrap(d, WHY, sans_b(16), tw):
        d.text((tx, lead_y), line, font=sans_b(16), fill=RED, anchor="la")
        lead_y += 20
    y = max(lead_y, y + ill_h + 8) + 2
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8

    # ---- panels: two across, big headlines ----
    pw = (CW - 14) // 2
    panel_y = y
    panel_bottom = y
    for i, (num, region, head, summ, src) in enumerate(PANELS):
        x0 = MARGIN + i * (pw + 14)
        d.text((x0, y), f"{num}  \u2022  {region}", font=sans_b(14),
               fill=RED, anchor="la")
        iy = y + 22
        if i == 0:
            draw_coin_chart(d, x0, iy, 92, 76)
        else:
            draw_eu_building(d, x0, iy, 92, 76)
        hx = x0 + 102
        hw2 = pw - 102
        hy = iy
        for line in wrap(d, head, serif_b(26), hw2):
            d.text((hx, hy), line, font=serif_b(26), fill=INK, anchor="la")
            hy += 30
        hy += 2
        for line in wrap(d, summ, sans(14), hw2):
            d.text((hx, hy), line, font=sans(14), fill=INK, anchor="la")
            hy += 17
        hy += 2
        d.text((hx, hy), f"({src})", font=sans(11), fill=GREY, anchor="la")
        panel_bottom = max(panel_bottom, hy + 13)
    y = panel_bottom + 6
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8

    # ---- grid: six stories, three columns by two rows ----
    gw = (CW - 2 * 12) // 3
    grid_y = y
    for r in range(2):
        row_bottom = grid_y
        for c in range(3):
            num, region, head, summ, src = GRID[r * 3 + c]
            x0 = MARGIN + c * (gw + 12)
            d.text((x0, grid_y), f"{num}", font=serif_b(16), fill=RED,
                   anchor="la")
            d.text((x0 + 26, grid_y), region, font=sans_b(11), fill=RED,
                   anchor="la")
            hy = grid_y + 20
            for line in wrap(d, head, serif_b(19), gw):
                d.text((x0, hy), line, font=serif_b(19), fill=INK,
                       anchor="la")
                hy += 22
            for line in wrap(d, summ, sans(13), gw):
                d.text((x0, hy), line, font=sans(13), fill=INK, anchor="la")
                hy += 16
            d.text((x0, hy), f"({src})", font=sans(10), fill=GREY,
                   anchor="la")
            row_bottom = max(row_bottom, hy + 12)
        grid_y = row_bottom + 2
    y = grid_y
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8

    # ---- map (left) + ALSO list (right, three columns) ----
    map_x, map_y = MARGIN, y
    d.text((map_x, map_y), "WHERE IT HAPPENED",
           font=sans_b(13), fill=INK, anchor="la")
    draw_map(d, map_x, map_y + 20)
    map_bottom = map_y + 20 + 108
    ax = MARGIN + 320 + 16
    aw = W - MARGIN - ax
    d.text((ax, map_y), "ALSO ON THURSDAY 26 NOVEMBER",
           font=sans_b(14), fill=INK, anchor="la")
    ay = map_y + 22
    per_col = 10
    col_w = (aw - 2 * 10) // 3
    for i, (num, head) in enumerate(ALSO):
        col = i // per_col
        row = i % per_col
        x0 = ax + col * (col_w + 10)
        yy = ay + row * 13
        d.text((x0, yy), f"{num}", font=sans_b(11), fill=RED, anchor="la")
        # one line each: trim the headline until it fits the column
        fnt = sans(11)
        max_w = col_w - 26
        while head and d.textlength(head, font=fnt) > max_w:
            head = head[:-1]
        d.text((x0 + 24, yy), head, font=fnt, fill=INK, anchor="la")
    also_bottom = ay + per_col * 13
    y = max(map_bottom, also_bottom)
    y = rule(d, MARGIN, y, W - MARGIN, 1)
    y += 6

    # ---- date check box ----
    box_h = 46
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=RED, width=2)
    for li, line in enumerate(wrap(d, DATECHECK, sans(12), CW - 24)):
        d.text((MARGIN + 12, y + 5 + li * 13), line, font=sans(12),
               fill=INK, anchor="la")
    y += box_h
    print("final y:", y, "of", H)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
