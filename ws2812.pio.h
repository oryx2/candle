// WS2812 PIO程序头文件
// 基于Pico SDK标准WS2812驱动

#pragma once

#include "hardware/pio.h"

// WS2812 PIO程序指令
// 这个程序实现WS2812的时序协议
static const uint16_t ws2812_program_instructions[] = {
    0x6221, //  0: out    x, 1            side 0 [2]
    0x1123, //  1: jmp    !x, 3           side 1 [1]
    0x1400, //  2: jmp    0               side 1 [4]
    0xa442, //  3: nop                    side 0 [4]
    0x0000, //  4: jmp    0               side 0
};

static const struct pio_program ws2812_program = {
    .instructions = ws2812_program_instructions,
    .length = 5,
    .origin = -1,
};

static inline pio_sm_config ws2812_program_get_default_config(uint offset) {
    pio_sm_config c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, offset + 0, offset + 4);
    sm_config_set_sideset(&c, 1, false, false);
    return c;
}

// 初始化WS2812 PIO状态机
// pio: PIO实例 (pio0 或 pio1)
// sm: 状态机编号 (0-3)
// offset: PIO程序偏移量
// pin: GPIO引脚号
// freq: 频率 (通常800kHz)
// rgbw: 是否为RGBW (false表示RGB)
static inline void ws2812_program_init(PIO pio, uint sm, uint offset, uint pin, float freq, bool rgbw) {
    pio_sm_config c = ws2812_program_get_default_config(offset);
    sm_config_set_sideset_pins(&c, pin);
    sm_config_set_out_shift(&c, false, true, rgbw ? 32 : 24);
    sm_config_set_fifo_join(&c, PIO_FIFO_JOIN_TX);
    float div = (float)clock_get_hz(clk_sys) / (freq * 3);
    sm_config_set_clkdiv(&c, div);
    pio_gpio_init(pio, pin);
    pio_sm_set_consecutive_pindirs(pio, sm, pin, 1, true);
    pio_sm_init(pio, sm, offset, &c);
    pio_sm_set_enabled(pio, sm, true);
}
