/* IMU on SPI1 — LSM6-class WHO_AM_I, mode 0. */
#include "bringup_hal.h"

int lsm6_whoami(uint8_t *id)
{
    uint8_t tx[2] = { 0x8F, 0x00 };
    uint8_t rx[2] = { 0 };
    spi_set_mode("spi1", 0);
    if (spi_xfer("spi1", tx, rx, 2) != 0)
        return -1;
    *id = rx[1];
    return 0;
}
