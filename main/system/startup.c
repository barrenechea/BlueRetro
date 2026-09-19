/*
 * SPDX-FileCopyrightText: 2015-2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Vendored from ESP-IDF startup.c so BlueRetro can start the APP CPU as
 * bare metal before heap_caps_init(). See init_app_cpu_baremetal() in
 * bare_metal_app_cpu.c. Constructors use __libc_init_array() as IDF 6 does.
 */

#include <stdint.h>
#include <string.h>

#include "esp_private/esp_system_attr.h"
#include "esp_err.h"
#include "esp_compiler.h"
#include "esp_macros.h"

#include "esp_system.h"
#include "esp_log.h"

#include "sdkconfig.h"

#include "soc/soc_caps.h"
#include "esp_cpu.h"

#include "esp_private/startup_internal.h"

#ifdef BLUERETRO
#include "bare_metal_app_cpu.h"
#endif

// Ensure that system configuration matches the underlying number of cores.
// This should enable us to avoid checking for both every time.
#if !(SOC_CPU_CORES_NUM > 1) && !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
#error "System has been configured to run on multiple cores, but target SoC only has a single core."
#endif

#ifndef BLUERETRO
uint64_t g_startup_time = 0;
#endif

// App entry point for core 0
extern void esp_startup_start_app(void);

// Entry point for core 0 from hardware init (port layer)
#ifdef BLUERETRO
void ld_include_my_startup_file() {}
void start_cpu0(void) __attribute__((alias("start_cpu0_default"))) __attribute__((noreturn));
#else
void start_cpu0(void) __attribute__((weak, alias("start_cpu0_default"))) __attribute__((noreturn));
#endif

#if !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
// Entry point for core [1..X] from hardware init (port layer)
void start_cpu_other_cores(void) __attribute__((weak, alias("start_cpu_other_cores_default"))) __attribute__((noreturn));

// App entry point for core [1..X]
void esp_startup_start_app_other_cores(void) __attribute__((weak, alias("esp_startup_start_app_other_cores_default"))) __attribute__((noreturn));

static volatile bool s_system_inited[SOC_CPU_CORES_NUM] = { false };

const sys_startup_fn_t g_startup_fn[SOC_CPU_CORES_NUM] = { [0] = start_cpu0,
#if SOC_CPU_CORES_NUM > 1
                                                           [1 ... SOC_CPU_CORES_NUM - 1] = start_cpu_other_cores
#endif
                                                         };

static volatile bool s_system_full_inited = false;
#else
#ifndef BLUERETRO
const sys_startup_fn_t g_startup_fn[1] = { start_cpu0 };
#endif
#endif

ESP_LOG_ATTR_TAG(TAG, "cpu_start");

/* declare the start and stop symbols surrounding the array of init functions
 * registered by calling the system init function macros */
_SECTION_ATTR_SYMBOL_DECL_GENERIC(esp_system_init_fn_t, esp_sys_init_fn)

/**
 * @brief Call component init functions defined using the system init function macros.
 * The esp_system_init_fn_t structures describing these functions are collected into
 * an array [_esp_sys_init_fn_start, _esp_sys_init_fn_end) by the
 * linker. The functions are sorted by their priority value.
 * The sequence of the init function calls (sorted by priority) is documented in
 * system_init_fn.txt file.
 * @param stage_num Stage number of the init function call (0, 1).
 */
__attribute__((no_sanitize_undefined)) /* TODO: IDF-8133 */
static void do_system_init_fn(uint32_t stage_num)
{
    const esp_system_init_fn_t *p;

    int core_id = esp_cpu_get_core_id();
    for (p = _SECTION_START(esp_sys_init_fn); p < _SECTION_END(esp_sys_init_fn); ++p) {
        if (p->stage == stage_num && (p->cores & BIT(core_id)) != 0) {
            // During core init, stdout is not initialized yet, so use early logging.
            ESP_EARLY_LOGD(TAG, "calling init function: %p on core: %d", p->fn, core_id);
            esp_err_t err = (*(p->fn))();
            if (err != ESP_OK) {
                ESP_EARLY_LOGE(TAG, "init function %p has failed (0x%x), aborting", p->fn, err);
                abort();
            }
        }
    }

#if !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
    s_system_inited[core_id] = true;
#endif
}

#if !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
static void  esp_startup_start_app_other_cores_default(void)
{
    while (1) {
        esp_rom_delay_us(UINT32_MAX);
    }
}

/* This function has to be in IRAM, as while it is running on CPU1, CPU0 may do some flash operations
 * (e.g. initialize the core dump), which means that cache will be disabled.
 */
static void ESP_SYSTEM_IRAM_ATTR start_cpu_other_cores_default(void)
{
    do_system_init_fn(ESP_SYSTEM_INIT_STAGE_SECONDARY);

    while (!s_system_full_inited) {
        esp_rom_delay_us(100);
    }

    esp_startup_start_app_other_cores();
}
#endif

static void do_core_init(void)
{
    do_system_init_fn(ESP_SYSTEM_INIT_STAGE_CORE);
}

static void do_secondary_init(void)
{
#if !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
    // The port layer transferred control to this function with other cores 'paused',
    // resume execution so that cores might execute component initialization functions.
    startup_resume_other_cores();
#endif

    // Execute initialization functions esp_system_init_fn_t assigned to the main core. While
    // this is happening, all other cores are executing the initialization functions
    // assigned to them since they have been resumed already.
    do_system_init_fn(ESP_SYSTEM_INIT_STAGE_SECONDARY);

#if !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
    // Wait for all cores to finish secondary init.
    volatile bool system_inited = false;

    while (!system_inited) {
        system_inited = true;
        for (int i = 0; i < SOC_CPU_CORES_NUM; i++) {
            system_inited &= s_system_inited[i];
        }
        esp_rom_delay_us(100);
    }
#endif
}

static void start_cpu0_default(void)
{
    extern void __libc_init_array(void);

#ifdef BLUERETRO
    // Init Core1
    init_app_cpu_baremetal();
    ESP_EARLY_LOGI(TAG, "App cpu up.");
#endif

    // Initialize core components and services.
    // Operations that needs the cache to be disabled have to be done here.
    do_core_init();

    // Execute constructors.
    __libc_init_array();

    /* ----------------------------------Separator-----------------------------
     * After this stage, other CPU start running with the cache, however the scheduler (and ipc service) is not available.
     * Don't touch the cache/MMU until the OS is up.
     */

    // Execute init functions of other components; blocks
    // until all cores finish (when !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE).
    do_secondary_init();

#if SOC_CPU_CORES_NUM > 1 && !CONFIG_ESP_SYSTEM_SINGLE_CORE_MODE
    s_system_full_inited = true;
#endif

    esp_startup_start_app();

    ESP_INFINITE_LOOP();
}
