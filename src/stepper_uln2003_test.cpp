#include "pico/stdlib.h"
#include <stdio.h>

#define int_1 14
#define int_2 15
#define int_3 16
#define int_4 17

static uint64_t motor_speed = 10000; // variable to set stepper speed
static int count = 0;               // count of steps made
static int counts_per_rev = 64*64;    // number of steps per full revolution
static int lookup[8] = {
    0b1000,
    0b1100,
    0b0100,
    0b0110,
    0b0010,
    0b0011,
    0b0001,
    0b1001};

void set_output(int out) {
    gpio_put(int_1, (lookup[out] >> 0) & 0x1);
    gpio_put(int_2, (lookup[out] >> 1) & 0x1);
    gpio_put(int_3, (lookup[out] >> 2) & 0x1);
    gpio_put(int_4, (lookup[out] >> 3) & 0x1);
}

void anticlockwise() {
    for (int i = 0; i < 8; i++) {
        set_output(i);
        sleep_us(motor_speed);
    }
}

void clockwise() {
    for (int i = 7; i >= 0; i--) {
        set_output(i);
        sleep_us(motor_speed);
    }
}

int main() {
    stdio_init_all();
    gpio_init(int_1);
    gpio_init(int_2);
    gpio_init(int_3);
    gpio_init(int_4);
    gpio_set_dir(int_1, GPIO_OUT);
    gpio_set_dir(int_2, GPIO_OUT);
    gpio_set_dir(int_3, GPIO_OUT);
    gpio_set_dir(int_4, GPIO_OUT);

    while (1) {
        if (count < counts_per_rev) {
            clockwise();
        } else if (count == counts_per_rev * 2) {
            count = 0;
        } else {
            anticlockwise();
        }
        count++;
    }
    return 0;
}
