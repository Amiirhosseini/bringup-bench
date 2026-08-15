#ifdef BRINGUP_HOST
#include "bringup_hal.h"

int i2c_write(const char *bus, uint8_t addr, const uint8_t *data, uint32_t n)
{
    (void)bus; (void)addr; (void)data; (void)n;
    return 0;
}
int i2c_read(const char *bus, uint8_t addr, uint8_t *data, uint32_t n)
{
    (void)bus; (void)addr; (void)n;
    if (data) data[0] = 0x54;
    return 0;
}
int spi_set_mode(const char *bus, int mode) { (void)bus; (void)mode; return 0; }
int spi_xfer(const char *bus, const uint8_t *tx, uint8_t *rx, uint32_t n)
{
    (void)bus; (void)tx; (void)n;
    if (rx && n >= 2) rx[1] = 0x6A;
    return 0;
}
void usart_set_baud(const char *bus, uint32_t baud) { (void)bus; (void)baud; }
void usart_set_format(const char *bus, int bits, int parity, int stop)
{
    (void)bus; (void)bits; (void)parity; (void)stop;
}
void rcc_enable(const char *clock_name) { (void)clock_name; }
#endif
