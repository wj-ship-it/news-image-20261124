#!/usr/bin/env python3
"""Render news-frontpage.png: a newspaper front page summing up
24 November 2026 world news. Pure PIL, no network."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 48
CONTENT_W = W - 2 * MARGIN

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

INK = (18, 18, 18)
GREY = (90, 90, 90)
PAPER = (250, 248, 240)

STORIES = [
    ("HUANG ADMITS 'TERRIBLE MISTAKES' AS NVIDIA COMEBACK FADES",
     "Reinstated CEO tells staff he is in therapy a day after returning to lead Nvidia."),
    ("ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF IN GAZA CITY",
     "Naeem Abu Nahal and two policemen among the dead despite the ceasefire in place."),
    ("RUSSIAN STRIKE HITS ZAPORIZHZHIA FLAT: 2 DEAD, 40 WOUNDED",
     "Overnight attack wounds four children; apartment block struck, governor says."),
    ("IRAN VOWS TO FIGHT US NAVAL BLOCKADE 'WITH ALL TOOLS'",
     "Vance and Rubio meet Qatar's prime minister at the White House as tensions rise."),
    ("NATO VOWS TO DEFEND SPACE AFTER NUCLEAR SATELLITE REPORTS",
     "Alliance chief responds to reports Russia is preparing a nuclear-armed satellite launch."),
    ("CROWDSTRIKE BUYS ZSCALER IN $43.9 BILLION DEAL",
     "Cybersecurity giants combine in one of the year's biggest tech takeovers."),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns list of lines that all fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, path, start_size, max_width, max_lines, min_size=14):
    """Shrink the font until the wrapped text fits max_width and max_lines."""
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_width)


def draw_tracked(draw, cx, y, text, fnt, fill, tracking=4):
    """Draw text centred on cx with extra letter spacing."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def draw_block(draw, x, y, width, headline, summary,
               head_size, sum_size, head_lines, sum_lines, align="left"):
    """Draw one story block; returns the y just below the block."""
    head_fnt, head_wrapped = fit(draw, headline, SANS_BOLD, head_size,
                                 width, head_lines)
    sum_fnt, sum_wrapped = fit(draw, summary, SANS, sum_size,
                               width, sum_lines)
    cy = y
    lh = int(head_fnt.size * 1.18)
    for line in head_wrapped:
        if align == "center":
            tw = draw.textlength(line, font=head_fnt)
            draw.text((x + (width - tw) / 2, cy), line, font=head_fnt, fill=INK)
        else:
            draw.text((x, cy), line, font=head_fnt, fill=INK)
        cy += lh
    cy += 8
    slh = int(sum_fnt.size * 1.30)
    for line in sum_wrapped:
        if align == "center":
            tw = draw.textlength(line, font=sum_fnt)
            draw.text((x + (width - tw) / 2, cy), line, font=sum_fnt, fill=GREY)
        else:
            draw.text((x, cy), line, font=sum_fnt, fill=GREY)
        cy += slh
    return cy


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Thin frame around the page.
    draw.rectangle([18, 18, W - 19, H - 19], outline=INK, width=2)

    # ---- Masthead ----
    mast_fnt = font(SERIF_BOLD, 116)
    title = "THE WORLD"
    tw = draw.textlength(title, font=mast_fnt)
    draw.text(((W - tw) / 2, 30), title, font=mast_fnt, fill=INK)

    date_fnt = font(SANS, 25)
    draw_tracked(draw, W / 2, 168, "TUESDAY 24 NOVEMBER 2026",
                 date_fnt, GREY, tracking=5)

    # Thick rule + thin rule under the dateline.
    draw.rectangle([MARGIN, 214, W - MARGIN, 219], fill=INK)
    draw.rectangle([MARGIN, 226, W - MARGIN, 228], fill=INK)

    # ---- Lead story (full width) ----
    lead_y = 248
    lead_bottom = draw_block(
        draw, MARGIN, lead_y, CONTENT_W,
        STORIES[0][0], STORIES[0][1],
        head_size=40, sum_size=23, head_lines=2, sum_lines=2,
        align="center")

    # Rule under the lead story.
    rule_y = lead_bottom + 18
    draw.rectangle([MARGIN, rule_y, W - MARGIN, rule_y + 2], fill=INK)

    # ---- Grid: five stories, 2 cols x 2 rows + last one full width ----
    grid_top = rule_y + 26
    grid_bottom = 960
    col_gap = 36
    col_w = (CONTENT_W - col_gap) // 2
    row_gap = 22
    rows = 3
    row_h = (grid_bottom - grid_top - (rows - 1) * row_gap) // rows

    cells = [
        (MARGIN, grid_top, col_w),                                  # story 2
        (MARGIN + col_w + col_gap, grid_top, col_w),                # story 3
        (MARGIN, grid_top + row_h + row_gap, col_w),                # story 4
        (MARGIN + col_w + col_gap, grid_top + row_h + row_gap, col_w),  # story 5
        (MARGIN, grid_top + 2 * (row_h + row_gap), CONTENT_W),      # story 6
    ]
    for (cx, cy, cw), (headline, summary) in zip(cells, STORIES[1:]):
        draw_block(draw, cx, cy, cw, headline, summary,
                   head_size=27, sum_size=20, head_lines=3, sum_lines=3)

    # Horizontal rules between grid rows (clear of the text above/below).
    for r in (1, 2):
        ry = grid_top + r * row_h + (r - 1) * row_gap + row_gap // 2
        draw.line([MARGIN, ry, W - MARGIN, ry], fill=(170, 170, 165), width=1)
    # Vertical divider between the two columns, rows 1-2 only.
    vx = MARGIN + col_w + col_gap // 2
    draw.line([vx, grid_top + 6, vx, grid_top + 2 * row_h + row_gap - 6],
              fill=(170, 170, 165), width=1)

    # ---- Footer ----
    foot_fnt = font(SANS, 15)
    footer = "THE WORLD  ·  TUESDAY 24 NOVEMBER 2026  ·  SIX STORIES, ONE PAGE"
    fw = draw.textlength(footer, font=foot_fnt)
    draw.text(((W - fw) / 2, 968), footer, font=foot_fnt, fill=GREY)

    img.save("news-frontpage.png", optimize=True)
    print("wrote news-frontpage.png", img.size, img.mode)


if __name__ == "__main__":
    main()
