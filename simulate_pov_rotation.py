"""
模拟旋转 LED 矩阵：左侧为真实 3D 立方体（可鼠标拖动旋转），右侧为 POV 2D 切片动画。
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 立方体 8 个顶点（中心在原点，边长 2）
CUBE_VERTS = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1,  1], [1, -1,  1], [1, 1,  1], [-1, 1,  1],
])
CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

def rotate_y(points, angle_deg):
    a = np.radians(angle_deg)
    c, s = np.cos(a), np.sin(a)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return (R @ points.T).T

def draw_3d_cube(ax, angle_deg=0):
    """在 3D 坐标系中画立方体线框（绕 Y 轴旋转 angle_deg）。"""
    v = rotate_y(CUBE_VERTS.copy(), angle_deg)
    for i, j in CUBE_EDGES:
        ax.plot3D([v[i, 0], v[j, 0]], [v[i, 1], v[j, 1]], [v[i, 2], v[j, 2]],
                  color='#1f77b4', linewidth=2.5)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-1.5, 1.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=20, azim=45)

def project_front_edges(verts_rot):
    out_xy = []
    for i, j in CUBE_EDGES:
        if verts_rot[i, 2] <= 0 and verts_rot[j, 2] <= 0:
            continue
        out_xy.append(((verts_rot[i, 0], verts_rot[i, 1]), (verts_rot[j, 0], verts_rot[j, 1])))
    return out_xy

def rasterize_line(grid, p1, p2, size, thick=2):
    scale = (size - 1) / 2.2
    cx = cy = (size - 1) / 2.0
    x1 = int(round(p1[0] * scale + cx))
    y1 = int(round(-p1[1] * scale + cy))
    x2 = int(round(p2[0] * scale + cx))
    y2 = int(round(-p2[1] * scale + cy))
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    r = thick // 2
    for t in np.linspace(0, 1, int(steps) + 1):
        x = int(round(x1 + t * (x2 - x1)))
        y = int(round(y1 + t * (y2 - y1)))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                u, v = x + dx, y + dy
                if 0 <= u < size and 0 <= v < size:
                    grid[v, u] = 1

def generate_cube_frame(angle_deg, size=64):
    verts = rotate_y(CUBE_VERTS.copy(), angle_deg)
    grid = np.zeros((size, size), dtype=np.float32)
    for (p1, p2) in project_front_edges(verts):
        rasterize_line(grid, p1, p2, size)
    return grid.astype(int)

N_ANGLES = 24
DISPLAY_SIZE = 64

def main():
    fig = plt.figure(figsize=(11, 5))
    # 左：真实 3D 立方体（可鼠标拖动旋转）
    ax3d = fig.add_subplot(121, projection='3d')
    draw_3d_cube(ax3d, 0)
    ax3d.set_title('3D cube (drag to rotate)', fontsize=12)

    # 右：POV 2D 切片动画
    ax2d = fig.add_subplot(122)
    ax2d.set_title('POV LED slice (rotating)', fontsize=12)
    ax2d.axis('off')
    ax2d.set_aspect('equal')
    frames = [generate_cube_frame(i * 360 / N_ANGLES, DISPLAY_SIZE) for i in range(N_ANGLES)]
    im = ax2d.imshow(1 - frames[0], cmap='gray', interpolation='nearest', vmin=0, vmax=1)
    ax2d.set_xlim(0, DISPLAY_SIZE)
    ax2d.set_ylim(DISPLAY_SIZE, 0)

    def update(i):
        angle = i * 360 / N_ANGLES
        ax3d.cla()
        draw_3d_cube(ax3d, angle)
        im.set_data(1 - frames[i % N_ANGLES])
        return [im]

    ani = animation.FuncAnimation(fig, update, frames=N_ANGLES, interval=80, blit=False)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    import sys
    if '--check' in sys.argv:
        # 无 GUI：生成一帧并保存，检查 3D/2D 是否正常
        fig = plt.figure(figsize=(11, 5))
        ax3d = fig.add_subplot(121, projection='3d')
        draw_3d_cube(ax3d, 0)
        ax3d.set_title('3D cube (drag to rotate)', fontsize=12)
        ax2d = fig.add_subplot(122)
        ax2d.set_title('POV LED slice (rotating)', fontsize=12)
        ax2d.axis('off')
        ax2d.set_aspect('equal')
        frame = generate_cube_frame(0, DISPLAY_SIZE)
        ax2d.imshow(1 - frame, cmap='gray', interpolation='nearest', vmin=0, vmax=1)
        ax2d.set_xlim(0, DISPLAY_SIZE)
        ax2d.set_ylim(DISPLAY_SIZE, 0)
        plt.tight_layout()
        out = 'simulate_pov_check.png'
        plt.savefig(out, dpi=100)
        plt.close()
        # 检查 2D 帧是否有线（非全白/全黑）
        n_on = int(np.sum(frame))
        assert frame.shape == (DISPLAY_SIZE, DISPLAY_SIZE), 'frame shape wrong'
        assert 10 < n_on < DISPLAY_SIZE * DISPLAY_SIZE - 10, f'frame too empty or full: n_on={n_on}'
        print(f'OK: saved {out}, 2D frame has {n_on} line pixels')
    else:
        main()
