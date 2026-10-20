// SPDX-License-Identifier: MIT
// SAAYA fan branch for Wokwi: 2N3904 PWM driver + Arctic P12 Pro 4-wire fan + INA219 power monitor.
//
// PWM pin  <- ESP32 IO25 (through the 1 kOhm base resistor in hardware). GPIO HIGH turns Q1 on and
//             pulls the fan's PWM input LOW, so the fan sees (1 - GPIO duty). The firmware writes
//             255 - duty*2.55 for exactly this reason.
// TACH pin -> ESP32 IO34: 2 pulses per revolution (open collector, 10 kOhm pull-up to 3V3).
// I2C      :  INA219 at 0x40 on the high side of the 12 V fan supply (0.1 Ohm shunt). Registers
//             follow the TI datasheet: current = shunt * CAL / 4096, power = current * bus / 5000.
// Fan model:  0 rpm below 5 % input, otherwise 450 + 2550 * (d - 0.05) / 0.95 rpm, first-order
//             response (1.2 s up, 2.5 s down); current 0.03 + 0.30 * (rpm / 3000)^2 A at 12 V.
// Controls :  blocked (stalled rotor), tachCut (tach wire cut), inaConnected (INA219 answers).
#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
  pin_t pwm, tach;
  uint32_t blocked, tach_cut, ina_connected;
  // PWM duty estimate by sampling (cheaper than watching 25 kHz edges)
  uint32_t samples, highs;
  float gpio_high, fan_in;
  // fan
  float rpm, amps;
  bool tach_level;
  timer_t sample_timer, physics_timer, tach_timer, log_timer;
  // INA219
  uint16_t reg[6];
  uint8_t pointer;
  uint8_t wcount;
  uint16_t rvalue;
  uint8_t rcount;
} chip_state_t;

static void update_ina(chip_state_t *s) {
  const float shunt_ohm = 0.1f, supply = 12.0f;
  float vshunt = s->amps * shunt_ohm;
  float vbus = supply - vshunt;                    // VIN- side, measured to GND
  int32_t shunt_raw = (int32_t)lroundf(vshunt / 10e-6f);
  uint32_t bus_raw = (uint32_t)lroundf(vbus / 0.004f);
  s->reg[1] = (uint16_t)(int16_t)shunt_raw;
  s->reg[2] = (uint16_t)((bus_raw << 3) | 0x02);   // CNVR set
  uint16_t cal = s->reg[5] & 0xFFFE;
  int32_t current = (int32_t)((int64_t)shunt_raw * cal / 4096);
  s->reg[4] = (uint16_t)(int16_t)current;
  s->reg[3] = (uint16_t)((int64_t)current * bus_raw / 5000);
}

static void on_sample(void *user_data) {
  chip_state_t *s = user_data;
  s->samples++;
  if (pin_read(s->pwm)) s->highs++;
  if (s->samples >= 200) {                         // ~0.2 s window
    s->gpio_high = (float)s->highs / (float)s->samples;
    s->fan_in = 1.0f - s->gpio_high;               // Q1 inverts
    s->samples = s->highs = 0;
  }
}

static void schedule_tach(chip_state_t *s);

static void on_tach(void *user_data) {
  chip_state_t *s = user_data;
  if (attr_read(s->tach_cut) || s->rpm < 1.0f) {
    s->tach_level = true;                          // pulled up, no pulses
    pin_write(s->tach, HIGH);
    timer_start(s->tach_timer, 20000, false);      // check again in 20 ms
    return;
  }
  s->tach_level = !s->tach_level;
  pin_write(s->tach, s->tach_level ? HIGH : LOW);
  schedule_tach(s);
}

static void schedule_tach(chip_state_t *s) {
  float pulses_per_s = s->rpm * 2.0f / 60.0f;      // 2 pulses per revolution
  float half_period_us = 1e6f / (2.0f * pulses_per_s);
  if (half_period_us < 50) half_period_us = 50;
  timer_start(s->tach_timer, (uint32_t)half_period_us, false);
}

static void on_physics(void *user_data) {         // every 10 ms
  chip_state_t *s = user_data;
  bool blocked = attr_read(s->blocked) != 0;
  float d = s->fan_in;
  float target = (blocked || d < 0.05f) ? 0.0f : 450.0f + 2550.0f * (d - 0.05f) / 0.95f;
  if (blocked) s->rpm = 0;
  else {
    float tau = target > s->rpm ? 1200.0f : 2500.0f;
    s->rpm += (target - s->rpm) * (1.0f - expf(-10.0f / tau));
    if (s->rpm < 1.0f) s->rpm = 0;
  }
  s->amps = (blocked && d >= 0.05f) ? 0.05f : (d >= 0.05f ? 0.03f : 0.01f) + 0.30f * (s->rpm / 3000.0f) * (s->rpm / 3000.0f);
  update_ina(s);
}

static void on_log(void *user_data) {
  chip_state_t *s = user_data;
  printf("fan: GPIO high %.0f%% -> fan input %.0f%%, %.0f rpm, %.3f A%s%s\n", s->gpio_high * 100, s->fan_in * 100, s->rpm, s->amps,
         attr_read(s->blocked) ? " [BLOCKED]" : "", attr_read(s->tach_cut) ? " [TACH CUT]" : "");
}

static bool i2c_connect(void *user_data, uint32_t address, bool read) {
  chip_state_t *s = user_data;
  if (!attr_read(s->ina_connected)) return false;
  if (read) { s->rvalue = s->reg[s->pointer % 6]; s->rcount = 0; }
  else s->wcount = 0;
  return true;
}

static uint8_t i2c_read(void *user_data) {
  chip_state_t *s = user_data;
  uint8_t b = s->rcount == 0 ? (uint8_t)(s->rvalue >> 8) : (uint8_t)(s->rvalue & 0xFF);
  s->rcount++;
  return b;
}

static bool i2c_write(void *user_data, uint8_t data) {
  chip_state_t *s = user_data;
  if (s->wcount == 0) s->pointer = data;
  else if (s->wcount == 1) s->rvalue = (uint16_t)(data << 8);
  else if (s->wcount == 2) {
    uint16_t v = s->rvalue | data;
    if (s->pointer == 0) s->reg[0] = (v & 0x8000) ? 0x399F : v;   // bit 15 = reset
    else if (s->pointer == 5) s->reg[5] = v;
    update_ina(s);
  }
  s->wcount++;
  return true;
}

void chip_init(void) {
  chip_state_t *s = calloc(1, sizeof(chip_state_t));
  s->pwm = pin_init("PWM", INPUT);
  s->tach = pin_init("TACH", OUTPUT_HIGH);
  s->tach_level = true;
  s->blocked = attr_init("blocked", 0);
  s->tach_cut = attr_init("tachCut", 0);
  s->ina_connected = attr_init("inaConnected", 1);
  s->reg[0] = 0x399F;
  s->gpio_high = 1.0f;                             // boot: firmware drives IO25 HIGH -> fan input 0 %
  const timer_config_t ts = { .user_data = s, .callback = on_sample };
  const timer_config_t tp = { .user_data = s, .callback = on_physics };
  const timer_config_t tt = { .user_data = s, .callback = on_tach };
  const timer_config_t tl = { .user_data = s, .callback = on_log };
  s->sample_timer = timer_init(&ts);
  s->physics_timer = timer_init(&tp);
  s->tach_timer = timer_init(&tt);
  s->log_timer = timer_init(&tl);
  timer_start(s->sample_timer, 997, true);         // not a multiple of the 40 us PWM period
  timer_start(s->physics_timer, 10000, true);
  timer_start(s->tach_timer, 20000, false);
  timer_start(s->log_timer, 2000000, true);
  const i2c_config_t cfg = {
    .user_data = s, .address = 0x40,
    .scl = pin_init("SCL", INPUT_PULLUP), .sda = pin_init("SDA", INPUT_PULLUP),
    .connect = i2c_connect, .read = i2c_read, .write = i2c_write, .disconnect = 0,
  };
  i2c_init(&cfg);
  printf("SAAYA fan branch ready: 2N3904 driver, P12 Pro model, INA219 at 0x40\n");
}
