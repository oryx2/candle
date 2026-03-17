/*
 * WS2812 RGB LED 测试程序 (Pico Zero 板载LED)
 * 
 * 功能:
 * - 控制GPIO 16上的WS2812 RGB LED
 * - 实现闪烁效果
 * - 支持多种颜色和闪烁模式
 * 
 * 硬件:
 * - Raspberry Pi Pico Zero
 * - 板载WS2812 RGB LED (GPIO 16)
 * 
 * 使用方法:
 * 1. 上传程序到Pico Zero
 * 2. 观察LED闪烁效果
 */

#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "ws2812.pio.h"

// ============================================================================
// GPIO引脚定义
// ============================================================================
#define WS2812_PIN 16 // WS2812 LED引脚 (Pico Zero板载LED)

// ============================================================================
// WS2812参数
// ============================================================================
#define NUM_PIXELS 1        // LED数量 (板载只有1个)
#define PIO_FREQ 800000     // PIO频率: 800kHz (WS2812需要800kHz)
#define IS_RGBW false        // 是否为RGBW (false表示RGB)

// ============================================================================
// 颜色定义 (RGB格式，24位)
// ============================================================================
#define COLOR_BLACK   0x000000  // 黑色 (关闭)
#define COLOR_RED     0xFF0000  // 红色
#define COLOR_GREEN   0x00FF00  // 绿色
#define COLOR_BLUE    0x0000FF  // 蓝色
#define COLOR_YELLOW  0xFFFF00  // 黄色
#define COLOR_CYAN    0x00FFFF  // 青色
#define COLOR_MAGENTA 0xFF00FF  // 洋红色
#define COLOR_WHITE   0xFFFFFF  // 白色

// ============================================================================
// 全局变量
// ============================================================================
static PIO pio = pio0;           // 使用PIO0
static uint sm = 0;               // 状态机编号
static uint offset;               // PIO程序偏移量

// ============================================================================
// 函数: ws2812_init
// 功能: 初始化WS2812 PIO程序
// ============================================================================
void ws2812_init(void) {
    // 加载PIO程序
    offset = pio_add_program(pio, &ws2812_program);
    
    // 初始化PIO状态机
    ws2812_program_init(pio, sm, offset, WS2812_PIN, PIO_FREQ, IS_RGBW);
}

// ============================================================================
// 函数: set_pixel_color
// 功能: 设置LED颜色
// 参数: color - RGB颜色值 (24位，格式: 0xRRGGBB)
// ============================================================================
void set_pixel_color(uint32_t color) {
    // WS2812需要GRB格式，但PIO程序会自动处理RGB格式
    // 将24位RGB颜色值写入PIO FIFO
    pio_sm_put_blocking(pio, sm, color);
}

// ============================================================================
// 函数: clear_pixel
// 功能: 关闭LED
// ============================================================================
void clear_pixel(void) {
    set_pixel_color(COLOR_BLACK);
}

// ============================================================================
// 函数: blink_single
// 功能: 单次闪烁
// 参数: color - 颜色
//       on_time_ms - 点亮时间(毫秒)
//       off_time_ms - 熄灭时间(毫秒)
// ============================================================================
void blink_single(uint32_t color, uint32_t on_time_ms, uint32_t off_time_ms) {
    set_pixel_color(color);
    sleep_ms(on_time_ms);
    clear_pixel();
    sleep_ms(off_time_ms);
}

// ============================================================================
// 函数: blink_pattern
// 功能: 闪烁模式1 - 简单闪烁
// ============================================================================
void blink_pattern_simple(void) {
    printf("模式: 简单闪烁 (红色)\n");
    while (1) {
        blink_single(COLOR_RED, 500, 500);
    }
}

// ============================================================================
// 函数: blink_pattern_fast
// 功能: 闪烁模式2 - 快速闪烁
// ============================================================================
void blink_pattern_fast(void) {
    printf("模式: 快速闪烁 (绿色)\n");
    while (1) {
        blink_single(COLOR_GREEN, 100, 100);
    }
}

// ============================================================================
// 函数: blink_pattern_slow
// 功能: 闪烁模式3 - 慢速闪烁
// ============================================================================
void blink_pattern_slow(void) {
    printf("模式: 慢速闪烁 (蓝色)\n");
    while (1) {
        blink_single(COLOR_BLUE, 1000, 1000);
    }
}

// ============================================================================
// 函数: blink_pattern_rainbow
// 功能: 闪烁模式4 - 彩虹闪烁
// ============================================================================
void blink_pattern_rainbow(void) {
    printf("模式: 彩虹闪烁\n");
    uint32_t colors[] = {
        COLOR_RED,
        COLOR_YELLOW,
        COLOR_GREEN,
        COLOR_CYAN,
        COLOR_BLUE,
        COLOR_MAGENTA
    };
    int num_colors = sizeof(colors) / sizeof(colors[0]);
    
    while (1) {
        for (int i = 0; i < num_colors; i++) {
            blink_single(colors[i], 200, 100);
        }
    }
}

// ============================================================================
// 函数: blink_pattern_fade
// 功能: 闪烁模式5 - 渐亮渐暗
// ============================================================================
void blink_pattern_fade(void) {
    printf("模式: 渐亮渐暗 (白色)\n");
    while (1) {
        // 渐亮
        for (int brightness = 0; brightness <= 255; brightness += 5) {
            uint32_t color = (brightness << 16) | (brightness << 8) | brightness;
            set_pixel_color(color);
            sleep_ms(10);
        }
        // 渐暗
        for (int brightness = 255; brightness >= 0; brightness -= 5) {
            uint32_t color = (brightness << 16) | (brightness << 8) | brightness;
            set_pixel_color(color);
            sleep_ms(10);
        }
    }
}

// ============================================================================
// 函数: blink_pattern_double
// 功能: 闪烁模式6 - 双闪
// ============================================================================
void blink_pattern_double(void) {
    printf("模式: 双闪 (黄色)\n");
    while (1) {
        // 快速闪烁两次
        blink_single(COLOR_YELLOW, 100, 50);
        blink_single(COLOR_YELLOW, 100, 50);
        // 长间隔
        sleep_ms(500);
    }
}

// ============================================================================
// 函数: blink_pattern_sos
// 功能: 闪烁模式7 - SOS信号 (三短三长三短)
// ============================================================================
void blink_pattern_sos(void) {
    printf("模式: SOS信号\n");
    while (1) {
        // 三短 (S)
        for (int i = 0; i < 3; i++) {
            blink_single(COLOR_WHITE, 100, 100);
        }
        sleep_ms(300);
        
        // 三长 (O)
        for (int i = 0; i < 3; i++) {
            blink_single(COLOR_WHITE, 300, 100);
        }
        sleep_ms(300);
        
        // 三短 (S)
        for (int i = 0; i < 3; i++) {
            blink_single(COLOR_WHITE, 100, 100);
        }
        sleep_ms(1000);
    }
}

// ============================================================================
// 主函数
// ============================================================================
int main() {
    // 初始化stdio (用于printf调试)
    stdio_init_all();
    
    printf("\n");
    printf("========================================\n");
    printf("WS2812 RGB LED 测试程序\n");
    printf("========================================\n");
    printf("引脚: GPIO %d\n", WS2812_PIN);
    printf("LED数量: %d\n", NUM_PIXELS);
    printf("\n");
    
    // 初始化WS2812
    printf("初始化WS2812...\n");
    ws2812_init();
    printf("初始化完成\n\n");
    
    // 关闭LED
    clear_pixel();
    sleep_ms(500);
    
    // ========================================================================
    // 选择闪烁模式 (修改这里切换模式)
    // ========================================================================
    int mode = 0; // 0-6: 不同闪烁模式
    
    printf("可用模式:\n");
    printf("  0 - 简单闪烁 (红色)\n");
    printf("  1 - 快速闪烁 (绿色)\n");
    printf("  2 - 慢速闪烁 (蓝色)\n");
    printf("  3 - 彩虹闪烁\n");
    printf("  4 - 渐亮渐暗 (白色)\n");
    printf("  5 - 双闪 (黄色)\n");
    printf("  6 - SOS信号\n");
    printf("\n");
    printf("当前模式: %d\n\n", mode);
    
    // 根据模式执行
    switch (mode) {
        case 0:
            blink_pattern_simple();
            break;
        case 1:
            blink_pattern_fast();
            break;
        case 2:
            blink_pattern_slow();
            break;
        case 3:
            blink_pattern_rainbow();
            break;
        case 4:
            blink_pattern_fade();
            break;
        case 5:
            blink_pattern_double();
            break;
        case 6:
            blink_pattern_sos();
            break;
        default:
            printf("未知模式，使用默认模式\n");
            blink_pattern_simple();
            break;
    }
    
    return 0;
}
