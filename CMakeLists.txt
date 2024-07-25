cmake_minimum_required(VERSION 3.13)
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
include($ENV{FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)

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

add_executable(vl53l0x_test
  src/vl53l0x_test.cpp
  src/VL53L0X/VL53L0X.cpp
)

add_executable(encoder_test
  src/encoder_test.c
)

add_executable(motor_servo_test
  src/motor_servo_test.c
)

add_executable(rtos_blink_example
  src/rtos_blink_example.c
)

add_executable(icm42688_test_interrupt
  src/icm42688_test_interrupt.cpp
  src/ICM42688/ICM42688.cpp
)

add_executable(stepper_uln2003_test
  src/stepper_uln2003_test.cpp
)

add_executable(stepper_a4988_test
  src/stepper_a4988_test.cpp
)


target_include_directories(rtos_blink_example PRIVATE ${CMAKE_CURRENT_LIST_DIR} scr)
target_include_directories(icm42688_test_interrupt PRIVATE ${CMAKE_CURRENT_LIST_DIR} scr)

pico_enable_stdio_usb(motor_test 1)
pico_enable_stdio_uart(motor_test 1)

pico_enable_stdio_usb(blink 1)
pico_enable_stdio_uart(blink 1)

pico_enable_stdio_usb(motor_pwm_test 1)
pico_enable_stdio_uart(motor_pwm_test 1)

pico_enable_stdio_usb(icm42688_test 1)
pico_enable_stdio_uart(icm42688_test 1)

pico_enable_stdio_usb(vl53l0x_test 1)
pico_enable_stdio_uart(vl53l0x_test 1)

pico_enable_stdio_usb(encoder_test 1)
pico_enable_stdio_uart(encoder_test 1)

pico_enable_stdio_usb(motor_servo_test 1)
pico_enable_stdio_uart(motor_servo_test 1)

pico_enable_stdio_usb(rtos_blink_example 1)
pico_enable_stdio_uart(rtos_blink_example 1)

pico_enable_stdio_usb(icm42688_test_interrupt 1)
pico_enable_stdio_uart(icm42688_test_interrupt 1)

pico_enable_stdio_usb(stepper_uln2003_test 1)
pico_enable_stdio_uart(stepper_uln2003_test 1)

pico_enable_stdio_usb(stepper_a4988_test 1)
pico_enable_stdio_uart(stepper_a4988_test 1)

pico_add_extra_outputs(blink)
pico_add_extra_outputs(motor_test)
pico_add_extra_outputs(motor_pwm_test)
pico_add_extra_outputs(icm42688_test)
pico_add_extra_outputs(vl53l0x_test)
pico_add_extra_outputs(encoder_test)
pico_add_extra_outputs(motor_servo_test)
pico_add_extra_outputs(rtos_blink_example)
pico_add_extra_outputs(icm42688_test_interrupt)
pico_add_extra_outputs(stepper_uln2003_test)
pico_add_extra_outputs(stepper_a4988_test)

target_link_libraries(motor_test pico_stdlib hardware_pwm)
target_link_libraries(blink pico_stdlib hardware_pwm)
target_link_libraries(motor_pwm_test pico_stdlib hardware_pwm)
target_link_libraries(icm42688_test pico_stdlib hardware_spi)
target_link_libraries(vl53l0x_test pico_stdlib hardware_i2c)
target_link_libraries(encoder_test pico_stdlib)
target_link_libraries(motor_servo_test pico_stdlib hardware_pwm)
target_link_libraries(rtos_blink_example pico_stdlib FreeRTOS-Kernel-Heap4)
target_link_libraries(icm42688_test_interrupt pico_stdlib hardware_spi FreeRTOS-Kernel-Heap4)
target_link_libraries(stepper_uln2003_test pico_stdlib)
target_link_libraries(stepper_a4988_test pico_stdlib)