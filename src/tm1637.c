// Commands for controlling a TM1637 7-segment display
//
// Copyright (C) 2023  Jookia <contact@jookia.org>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "command.h"
#include "basecmd.h"
#include "sched.h"
#include "board/gpio.h"
#include "board/irq.h"
#include "board/misc.h"
#include <string.h>

#define MODE_OPEN 0
#define MODE_LOW 1
#define MODE_UNSET 255

struct tm1637_pin {
    uint32_t gpio_num;
    uint8_t mode;
    struct gpio_in in;
    struct gpio_out out;
};

void
tm1637_pin_new(struct tm1637_pin *pin, uint32_t gpio_num) {
    pin->gpio_num = gpio_num;
    pin->mode = MODE_UNSET;
}

void
tm1637_pin_reset(struct tm1637_pin *pin) {
    if (pin->mode == MODE_OPEN) {
        gpio_in_reset(pin->in, 1);
    } else if (pin->mode == MODE_LOW) {
        gpio_out_reset(pin->out, 1);
    }
    pin->mode = MODE_UNSET;
}

uint8_t
tm1637_pin_open(struct tm1637_pin *pin) {
    if (pin->mode != MODE_OPEN) {
        tm1637_pin_reset(pin);
        pin->in = gpio_in_setup(pin->gpio_num, 1);
        pin->mode = MODE_OPEN;
    }
    return gpio_in_read(pin->in);
}

void
tm1637_pin_low(struct tm1637_pin *pin) {
    if (pin->mode != MODE_LOW) {
        tm1637_pin_reset(pin);
        pin->out = gpio_out_setup(pin->gpio_num, 0);
        pin->mode = MODE_LOW;
    }
}

struct tm1637_state {
    struct timer timer;
    struct tm1637_pin clk;
    struct tm1637_pin dio;
    uint8_t data[9];
    uint8_t bit_position;
    uint8_t step;
};

#define TIMER_WAIT_TIME_US 100

int
tm1637_step(struct tm1637_state *s) {
    switch(s->step) {
        // IDLE
        case 0: {
            if(!tm1637_pin_open(&s->clk)) {
                s->step = 10; // BUS RESET
            } else if(!tm1637_pin_open(&s->dio)) {
                s->step = 10; // BUS RESET
            } else {
                s->step = 20; // START
            }
            break;
        }
        // BUS RESET
        case 10: tm1637_pin_low(&s->clk); s->step++; break;
        case 11: tm1637_pin_low(&s->dio); s->step++; break;
        case 12: tm1637_pin_open(&s->clk); s->step++; break;
        case 13: {
            tm1637_pin_open(&s->dio);
            s->bit_position++;
            if(s->bit_position == 11) {
                s->bit_position = 0;
                s->step++; // START
            } else {
                s->step = 10; // BUS RESET
            }
            break;
        }
        case 14: {
            if(!tm1637_pin_open(&s->clk)) {
                s->step = 0; // ERROR
            } else if(!tm1637_pin_open(&s->dio)) {
                s->step = 0; // ERROR
            } else {
                s->step = 20; // START
            }
            break;
        }
        // START
        case 20: tm1637_pin_low(&s->dio); s->step++; break;
        case 21: tm1637_pin_low(&s->clk); s->step = 30; break; // WRITE BIT
        // WRITE BIT
        case 30: tm1637_pin_low(&s->clk); s->step++; break;
        case 31: {
            int byte = s->data[s->bit_position / 8];
            int bit = (byte >> s->bit_position % 8) & 1;
            if(bit) {
                if(!tm1637_pin_open(&s->dio)) {
                     s->step = 0; // ERROR
                }
            } else {
                tm1637_pin_low(&s->dio);
            }
            s->step++;
            break;
        }
        case 32: {
            s->bit_position++;
            if(!tm1637_pin_open(&s->clk)) {
                s->step = 0; // ERROR
            } else if(s->bit_position % 8 == 0) {
                s->step = 40; // ACK
            } else {
                s->step = 30; // WRITE BIT
            }
            break;
        }
        // ACK
        case 40: tm1637_pin_low(&s->clk); s->step++; break;
        case 41: tm1637_pin_open(&s->dio); s->step++; break;
        case 42: {
            if(!tm1637_pin_open(&s->clk)) {
                s->step = 0; // ERROR
            } else {
                s->step++;
            }
            break;
        }
        case 43: {
            if(tm1637_pin_open(&s->dio)) {
                s->step = 0; // ERROR
            } else if(s->bit_position == 8 ||
                s->bit_position == 64 ||
                s->bit_position == 72) {
                s->step++;
            } else {
                s->step = 30; // WRITE BIT
            }
            break;
        }
        case 44: tm1637_pin_low(&s->clk); s->step++; break;
        case 45: tm1637_pin_low(&s->dio); s->step = 50; break; // STOP
        // STOP
        case 50: tm1637_pin_low(&s->clk); s->step++; break;
        case 51: tm1637_pin_low(&s->dio); s->step++; break;
        case 52: {
            if(!tm1637_pin_open(&s->clk)) {
                s->step = 0; // ERROR
            } else {
                s->step++;
            }
            break;
        }
        case 53: {
            if(!tm1637_pin_open(&s->dio)) {
                s->step = 0; // ERROR
            } else if(s->bit_position == 8 ||
                s->bit_position == 64) {
                s->step = 20; // START
            } else {
                s->step = 0; // IDLE
            }
            break;
        }
    }
    return (s->step != 0);
}

void
command_config_tm1637(uint32_t *args)
{
    struct tm1637_state *s = oid_alloc(
        args[0], command_config_tm1637, sizeof(*s));
    memset(&s->timer, 0, sizeof(s->timer));
    tm1637_pin_new(&s->clk, args[1]);
    tm1637_pin_new(&s->dio, args[2]);
    memset(s->data, 0, sizeof(s->data));
    s->bit_position = 0;
    s->step = 0;
}
DECL_COMMAND(command_config_tm1637,
    "config_tm1637 oid=%c clk_pin=%u dio_pin=%u");

void
tm1637_shutdown(void)
{
    uint8_t i;
    struct tm1637_state *s;
    foreach_oid(i, s, command_config_tm1637) {
        tm1637_pin_reset(&s->clk);
        tm1637_pin_reset(&s->dio);
    }
}
DECL_SHUTDOWN(tm1637_shutdown);

struct tm1637_state *current_state = NULL;

int
try_lock_state(struct tm1637_state *state) {
    if(current_state == NULL) {
        current_state = state;
    }
    return current_state == state;
}

void
unlock_state(void) {
    current_state = NULL;
}

uint_fast8_t tm1637_timer_step(struct timer *timer) {
    struct tm1637_state *s = container_of(timer, struct tm1637_state, timer);
    if(!try_lock_state(s)) {
        timer->waketime += timer_from_us(TIMER_WAIT_TIME_US * 500);
        return SF_RESCHEDULE;
    }
    if(tm1637_step(s)) {
        timer->waketime += timer_from_us(TIMER_WAIT_TIME_US);
        return SF_RESCHEDULE;
    } else {
        timer->waketime = 0;
        memset(s->data, 0, sizeof(s->data));
        s->bit_position = 0;
        s->step = 0;
        unlock_state();
        return SF_DONE;
    }
}

void
command_tm1637_send(uint32_t *args)
{
    struct tm1637_state *s = oid_lookup(args[0], command_config_tm1637);
    uint8_t data_len = args[1];
    uint8_t *data = command_decode_ptr(args[2]);
    if (data_len != sizeof(s->data))
        shutdown("tm1637 data wrong size");
    irq_disable();
    if(s->timer.waketime == 0) {
        memset(&s->timer, 0, sizeof(s->timer));
        s->timer.waketime = timer_read_time() + timer_from_us(TIMER_WAIT_TIME_US);
        s->timer.func = tm1637_timer_step;
        sched_add_timer(&s->timer);
        memcpy(&s->data, data, data_len);
        s->bit_position = 0;
        s->step = 0;
    }
    irq_enable();
}
DECL_COMMAND(command_tm1637_send, "tm1637_send oid=%c data=%*s");
