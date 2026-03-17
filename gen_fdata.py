#!/usr/bin/env python3
"""
Generate fdata .h files from programmatic 24x8 frame bitmaps.
Frame layout: 24 rows, 8 columns. Output: const uint32_t framedata_xxx[N][24][8]
"""
import math
import random
import sys


def pixel_to_word(x, y, on):
    """Encode one pixel at (x,y) into the word for column x at row y. x in 0..7, y in 0..23."""
    word = 0x0401FF00 | (1 << x)
    if on:
        if y == 8:
            word &= ~(1 << 16)
        elif y == 9:
            word &= ~(1 << 26)
        else:
            word &= ~(1 << (y + 8))
    return word


def frame_row_to_line(bitmap_row):
    """bitmap_row: list of 8 bools. Output one line of 8 hex words."""
    words = []
    for x in range(8):
        word = pixel_to_word(x, 0, bitmap_row[x])  # row index passed by caller via bitmap
        words.append(f"0x{word:08X}")
    return "  { " + ", ".join(words) + " },"


def frame_to_c_block(frame, indent=" "):
    """frame: list of 24 rows, each row = list of 8 bools. Output C block for one frame."""
    lines = []
    for y, row in enumerate(frame):
        words = []
        for x in range(8):
            word = pixel_to_word(x, y, row[x])
            words.append(f"0x{word:08X}")
        lines.append(indent + " {" + ", ".join(words) + " },")
    return "\n".join(lines)


def write_fdata_h(filename, name, frames):
    """frames: list of frames, each frame = 24 rows of 8 bools."""
    n_frames = len(frames)
    with open(filename, "w") as f:
        f.write(f"const uint32_t framedata_{name}[{n_frames}][24][8]= {{\n")
        for i, frame in enumerate(frames):
            f.write(" },{\n" if i > 0 else " {\n")
            f.write(frame_to_c_block(frame))
            f.write("\n")
        f.write(" }\n};\n")
    print(f"Wrote {filename}: {n_frames} frames")


# --- Effects ---

def make_frame_wave(phase, amplitude=3, center=12):
    """Sine wave: one frame. phase in 0..2*pi."""
    frame = []
    for y in range(24):
        row = []
        for x in range(8):
            # wave: x is horizontal, wave goes vertically
            wave_y = center + amplitude * math.sin(phase + x * 0.8)
            on = abs(y - wave_y) < 1.2
            row.append(on)
        frame.append(row)
    return frame


def make_frames_wave(n_frames=48):
    phases = [2 * math.pi * i / n_frames for i in range(n_frames)]
    return [make_frame_wave(p) for p in phases]


def make_frame_sparkle(seed=None):
    """Random sparkle: ~15% pixels on."""
    if seed is not None:
        random.seed(seed)
    frame = [[random.random() < 0.15 for _ in range(8)] for _ in range(24)]
    return frame


def make_frames_sparkle(n_frames=60):
    return [make_frame_sparkle(i) for i in range(n_frames)]


def make_frame_breath(phase):
    """Horizontal band that moves up/down (breathing). phase 0..2*pi."""
    center = 12 + 6 * math.sin(phase)
    width = 4 + 2 * math.sin(phase * 2)
    frame = []
    for y in range(24):
        row = []
        d = abs(y - center)
        on = d < width
        for x in range(8):
            row.append(on)
        frame.append(row)
    return frame


def make_frames_breath(n_frames=48):
    phases = [2 * math.pi * i / n_frames for i in range(n_frames)]
    return [make_frame_breath(p) for p in phases]


def make_frame_bounce(phase):
    """Single bright row bouncing. phase 0..2*pi."""
    y = int(11.5 + 10.5 * math.sin(phase))
    y = max(0, min(23, y))
    frame = [[False] * 8 for _ in range(24)]
    for x in range(8):
        frame[y][x] = True
    return frame


def make_frames_bounce(n_frames=32):
    phases = [2 * math.pi * i / n_frames for i in range(n_frames)]
    return [make_frame_bounce(p) for p in phases]


def make_frame_drip(phase):
    """Drops falling: a few columns have a bright pixel falling."""
    frame = [[False] * 8 for _ in range(24)]
    for x in [1, 3, 5, 7]:
        y = int((phase * 24 + x * 3) % 28) - 2
        if 0 <= y < 24:
            frame[y][x] = True
    return frame


def make_frames_drip(n_frames=48):
    phases = [i / n_frames for i in range(n_frames)]
    return [make_frame_drip(p) for p in phases]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gen_fdata.py <effect> [outname]")
        print("  effect: wave | sparkle | breath | bounce | drip")
        sys.exit(1)
    effect = sys.argv[1].lower()
    outname = sys.argv[2] if len(sys.argv) > 2 else effect
    if effect == "wave":
        frames = make_frames_wave()
    elif effect == "sparkle":
        frames = make_frames_sparkle()
    elif effect == "breath":
        frames = make_frames_breath()
    elif effect == "bounce":
        frames = make_frames_bounce()
    elif effect == "drip":
        frames = make_frames_drip()
    else:
        print("Unknown effect:", effect)
        sys.exit(1)
    write_fdata_h(f"fdata-{outname}.h", outname, frames)
