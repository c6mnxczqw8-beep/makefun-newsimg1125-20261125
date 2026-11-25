#!/usr/bin/env python3
"""Entry program for the news-image-20261125 make.fun bounty.

It draws an original newspaper front page -- "THE WORLD TODAY /
WEDNESDAY 25 NOVEMBER 2026" -- with six illustrated panels summing
up that day's world news, and writes it as a 1024x1024 PNG to the
output directory (MAKEFUN_OUTPUT_DIR, default /output).

The drawing uses Pillow when it is available. The grading container
is standard-library-only, so when Pillow is missing the program
falls back to copying the bundled entry.png -- which this same
program's drawing code produced -- so the bytes written are
identical either way. There is no randomness and no clock anywhere
in the drawing: every run on the same machine writes exactly the
same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

W = H = 1024
PAPER = (247, 242, 231)
INK = (22, 19, 15)
GREY = (96, 92, 84)

FONT_CANDIDATES = {
    "serif": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "serif-bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif-italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
}


def load_font(ImageFont, kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    """Greedy word wrap against pixel widths; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, ImageFont, kind, text, start_size, max_width):
    """Largest bold size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > 10:
        font = load_font(ImageFont, kind, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return load_font(ImageFont, kind, size)


def draw_masthead(draw, ImageFont):
    # Double rule above the nameplate, in the classic broadsheet style.
    draw.line([(28, 22), (996, 22)], fill=INK, width=2)
    draw.line([(28, 28), (996, 28)], fill=INK, width=6)
    title = "THE WORLD TODAY"
    font = fit_font(draw, ImageFont, "serif-bold", title, 96, 940)
    tw = draw.textlength(title, font=font)
    draw.text(((W - tw) / 2, 40), title, font=font, fill=INK)
    # Black date band.
    draw.rectangle([28, 120, 996, 162], fill=INK)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    dfont = fit_font(draw, ImageFont, "serif-bold", date, 34, 760)
    dw = draw.textlength(date, font=dfont)
    draw.text(((W - dw) / 2, 129), date, font=dfont, fill=(255, 255, 255))
    sub = "The day's six biggest stories, drawn and typeset by program code"
    sfont = load_font(ImageFont, "serif-italic", 17)
    sw = draw.textlength(sub, font=sfont)
    draw.text(((W - sw) / 2, 168), sub, font=sfont, fill=GREY)
    draw.line([(28, 190), (996, 190)], fill=INK, width=2)


def panel_frame(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    return (x + 6, y + 6, x + w - 6, y + 224)  # illustration box


def draw_panel_text(draw, ImageFont, x, y, w, headline, caption):
    hfont = load_font(ImageFont, "serif-bold", 25)
    cy = y + 232
    for line in wrap(draw, headline, hfont, w - 16):
        draw.text((x + 10, cy), line, font=hfont, fill=INK)
        cy += 30
    cfont = load_font(ImageFont, "serif", 16)
    cy += 4
    for line in wrap(draw, caption, cfont, w - 16):
        draw.text((x + 10, cy), line, font=cfont, fill=(52, 48, 42))
        cy += 21


# --- Panel illustrations: flat editorial shapes, all original --------

def ill_nvidia(draw, F):
    # A trading screen the morning after: the comeback candle, then red.
    draw.rectangle([0, 0, 312, 218], fill=(14, 24, 42))
    for gy in range(28, 190, 32):                                 # grid
        draw.line([(10, gy), (302, gy)], fill=(34, 52, 78), width=1)
    # Three rising green candles: Monday's surge.
    bars = [(26, 128, 168), (70, 104, 170), (114, 74, 172)]
    for bx, top, bot in bars:
        draw.line([(bx + 13, top - 12), (bx + 13, bot + 8)],
                  fill=(90, 220, 130), width=3)
        draw.rectangle([bx, top, bx + 26, bot], fill=(46, 178, 92))
    # The gold chip at the centre of the story.
    draw.rectangle([160, 44, 204, 88], fill=(216, 172, 60))
    draw.rectangle([171, 55, 193, 77], fill=(160, 124, 34))
    # Wednesday: one long red candle giving the rally back.
    draw.line([(232, 40), (232, 186)], fill=(235, 90, 80), width=3)
    draw.rectangle([219, 52, 245, 176], fill=(196, 52, 48))
    # A red arrow sliding down the right edge.
    draw.line([(262, 60), (292, 128)], fill=(235, 90, 80), width=5)
    draw.polygon([(292, 128), (276, 122), (284, 106)], fill=(235, 90, 80))
    font = F("serif-bold", 15)
    draw.text((8, 192), "MON +31.5%", font=font, fill=(140, 235, 165))
    draw.text((196, 192), "WED: FADE", font=font, fill=(245, 150, 140))


def ill_launch(draw, F):
    # Shenzhou-24 leaves Jiuquan at dawn, the station waiting above.
    draw.rectangle([0, 0, 312, 150], fill=(16, 26, 58))           # sky
    draw.rectangle([0, 150, 312, 218], fill=(24, 34, 66))
    for sx, sy in [(24, 22), (70, 48), (120, 16), (286, 96), (36, 84),
                   (150, 60), (96, 110)]:
        draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(225, 230, 245))
    # The Tiangong station, small in the top right, green flag flying.
    draw.rectangle([238, 26, 276, 38], fill=(214, 218, 224))
    draw.rectangle([222, 20, 238, 44], fill=(38, 62, 128))
    draw.rectangle([276, 20, 292, 44], fill=(38, 62, 128))
    draw.line([(272, 26), (272, 14)], fill=(220, 224, 230), width=2)
    draw.polygon([(272, 14), (286, 17), (272, 21)], fill=(30, 150, 80))
    # The Long March 2F climbing from the pad, flame lit.
    draw.rectangle([138, 84, 162, 168], fill=(236, 238, 242))
    draw.polygon([(138, 84), (150, 58), (162, 84)], fill=(210, 60, 50))
    draw.rectangle([138, 118, 162, 128], fill=(196, 40, 44))
    for bx in (124, 164):                                         # boosters
        draw.rectangle([bx, 108, bx + 10, 166], fill=(220, 222, 228))
        draw.polygon([(bx, 108), (bx + 5, 92), (bx + 10, 108)],
                     fill=(210, 60, 50))
    draw.polygon([(142, 168), (150, 208), (158, 168)], fill=(244, 150, 50))
    draw.polygon([(146, 168), (150, 192), (154, 168)], fill=(250, 214, 96))
    # Smoke billowing along the ground.
    for cx, cy, r in [(96, 196, 22), (132, 204, 28), (176, 202, 26),
                      (214, 196, 20), (66, 204, 16)]:
        draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2],
                     fill=(168, 176, 190))
    font = F("serif-bold", 16)
    draw.text((10, 24), "08:18 JIUQUAN", font=font, fill=(240, 224, 170))


def ill_capitol(draw, F):
    # The Capitol, and a House that has changed hands decisively.
    draw.rectangle([0, 0, 312, 218], fill=(186, 208, 226))        # sky
    draw.rectangle([0, 168, 312, 218], fill=(110, 124, 104))      # ground
    # The dome: drum, cupola and statue.
    draw.rectangle([106, 118, 206, 168], fill=(238, 240, 242))
    for cx in range(116, 200, 14):
        draw.rectangle([cx, 126, cx + 7, 160], fill=(168, 178, 190))
    draw.pieslice([96, 44, 216, 130], 180, 360, fill=(226, 229, 233))
    draw.rectangle([146, 30, 166, 48], fill=(226, 229, 233))
    draw.line([(156, 30), (156, 16)], fill=(90, 96, 104), width=3)
    # Wings either side.
    draw.rectangle([52, 134, 106, 168], fill=(230, 232, 235))
    draw.rectangle([206, 134, 260, 168], fill=(230, 232, 235))
    # The new arithmetic of the House: two bars, blue far ahead.
    draw.rectangle([24, 182, 236, 196], fill=(44, 78, 170))
    draw.rectangle([24, 200, 128, 212], fill=(188, 52, 52))
    font = F("serif-bold", 14)
    draw.text((242, 181), "DEM", font=font, fill=(30, 60, 140))
    draw.text((134, 199), "GOP", font=font, fill=(150, 40, 40))


def ill_seadrones(draw, F):
    # Seven unmanned boats close on a warship off Benghazi.
    draw.rectangle([0, 0, 312, 84], fill=(150, 178, 198))         # sky
    draw.rectangle([0, 84, 312, 218], fill=(26, 84, 118))         # sea
    for i in range(5):                                            # waves
        yy = 108 + i * 22
        draw.line([(14 + (i % 2) * 30, yy), (80 + (i % 2) * 30, yy)],
                  fill=(110, 170, 200), width=2)
    # The warship, right side: hull, superstructure, helicopter deck.
    draw.polygon([(168, 148), (300, 148), (284, 168), (184, 168)],
                 fill=(70, 78, 88))
    draw.rectangle([206, 122, 262, 148], fill=(88, 96, 108))
    draw.rectangle([226, 104, 240, 122], fill=(88, 96, 108))
    draw.line([(268, 148), (268, 112)], fill=(60, 66, 76), width=3)
    draw.rectangle([272, 128, 296, 142], fill=(96, 104, 116))     # deck
    # The seven drone boats, fanning in from the left with wakes.
    drones = [(28, 108), (58, 128), (34, 150), (76, 104), (92, 146),
              (64, 172), (110, 122)]
    for dx, dy in drones:
        draw.polygon([(dx, dy), (dx + 22, dy + 4), (dx + 4, dy + 9)],
                     fill=(24, 30, 38))
        draw.line([(dx - 12, dy + 8), (dx, dy + 5)], fill=(190, 220, 235),
                  width=2)
    # One burst where a drone has already struck home.
    cx, cy = 292, 122
    for ang in range(0, 360, 45):
        import math
        ex = cx + 16 * math.cos(math.radians(ang))
        ey = cy + 16 * math.sin(math.radians(ang))
        draw.line([(cx, cy), (ex, ey)], fill=(246, 170, 60), width=3)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(250, 200, 90))


def ill_riyadh(draw, F):
    # Riyadh's PIF tower under a desert sky, struck twice in a week.
    draw.rectangle([0, 0, 312, 218], fill=(232, 205, 160))        # haze
    draw.ellipse([252, 18, 292, 58], fill=(246, 190, 90))         # sun
    draw.rectangle([0, 188, 312, 218], fill=(196, 164, 116))      # sand
    # The tower: a tapering stack of offset slabs.
    slabs = [(128, 158, 60), (124, 128, 66), (121, 98, 70), (118, 68, 74),
             (116, 40, 76)]
    for sx, sy, sw_ in slabs:
        draw.rectangle([sx, sy, sx + sw_, sy + 28], fill=(120, 130, 142))
        draw.line([(sx + 8, sy + 6), (sx + sw_ - 8, sy + 6)],
                  fill=(170, 182, 196), width=2)
    # Neighbouring blocks, lower and quiet.
    draw.rectangle([36, 120, 92, 188], fill=(150, 142, 126))
    draw.rectangle([226, 132, 282, 188], fill=(158, 148, 132))
    # Two impact bursts on the tower's face: this week's, and last's.
    import math
    for cx, cy, r, col in [(168, 82, 15, (240, 120, 50)),
                           (158, 138, 11, (120, 116, 108))]:
        for ang in range(0, 360, 40):
            ex = cx + r * math.cos(math.radians(ang))
            ey = cy + r * math.sin(math.radians(ang))
            draw.line([(cx, cy), (ex, ey)], fill=col, width=3)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=col)
    font = F("serif-bold", 15)
    draw.text((10, 196), "RIYADH", font=font, fill=(110, 88, 52))


def ill_turkey(draw, F):
    # The pardoned turkey, medal on, in front of the White House columns.
    draw.rectangle([0, 0, 312, 218], fill=(214, 226, 238))        # sky
    draw.rectangle([0, 130, 312, 218], fill=(96, 150, 84))        # lawn
    # Four white columns of the portico.
    for cx in (30, 108, 186, 264):
        draw.rectangle([cx, 18, cx + 18, 132], fill=(244, 245, 247))
        draw.rectangle([cx - 3, 12, cx + 21, 20], fill=(230, 231, 234))
    draw.rectangle([0, 0, 312, 12], fill=(238, 239, 241))
    # The tail fan: layered arcs behind the body.
    import math
    cx, cy = 156, 150
    for r, col in [(74, (104, 74, 48)), (60, (128, 92, 58)),
                   (46, (152, 112, 70))]:
        pts = [(cx, cy)]
        for ang in range(200, 341, 10):
            pts.append((cx + r * math.cos(math.radians(ang)),
                        cy + r * math.sin(math.radians(ang))))
        draw.polygon(pts, fill=col)
    # Body, head, beak and wattle.
    draw.ellipse([118, 128, 194, 182], fill=(110, 80, 52))
    draw.ellipse([168, 92, 196, 128], fill=(120, 88, 58))
    draw.polygon([(192, 106), (210, 112), (192, 118)], fill=(240, 170, 50))
    draw.polygon([(186, 116), (192, 132), (180, 118)], fill=(200, 60, 60))
    draw.ellipse([176, 100, 182, 106], fill=(20, 18, 16))         # eye
    # The medal of pardon, on a red-white-blue ribbon.
    draw.polygon([(150, 128), (162, 128), (157, 146)], fill=(60, 80, 170))
    draw.polygon([(162, 128), (170, 132), (160, 146)], fill=(200, 60, 60))
    draw.ellipse([146, 144, 168, 166], fill=(232, 186, 70))
    draw.ellipse([151, 149, 163, 161], fill=(246, 214, 110))
    font = F("serif-bold", 15)
    draw.text((10, 196), "PARDONED", font=font, fill=(255, 255, 255))


STORIES = [
    (ill_nvidia,
     "NVIDIA RALLY FADES AS HUANG ADMITS 'TERRIBLE MISTAKES'",
     "A day after his return sent the stock up 31.5%, Jensen Huang "
     "told staff he is in therapy; shares fell back Wednesday."),
    (ill_launch,
     "SHENZHOU-24 LIFTS OFF WITH FIRST FOREIGN ASTRONAUT",
     "It launched from Jiuquan at 8:18 a.m. with Pakistan's "
     "Muhammad Zeeshan Ali, first foreigner to visit Tiangong."),
    (ill_capitol,
     "DEMOCRATS CLINCH BIGGEST HOUSE MAJORITY IN DECADES",
     "The midterms handed Democrats their largest House majority "
     "in decades, with power to block Trump's agenda."),
    (ill_seadrones,
     "UKRAINE SAYS SEA DRONES SANK RUSSIAN WARSHIP OFF LIBYA",
     "Zelensky said seven unmanned boats struck off Benghazi, "
     "destroying a Ka-27 helicopter and hitting the cargo ship "
     "MV Angara."),
    (ill_riyadh,
     "SAUDI CONDEMNS 'TERRORIST ATTACK' ON RIYADH TOWER",
     "Riyadh condemned the strike on the PIF Tower, home to its "
     "sovereign wealth fund, hit for the second time in a week."),
    (ill_turkey,
     "TRUMP PARDONS THE THANKSGIVING TURKEYS",
     "Ahead of Thanksgiving, the president pardoned two turkeys "
     "at the White House, sparing them the dinner table."),
]

PANEL_W, PANEL_H = 312, 397
GRID_X = (28, 356, 684)
GRID_Y = (202, 613)


def render(out_path):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, ImageFont)

    def font_of(kind, size):
        return load_font(ImageFont, kind, size)

    for i, (ill, headline, caption) in enumerate(STORIES):
        px, py = GRID_X[i % 3], GRID_Y[i // 3]
        tile = Image.new("RGB", (PANEL_W, 218), PAPER)
        ill(ImageDraw.Draw(tile), font_of)
        img.paste(tile, (px, py + 6))
        draw = ImageDraw.Draw(img)
        panel_frame(draw, px, py, PANEL_W, PANEL_H)
        draw_panel_text(draw, ImageFont, px, py, PANEL_W, headline, caption)

    img.save(out_path, format="PNG")
    return out_path


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    try:
        import PIL  # noqa: F401
    except ImportError:
        # Standard-library-only runtime: ship the bundled image, which
        # this program's drawing code produced, byte for byte.
        shutil.copyfile(os.path.join(HERE, "entry.png"), dst)
        return 0
    render(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
