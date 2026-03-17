#!/usr/bin/env python3
"""
2D 动画查看 fdata-fire.h 的切片数据。
默认按“扫描模式”播放：每个动画帧内循环 24 个角度切片。
可用 --theta 固定显示某一个角度切片。
"""
import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation

W, H = 8, 10
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
    return [int(h, 16) for h in hexes]


def build_frames(words):
    """
    根据头文件里的数组维度推导:
    framedata_fire[FRAME][24][8]
    返回 list[FRAME][24][10][8]
    """
    total_words = len(words)
    per_frame = N_THETA * N_COL
    if total_words % per_frame != 0:
        raise SystemExit(f"数据长度 {total_words} 不是 {per_frame} 的整数倍")
    n_frame = total_words // per_frame
    frames = []
    idx = 0
    for _ in range(n_frame):
        thetas = []
        for _ in range(N_THETA):
            cols = [word_to_column_pixels(words[idx + c]) for c in range(N_COL)]
            idx += N_COL
            # [y][x]
            mat = [[cols[x][y] for x in range(W)] for y in range(H)]
            thetas.append(mat)
        frames.append(thetas)
    return frames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=int, default=-1, help="固定角度切片 0..23")
    parser.add_argument("--interval", type=int, default=40, help="帧间隔(ms)")
    args = parser.parse_args()

    header_path = Path(__file__).resolve().parent / "fdata-fire.h"
    words = parse_header(header_path)
    frames = build_frames(words)
    n_frame = len(frames)

    fig, ax = plt.subplots(figsize=(3, 4))
    ax.axis("off")
    ax.set_aspect("equal")

    def get_matrix(f, t):
        return frames[f][t]

    if 0 <= args.theta < N_THETA:
        mat0 = get_matrix(0, args.theta)
        im = ax.imshow([[1 - v for v in row] for row in mat0], cmap="gray", interpolation="nearest", vmin=0, vmax=1)
        ax.set_title(f"fire: theta={args.theta}")

        def update(i):
            f = i % n_frame
            mat = get_matrix(f, args.theta)
            im.set_data([[1 - v for v in row] for row in mat])
            ax.set_title(f"fire: frame={f} theta={args.theta}")
            return [im]
    else:
        # 扫描模式：每帧循环 24 个切片
        mat0 = get_matrix(0, 0)
        im = ax.imshow([[1 - v for v in row] for row in mat0], cmap="gray", interpolation="nearest", vmin=0, vmax=1)
        ax.set_title("fire: scan mode")

        def update(i):
            f = (i // N_THETA) % n_frame
            t = i % N_THETA
            mat = get_matrix(f, t)
            im.set_data([[1 - v for v in row] for row in mat])
            ax.set_title(f"fire: frame={f} theta={t}")
            return [im]

    ani = animation.FuncAnimation(fig, update, interval=args.interval, blit=False, repeat=True)
    plt.show()


if __name__ == "__main__":
    main()
