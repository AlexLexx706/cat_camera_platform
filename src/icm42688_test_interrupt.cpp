#include "ICM42688/ICM42688.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include "FreeRTOS.h"
#include <math.h>
#include <stdio.h>

#define ICM42688_IRQ_PIN 22

volatile bool dataReady = false;

void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == 22) {
        // printf("IMU_I\n");
        dataReady = true;
    }
}

ICM42688 IMU = ICM42688();
int main() {
    stdio_init_all();
    gpio_set_irq_enabled_with_callback(
        ICM42688_IRQ_PIN,
        GPIO_IRQ_EDGE_RISE, true, &gpio_callback);

    // start communication with IMU
    int status = IMU.begin();
    if (status < 0) {
        printf("IMU initialization unsuccessful\n");
        printf("Check IMU wiring or try cycling power\n");
        printf("Status: %d\n", status);
    }
    // set output data rate to 12.5 Hz
    IMU.setAccelODR(ICM42688::odr12_5);
    IMU.setGyroODR(ICM42688::odr12_5);
    IMU.setGyroFS(ICM42688::dps125);
    IMU.setAccelFS(ICM42688::gpm2);

    // enabling the data ready interrupt
    IMU.enableDataReadyInterrupt(); 

    while (1) {
        if (!dataReady)
            continue;
        dataReady = false;

        // read the sensor
        IMU.getAGT();

        // display the data
        printf("%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\n",
            IMU.accX(), IMU.accY(), IMU.accZ(),
            IMU.gyrX(), IMU.gyrY(), IMU.gyrZ(),
            IMU.temp());
    }
}