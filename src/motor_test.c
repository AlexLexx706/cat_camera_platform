#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include <math.h>
#include <stdio.h>

const uint INT1 = 2;
const uint INT2 = 3;

const uint INT3 = 4;
const uint INT4 = 5;

int main() {
    stdio_init_all();
    gpio_init(INT1);
    gpio_init(INT2);
    gpio_set_dir(INT1, GPIO_OUT);
    gpio_set_dir(INT2, GPIO_OUT);

    gpio_init(INT3);
    gpio_init(INT4);
    gpio_set_dir(INT3, GPIO_OUT);
    gpio_set_dir(INT4, GPIO_OUT);

    while (1) {
        printf("stop\n");
        gpio_put(INT1, 0);
        gpio_put(INT2, 0);
        gpio_put(INT3, 0);
        gpio_put(INT4, 0);
        sleep_ms(5000);

        printf("Forward\n");
        gpio_put(INT1, 1);
        gpio_put(INT2, 0);
        gpio_put(INT3, 1);
        gpio_put(INT4, 0);
        sleep_ms(5000);

        printf("Stop\n");
        gpio_put(INT1, 0);
        gpio_put(INT2, 0);
        gpio_put(INT3, 0);
        gpio_put(INT4, 0);
        sleep_ms(5000);

        printf("Backward\n");
        gpio_put(INT1, 0);
        gpio_put(INT2, 1);
        gpio_put(INT3, 0);
        gpio_put(INT4, 1);
        sleep_ms(5000);
    }
}