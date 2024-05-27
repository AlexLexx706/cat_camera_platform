#!/bin/bash
export PICO_SDK_PATH=$PWD/../pico-sdk/
export FREERTOS_KERNEL_PATH=$PWD/../FreeRTOS-Kernel
mkdir build
cd build
cmake ..
make -j9