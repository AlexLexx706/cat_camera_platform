#include "ICM42688/ICM42688.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>

#define ICM42688_IRQ_PIN 22

volatile bool dataReady = false;
static ICM42688 IMU;
// SemaphoreHandle_t mutex;

static void gpio_callback(uint gpio, uint32_t events) {
    // IMU Interrupt pin
    if (gpio == ICM42688_IRQ_PIN) {
        dataReady = true;
    }
}

static void test_task(void *) {
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        printf("test\n");
    }
}

static void process_imu(void *) {

    while (true) {
        if (!dataReady)
            continue;
        dataReady = false;

        // read the sensor
        IMU.getAGT();

        // display the data
        printf("%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\n", IMU.accX(),
            IMU.accY(), IMU.accZ(), IMU.gyrX(), IMU.gyrY(), IMU.gyrZ(),
            IMU.temp());
    }
}

int main() {
    stdio_init_all();
    sleep_ms(5000);
    printf("1.\n");
    gpio_set_irq_enabled_with_callback(
        ICM42688_IRQ_PIN,
        GPIO_IRQ_EDGE_RISE,
        true, &gpio_callback);
    printf("2.\n");

    // start communication with IMU
    int status = IMU.begin();
    printf("3.\n");

    if (status < 0) {
        printf("IMU initialization unsuccessful\n");
        printf("Check IMU wiring or try cycling power\n");
        printf("Status: %d\n", status);
    }

    printf("4.\n");
    // set output data rate to 12.5 Hz
    IMU.setAccelODR(ICM42688::odr12_5);
    IMU.setGyroODR(ICM42688::odr12_5);
    IMU.setGyroFS(ICM42688::dps125);
    IMU.setAccelFS(ICM42688::gpm2);
    printf("5.\n");
    IMU.enableDataReadyInterrupt();
    printf("6.\n");
    xTaskCreate(process_imu, "imu Task", 1024, NULL, 1, NULL);
    xTaskCreate(test_task, "test_task", 1024, NULL, 1, NULL);
    // enabling the data ready interrupt
    printf("7.\n");
    vTaskStartScheduler();

    printf("fail!!!\n");
    while (true) {}
}