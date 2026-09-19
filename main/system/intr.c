/*
 * Copyright (c) 2021, Jacques Gagnon
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdbool.h>
#include <esp32/rom/ets_sys.h>
#include <esp_cpu.h>
#include <xt_instr_macros.h>
#include <xtensa/xt_specreg.h>
#include "intr.h"

#define INT_MUX_DISABLED_INTNO 6

/*
-------------------------------------------------------------------------------
  Call this function to disable non iram located interrupts.
    newmask       - mask containing the interrupts to disable.
-------------------------------------------------------------------------------
*/
static inline uint32_t xt_int_disable_mask(uint32_t newmask)
{
    uint32_t oldint = 0;
    uint32_t masked;

    XSR(XT_REG_INTENABLE, oldint);
    asm volatile ("rsync");
    masked = oldint & newmask;
    WSR(XT_REG_INTENABLE, masked);
    asm volatile ("rsync");

    return oldint;
}

/*
-------------------------------------------------------------------------------
  Call this function to enable non iram located interrupts.
    newmask       - mask containing the interrupts to enable.
-------------------------------------------------------------------------------
*/
static inline void xt_int_enable_mask(uint32_t newmask)
{
    uint32_t oldint = 0;

    XSR(XT_REG_INTENABLE, oldint);
    asm volatile ("rsync");
    oldint |= newmask;
    WSR(XT_REG_INTENABLE, oldint);
    asm volatile ("rsync");
}

int32_t intexc_alloc_iram(uint32_t source, uint32_t intr_num, XT_INTEXC_HOOK handler) {
    uint32_t intr_level = 0;
    uint32_t core_id = esp_cpu_get_core_id();

    switch (intr_num) {
        case 19:
        case 20:
        case 21:
            intr_level = 2;
            break;
        case 23:
            intr_level = 3;
            break;
        default:
            return -1;
    }

    _xt_intexc_hooks[intr_level] = handler;
    intr_matrix_set(core_id, source, intr_num);
    xt_int_enable_mask(1 << intr_num);

    return 0;
}

int32_t intexc_free_iram(uint32_t source, uint32_t intr_num) {
    uint32_t intr_level = 0;
    uint32_t core_id = esp_cpu_get_core_id();

    switch (intr_num) {
        case 19:
        case 20:
        case 21:
            intr_level = 2;
            break;
        case 23:
            intr_level = 3;
            break;
        default:
            return -1;
    }

    xt_int_disable_mask(1 << intr_num);
    intr_matrix_set(core_id, source, INT_MUX_DISABLED_INTNO);
    _xt_intexc_hooks[intr_level] = 0;

    return 0;
}
