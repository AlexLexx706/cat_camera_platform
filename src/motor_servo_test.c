#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include <math.h>
#include <stdio.h>

#define INT1 2
#define INT2 3
#define INT3 4
#define INT4 5

#define EN1 0
#define EN2 1

#define MIN_PWM 6000
#define MAX_PWM 16384

#define ENC_A1 8
#define ENC_B1 9

#define ENC_A2 10
#define ENC_B2 11

typedef struct {
    uint int_1;
    uint int_2;
    uint en_1;
    uint16_t max_pwm;
    uint16_t min_pwm;
} MotorDesc;

MotorDesc motor_1 = {INT1, INT2, EN1, MAX_PWM, 0};
MotorDesc motor_2 = {INT3, INT4, EN2, MAX_PWM, 0};

typedef struct EncoderState {
    int8_t last_encoded;
    int32_t encoder_value;
} EncoderState;

EncoderState enc_1 = {};
EncoderState enc_2 = {};

void enc_callback(uint gpio, uint32_t events) {
    EncoderState *state;
    int encoded;
    if (gpio == ENC_A1 || gpio == ENC_B1) {
        state = &enc_1;
        encoded = (gpio_get(ENC_A1) << 1) | gpio_get(ENC_B1);
    } else {
        state = &enc_2;
        encoded = (gpio_get(ENC_A2) << 1) | gpio_get(ENC_B2);
    }
    int sum = (state->last_encoded << 2) | encoded;

    if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
        state->encoder_value += 1;
    if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
        state->encoder_value -= 1;
    state->last_encoded = encoded;
}

void init_encoders() {
    gpio_init(ENC_A1);
    gpio_init(ENC_A2);
    gpio_init(ENC_B1);
    gpio_init(ENC_B2);

    gpio_set_dir(ENC_A1, GPIO_IN);
    gpio_set_dir(ENC_A2, GPIO_IN);
    gpio_set_dir(ENC_B1, GPIO_IN);
    gpio_set_dir(ENC_B2, GPIO_IN);

    //https://cdn-shop.adafruit.com/product-files/4640/n20+motors_C15011+6V.pdf
    gpio_pull_up(ENC_A1);
    gpio_pull_up(ENC_A2);
    gpio_pull_up(ENC_B1);
    gpio_pull_up(ENC_B2);

    gpio_set_irq_enabled_with_callback(
        ENC_A1, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &enc_callback);

    gpio_set_irq_enabled_with_callback(
        ENC_B1, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &enc_callback);

    gpio_set_irq_enabled_with_callback(
        ENC_A2, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &enc_callback);

    gpio_set_irq_enabled_with_callback(
        ENC_B2, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &enc_callback);
}

void init_motor(MotorDesc *desc) {
    gpio_init(desc->int_1);
    gpio_init(desc->int_2);

    gpio_set_dir(desc->int_1, GPIO_OUT);
    gpio_set_dir(desc->int_2, GPIO_OUT);
    gpio_set_function(desc->en_1, GPIO_FUNC_PWM);
}

void motor_pwm(MotorDesc *desc, float value) {
    if (value > 0) {
        gpio_put(desc->int_1, 1);
        gpio_put(desc->int_2, 0);
        if (value > desc->max_pwm) {
            value = desc->max_pwm;
        }
        pwm_set_gpio_level(EN1, value);
    } else if (value < 0) {
        gpio_put(desc->int_1, 0);
        gpio_put(desc->int_2, 1);
        value = -value;

        if (value > desc->max_pwm) {
            value = desc->max_pwm;
        }
        pwm_set_gpio_level(EN1, value);
    } else {
        gpio_put(desc->int_1, 0);
        gpio_put(desc->int_2, 0);
        pwm_set_gpio_level(desc->en_1, 0);
    }
}

uint64_t prev_t = 0;
float e_prev = 0;
float e_integral = 0;

// PID constants
float k_p = 1000;
float k_d = 20;
float k_i = 0.0;

static inline uint64_t micros() {return to_us_since_boot(get_absolute_time());}

void servo_test() {
    // set target position
    // int target = 1200;
    int target = 1000 * sin(prev_t / 1e6);

    // time difference
    uint64_t curr_t = micros();
    float delta_t = ((float)(curr_t - prev_t)) / (1.0e6);
    prev_t = curr_t;

    int32_t pos = enc_1.encoder_value;

    // error
    int e = pos - target;

    // derivative
    float d_e_dt = (e - e_prev) / (delta_t);

    // integral
    e_integral = e_integral + e * delta_t;

    // control signal
    float u = k_p * e + k_d * d_e_dt + k_i * e_integral;

    // store previous error
    e_prev = e;
    motor_pwm(&motor_1, u);

    printf("%d %d %f\n", target, pos, u);
    sleep_ms(10);
}

int main() {
    stdio_init_all();
    init_motor(&motor_1);
    init_motor(&motor_2);
    init_encoders();

    uint slice_num = pwm_gpio_to_slice_num(EN1);
    pwm_set_wrap(slice_num, MAX_PWM);
    pwm_set_enabled(slice_num, true);
    uint32_t cur_time_ms;

    while (1) {
        servo_test();
        // sleep_ms(20);
    }
}