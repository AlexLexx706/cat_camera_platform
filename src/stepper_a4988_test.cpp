#include "pico/stdlib.h"
#include <stdio.h>

#define EN_PIN 14
#define STEP_PIN 15
#define DIR_PIN 16
#define HIGH 1
#define LOW 0

#define steps_per_revolution 64*64


#define SPEED_1 2000
#define SPEED_2 1000
#define SPEED_3 500



int main() {
    stdio_init_all();
    gpio_init(EN_PIN);
    gpio_init(STEP_PIN);
    gpio_init(DIR_PIN);

    gpio_set_dir(EN_PIN, GPIO_OUT);
    gpio_set_dir(STEP_PIN, GPIO_OUT);
    gpio_set_dir(DIR_PIN, GPIO_OUT);


    while (1) {
        gpio_put(EN_PIN, LOW);
        // Set the spinning direction clockwise:
        gpio_put(DIR_PIN, HIGH);

        // Spin the stepper motor 1 revolution slowly:
        for (int i = 0; i < steps_per_revolution; i++) {
            // These four lines result in 1 step:
            gpio_put(STEP_PIN, HIGH);
            sleep_us(SPEED_1);
            gpio_put(STEP_PIN, LOW);
            sleep_us(SPEED_1);
        }
        gpio_put(EN_PIN, HIGH);
        sleep_ms(3000);

        // Set the spinning direction counterclockwise:
        gpio_put(EN_PIN, LOW);
        gpio_put(DIR_PIN, LOW);

        // Spin the stepper motor 1 revolution quickly:
        for (int i = 0; i < steps_per_revolution; i++) {
            // These four lines result in 1 step:
            gpio_put(STEP_PIN, HIGH);
            sleep_us(SPEED_2);
            gpio_put(STEP_PIN, LOW);
            sleep_us(SPEED_2);
        }

        gpio_put(EN_PIN, HIGH);
        sleep_ms(3000);


        // Set the spinning direction clockwise:
        gpio_put(EN_PIN, LOW);
        gpio_put(DIR_PIN, HIGH);

        // Spin the stepper motor 5 revolutions fast:
        for (int i = 0; i < 5 * steps_per_revolution; i++) {
            // These four lines result in 1 step:
            gpio_put(STEP_PIN, HIGH);
            sleep_us(SPEED_3);
            gpio_put(STEP_PIN, LOW);
            sleep_us(SPEED_3);
        }

        gpio_put(EN_PIN, HIGH);
        sleep_ms(3000);

        // Set the spinning direction counterclockwise:
        gpio_put(EN_PIN, LOW);
        gpio_put(DIR_PIN, LOW);

        // Spin the stepper motor 5 revolutions fast:
        for (int i = 0; i < 5 * steps_per_revolution; i++) {
            // These four lines result in 1 step:
            gpio_put(STEP_PIN, HIGH);
            sleep_us(SPEED_3);
            gpio_put(STEP_PIN, LOW);
            sleep_us(SPEED_3);
        }

        gpio_put(EN_PIN, HIGH);
        sleep_ms(3000);
    }
    return 0;
}