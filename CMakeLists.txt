cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)

project(test_project C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(motor_test
  src/motor_test.c
)

add_executable(blink
  src/blink_test.c
)

add_executable(motor_pwm_test
  src/motor_pwm_test.cxx
)

add_executable(icm42688_test
  src/ICM42688/ICM42688.cpp
  src/icm42688_test.cpp
)



pico_enable_stdio_usb(motor_test 1)
pico_enable_stdio_uart(motor_test 1)
pico_enable_stdio_uart(icm42688_test 1)

pico_enable_stdio_usb(blink 1)
pico_enable_stdio_uart(blink 1)

pico_enable_stdio_usb(motor_pwm_test 1)
pico_enable_stdio_uart(motor_pwm_test 1)

pico_enable_stdio_usb(icm42688_test 1)
pico_enable_stdio_uart(icm42688_test 1)

pico_add_extra_outputs(blink)
pico_add_extra_outputs(motor_test)
pico_add_extra_outputs(motor_pwm_test)
pico_add_extra_outputs(icm42688_test)

target_link_libraries(motor_test pico_stdlib hardware_pwm)
target_link_libraries(blink pico_stdlib hardware_pwm)
target_link_libraries(motor_pwm_test pico_stdlib hardware_pwm)
target_link_libraries(icm42688_test pico_stdlib hardware_spi)