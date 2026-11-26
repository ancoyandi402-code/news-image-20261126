#!/usr/bin/env python3
"""News Image 26 Nov 2026 -- one-day newspaper front page, 1024x1024.

Renders Thursday 26 November 2026's world news as a single front page,
designed to stay readable when shrunk to 300px: a huge date, a key-numbers
strip in large type, three big lead stories with illustrations, a world map
with numbered pins, a dated brief list, and a DATE CHECK box.

Deterministic: no network, no clock, no randomness. Same bytes every run.
Run:  MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MX = 28            # side margin
RX = W - MX        # right content edge (996)
CW = RX - MX       # content width (968)

PAPER = (250, 247, 240)
INK = (18, 18, 18)
RED = (155, 28, 28)
NAVY = (20, 32, 64)
GREY = (90, 88, 82)
SEA = (214, 232, 242)
LAND = (196, 178, 138)
GOLD = (200, 160, 40)
SKY = (58, 110, 165)
WHITE = (255, 255, 255)
HL_RED = (240, 150, 150)
HL_GOLD = (240, 220, 140)
HL_BLUE = (150, 190, 230)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

_cache = {}


def _load(name, size):
    key = (name, size)
    f = _cache.get(key)
    if f is None:
        f = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        _cache[key] = f
    return f


def serif(size):
    return _load("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return _load("DejaVuSans.ttf", size)


def sans_b(size):
    return _load("DejaVuSans-Bold.ttf", size)


def wrap(d, text, font, max_w):
    """Word-wrap text to fit max_w; returns a list of lines."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = w if not cur else cur + " " + w
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_first(d, text, font, first_w, rest_w):
    """Wrap with a narrower first line (room for a bold prefix)."""
    words = text.split()
    lines = []
    cur = ""
    limit = first_w
    for w in words:
        t = w if not cur else cur + " " + w
        if d.textlength(t, font=font) <= limit:
            cur = t
        else:
            lines.append(cur)
            cur = w
            limit = rest_w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, max_w, fill, lh):
    """Draw wrapped text starting at (x, y); return y below last line."""
    for line in wrap(d, text, font, max_w):
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def centre(d, cx, y, text, font, fill):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma")


def rule(d, y, weight=1, x0=MX, x1=RX, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=weight)


def trim_to(d, text, font, max_w):
    """Cut characters off the end until the text fits max_w."""
    while text and d.textlength(text, font=font) > max_w:
        text = text[:-1]
    return text


# ---------------------------------------------------------------- data

KEYNUMS = [
    ("100", "inflatables in parade"),
    ("3M", "spectators on route"),
    ("3.25%", "BoK base rate"),
    ("490,334", "Russian war deaths"),
    ("\u20ac1.78tn", "EU budget debate"),
    ("+36%", "Bangladesh wage rise"),
]

LEAD_HEADLINE = "A century of balloons: Macy's 100th Thanksgiving parade"
LEAD_SUMMARY = ("A record 100 inflatables and 3 million spectators on a 2.5-mile "
                "route through New York -- but a storm may ground the giant "
                "balloons if gusts top 34 mph.")
LEAD_WHY = ("WHY IT MATTERS: the centennial parade is the one story that could "
            "only happen today -- Thanksgiving itself.")

PANELS = [
    {
        "num": 2, "region": "ASIA", "kind": "coin",
        "headline": "Bank of Korea lifts base rate to 3.25%",
        "summary": ("Third hike of the cycle, to curb inflation as a chip-export "
                    "boom runs hot. Growth outlook raised to 3.9% for 2026."),
        "source": "(Yonhap)",
    },
    {
        "num": 3, "region": "EUROPE", "kind": "eu",
        "headline": "EU budget battle: \u20ac1.78 trillion on the table",
        "summary": ("Leaders meet in Brussels over the 2028-2034 framework and "
                    "Ukraine's 2027 funding; five Central European states opposed."),
        "source": "(Europe News Hub)",
    },
]

GRID = [
    (4, "EUROPE", "London Tube stops as drivers walk out",
     "RMT strike from midday; no Piccadilly or Circle.", "(TfL / BBC)"),
    (5, "SPORT", "Mahomes vs Allen, episode XI",
     "Chiefs (8-2) visit Bills (9-1) in the nightcap.", "(CNN)"),
    (6, "ASIA", "North Korea expels Swiss diplomat",
     "Pyongyang shuts Switzerland's new office.", "(Jabulani Radio)"),
    (10, "ASIA", "India marks 77th Constitution Day",
     "77 years on; Preamble readings nationwide.", "(selfstudys)"),
    (11, "MIDDLE EAST", "Israeli strike kills Hamas official in Gaza City",
     "Airstrike kills Hamas official Abu al-Ouf.", "(EUR Radio)"),
    (12, "SPORT", "IPL 2027 auction: 1,220 players register",
     "1,220 cricketers enrolled for the 2027 auction.", "(selfstudys)"),
]

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

DATECHECK_BODY = ("Every story here happened or was first reported on Thursday "
                  "26 November 2026. Left out on purpose: Wed 25 Nov \u2014 "
                  "Hormuz tankers hit mines; Nvidia reinstates Huang; COP31 "
                  "collapses; Shenzhou-24 lifts off. Tue 24 Nov \u2014 ICJ rules "
                  "on Myanmar; Sanofi/Insmed.")

# Rough continent shapes, in map-local coordinates (map is 320x108).
CONTINENTS = [
    [(6, 22), (28, 8), (58, 5), (92, 10), (108, 20), (98, 36),
     (68, 48), (38, 44), (12, 34)],                       # North America
    [(72, 56), (94, 52), (104, 64), (94, 86), (78, 80),
     (70, 66)],                                            # South America
    [(158, 16), (178, 8), (198, 13), (192, 28), (172, 30),
     (160, 26)],                                           # Europe
    [(162, 40), (192, 36), (208, 48), (198, 74), (178, 88),
     (166, 64)],                                           # Africa
    [(202, 10), (258, 6), (298, 13), (308, 28), (278, 44),
     (238, 40), (212, 28)],                               # Asia
    [(262, 72), (292, 68), (302, 80), (282, 92), (266, 84)],  # Australia
]

# (story number, map-local x, map-local y) -- spread so pins never touch.
PINS = [
    (1, 55, 28),
    (4, 165, 22),
    (3, 188, 30),
    (11, 208, 38),
    (8, 228, 42),
    (2, 285, 32),
]


# ---------------------------------------------------------------- pictures

def draw_balloons(d, x, y, w=250, h=120):
    """Three parade balloons over a row of crowd heads, pale blue sky."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SEA, outline=INK, width=2)
    # Strings first, so balloons sit on top of their tops.
    for cx, top in ((x + 56, y + 68), (x + 132, y + 66), (x + 206, y + 66)):
        d.line([(cx, top), (cx, y + 100)], fill=INK, width=2)
    # Crowd: nine small black heads along the bottom.
    for i in range(9):
        cx = x + 16 + i * 26
        cy = y + h - 13
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    # Balloons: red, gold, blue ovals with a pale highlight spot.
    for (bx0, by0, bx1, by1, colour, hl) in (
            (x + 24, y + 16, x + 88, y + 68, (178, 40, 40), HL_RED),
            (x + 98, y + 10, x + 166, y + 66, GOLD, HL_GOLD),
            (x + 178, y + 18, x + 234, y + 66, SKY, HL_BLUE)):
        d.ellipse([bx0, by0, bx1, by1], fill=colour, outline=INK, width=2)
        d.ellipse([bx0 + 12, by0 + 8, bx0 + 26, by0 + 20], fill=hl)


def draw_coin(d, x, y, w=92, h=76):
    """Gold percent coin with a red rising arrow."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=PAPER, outline=INK, width=2)
    d.ellipse([x + 7, y + 17, x + 49, y + 59], fill=GOLD, outline=INK, width=2)
    d.text((x + 28, y + 38), "%", font=sans_b(20), fill=INK, anchor="mm")
    d.line([(x + 52, y + 58), (x + 64, y + 46), (x + 72, y + 52),
            (x + 86, y + 28)], fill=RED, width=4, joint="curve")
    d.polygon([(x + 88, y + 20), (x + 96, y + 30), (x + 80, y + 32)],
              fill=RED)


def draw_eu(d, x, y, w=92, h=76):
    """Navy tile, ring of gold stars, white columned building."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY, outline=INK, width=2)
    cx, cy, r = x + 46, y + 24, 16
    for i in range(12):
        import math
        a = math.radians(i * 30)
        sx = cx + r * math.cos(a)
        sy = cy + r * math.sin(a)
        d.ellipse([sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5], fill=GOLD)
    # White building: pediment, four columns, base.
    d.polygon([(x + 24, y + 54), (x + 68, y + 54), (x + 46, y + 42)],
              fill=WHITE)
    for col_x in (x + 28, x + 39, x + 50, x + 61):
        d.rectangle([col_x, y + 56, col_x + 5, y + 68], fill=WHITE)
    d.rectangle([x + 22, y + 68, x + 70, y + 72], fill=WHITE)


def draw_map(d, x, y, w=320, h=108):
    """Pale-blue sea, tan continents, red numbered pins."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SEA, outline=INK, width=2)
    for poly in CONTINENTS:
        pts = [(x + px, y + py) for px, py in poly]
        d.polygon(pts, fill=LAND)
    for num, px, py in PINS:
        cx, cy = x + px, y + py
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=WHITE,
                  width=1)
        d.text((cx, cy), str(num), font=sans_b(11), fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- sections

def draw_top_bar(d):
    d.rectangle([0, 0, W - 1, 30], fill=NAVY)
    d.text((MX, 8), "THE WORLD IN ONE DAY", font=sans_b(15), fill=WHITE)
    d.text((RX, 8), "39 STORIES \u2022 6 CONTINENTS \u2022 EVERY ONE DATED",
           font=sans_b(15), fill=WHITE, anchor="ra")


def draw_masthead(d):
    centre(d, W // 2, 42, "Thursday 26 November 2026", serif(50), INK)
    rule(d, 98, 3)
    rule(d, 105, 1)
    centre(d, W // 2, 112,
           "Macy's 100th parade  \u2022  Korea hikes to 3.25%  \u2022  "
           "EU budget battle  \u2022  Tube strike",
           sans_b(17), RED)
    rule(d, 138)


def draw_keynums(d):
    gap = 6
    bw = (CW - 5 * gap) // 6
    y = 147
    for i, (num, label) in enumerate(KEYNUMS):
        x = MX + i * (bw + gap)
        d.rectangle([x, y, x + bw, y + 56], outline=INK, width=1)
        centre(d, x + bw // 2, y + 7, num, serif(34), RED)
        centre(d, x + bw // 2, y + 42, label, sans(11), INK)
    rule(d, 211)


def draw_lead(d):
    d.text((MX, 219), "1  \u2022  TOP STORY  \u2022  UNITED STATES",
           font=sans_b(16), fill=RED)
    draw_balloons(d, MX, 249)
    tx = MX + 250 + 16
    tw = RX - tx
    para(d, tx, 249, LEAD_HEADLINE, serif(38), tw, INK, 41)
    para(d, tx, 335, LEAD_SUMMARY, sans(17), tw, INK, 20)
    para(d, tx, 381, LEAD_WHY, sans_b(16), tw, RED, 17)
    rule(d, 424)


def draw_panels(d):
    for i, p in enumerate(PANELS):
        px = MX + i * (474 + 20)
        d.text((px, 434), "%d  \u2022  %s" % (p["num"], p["region"]),
               font=sans_b(14), fill=RED)
        if p["kind"] == "coin":
            draw_coin(d, px, 456)
        else:
            draw_eu(d, px, 456)
        tx = px + 104
        tw = 370
        para(d, tx, 456, p["headline"], serif(26), tw, INK, 31)
        para(d, tx, 522, p["summary"], sans(14), tw, INK, 17)
        d.text((tx, 576), p["source"], font=sans(11), fill=GREY)
    rule(d, 589)


def draw_grid(d):
    col_w = 309
    col_gap = 20
    row_tops = (598, 692)
    for r, top in enumerate(row_tops):
        for c in range(3):
            num, region, head, summ, src = GRID[r * 3 + c]
            x = MX + c * (col_w + col_gap)
            num_f = serif(16)
            d.text((x, top), str(num), font=num_f, fill=RED)
            nw = d.textlength(str(num), font=num_f)
            d.text((x + nw + 6, top + 4), region, font=sans_b(11), fill=RED)
            para(d, x, top + 24, head, serif(19), col_w, INK, 22)
            para(d, x, top + 68, summ, sans(13), col_w, INK, 16)
            d.text((x, top + 79), src, font=sans(10), fill=GREY)
    rule(d, 786)


def draw_map_also(d):
    d.text((MX, 796), "WHERE IT HAPPENED", font=sans_b(13), fill=INK)
    d.text((364, 796), "ALSO ON THURSDAY 26 NOVEMBER", font=sans_b(14),
           fill=INK)
    draw_map(d, MX, 815)
    col_w = 204
    col_gap = 10
    for i, (num, head) in enumerate(ALSO):
        col = i // 10
        row = i % 10
        x = 364 + col * (col_w + col_gap)
        y = 815 + row * 13
        d.text((x, y), str(num), font=sans_b(11), fill=RED)
        head = trim_to(d, head, sans(11), col_w - 18)
        d.text((x + 18, y), head, font=sans(11), fill=INK)
    rule(d, 947)


def draw_datecheck(d):
    d.rectangle([MX, 954, RX, 1000], outline=RED, width=2)
    prefix = "DATE CHECK \u2014 "
    f_body = sans(12)
    f_pre = sans_b(12)
    first_w = (RX - 10) - (MX + 10) - d.textlength(prefix, font=f_pre)
    rest_w = (RX - 10) - (MX + 10)
    lines = wrap_first(d, DATECHECK_BODY, f_body, first_w, rest_w)
    y = 961
    for i, line in enumerate(lines):
        if i == 0:
            d.text((MX + 10, y), prefix, font=f_pre, fill=INK)
            pw = d.textlength(prefix, font=f_pre)
            d.text((MX + 10 + pw, y), line, font=f_body, fill=INK)
        else:
            d.text((MX + 10, y), line, font=f_body, fill=INK)
        y += 15
    return 1000


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    draw_top_bar(d)
    draw_masthead(d)
    draw_keynums(d)
    draw_lead(d)
    draw_panels(d)
    draw_grid(d)
    draw_map_also(d)
    final_y = draw_datecheck(d)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path)
    print("final y: %d of %d" % (final_y, H))
    print("wrote %s (%d, %d)" % (out_path, W, H))


if __name__ == "__main__":
    main()
