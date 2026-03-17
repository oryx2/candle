#!/usr/bin/env python3
"""
把 cube_frames/ 下 576 张 8x10 切片图按 POV 顺序循环播放，视觉上呈现旋转的 3D 立方体。
顺序: f00_t00 .. f00_t23, f01_t00 .. f01_t23, ... (每 24 张为一圈，共 24 圈相位)
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

FRAMES_DIR = Path(__file__).resolve().parent / "cube_frames"
# 每张图 8x10，放大倍数便于观看
SCALE = 8
N_FRAME = 24
N_THETA = 24
TOTAL = N_FRAME * N_THETA  # 576


def load_all_frames():
    """按 f00_t00, f00_t01, ..., f23_t23 顺序加载 576 张图，返回 (576, 10, 8) 数组。"""
    out = []
    for f in range(N_FRAME):
        for t in range(N_THETA):
            path = FRAMES_DIR / f"f{f:02d}_t{t:02d}.png"
            if not path.exists():
                raise FileNotFoundError(f"缺少 {path}，请先运行: python3 fdata_to_images.py")
            img = np.array(plt.imread(path))
            if img.ndim == 3:
                img = img[:, :, 0] if img.shape[2] >= 1 else img.mean(axis=2)
            if img.max() > 1:
                img = img.astype(np.float32) / 255.0
            out.append(img)
    return np.stack(out)


def main():
    if not FRAMES_DIR.is_dir():
        print(f"目录不存在: {FRAMES_DIR}")
        print("请先运行: python3 fdata_to_images.py")
        sys.exit(1)

    frames = load_all_frames()
    h, w = frames.shape[1], frames.shape[2]
    # 放大显示
    big_h, big_w = h * SCALE, w * SCALE
    fig, ax = plt.subplots(figsize=(4, 5))
    ax.set_title("POV cube (576 slices)")
    ax.axis("off")
    ax.set_aspect("equal")

    # 用 nearest 保持像素块感，放大后更像 LED
    im = ax.imshow(
        np.kron(frames[0], np.ones((SCALE, SCALE))),
        cmap="gray",
        interpolation="nearest",
        vmin=0,
        vmax=1,
    )
    ax.set_xlim(0, big_w)
    ax.set_ylim(big_h, 0)

    def update(i):
        im.set_data(np.kron(frames[i % TOTAL], np.ones((SCALE, SCALE))))
        return [im]

    # 一周期 = 全部 576 帧，循环播放
    ani = animation.FuncAnimation(
        fig, update, frames=TOTAL, interval=25, blit=True, repeat=True
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
