#include "bringup_hal.h"

void board_clocks_enable(void)
{
    rcc_enable("I2C1");
    rcc_enable("SPI1");
    rcc_enable("USART2");
}

void console_init(void)
{
    usart_set_baud("usart2", 57600);
    usart_set_format("usart2", 8, 0, 1);
}
