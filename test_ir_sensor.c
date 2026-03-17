/*
 * 红外传感器测试程序
 * 
 * 功能:
 * - 测试GPIO 28上的红外传感器
 * - 使用 GPIO 27 点亮/熄灭做指示（可接 LED）
 * - 传感器触发时(低电平)点亮，未触发时慢闪（心跳）
 * 
 * 使用方法:
 * 1. 上传程序到Pico
 * 2. 观察 GPIO 27 上的 LED 指示
 * 3. 触发传感器（遮挡/接近），观察 LED 变化
 */

#include "pico/stdlib.h"

// ============================================================================
// GPIO引脚定义
// ============================================================================
#define IR_SENSOR    28  // 红外传感器引脚（与 candle.c 一致）
#define LED_INDICATOR 27 // 指示 LED 引脚（点亮/熄灭）

// ============================================================================
// 主函数
// ============================================================================
int main() {
  stdio_init_all();

  // ========================================================================
  // GPIO初始化
  // ========================================================================
  gpio_init(IR_SENSOR);
  gpio_init(LED_INDICATOR);

  // 红外传感器设为输入，启用上拉电阻
  gpio_set_dir(IR_SENSOR, GPIO_IN);
  gpio_pull_up(IR_SENSOR); // 上拉，未触发时为高电平

  // 指示 LED 设为输出
  gpio_set_dir(LED_INDICATOR, GPIO_OUT);
  gpio_put(LED_INDICATOR, 0);

  printf("红外传感器测试程序启动\n");
  printf("传感器引脚: GPIO %d\n", IR_SENSOR);
  printf("指示 LED: GPIO %d (触发=常亮, 未触发=慢闪)\n", LED_INDICATOR);
  printf("传感器触发时: 低电平 (0)\n");
  printf("传感器未触发时: 高电平 (1)\n");
  printf("\n");

  // ========================================================================
  // 主循环：实时指示传感器状态（尽量简单）
  uint32_t edge_count = 0;
  uint32_t last_state = 1;
  absolute_time_t last_time = get_absolute_time();

  while (1) {
    uint32_t sensor_state = gpio_get(IR_SENSOR);
    bool triggered = (sensor_state == 0); // 低电平表示触发

    // 显示状态：
    // - 未触发：GPIO 27 慢闪（心跳）
    // - 触发：GPIO 27 常亮
    if (triggered) {
      gpio_put(LED_INDICATOR, 1);
    } else {
      // 约 1Hz 闪烁（500ms 亮 / 500ms 灭）
      bool on = (to_ms_since_boot(get_absolute_time()) / 500) & 1u;
      gpio_put(LED_INDICATOR, on ? 1 : 0);
    }

    // 仅在边沿变化时打印一次（方便看信号是否抖动/频率）
    if (sensor_state != last_state) {
      edge_count++;
      absolute_time_t now = get_absolute_time();
      int64_t diff = absolute_time_diff_us(last_time, now);
      last_time = now;

      printf("IR 边沿 #%lu: %s (间隔: %lld us)\n",
             edge_count,
             triggered ? "触发(0)" : "释放(1)",
             diff);
      last_state = sensor_state;
    }

    sleep_ms(5);

  }

  return 0;
}
