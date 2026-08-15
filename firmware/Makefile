# Host-side stubs so example firmware compiles with gcc -DBRINGUP_HOST
CC ?= gcc
CFLAGS ?= -std=c11 -Wall -Wextra -Iinclude -DBRINGUP_HOST

HOST_STUB = src/host_hal.c
SRCS = src/opt3001.c src/lsm6.c src/board_init.c $(HOST_STUB)

.PHONY: host-check clean

host-check: $(SRCS) include/bringup_hal.h
	$(CC) $(CFLAGS) -c src/opt3001.c -o /tmp/opt3001.o
	$(CC) $(CFLAGS) -c src/lsm6.c -o /tmp/lsm6.o
	$(CC) $(CFLAGS) -c src/board_init.c -o /tmp/board_init.o
	@echo "firmware objects compile"

clean:
	rm -f /tmp/opt3001.o /tmp/lsm6.o /tmp/board_init.o
