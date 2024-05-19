#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include <math.h>
#include <stdio.h>

const uint INT1 = 2;
const uint INT2 = 3;
const uint INT3 = 4;
const uint INT4 = 5;

const uint EN1 = 0;
const uint EN2 = 1;

int main() {
    stdio_init_all();
    gpio_init(INT1);
    gpio_init(INT2);
    gpio_init(INT3);
    gpio_init(INT4);

    gpio_set_dir(INT1, GPIO_OUT);
    gpio_set_dir(INT2, GPIO_OUT);
    gpio_set_dir(INT3, GPIO_OUT);
    gpio_set_dir(INT4, GPIO_OUT);

    const uint16_t max_pwm_value = 16384;
    const uint16_t min_pwm_value = 6000;
    const uint16_t max_control_value = max_pwm_value - min_pwm_value;

    gpio_set_function(EN1, GPIO_FUNC_PWM);
    gpio_set_function(EN2, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(EN1);
    pwm_set_wrap(slice_num, max_pwm_value);
    pwm_set_enabled(slice_num, true);

    float period = 10.f;

    uint32_t cur_time_ms;

    float control_value;
    uint16_t pwm_value;

    while (1) {
        cur_time_ms = to_ms_since_boot(get_absolute_time());
        control_value = (sinf(cur_time_ms / 1000.f / period * M_PI));
        float tmp_control_value = control_value;
        if (control_value >= 0) {
            gpio_put(INT1, 1);
            gpio_put(INT2, 0);
            gpio_put(INT3, 1);
            gpio_put(INT4, 0);
        } else {
            tmp_control_value = -control_value;
            gpio_put(INT1, 0);
            gpio_put(INT2, 1);
            gpio_put(INT3, 0);
            gpio_put(INT4, 1);
        }
        // convert control value (0-1) to pwm_value
        pwm_value = tmp_control_value * max_control_value + min_pwm_value;
        pwm_set_gpio_level(EN1, pwm_value);
        pwm_set_gpio_level(EN2, pwm_value);

        sleep_ms(20);
        // printf("%3.6f\n", control_value);
    }
}