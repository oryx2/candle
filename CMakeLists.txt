cmake_minimum_required(VERSION 3.13)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(candle)

pico_sdk_init()


add_executable(candle
	candle.c
	)

target_include_directories(candle PRIVATE .)

target_link_libraries(candle
	pico_stdlib
	pico_multicore
	hardware_pwm
	hardware_adc
)

pico_add_extra_outputs(candle)

# ============================================================================
# 红外传感器测试程序
# ============================================================================
add_executable(test_ir_sensor
	test_ir_sensor.c
	)

target_include_directories(test_ir_sensor PRIVATE .)

target_link_libraries(test_ir_sensor
	pico_stdlib
	)

pico_add_extra_outputs(test_ir_sensor)

# ============================================================================
# WS2812 RGB LED 测试程序 (Pico Zero板载LED)
# ============================================================================
add_executable(test_ws2812
	test_ws2812.c
	)

target_include_directories(test_ws2812 PRIVATE .)

target_link_libraries(test_ws2812
	pico_stdlib
	hardware_pio
	)

pico_add_extra_outputs(test_ws2812)

# ============================================================================
# LED 矩阵测试程序
# ============================================================================
add_executable(candle_led_matrix_test
	candle_led_matrix_test.c
	)

target_include_directories(candle_led_matrix_test PRIVATE .)

target_link_libraries(candle_led_matrix_test
	pico_stdlib
	pico_multicore
	hardware_pwm
	hardware_adc
)

pico_add_extra_outputs(candle_led_matrix_test)
