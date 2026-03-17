#!/usr/bin/env python3
"""
LED矩阵仿真程序
模拟8x10 LED矩阵的显示效果
- 8列（阳极）：GPIO 0-7
- 10行（阴极）：GPIO 8-15 (行0-7), GPIO 16 (行8), GPIO 26 (行9)
"""

import sys
import time
import os
import re

# 引脚定义
ANODES = 0x000000FF    # GPIO 0-7 (列)
CATHODES = 0x0401FF00  # GPIO 8-15, 16, 26 (行)

# 字体数据（从 font.h 解析）
FONT_DATA = None

def parse_led_data(value):
    """
    解析32位LED数据值，返回8x10矩阵状态
    返回: matrix[10][8] - True表示LED点亮，False表示关闭
    """
    matrix = [[False] * 8 for _ in range(10)]
    
    # 提取阳极（列选择）- 位0-7
    anode_bits = value & 0xFF
    if anode_bits == 0:
        return matrix  # 没有选中任何列
    
    # 找出选中的列（可能有多个，但通常只有一个）
    selected_cols = []
    for col in range(8):
        if anode_bits & (1 << col):
            selected_cols.append(col)
    
    # 提取阴极状态
    # 行0-7: 位8-15
    for row in range(8):
        gpio_bit = 8 + row
        if not (value & (1 << gpio_bit)):  # 位为0表示LED点亮
            for col in selected_cols:
                matrix[row][col] = True
    
    # 行8: 位16
    if not (value & (1 << 16)):
        for col in selected_cols:
            matrix[8][col] = True
    
    # 行9: 位26
    if not (value & (1 << 26)):
        for col in selected_cols:
            matrix[9][col] = True
    
    return matrix

def display_matrix(matrix, title="LED Matrix"):
    """
    显示8x10 LED矩阵
    """
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    print("  列: 0  1  2  3  4  5  6  7")
    print("  " + "-" * 33)
    
    for row in range(10):
        row_label = f"行{row:2d}"
        row_data = "  "
        for col in range(8):
            if matrix[row][col]:
                row_data += "██ "
            else:
                row_data += "░░ "
        print(f"{row_label} {row_data}")
    
    print(f"{'='*50}\n")

def display_matrix_compact(matrix, title="LED Matrix"):
    """
    紧凑显示（使用字符）
    """
    print(f"\n{title}:")
    print("  0 1 2 3 4 5 6 7")
    for row in range(10):
        row_data = f"{row:2d}"
        for col in range(8):
            row_data += " ●" if matrix[row][col] else " ·"
        print(row_data)
    print()

def simulate_slice(slice_data):
    """
    模拟一个切片（8个数据值，代表8列）
    """
    # 合并所有列的数据
    combined_matrix = [[False] * 8 for _ in range(10)]
    
    for col in range(8):
        if col < len(slice_data):
            value = slice_data[col]
            col_matrix = parse_led_data(value)
            for row in range(10):
                combined_matrix[row][col] = col_matrix[row][col]
    
    return combined_matrix

def demo_single_value():
    """
    演示单个值的解析
    """
    print("\n" + "="*60)
    print("示例1: 解析单个值 0x0401FF01")
    print("="*60)
    value = 0x0401FF01
    print(f"输入值: 0x{value:08X}")
    print("解析:")
    print("  - 阳极: GPIO 0 (列0) 被选中")
    print("  - 阴极: 所有行都是高电平 (LED关闭)")
    matrix = parse_led_data(value)
    display_matrix(matrix, "0x0401FF01")
    
    print("\n" + "="*60)
    print("示例2: 解析单个值 0x00000304")
    print("="*60)
    value = 0x00000304
    print(f"输入值: 0x{value:08X}")
    print("解析:")
    print("  - 阳极: GPIO 2 (列2) 被选中")
    print("  - 阴极: GPIO 10, 11 为低电平 (行2, 3点亮)")
    matrix = parse_led_data(value)
    display_matrix(matrix, "0x00000304")

def demo_slice():
    """
    演示一个完整切片（8列数据）
    """
    print("\n" + "="*60)
    print("示例3: 模拟一个完整切片（8列数据）")
    print("="*60)
    
    # 从fire数据中取第一个切片的8列
    slice_data = [
        0x0401FF01,  # 列0
        0x0401FF02,  # 列1
        0x00000704,  # 列2
        0x00000308,  # 列3
        0x00000310,  # 列4
        0x00000320,  # 列5
        0x0401FF40,  # 列6
        0x0401FF80,  # 列7
    ]
    
    print("切片数据:")
    for i, val in enumerate(slice_data):
        print(f"  列{i}: 0x{val:08X}")
    
    matrix = simulate_slice(slice_data)
    display_matrix(matrix, "完整切片显示")

def interactive_mode():
    """
    交互模式：用户可以输入十六进制值查看效果
    """
    print("\n" + "="*60)
    print("交互模式")
    print("="*60)
    print("输入十六进制值（如 0x0401FF01 或 0401FF01）")
    print("输入 'q' 退出")
    print("输入 'slice' 进入切片模式（输入8个值）")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() == 'q':
                break
            
            if user_input.lower() == 'slice':
                print("\n切片模式：请输入8个十六进制值（每行一个）")
                slice_data = []
                for i in range(8):
                    val_input = input(f"列{i}: ").strip()
                    if val_input.startswith('0x') or val_input.startswith('0X'):
                        val = int(val_input, 16)
                    else:
                        val = int(val_input, 16)
                    slice_data.append(val)
                
                matrix = simulate_slice(slice_data)
                display_matrix(matrix, "切片显示")
                continue
            
            if user_input.lower().startswith('font:'):
                # 字体模式: font:A 或 font:ABC
                text = user_input[5:].strip()
                if len(text) == 1:
                    display_font_char(text)
                else:
                    display_font_string(text)
                continue
            
            if len(user_input) == 1 and ord(user_input) >= ord('!') and ord(user_input) <= ord('~'):
                # 单个字符，显示字体
                display_font_char(user_input)
                continue
            
            # 解析单个值
            if user_input.startswith('0x') or user_input.startswith('0X'):
                value = int(user_input, 16)
            else:
                value = int(user_input, 16)
            
            print(f"\n解析值: 0x{value:08X}")
            
            # 显示详细信息
            anode = value & 0xFF
            cathodes = (value & CATHODES) >> 8
            
            print(f"阳极 (列): ", end="")
            cols = []
            for i in range(8):
                if anode & (1 << i):
                    cols.append(str(i))
            print(", ".join(cols) if cols else "无")
            
            print(f"阴极状态: ", end="")
            rows_off = []
            for row in range(8):
                if not (value & (1 << (8 + row))):
                    rows_off.append(f"行{row}")
            if not (value & (1 << 16)):
                rows_off.append("行8")
            if not (value & (1 << 26)):
                rows_off.append("行9")
            print(", ".join(rows_off) if rows_off else "全部关闭")
            
            matrix = parse_led_data(value)
            display_matrix_compact(matrix, f"0x{value:08X}")
            
        except ValueError:
            print("错误: 无效的十六进制值")
        except KeyboardInterrupt:
            print("\n退出...")
            break
        except Exception as e:
            print(f"错误: {e}")

def load_font_data(filename='font.h'):
    """
    从 font.h 文件加载字体数据
    """
    global FONT_DATA
    if FONT_DATA is not None:
        return FONT_DATA
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # 提取所有十六进制值
        pattern = r'0x([0-9A-Fa-f]{2})'
        matches = re.findall(pattern, content)
        font_bytes = [int(m, 16) for m in matches]
        
        FONT_DATA = font_bytes
        print(f"已加载字体数据: {len(font_bytes)} 字节, {len(font_bytes)//5} 个字符")
        return font_bytes
    except FileNotFoundError:
        print(f"警告: 找不到字体文件 {filename}")
        return None
    except Exception as e:
        print(f"错误: 加载字体文件失败 - {e}")
        return None

def font_char_to_matrix(char, font_data=None):
    """
    将字符转换为8x10 LED矩阵显示
    字符从 '!' (0x21) 开始到 '~' (0x7E)
    每个字符5列，每列8位
    位为0表示点亮LED
    """
    if font_data is None:
        font_data = load_font_data()
        if font_data is None:
            return None
    
    # 检查字符范围
    if ord(char) < ord('!') or ord(char) > ord('~'):
        print(f"错误: 字符 '{char}' 不在支持的范围内 (! 到 ~)")
        return None
    
    # 计算字符在字体数组中的索引
    char_index = ord(char) - ord('!')
    start_index = char_index * 5
    
    if start_index + 5 > len(font_data):
        print(f"错误: 字体数据不足")
        return None
    
    # 创建8x10矩阵（实际使用8x5，因为字符只有5列）
    # 但为了兼容显示，我们创建8x10，字符显示在中间
    matrix = [[False] * 8 for _ in range(10)]
    
    # 读取5列数据
    for col in range(5):
        byte_val = font_data[start_index + col]
        # 每列8位，位为0时点亮
        for row in range(8):
            if (byte_val & (1 << row)) == 0:
                # 字符显示在行1-8（跳过行0和行9）
                matrix[row + 1][col] = True
    
    return matrix

def display_font_char(char, font_data=None):
    """
    显示单个字符
    """
    matrix = font_char_to_matrix(char, font_data)
    if matrix is None:
        return
    
    print(f"\n字符: '{char}' (ASCII: {ord(char)})")
    display_matrix(matrix, f"字符 '{char}'")

def display_font_string(text, font_data=None):
    """
    显示字符串（多个字符横向排列）
    由于矩阵只有8列，每个字符5列，所以最多显示1个字符（5列）+ 间距
    或者显示多个字符但会重叠
    """
    if font_data is None:
        font_data = load_font_data()
        if font_data is None:
            return
    
    # 每个字符5列，矩阵只有8列
    # 可以显示1个完整字符，或者2个字符（会有点重叠）
    max_chars = min(len(text), 2)  # 最多显示2个字符
    display_text = text[:max_chars]
    
    if len(text) > max_chars:
        print(f"注意: 字符串 \"{text}\" 太长，只显示前 {max_chars} 个字符")
    
    # 创建合并矩阵
    combined_matrix = [[False] * 8 for _ in range(10)]
    
    col_offset = 0
    for i, char in enumerate(display_text):
        char_matrix = font_char_to_matrix(char, font_data)
        if char_matrix is None:
            continue
        
        # 复制字符到合并矩阵
        for row in range(10):
            for col in range(5):
                if col_offset + col < 8:
                    combined_matrix[row][col_offset + col] = char_matrix[row][col]
        
        # 如果还有空间，添加1列间距
        if i < len(display_text) - 1 and col_offset + 5 < 8:
            col_offset += 6  # 5列字符 + 1列间距
        else:
            col_offset += 5  # 最后一个字符，不加间距
    
    print(f"\n字符串: \"{text}\" (显示: \"{display_text}\")")
    display_matrix(combined_matrix, f"字符串 \"{display_text}\"")

def demo_font():
    """
    演示字体显示
    """
    print("\n" + "="*60)
    print("字体显示演示")
    print("="*60)
    
    font_data = load_font_data()
    if font_data is None:
        return
    
    # 显示一些示例字符
    demo_chars = ['A', 'B', 'C', '0', '1', '2', '!', '@', '#']
    
    for char in demo_chars:
        display_font_char(char, font_data)
        time.sleep(0.3)
    
    # 显示字符串
    print("\n" + "="*60)
    print("字符串显示示例")
    print("="*60)
    display_font_string("ABC", font_data)
    display_font_string("123", font_data)
    display_font_string("Hi!", font_data)

def animate_slice(slice_data, delay=0.1):
    """
    动画显示一个切片（逐列扫描效果）
    """
    print("\n动画模式：逐列扫描显示")
    print("按Ctrl+C停止\n")
    
    try:
        while True:
            for col in range(8):
                if col < len(slice_data):
                    value = slice_data[col]
                    col_matrix = parse_led_data(value)
                    os.system('clear' if os.name != 'nt' else 'cls')
                    print(f"\n列 {col}: 0x{value:08X}")
                    display_matrix_compact(col_matrix, f"列{col}")
                    time.sleep(delay)
    except KeyboardInterrupt:
        print("\n动画停止")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            demo_single_value()
            demo_slice()
            demo_font()
        elif sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
            interactive_mode()
        elif sys.argv[1] == '--animate' or sys.argv[1] == '-a':
            # 动画模式
            slice_data = [
                0x0401FF01, 0x0401FF02, 0x00000704, 0x00000308,
                0x00000310, 0x00000320, 0x0401FF40, 0x0401FF80,
            ]
            delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
            animate_slice(slice_data, delay)
        elif sys.argv[1] == '--font' or sys.argv[1] == '-f':
            # 字体显示模式
            if len(sys.argv) > 2:
                # 显示指定字符或字符串
                text = sys.argv[2]
                if len(text) == 1:
                    display_font_char(text)
                else:
                    display_font_string(text)
            else:
                demo_font()
        elif sys.argv[1].startswith('--font='):
            # --font=ABC 格式
            text = sys.argv[1].split('=', 1)[1]
            if len(text) == 1:
                display_font_char(text)
            else:
                display_font_string(text)
        else:
            # 解析命令行参数作为十六进制值
            try:
                value = int(sys.argv[1], 16)
                matrix = parse_led_data(value)
                display_matrix(matrix, f"0x{value:08X}")
            except ValueError:
                print("错误: 无效的十六进制值")
    else:
        # 默认运行演示
        demo_single_value()
        demo_slice()
        print("\n提示: 使用 --interactive 或 -i 进入交互模式")
        print("      使用 --demo 查看演示")
        print("      使用 --animate 或 -a 查看动画效果")
        print("      使用 --font 或 -f 查看字体演示")
        print("      使用 --font=字符 显示指定字符")
        print("      直接传入十六进制值查看单个值")

if __name__ == "__main__":
    main()
