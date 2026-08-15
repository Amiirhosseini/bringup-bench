/* Example I2C whoami — address must match the ADDR pin (0x44 when ADDR=GND). */
#include "bringup_hal.h"

#define OPT3001_ADDR  0x44u

int opt3001_whoami(uint8_t *id)
{
    uint8_t reg = 0x7E;
    if (i2c_write("i2c1", OPT3001_ADDR, &reg, 1) != 0)
        return -1;
    return i2c_read("i2c1", OPT3001_ADDR, id, 1);
}
