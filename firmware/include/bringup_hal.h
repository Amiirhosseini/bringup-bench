/* Minimal HAL used by generated stubs and example firmware.
 * Host builds can compile this file with -DBRINGUP_HOST.
 */
#ifndef BRINGUP_HAL_H
#define BRINGUP_HAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int i2c_write(const char *bus, uint8_t addr, const uint8_t *data, uint32_t n);
int i2c_read(const char *bus, uint8_t addr, uint8_t *data, uint32_t n);
int spi_set_mode(const char *bus, int mode);
int spi_xfer(const char *bus, const uint8_t *tx, uint8_t *rx, uint32_t n);
void usart_set_baud(const char *bus, uint32_t baud);
void usart_set_format(const char *bus, int bits, int parity, int stop);
void rcc_enable(const char *clock_name);

#ifdef __cplusplus
}
#endif
#endif
