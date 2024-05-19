#include "ICM42688/ICM42688.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include <math.h>
#include <stdio.h>

ICM42688 IMU = ICM42688();
int main() {
    stdio_init_all();
    // start communication with IMU
    int status = IMU.begin();
    if (status < 0) {
        printf("IMU initialization unsuccessful\n");
        printf("Check IMU wiring or try cycling power\n");
        printf("Status: %d\n", status);
    }
    printf("ax,ay,az,gx,gy,gz,temp_C\n");

    while (1) {
        // read the sensor
        IMU.getAGT();
        // display the data
        printf("%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\n", IMU.accX(),
               IMU.accY(), IMU.accZ(), IMU.gyrX(), IMU.gyrY(), IMU.gyrZ(),
               IMU.temp());
        sleep_ms(20);
    }
}