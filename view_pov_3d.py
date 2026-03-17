#!/usr/bin/env python3
"""
把 24 角度切片合成 3D 点云，直观看到 POV 的 3D 形状。
数据来源: fdata-cube-rotate.h
"""
import argparse
import math
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


def frame_points(words, frame_idx, n_frame):
    """返回该帧的 3D 点云 (x, y, z)."""
    pts = []
    for t in range(N_THETA):
        theta = 2 * math.pi * t / N_THETA
        ct, st = math.cos(theta), math.sin(theta)
        base = frame_idx * N_THETA * N_COL + t * N_COL
        for c in range(N_COL):
            col = word_to_column_pixels(words[base + c])
            r = c + 1  # 半径 1..8
            x = r * ct
            y = r * st
            for y_idx in range(H):
                if col[y_idx]:
                    z = y_idx - (H - 1) / 2.0
                    pts.append((x, y, z))
    return pts


def setup_axes(ax):
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1, 1, 0.7])
    lim = N_COL + 1
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-(H / 2), H / 2)
    ax.view_init(elev=18, azim=45)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", type=int, default=0, help="0-23，静态显示该帧")
    parser.add_argument("--animate", action="store_true", help="动画播放 24 帧")
    parser.add_argument(
        "--integrate",
        type=int,
        default=1,
        help="时间积分窗口（帧数），1=不积分",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="cube",
        choices=["cube", "fire", "liquid", "sparkle", "wave"],
        help="选择数据源",
    )
    args = parser.parse_args()

    data_map = {
        "cube": "fdata-cube-rotate.h",
        "fire": "fdata-fire.h",
        "liquid": "fdata-liquid.h",
        "sparkle": "fdata-sparkle.h",
        "wave": "fdata-wave.h",
    }
    header_path = Path(__file__).resolve().parent / data_map[args.data]
    words = parse_header(header_path)
    per_frame = N_THETA * N_COL
    if len(words) % per_frame != 0:
        raise SystemExit(f"数据长度 {len(words)} 不是 {per_frame} 的整数倍")
    n_frame = len(words) // per_frame

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    setup_axes(ax)

    def draw_frame(idx, integrate_n=1):
        ax.cla()
        setup_axes(ax)
        pts = []
        for k in range(integrate_n):
            fi = (idx - k) % n_frame
            pts.extend(frame_points(words, fi, n_frame))
        if not pts:
            return []
        xs, ys, zs = zip(*pts)
        return ax.scatter(xs, ys, zs, s=18, c="#1f77b4", depthshade=True)

    if args.animate:
        def update(i):
            draw_frame(i % n_frame, integrate_n=max(1, args.integrate))
            if args.integrate > 1:
                ax.set_title(f"POV 3D ({args.data}) frame {i % n_frame}, integrate {args.integrate}")
            else:
                ax.set_title(f"POV 3D ({args.data}) frame {i % n_frame}")
            return []
        # Keep a reference to avoid garbage collection stopping the animation.
        ani = animation.FuncAnimation(fig, update, frames=n_frame, interval=120, blit=False, repeat=True)
        plt.show()
    else:
        if not (0 <= args.frame < n_frame):
            raise SystemExit(f"frame 必须在 0..{n_frame - 1}")
        draw_frame(args.frame, integrate_n=max(1, args.integrate))
        if args.integrate > 1:
            ax.set_title(f"POV 3D ({args.data}) frame {args.frame}, integrate {args.integrate}")
        else:
            ax.set_title(f"POV 3D ({args.data}) frame {args.frame}")
        plt.show()


if __name__ == "__main__":
    main()
