#!/usr/bin/env python3
"""
从 fdata-cube-rotate.h 逆向出 576 张 8x10 的切片图（与 convert.py 输入格式一致）。
用法: python3 fdata_to_images.py [输出目录]
默认输出到 ./cube_frames/
"""
import re
import sys
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("需要 PIL: pip install Pillow")
    sys.exit(1)

# 与 convert.py 一致：8 列 x 10 行
W, H = 8, 10

def word_to_column_pixels(word):
    """将一个 uint32 word 解码为一列 10 个像素（0=灭 1=亮）。convert 里清零表示亮。"""
    col = [0] * H
    for y in range(H):
        if y <= 7:
            bit = (word >> (y + 8)) & 1
        elif y == 8:
            bit = (word >> 16) & 1
        else:
            bit = (word >> 26) & 1
        if bit == 0:
            col[y] = 1
    return col

def parse_header(path):
    """从 .h 文件里按顺序提取所有 0xXXXXXXXX，返回 (24, 24, 8) 的列表。"""
    with open(path, "r") as f:
        text = f.read()
    hexes = re.findall(r"0x[0-9A-Fa-f]+", text)
    n = 24 * 24 * 8
    if len(hexes) < n:
        raise SystemExit(f"期望至少 {n} 个十六进制数，得到 {len(hexes)}")
    words = [int(h, 16) for h in hexes[:n]]
    # 形状: [anim_frame][theta][col]
    return [
        [[words[f * 24 * 8 + t * 8 + c] for c in range(8)] for t in range(24)]
        for f in range(24)
    ]

def main():
    script_dir = Path(__file__).resolve().parent
    header_path = script_dir / "fdata-cube-rotate.h"
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir / "cube_frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = parse_header(header_path)
    count = 0
    for f in range(24):
        for t in range(24):
            # 一张图: 8 列 x 10 行，每列一个 word
            pixels = []
            for c in range(8):
                pixels.append(word_to_column_pixels(data[f][t][c]))
            # pixels[c][y] -> 图像 [y][c]，PIL 用 (width, height) = (8, 10)
            img_arr = [[pixels[c][y] for c in range(8)] for y in range(10)]
            flat = [img_arr[y][x] for y in range(10) for x in range(8)]
            # 转成 0/255 灰度
            gray = [(255 if p else 0) for p in flat]
            im = Image.new("L", (W, H))
            im.putdata(gray)
            name = f"f{f:02d}_t{t:02d}.png"
            im.save(out_dir / name)
            count += 1
    print(f"已写出 {count} 张图到 {out_dir}")

if __name__ == "__main__":
    main()
