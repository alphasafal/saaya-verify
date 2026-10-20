// SPDX-License-Identifier: MIT
// Sensirion SHT30 temperature / humidity sensor (I2C) for Wokwi.
// Implements the commands the Adafruit SHT31 library (and SHT30, identical protocol) uses:
//   0x30A2 soft reset, 0xF32D read status, 0x3041 clear status, 0x306D/0x3066 heater on/off,
//   0x2400/0x240B/0x2416 and 0x2C06/0x2C0D/0x2C10 single-shot measurement,
// returning 16-bit raw words each followed by the datasheet CRC-8 (poly 0x31, init 0xFF).
// Attributes / controls: address (68 = 0x44 ADDR low, 69 = 0x45 ADDR high), temperature (°C),
// humidity (%RH), connected (1 = answers, 0 = NACK, i.e. unplugged).
#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
  uint32_t temperature, humidity, connected;
  uint32_t address;
  uint16_t cmd;
  uint8_t cmd_len;
  uint8_t out[6];
  uint8_t out_len, out_pos;
  bool heater;
} chip_state_t;

static uint8_t crc8(const uint8_t *d, int n) {
  uint8_t c = 0xFF;
  for (int i = 0; i < n; i++) {
    c ^= d[i];
    for (int b = 0; b < 8; b++) c = (c & 0x80) ? (uint8_t)((c << 1) ^ 0x31) : (uint8_t)(c << 1);
  }
  return c;
}

static void put_word(chip_state_t *s, uint16_t w) {
  uint8_t *p = &s->out[s->out_len];
  p[0] = (uint8_t)(w >> 8);
  p[1] = (uint8_t)(w & 0xFF);
  p[2] = crc8(p, 2);
  s->out_len += 3;
}

static uint16_t raw(float v) {
  if (v < 0) v = 0;
  if (v > 65535.0f) v = 65535.0f;
  return (uint16_t)(v + 0.5f);
}

static void execute(chip_state_t *s) {
  s->out_len = 0;
  s->out_pos = 0;
  switch (s->cmd) {
    case 0x2400: case 0x240B: case 0x2416:
    case 0x2C06: case 0x2C0D: case 0x2C10: {
      float t = attr_read_float(s->temperature);
      float h = attr_read_float(s->humidity);
      if (h < 0) h = 0;
      if (h > 100) h = 100;
      put_word(s, raw((t + 45.0f) / 175.0f * 65535.0f));
      put_word(s, raw(h / 100.0f * 65535.0f));
      break;
    }
    case 0xF32D: put_word(s, s->heater ? 0x2000 : 0x0000); break;
    case 0x30A2: s->heater = false; break;
    case 0x306D: s->heater = true; break;
    case 0x3066: s->heater = false; break;
    case 0x3041: break;
    default: printf("SHT30 0x%02X: unknown command 0x%04X\n", (unsigned)s->address, (unsigned)s->cmd); break;
  }
}

static bool on_connect(void *user_data, uint32_t address, bool read) {
  chip_state_t *s = user_data;
  if (!attr_read(s->connected)) return false;     // unplugged: no ACK
  if (!read) s->cmd_len = 0;
  else s->out_pos = 0;
  return true;
}

static uint8_t on_read(void *user_data) {
  chip_state_t *s = user_data;
  return s->out_pos < s->out_len ? s->out[s->out_pos++] : 0xFF;
}

static bool on_write(void *user_data, uint8_t data) {
  chip_state_t *s = user_data;
  if (s->cmd_len == 0) { s->cmd = (uint16_t)(data << 8); s->cmd_len = 1; }
  else if (s->cmd_len == 1) { s->cmd |= data; s->cmd_len = 2; execute(s); }
  return true;
}

void chip_init(void) {
  chip_state_t *s = calloc(1, sizeof(chip_state_t));
  s->address = attr_init("address", 0x44);
  s->temperature = attr_init_float("temperature", 33.0f);
  s->humidity = attr_init_float("humidity", 50.0f);
  s->connected = attr_init("connected", 1);
  uint32_t addr = attr_read(s->address);
  s->address = addr;
  const i2c_config_t cfg = {
    .user_data = s,
    .address = addr,
    .scl = pin_init("SCL", INPUT_PULLUP),
    .sda = pin_init("SDA", INPUT_PULLUP),
    .connect = on_connect,
    .read = on_read,
    .write = on_write,
    .disconnect = 0,
  };
  i2c_init(&cfg);
  printf("SHT30 ready at 0x%02X\n", (unsigned)addr);
}
