#!/usr/bin/env python3
"""Draw the news-image entry: a one-page newspaper summing up the world news
of Saturday 21 November 2026. 35 stories: 3 illustrated leads, 8 illustrated
secondaries, 24 numbered briefs, a UTC timeline and a DATE CHECK box.

Output: entry.png in this directory (PNG, at most 1 MiB, 1024x1024).
Run: python3 draw_news.py
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 233)
INK = (24, 22, 18)
NAVY = (30, 58, 95)
RED = (176, 32, 32)
GOLD = (200, 150, 40)
MUTED = (110, 105, 95)
LINE = (200, 192, 172)
WHITE = (255, 255, 255)
BLUE = (43, 108, 176)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

REGION_COLORS = {
    "ASIA": (190, 90, 30), "EUROPE": (43, 108, 176), "AMERICAS": (60, 140, 90),
    "AFRICA": (150, 110, 30), "MIDDLE EAST": (150, 60, 120), "OCEANIA": (60, 130, 150),
    "GLOBAL": (120, 60, 160),
}

# (region, topic, headline, summary, source)
LEADS = [
    ("GLOBAL", "CLIMATE", "COP31 slips into second day of overtime",
     "Turkish minister Kurum offers a last-minute text; EU warns 'good deal or no deal at all'.",
     "AP \u00b7 REUTERS"),
    ("EUROPE", "BALTIC", "Russian cargo ship ablaze after drone strike",
     "Sparta II hit in the Gulf of Finland, drifts into Finnish waters; Helsinki warns war is 'spilling over'.",
     "CNN \u00b7 YLE"),
    ("GLOBAL", "SCIENCE", "Riemann hypothesis proof independently verified",
     "Anthropic's Claude helped prove the 166-year-old problem; Lean FRO confirms the 17m-line proof.",
     "LEAN FRO \u00b7 MATHLIB"),
]

SECONDARIES = [
    ("AMERICAS", "CRIME", "Mexico captures FBI most wanted cartel boss",
     "El Chapo Isidro seized in Sinaloa raid; 11 dead in firefight as cartel violence erupts.",
     "AP \u00b7 FBI"),
    ("EUROPE", "UKRAINE WAR", "Missile strike on Kryvyi Rih kills two, wounds 60",
     "Ballistic missile hits Zelenskyy's hometown; a 7-year-old boy and a 20-year-old woman among the dead.",
     "AP"),
    ("AMERICAS", "MARKETS", "Nasdaq erases 2026 gains as tech crash deepens",
     "Nasdaq dives 5.3%, S&P 500 falls into correction; Anthropic -9%, Nvidia -14% on SEC probe.",
     "REUTERS"),
    ("GLOBAL", "CRYPTO", "Bitcoin falls below $58,000, lowest since 2024",
     "Down 54% from its record high; $1.54bn in liquidations hit 262,976 traders in 24 hours.",
     "BACoor"),
    ("EUROPE", "DIPLOMACY", "Zelensky agrees to trilateral peace talks",
     "US proposal for talks with Russia before Christmas, possibly at the G20 summit in Miami.",
     "WASHINGTON POST"),
    ("MIDDLE EAST", "GULF", "Iran strikes Bahrain facility as Hormuz war widens",
     "Iranian attack sets a civilian industrial facility ablaze; oil shipments through Hormuz down 15%.",
     "REUTERS"),
    ("ASIA", "QUAKE", "Magnitude 6.8 earthquake strikes off Timor-Leste",
     "103 km northeast of Lospalos at 143 km depth; USGS issues Green alert, no tsunami threat.",
     "USGS"),
    ("ASIA", "SPORT", "KL Rahul creates history with SENA century quartet",
     "First Indian opener to score Test centuries in all four SENA countries, at Wellington.",
     "PTI"),
]

BRIEFS = [
    ("Nigeria", "Boat capsizes en route to funeral, 24 dead"),
    ("Ohio", "Baby shower shooting leaves 3 dead"),
    ("Rome", "Paolo Bulgari dies at 89, luxury icon"),
    ("Johannesburg", "Mlambo-Ngcuka dies at 71, ex-UN Women chief"),
    ("Taipei", "Taiwan warns Canada on deeper China ties"),
    ("Rome", "Ex-police chief found dead amid inquiry"),
    ("Berlin", "IG Metall calls 23,000 out on Monday strike"),
    ("Copenhagen", "Denmark to expel envoy over murder plot"),
    ("Washington", "Nvidia halts H200 AI chip exports to China"),
    ("Delhi", "Modi opens SCO civilisational talks"),
    ("Helsinki", "Russian helicopter violates Finnish airspace"),
    ("Brussels", "EU and Indonesia sign trade agreements"),
    ("Brussels", "Costa proposes \u20ac1.78tn EU budget for 2028-34"),
    ("Basra", "Power station fire kills 4, injures 35"),
    ("Port-au-Prince", "Salvadoran soldier dies after Haiti blast"),
    ("Paris", "France to seek UNSC meeting on Myanmar"),
    ("Paris", "PSG's Doue suffers serious knee injury"),
    ("Munich", "Kane and Olise injured for Bayern"),
    ("Hong Kong", "Satwik-Chirag exit Hong Kong Open semis"),
    ("Kuala Lumpur", "India U17 qualify for AFC Asian Cup 2027"),
    ("Turin", "Alcaraz to face Zverev in ATP Finals decider"),
    ("Washington", "Trump favours economic squeeze on Iran"),
    ("Washington", "Trump warns Iran of 'very traumatic' outcome"),
    ("New York", "Gold falls below $3,550, lowest in a year"),
]

BRIEF_REGIONS = [
    "AFRICA", "AMERICAS", "EUROPE", "AFRICA",
    "ASIA", "EUROPE", "EUROPE", "EUROPE",
    "AMERICAS", "ASIA", "EUROPE", "EUROPE",
    "EUROPE", "MIDDLE EAST", "AMERICAS", "EUROPE",
    "EUROPE", "EUROPE", "ASIA", "ASIA",
    "EUROPE", "AMERICAS", "AMERICAS", "GLOBAL",
]

TIMELINE = [
    ("OVERNIGHT", "Mexico captures El Chapo Isidro"),
    ("09:42 UTC", "M6.8 quake off Timor-Leste"),
    ("MORNING", "Sparta II ablaze in Gulf of Finland"),
    ("MIDDAY", "Riemann proof verified"),
    ("AFTERNOON", "COP31 enters day 2 of overtime"),
    ("14:00 UTC", "Nasdaq erases 2026 gains"),
    ("EVENING", "Kryvyi Rih toll rises to 60 hurt"),
    ("LATE", "Bitcoin falls below $58,000"),
]


def region_counts():
    counts = {}
    for region, *_ in LEADS + SECONDARIES:
        counts[region] = counts.get(region, 0) + 1
    for r in BRIEF_REGIONS:
        counts[r] = counts.get(r, 0) + 1
    return counts


def text_block(draw, x, y, text, fnt, fill, max_w, line_h, max_lines):
    """Draw wrapped text, return the y just below the last line."""
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=1000) or [""])
    wrapped = []
    for ln in lines:
        while draw.textlength(ln, font=fnt) > max_w and len(ln) > 1:
            cut = len(ln) - 1
            while cut > 0 and draw.textlength(ln[:cut], font=fnt) > max_w:
                cut -= 1
            while cut > 0 and ln[cut] != " ":
                cut -= 1
            wrapped.append(ln[:cut].rstrip())
            ln = ln[cut:].strip()
        wrapped.append(ln)
    wrapped = wrapped[:max_lines]
    for i, ln in enumerate(wrapped):
        draw.text((x, y + i * line_h), ln, font=fnt, fill=fill)
    return y + len(wrapped) * line_h


# ---------- illustrations (all drawn in code) ----------

def illo_cop31_lead(draw, x, y, w, h):
    # COP31 in overtime: empty venue, clock, "NO DEAL" banner
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 80))
    # globe
    draw.ellipse([x + 12, y + 8, x + 72, y + 68], fill=(60, 160, 220))
    draw.ellipse([x + 28, y + 18, x + 52, y + 42], fill=(90, 180, 90))
    # clock showing overtime
    draw.ellipse([x + 88, y + 8, x + 128, y + 48], outline=WHITE, width=3)
    draw.line([(x + 108, y + 28), (x + 108, y + 14)], fill=WHITE, width=2)
    draw.line([(x + 108, y + 28), (x + 120, y + 28)], fill=WHITE, width=2)
    draw.text((x + 140, y + 8), "DAY 2", font=font(SANS_B, 28), fill=WHITE)
    draw.text((x + 140, y + 40), "OF OVERTIME", font=font(SANS_B, 14), fill=(160, 230, 210))
    draw.text((x + 12, y + 78), "ANTALYA \u00b7 KURUM OFFERS LAST-MINUTE TEXT", font=font(SANS_B, 10), fill=(160, 230, 210))
    draw.text((x + 12, y + 96), "EU: 'GOOD DEAL OR NO DEAL'", font=font(SANS_B, 12), fill=GOLD)


def illo_sparta(draw, x, y, w, h):
    # Russian cargo ship Sparta II on fire in the Gulf of Finland
    draw.rectangle([x, y, x + w, y + h], fill=(25, 45, 75))
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(20, 70, 110))
    # cargo ship hull
    draw.rectangle([x + 30, y + h - 62, x + 280, y + h - 34], fill=(140, 140, 150))
    draw.rectangle([x + 30, y + h - 62, x + 280, y + h - 56], fill=(90, 90, 100))
    # containers
    for cx in (50, 90, 130, 170):
        draw.rectangle([x + cx, y + h - 84, x + cx + 32, y + h - 62], fill=(200, 80, 60))
    # bridge
    draw.rectangle([x + 230, y + h - 84, x + 265, y + h - 62], fill=(200, 200, 200))
    # flames
    for fx, fh in [(60, 34), (100, 46), (140, 38), (180, 30)]:
        draw.polygon([(x + fx, y + h - 84), (x + fx + 12, y + h - 84 - fh),
                      (x + fx + 24, y + h - 84)], fill=(255, 150, 30))
        draw.polygon([(x + fx + 6, y + h - 84), (x + fx + 12, y + h - 84 - fh + 14),
                      (x + fx + 18, y + h - 84)], fill=(255, 220, 120))
    # smoke
    for sx, sy, r in [(180, 18, 12), (205, 10, 14), (230, 16, 11)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(90, 90, 100))
    # drones
    draw.text((x + 8, y + 6), "GULF OF FINLAND", font=font(SANS_B, 11), fill=WHITE)
    draw.text((x + 8, y + h - 22), "SPARTA II \u00b7 DRIFTS INTO FINNISH WATERS", font=font(SANS_B, 10), fill=GOLD)


def illo_riemann(draw, x, y, w, h):
    # Riemann hypothesis: zeta function, prime numbers, checkmark
    draw.rectangle([x, y, x + w, y + h], fill=(40, 30, 80))
    # zeta symbol and equation
    draw.text((x + 16, y + 8), "\u03b6(s) = 0", font=font(SERIF_B, 36), fill=WHITE)
    draw.text((x + 16, y + 52), "Re(s) = \u00bd", font=font(SERIF_B, 24), fill=GOLD)
    # prime numbers
    draw.text((x + 16, y + 84), "2  3  5  7  11  13  17  19  23  29", font=font(SANS_B, 11), fill=(180, 180, 220))
    # checkmark in circle
    draw.ellipse([x + w - 70, y + 12, x + w - 12, y + 70], outline=(80, 200, 120), width=4)
    draw.line([(x + w - 58, y + 42), (x + w - 44, y + 56), (x + w - 24, y + 26)],
              fill=(80, 200, 120), width=5)
    draw.text((x + w - 70, y + 76), "VERIFIED", font=font(SANS_B, 11), fill=(80, 200, 120))
    draw.text((x + 16, y + h - 22), "166 YEARS \u00b7 17M LINES OF LEAN", font=font(SANS_B, 10), fill=WHITE)


def illo_cartel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 30, 30))
    # handcuffs
    draw.ellipse([x + 12, y + 12, x + 36, y + 36], outline=(200, 200, 200), width=3)
    draw.ellipse([x + 40, y + 12, x + 64, y + 36], outline=(200, 200, 200), width=3)
    draw.line([(x + 36, y + 24), (x + 40, y + 24)], fill=(200, 200, 200), width=3)
    draw.text((x + 76, y + 6), "CAPTURED", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 76, y + 28), "EL CHAPO ISIDRO", font=font(SANS_B, 10), fill=(230, 160, 160))
    draw.text((x + 76, y + h - 16), "FBI TOP 10 \u00b7 11 DEAD", font=font(SANS_B, 9), fill=(230, 160, 160))


def illo_kryvyi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 20, 20))
    # missile trail
    draw.line([(x + 20, y + 8), (x + 50, y + 40)], fill=(255, 200, 90), width=3)
    draw.ellipse([x + 46, y + 36, x + 54, y + 44], fill=(255, 220, 130))
    # explosion
    draw.ellipse([x + 40, y + 30, x + 70, y + 52], fill=(255, 150, 40))
    draw.ellipse([x + 48, y + 36, x + 62, y + 48], fill=(255, 230, 150))
    draw.text((x + 82, y + 6), "2 DEAD", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 82, y + 28), "60 WOUNDED", font=font(SANS_B, 10), fill=(230, 160, 160))
    draw.text((x + 82, y + h - 16), "KRYVYI RIH \u00b7 ZELENSKYY'S HOME", font=font(SANS_B, 9), fill=(230, 160, 160))


def illo_nasdaq(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 20, 20))
    draw.rectangle([x, y, x + w, y + 20], fill=(40, 12, 12))
    draw.text((x + 8, y + 4), "NASDAQ \u00b7 FRIDAY", font=font(SANS_B, 10), fill=(230, 160, 160))
    pts = [(x + 16, y + 28), (x + 46, y + 26), (x + 76, y + 32), (x + 106, y + 40),
           (x + 136, y + 48)]
    draw.line(pts, fill=RED, width=3)
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 120, 120))
    draw.text((x + 145, y + 24), "-5.3%", font=font(SANS_B, 17), fill=WHITE)
    draw.text((x + 145, y + h - 16), "2026 GAINS ERASED", font=font(SANS_B, 9), fill=(230, 160, 160))


def illo_bitcoin(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 30, 10))
    draw.ellipse([x + 12, y + 8, x + 52, y + 48], fill=(240, 160, 40))
    draw.text((x + 32, y + 12), "B", font=font(SANS_B, 24), fill=WHITE, anchor="ma")
    draw.text((x + 66, y + 6), "$58K", font=font(SANS_B, 20), fill=WHITE)
    draw.text((x + 66, y + 30), "LOWEST SINCE SEP 2024", font=font(SANS_B, 9), fill=(230, 200, 160))
    draw.text((x + 66, y + h - 16), "DOWN 54% FROM RECORD", font=font(SANS_B, 9), fill=(230, 200, 160))


def illo_talks(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 58, 95))
    # three flags / handshake
    draw.rectangle([x + 12, y + 12, x + 36, y + 30], fill=(40, 80, 160))
    draw.rectangle([x + 40, y + 12, x + 64, y + 30], fill=(200, 60, 60))
    draw.rectangle([x + 12, y + 34, x + 64, y + 46], fill=(240, 200, 60))
    draw.text((x + 76, y + 6), "TALKS", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 76, y + 28), "BEFORE CHRISTMAS", font=font(SANS_B, 10), fill=(170, 200, 240))
    draw.text((x + 76, y + h - 16), "US \u00b7 UKRAINE \u00b7 RUSSIA", font=font(SANS_B, 9), fill=(170, 200, 240))


def illo_bahrain(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(80, 40, 20))
    # industrial facility on fire
    draw.rectangle([x + 12, y + 24, x + 64, y + 48], fill=(120, 120, 130))
    draw.rectangle([x + 20, y + 12, x + 28, y + 24], fill=(100, 100, 110))
    draw.polygon([(x + 20, y + 24), (x + 26, y + 8), (x + 32, y + 24)], fill=(255, 150, 30))
    draw.polygon([(x + 40, y + 24), (x + 46, y + 12), (x + 52, y + 24)], fill=(255, 200, 80))
    draw.text((x + 76, y + 6), "STRIKE", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 76, y + 28), "BAHRAIN FACILITY ABLAZE", font=font(SANS_B, 9), fill=(230, 200, 160))
    draw.text((x + 76, y + h - 16), "HORMUZ OIL -15%", font=font(SANS_B, 9), fill=(230, 200, 160))


def illo_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 50, 40))
    # seismograph lines
    draw.line([(x + 12, y + 30), (x + 24, y + 30), (x + 28, y + 14), (x + 32, y + 46),
               (x + 36, y + 22), (x + 40, y + 38), (x + 52, y + 30)], fill=(255, 200, 80), width=2)
    draw.text((x + 66, y + 6), "M6.8", font=font(SANS_B, 22), fill=WHITE)
    draw.text((x + 66, y + 32), "TIMOR-LESTE", font=font(SANS_B, 10), fill=(230, 200, 160))
    draw.text((x + 66, y + h - 16), "NO TSUNAMI THREAT", font=font(SANS_B, 9), fill=(230, 200, 160))


def illo_rahul(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 50))
    # cricket bat + ball
    draw.rounded_rectangle([x + 14, y + 8, x + 40, y + 40], radius=4, fill=(220, 190, 130))
    draw.rectangle([x + 24, y + 40, x + 30, y + 52], fill=(180, 150, 100))
    draw.ellipse([x + 52, y + 14, x + 68, y + 30], fill=RED)
    draw.arc([x + 54, y + 16, x + 66, y + 28], start=90, end=270, fill=WHITE, width=1)
    draw.text((x + 82, y + 6), "SENA 4/4", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 82, y + 28), "RAHUL MAKES HISTORY", font=font(SANS_B, 9), fill=(170, 230, 190))
    draw.text((x + 82, y + h - 16), "FIRST INDIAN OPENER", font=font(SANS_B, 9), fill=(170, 230, 190))


LEAD_ILLOS = [illo_cop31_lead, illo_sparta, illo_riemann]
SEC_ILLOS = [illo_cartel, illo_kryvyi, illo_nasdaq, illo_bitcoin,
             illo_talks, illo_bahrain, illo_quake, illo_rahul]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((8, 6), "THE WORLD IN ONE DAY", font=font(SANS_B, 12), fill=RED)
    d.text((W - 8, 6), "SATURDAY'S NEWS \u00b7 ONE PAGE \u00b7 35 STORIES",
           font=font(SANS_B, 11), fill=MUTED, anchor="ra")
    d.line([(8, 26), (W - 8, 26)], fill=INK, width=2)
    d.text((8, 30), "Saturday 21 November 2026", font=font(SERIF_B, 54), fill=INK)
    # calendar badge
    d.rectangle([W - 66, 30, W - 8, 84], outline=RED, width=2)
    d.text((W - 37, 32), "21", font=font(SANS_B, 26), fill=RED, anchor="ma")
    d.text((W - 37, 62), "NOV", font=font(SANS_B, 12), fill=RED, anchor="ma")
    d.text((8, 92), "COP31 in overtime \u00b7 Russian ship ablaze \u00b7 Riemann hypothesis verified",
           font=font(SERIF, 15), fill=RED)
    d.line([(8, 116), (W - 8, 116)], fill=INK, width=2)

    # ---- region bar
    counts = region_counts()
    total = sum(counts.values())
    assert total == 35, f"story count {total} != 35"
    order = ["ASIA", "EUROPE", "AMERICAS", "AFRICA", "MIDDLE EAST", "OCEANIA", "GLOBAL"]
    x = 8
    for region in order:
        label = f"{region} {counts.get(region, 0)}"
        tw = d.textlength(label, font=font(SANS_B, 10)) + 16
        d.rectangle([x, 118, x + tw, 132], fill=REGION_COLORS[region])
        d.text((x + 8, 119), label, font=font(SANS_B, 10), fill=WHITE)
        x += tw + 2

    # ---- timeline strip (two rows of four)
    d.rectangle([0, 134, W, 172], fill=(235, 230, 215))
    d.text((14, 138), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    for row_i in range(2):
        tx = 130 if row_i == 0 else 14
        ty = 138 if row_i == 0 else 155
        for time, label in TIMELINE[row_i * 4:(row_i + 1) * 4]:
            d.text((tx, ty), time, font=font(SANS_B, 10), fill=RED)
            tw = d.textlength(time, font=font(SANS_B, 10))
            d.text((tx + tw + 5, ty), label, font=font(SANS, 10), fill=INK)
            tx += tw + 5 + d.textlength(label, font=font(SANS, 10)) + 22
    d.line([(0, 172), (W, 172)], fill=LINE, width=1)

    # ---- three leads
    lw = 330
    for i, (region, topic, head, summ, src) in enumerate(LEADS):
        lx = 8 + i * (lw + 4)
        ly = 176
        LEAD_ILLOS[i](d, lx, ly, lw, 120)
        d.text((lx, ly + 124), f"{i + 1}  {region} \u00b7 {topic}",
               font=font(SANS_B, 10), fill=REGION_COLORS[region])
        y = text_block(d, lx, ly + 140, head, font(SERIF_B, 20), INK, lw, 23, max_lines=2)
        text_block(d, lx, y + 2, summ, font(SANS, 12), INK, lw, 15, max_lines=2)
        d.text((lx, 460), src, font=font(SANS_B, 9), fill=MUTED)

    d.line([(8, 468), (W - 8, 468)], fill=INK, width=2)

    # ---- eight secondaries, two rows of four (124px pitch, one-line summaries)
    sw = 248
    for row in range(2):
        for col in range(4):
            i = row * 4 + col
            region, topic, head, summ, src = SECONDARIES[i]
            sx = 8 + col * (sw + 4)
            sy = 472 + row * 124
            SEC_ILLOS[i](d, sx, sy, sw, 58)
            d.text((sx, sy + 62), f"{i + 4}  {region} \u00b7 {topic}",
                   font=font(SANS_B, 9), fill=REGION_COLORS[region])
            y = text_block(d, sx, sy + 76, head, font(SERIF_B, 14), INK, sw, 16, max_lines=2)
            text_block(d, sx, y + 1, summ, font(SANS, 10), MUTED, sw, 13, max_lines=1)

    d.line([(8, 724), (W - 8, 724)], fill=INK, width=2)

    # ---- briefs
    d.text((8, 730), "ALSO ON SATURDAY 21 NOVEMBER", font=font(SANS_B, 12), fill=NAVY)
    bw = 330
    for col in range(3):
        bx = 8 + col * (bw + 6)
        for r in range(8):
            i = col * 8 + r
            place, brief = BRIEFS[i]
            by = 750 + r * 25
            d.text((bx, by), str(12 + i), font=font(SANS_B, 11), fill=REGION_COLORS[BRIEF_REGIONS[i]])
            d.text((bx + 24, by), f"{place}: ", font=font(SANS_B, 11), fill=INK)
            pw = d.textlength(f"{place}: ", font=font(SANS_B, 11))
            text_block(d, bx + 24 + pw, by, brief, font(SANS, 11), INK, bw - 24 - pw, 14, max_lines=1)

    # ---- date check box
    d.rectangle([8, 942, W - 8, 988], outline=RED, width=2)
    d.text((16, 946), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    dc = ("Left out, first reported on Friday 20 November: Russia's Kyiv barrage (400+ drones) \u00b7 Cyclone Akvan's landfall \u00b7 "
          "the Hormuz tanker fire \u00b7 the four-point Shenzhen declaration \u00b7 Anthropic's IPO debut at $83. "
          "Thursday 19 November: the three-way summit itself \u00b7 the ICJ Rohingya judgment \u00b7 GTA VI's launch. "
          "Not yet news on Saturday: COP31's final text (Sun) \u00b7 Kenya's Ebola-free declaration (23 Dec).")
    text_block(d, 16, 962, dc, font(SANS, 10), INK, W - 32, 13, max_lines=2)

    # ---- footer
    d.text((8, 996), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 CNN \u00b7 USGS \u00b7 Lean FRO \u00b7 Mathlib \u00b7 PTI \u00b7 YLE \u00b7 FBI",
           font=font(SANS, 9), fill=MUTED)
    d.text((W - 8, 996), "Reads at three sizes: date and leads at thumbnail size \u00b7 all stories at full size.",
           font=font(SANS, 9), fill=MUTED, anchor="ra")

    img.save("entry.png", "PNG", optimize=True)
    print(f"wrote entry.png, size {img.size}, region counts {counts}")


if __name__ == "__main__":
    main()
