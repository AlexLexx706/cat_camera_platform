#include "VL53L0X/VL53L0X.h"
#include "pico/binary_info.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>

#define SDA_PIN 6
#define SCL_PIN 7

static VL53L0X sensor;

int main() {
    stdio_init_all();

    i2c_init(&i2c1_inst, 400 * 1000);
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);
    // Make the I2C pins available to picotool
    bi_decl(bi_2pins_with_func(SDA_PIN, SCL_PIN, GPIO_FUNC_I2C));

    sensor.setBus(&i2c1_inst);
    sensor.setTimeout(500);

    if (!sensor.init()) {
        printf("Failed to detect and initialize sensor!\n");
        while (1) {
            printf("Failed to detect and initialize sensor!\n");
            sleep_ms(1000);
        }
    }

    // Start continuous back-to-back mode (take readings as
    // fast as possible).  To use continuous timed mode
    // instead, provide a desired inter-measurement period in
    // ms (e.g. sensor.startContinuous(100)).
    sensor.startContinuous();

    while (1) {
        printf("%d\n", sensor.readRangeContinuousMillimeters());
        if (sensor.timeoutOccurred()) {
            printf("TIMEOUT\n");
        }
    }
}