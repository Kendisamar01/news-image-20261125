import math
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (244, 238, 222)
PAPER_SHADE = (231, 223, 203)
INK = (24, 23, 21)
RED = (166, 35, 32)

FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10011", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "00000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ",": ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ";": ("00000", "00100", "00000", "00000", "00000", "00100", "01000"),
    ":": ("00000", "00100", "00100", "00000", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def blank():
    buf = bytearray(PAPER * (W * H))
    seed = 20261125
    for _ in range(4200):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        px = seed % W
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        py = seed % H
        set_pixel(buf, px, py, PAPER_SHADE)
    return buf


def set_pixel(buf, x, y, color):
    x = int(x)
    y = int(y)
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_rect(buf, x, y, w, h, color):
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(W, int(x + w))
    y1 = min(H, int(y + h))
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        start = (yy * W + x0) * 3
        buf[start:start + len(row)] = row


def draw_line(buf, x1, y1, x2, y2, color):
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        set_pixel(buf, x1, y1, color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy


def dashed_line(buf, x1, y1, x2, y2, color, dash=5):
    steps = max(abs(int(x2) - int(x1)), abs(int(y2) - int(y1)), 1)
    for i in range(steps + 1):
        if (i // dash) % 2 == 0:
            t = i / steps
            set_pixel(buf, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, color)


def polygon(buf, points, color):
    ys = [p[1] for p in points]
    for yy in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        scan = yy + 0.5
        xs = []
        for i in range(len(points)):
            ax, ay = points[i]
            bx, by = points[(i + 1) % len(points)]
            if ay == by:
                continue
            if (ay <= scan < by) or (by <= scan < ay):
                xs.append(ax + (scan - ay) * (bx - ax) / (by - ay))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            fill_rect(buf, math.ceil(xs[k]), yy, max(1, int(xs[k + 1] - math.ceil(xs[k])) + 1), 1, color)


def disc(buf, cx, cy, r, color):
    for yy in range(int(cy - r), int(cy + r) + 1):
        dy = yy - cy
        span = math.sqrt(max(0.0, r * r - dy * dy))
        fill_rect(buf, cx - span, yy, 2 * span + 1, 1, color)


def spacing_for(scale):
    return max(1, scale // 2)


def text_width(text, scale, spacing=None):
    if not text:
        return 0
    gap = spacing if spacing is not None else spacing_for(scale)
    return len(text) * (5 * scale + gap) - gap


def draw_text(buf, text, x, y, scale, color, spacing=None):
    gap = spacing if spacing is not None else spacing_for(scale)
    cx = int(x)
    for char in text.upper():
        glyph = FONT.get(char, FONT["?"])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    fill_rect(buf, cx + gx * scale, y + gy * scale, scale, scale, color)
        cx += 5 * scale + gap


def centered_text(buf, text, y, scale, color, spacing=None):
    draw_text(buf, text, (W - text_width(text, scale, spacing)) // 2, y, scale, color, spacing)


def rule(buf, x1, y1, x2, y2, color, thick=1):
    if y1 == y2:
        fill_rect(buf, x1, y1, x2 - x1 + 1, thick, color)
    else:
        fill_rect(buf, x1, y1, thick, y2 - y1 + 1, color)


def label_tab(buf, text, x, y):
    w = text_width(text, 2) + 18
    fill_rect(buf, x, y, w, 20, RED)
    draw_text(buf, text, x + 9, y + 3, 2, PAPER)


def oil_drop(buf, cx, cy, r, color=RED):
    polygon(buf, [
        (cx, cy - r),
        (cx + r * 0.72, cy + r * 0.15),
        (cx + r * 0.5, cy + r * 0.7),
        (cx, cy + r),
        (cx - r * 0.5, cy + r * 0.7),
        (cx - r * 0.72, cy + r * 0.15),
    ], color)
    fill_rect(buf, cx - 1, cy - r + 2, 2, 4, PAPER)


def wave_line(buf, x, y, width, color=INK):
    prev = None
    for dx in range(0, width + 1, 4):
        py = y + int(2 * math.sin(dx / 17.0))
        if prev is not None:
            draw_line(buf, prev[0], prev[1], x + dx, py, color)
        prev = (x + dx, py)


def burst(buf, cx, cy, r, color=RED):
    for a in range(8):
        ang = a * math.pi / 4
        draw_line(buf, cx + math.cos(ang) * r * 0.45, cy + math.sin(ang) * r * 0.45,
                  cx + math.cos(ang) * r, cy + math.sin(ang) * r, color)


def tanker(buf, x, y, w, h):
    for k in range(3):
        wave_line(buf, x, y + h - 12 + k * 5, w, INK)
    polygon(buf, [
        (x + 10, y + h - 36),
        (x + w - 12, y + h - 36),
        (x + w - 24, y + h - 12),
        (x + 4, y + h - 12),
    ], INK)
    fill_rect(buf, x + 16, y + h - 40, w - 32, 4, INK)
    for k in range(3):
        tx = x + 28 + k * 34
        fill_rect(buf, tx, y + h - 58, 28, 18, INK)
        fill_rect(buf, tx + 3, y + h - 55, 22, 9, PAPER)
    fill_rect(buf, x + w - 50, y + h - 68, 22, 30, INK)
    fill_rect(buf, x + w - 46, y + h - 64, 14, 6, PAPER)
    draw_line(buf, x + w - 39, y + h - 84, x + w - 39, y + h - 68, INK)
    polygon(buf, [
        (x + w - 39, y + h - 84),
        (x + w - 20, y + h - 79),
        (x + w - 39, y + h - 74),
    ], RED)
    burst(buf, x + 63, y + h - 50, 15)
    burst(buf, x + w - 62, y + h - 50, 11)
    oil_drop(buf, x + 20, y + 17, 13)
    draw_text(buf, "OIL", x + 42, y + 10, 2, RED, 2)


def drone_intercept(buf, x, y, w, h):
    cx = x + w - 44
    cy = y + h // 2
    dashed_line(buf, x + 6, y + 8, cx - 12, cy, RED, 4)
    draw_line(buf, cx - 34, cy - 18, cx + 34, cy + 18, INK)
    draw_line(buf, cx - 34, cy + 18, cx + 34, cy - 18, INK)
    fill_rect(buf, cx - 9, cy - 6, 18, 12, INK)
    for rx, ry in ((cx - 34, cy - 18), (cx + 34, cy - 18), (cx - 34, cy + 18), (cx + 34, cy + 18)):
        disc(buf, rx, ry, 7, INK)
        draw_line(buf, rx - 9, ry, rx + 9, ry, INK)
    burst(buf, cx, cy, 14)


def flags_refinery(buf, x, y, w, h):
    draw_line(buf, x + 2, y + 2, x + 2, y + h - 2, INK)
    draw_line(buf, x + 62, y + 2, x + 62, y + h - 2, INK)
    for k in range(3):
        fill_rect(buf, x + 6, y + 4 + k * 8, 50, 8, PAPER if k == 0 else (INK if k == 2 else RED))
    for k in range(2):
        fill_rect(buf, x + 66, y + 4 + k * 12, 50, 12, (37, 79, 168) if k == 0 else (238, 190, 40))
    rule(buf, x + 6, y + 4, x + 56, y + 28, INK, 1)
    rule(buf, x + 66, y + 4, x + 116, y + 28, INK, 1)
    fill_rect(buf, x + 6, y + 38, 30, 26, INK)
    fill_rect(buf, x + 9, y + 41, 24, 20, PAPER)
    fill_rect(buf, x + 42, y + 46, 26, 18, INK)
    fill_rect(buf, x + 45, y + 49, 20, 12, PAPER)
    fill_rect(buf, x + 76, y + 34, 12, 30, INK)
    fill_rect(buf, x + 96, y + 44, 28, 20, INK)
    draw_line(buf, x + 36, y + 54, x + 76, y + 54, INK)
    draw_line(buf, x + 82, y + 45, x + 96, y + 45, INK)
    burst(buf, x + 89, y + 39, 9)


def icon(buf, kind, x, y):
    if kind == "scale":
        draw_line(buf, x + 14, y + 3, x + 14, y + 27, INK)
        draw_line(buf, x + 3, y + 8, x + 25, y + 8, RED)
        draw_line(buf, x + 3, y + 8, x + 7, y + 18, INK)
        draw_line(buf, x + 25, y + 8, x + 21, y + 18, INK)
        draw_line(buf, x + 2, y + 18, x + 12, y + 18, INK)
        draw_line(buf, x + 16, y + 18, x + 26, y + 18, INK)
    elif kind == "plane":
        polygon(buf, [(x + 2, y + 15), (x + 26, y + 9), (x + 20, y + 15),
                      (x + 26, y + 20), (x + 2, y + 15)], INK)
        draw_line(buf, x + 14, y + 4, x + 14, y + 26, RED)
        draw_line(buf, x + 6, y + 15, x + 22, y + 15, RED)
    elif kind == "trophy":
        polygon(buf, [(x + 6, y + 3), (x + 22, y + 3), (x + 19, y + 16),
                      (x + 9, y + 16)], RED)
        draw_line(buf, x + 14, y + 16, x + 14, y + 23, INK)
        draw_line(buf, x + 8, y + 24, x + 20, y + 24, INK)
        draw_line(buf, x + 6, y + 6, x + 2, y + 5, INK)
        draw_line(buf, x + 22, y + 6, x + 26, y + 5, INK)
    elif kind == "chip":
        fill_rect(buf, x + 7, y + 7, 14, 14, INK)
        fill_rect(buf, x + 10, y + 10, 8, 8, PAPER)
        fill_rect(buf, x + 12, y + 12, 4, 4, RED)
        for k in range(3):
            draw_line(buf, x + 9 + k * 5, y + 2, x + 9 + k * 5, y + 7, INK)
            draw_line(buf, x + 9 + k * 5, y + 21, x + 9 + k * 5, y + 26, INK)
            draw_line(buf, x + 2, y + 9 + k * 5, x + 7, y + 9 + k * 5, INK)
            draw_line(buf, x + 21, y + 9 + k * 5, x + 26, y + 9 + k * 5, INK)
    elif kind == "strike":
        draw_line(buf, x + 19, y + 2, x + 12, y + 15, INK)
        burst(buf, x + 11, y + 18, 10)
        fill_rect(buf, x + 5, y + 25, 16, 2, INK)
    elif kind == "cross":
        disc(buf, x + 14, y + 14, 12, RED)
        fill_rect(buf, x + 12, y + 6, 4, 16, PAPER)
        fill_rect(buf, x + 6, y + 12, 16, 4, PAPER)
    elif kind == "fire":
        polygon(buf, [(x + 14, y + 2), (x + 22, y + 12), (x + 19, y + 21),
                      (x + 14, y + 26), (x + 8, y + 19), (x + 6, y + 11)], RED)
        polygon(buf, [(x + 14, y + 11), (x + 18, y + 18), (x + 14, y + 23),
                      (x + 11, y + 18)], PAPER)
        fill_rect(buf, x + 4, y + 25, 20, 2, INK)


def brief(buf, y, text, lines, kind):
    rule(buf, 700, y, 996, y, INK, 1)
    icon(buf, kind, 708, y + 7)
    draw_text(buf, text, 744, y + 5, 2, RED)
    for k, line in enumerate(lines):
        draw_text(buf, line, 744, y + 23 + k * 18, 2, INK)


def draw_page(buf):
    fill_rect(buf, 0, 0, W, H, PAPER)

    centered_text(buf, "THE WORLD LEDGER", 20, 10, INK, 5)
    draw_text(buf, "NO. 1,208", 32, 60, 2, RED)
    draw_text(buf, "WORLD EDITION", 848, 60, 2, RED)
    rule(buf, 28, 98, 996, 98, INK, 2)
    rule(buf, 28, 104, 996, 104, INK, 1)

    fill_rect(buf, 28, 112, 968, 28, INK)
    centered_text(buf, "WEDNESDAY, NOVEMBER 25, 2026 - WORLD EDITION - NO. 1,208", 119, 2, PAPER)

    fill_rect(buf, 28, 148, 968, 54, RED)
    rule(buf, 28, 148, 996, 150, INK, 2)
    rule(buf, 28, 200, 996, 202, INK, 2)
    centered_text(buf, "WORLD, WEDNESDAY 25 NOVEMBER 2026", 159, 5, PAPER, 3)

    rule(buf, 688, 216, 688, 980, INK, 2)

    label_tab(buf, "STRAIT OF HORMUZ - IRAN", 30, 218)
    for k, line in enumerate(("TWO TANKERS HIT", "MINES IN STRAIT", "OF HORMUZ")):
        draw_text(buf, line, 42, 244 + k * 47, 6, INK, 3)
    for k, line in enumerate((
        "IRAN SAYS ROGUE VESSELS CAUGHT",
        "FIRE ON UNAUTHORIZED ROUTE;",
        "WORLD'S KEY OIL WATERWAY SHAKEN",
    )):
        draw_text(buf, line, 44, 394 + k * 18, 2, RED)
    for k, line in enumerate((
        "EARLY HOURS: IRGC NAVY SAID TWO",
        "SHIPS STRUCK NAVAL MINES WHILE",
        "CROSSING AN UNAUTHORIZED ROUTE.",
        "EXPLOSIONS AND ENGINE-ROOM FIRES",
        "SHUT THE BUSIEST OIL WATERWAY.",
    )):
        draw_text(buf, line, 44, 456 + k * 17, 2, INK)
    tanker(buf, 458, 442, 210, 100)
    rule(buf, 28, 550, 680, 550, INK, 2)

    label_tab(buf, "SAUDI ARABIA - HOUTHIS", 30, 558)
    for k, line in enumerate(("SAUDIS DOWN 4 DRONES", "OVER RAS TANURA")):
        draw_text(buf, line, 42, 584 + k * 29, 4, INK, 2)
    for k, line in enumerate((
        "DAY AFTER HOUTHI ATTACK ON RIYADH",
        "BUSINESS TOWER HURT 11",
    )):
        draw_text(buf, line, 44, 648 + k * 18, 2, RED)
    for k, line in enumerate((
        "COALITION DOWNED FOUR OVER",
        "EASTERN PROVINCE; FIRM REPLY.",
    )):
        draw_text(buf, line, 44, 692 + k * 17, 2, INK)
    drone_intercept(buf, 492, 684, 178, 48)
    rule(buf, 28, 738, 680, 738, INK, 2)

    label_tab(buf, "RUSSIA - UKRAINE", 30, 746)
    for k, line in enumerate(("PUTIN: RETALIATION", "FOR REFINERY ATTACKS", "'INEVITABLE'")):
        draw_text(buf, line, 42, 772 + k * 29, 4, INK, 2)
    for k, line in enumerate((
        "REPLY CERTAIN DESPITE TRUMP PLEA.",
        "ZELENSKYY: UKRAINE HIT SHIP IN",
        "THE GULF OF FINLAND.",
    )):
        draw_text(buf, line, 44, 866 + k * 18, 2, RED)
    for k, line in enumerate((
        "WEEKEND DRONE HIT A CARGO SHIP.",
        "RUSSIAN REFINERIES WERE STRUCK.",
    )):
        draw_text(buf, line, 44, 924 + k * 17, 2, INK)
    flags_refinery(buf, 492, 914, 178, 66)

    fill_rect(buf, 700, 216, 296, 30, RED)
    centered_text(buf, "THE DAY IN BRIEF", 223, 2, PAPER)

    brief(buf, 268, "HUAWEI - BROOKLYN", (
        "CHINA'S FIRM CONVICTED",
        "OF FRAUD; ACQUITTED OF",
        "RACKETEERING PLOT",
    ), "scale")
    brief(buf, 368, "FAA - CHICAGO", (
        "GROUND STOP AT O'HARE",
        "AFTER EQUIPMENT OUTAGE",
        "HALTED FLIGHTS, FAA SAID",
    ), "plane")
    brief(buf, 468, "SPORT - AFCON", (
        "CAS OVERTURNS CAF;",
        "SENEGAL REINSTATED AS",
        "2025 AFRICA CUP CHAMPS",
    ), "trophy")
    brief(buf, 568, "JAPAN - AI", (
        "TOKYO AIMS TO BE NO. 3",
        "AI POWER AFTER THE US",
        "AND CHINA, IT SAID",
    ), "chip")
    brief(buf, 668, "GAZA - AIRSTRIKE", (
        "ISRAELI STRIKE KILLS",
        "FOUR OF ONE FAMILY;",
        "LATEST CEASEFIRE BLOW",
    ), "strike")
    brief(buf, 768, "WHO - CUBA", (
        "WHO SENDS $2M TO CUBA",
        "FOR VACCINE PROGRAMS",
        "AND HOSPITAL EQUIPMENT",
    ), "cross")
    brief(buf, 868, "AUSTRALIA - BUSHFIRE", (
        "ISLAND FIRE OUT OF",
        "CONTROL; WARNING:",
        "IT'S TOO LATE TO LEAVE",
    ), "fire")

    fill_rect(buf, 28, 988, 968, 28, INK)
    centered_text(buf, "THE WORLD LEDGER - ALL NEWS OF WEDNESDAY, 25 NOVEMBER 2026", 995, 2, PAPER)


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def png_bytes(buf):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    buf = blank()
    draw_page(buf)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png_bytes(buf))


if __name__ == "__main__":
    main()
