#!/usr/bin/env python3
"""
显示单圈 24 个切片（8x10）的静态网格图。
默认读取 fdata-cube-rotate.h 的第 0 帧（frame=0）。
"""
import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt

W, H = 8, 10
N_FRAME = 24
N_THETA = 24
N_COL = 8


def word_to_column_pixels(word):
    """将一个 uint32 word 解码为一列 10 个像素（0=灭 1=亮）。"""
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
    """从 .h 文件里按顺序提取所有 0xXXXXXXXX，返回 list[int]。"""
    text = Path(path).read_text()
    hexes = re.findall(r"0x[0-9A-Fa-f]+", text)
    n = N_FRAME * N_THETA * N_COL
    if len(hexes) < n:
        raise SystemExit(f"期望至少 {n} 个十六进制数，得到 {len(hexes)}")
    return [int(h, 16) for h in hexes[:n]]


def slice_matrix(words, frame_idx, theta_idx):
    """返回 10x8 的切片矩阵（0/1）。"""
    base = frame_idx * N_THETA * N_COL + theta_idx * N_COL
    cols = [word_to_column_pixels(words[base + c]) for c in range(N_COL)]
    # [y][x]
    return [[cols[x][y] for x in range(W)] for y in range(H)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", type=int, default=0, help="0-23")
    parser.add_argument("--out", type=str, default="", help="输出 PNG 路径（不填则弹窗）")
    args = parser.parse_args()

    if not (0 <= args.frame < N_FRAME):
        raise SystemExit("frame 必须在 0..23")

    header_path = Path(__file__).resolve().parent / "fdata-cube-rotate.h"
    words = parse_header(header_path)

    rows, cols = 4, 6  # 24 切片
    fig, axes = plt.subplots(rows, cols, figsize=(10, 7))
    fig.suptitle(f"POV one revolution (frame {args.frame})")

    for t in range(N_THETA):
        r, c = divmod(t, cols)
        ax = axes[r][c]
        mat = slice_matrix(words, args.frame, t)
        ax.imshow([[1 - v for v in row] for row in mat], cmap="gray", interpolation="nearest", vmin=0, vmax=1)
        ax.set_title(f"t={t}", fontsize=8)
        ax.axis("off")

    plt.tight_layout()
    if args.out:
        plt.savefig(args.out, dpi=150)
        print(f"saved: {args.out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
