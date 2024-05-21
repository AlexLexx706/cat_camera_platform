#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include <stdio.h>

#define ENC_A1 8
#define ENC_B1 9

#define ENC_A2 10
#define ENC_B2 11

typedef struct EncoderState {
    int8_t last_encoded;
    int32_t encoder_value;
} EncoderState;

static EncoderState enc_1={};
static EncoderState enc_2={};

void enc_callback(uint gpio, uint32_t events) {
    EncoderState * state;
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

int main() {
    stdio_init_all();

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

    // Wait forever
    while (1) {
        printf("%d %d\n", enc_1.encoder_value, enc_2.encoder_value);
        sleep_ms(20);
    }
}
