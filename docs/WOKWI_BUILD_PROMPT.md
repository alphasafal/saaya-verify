# Prompt: build the complete SAAYA Node simulation in Wokwi

Copy everything below the line into ChatGPT, Claude, Gemini or Wokwi’s AI assistant. It is self-contained: the AI needs nothing else.

---

You are an expert embedded engineer and Wokwi power user. Build a **complete, working Wokwi simulation** (wokwi.com, ESP32 Arduino project) of the **SAAYA Node**. The SAAYA Node is the IoT controller of the SAAYA cool shelter, a rest shelter for outdoor workers in Vellore, India. The simulation will be shown live to examiners, so it must compile on the first try, run without errors and show every behaviour listed in the acceptance tests.

## 1. What you must deliver

Give me **every file in full**, each in its own code block headed by its exact file name. No placeholders, no “…”, no “rest unchanged”.

| File | Purpose |
|---|---|
| `sketch.ino` | Complete firmware (Section 6) |
| `controller.h` | Control rules, copied **verbatim** from Section 6.1 |
| `diagram.json` | Every part and wire (Sections 3 and 4) |
| `libraries.txt` | Arduino libraries (Section 7) |
| `sht30.chip.json` + `sht30.chip.c` | Custom chip: Sensirion SHT30 sensor (Section 5.1) |
| `saaya-fan.chip.json` + `saaya-fan.chip.c` | Custom chip: fan branch = 2N3904 driver + 4-wire PWM fan + INA219 (Section 5.2) |

Then give me (a) numbered steps to put the files into a new project at https://wokwi.com/projects/new/esp32, and (b) a 3-minute demo script based on Section 9.

## 2. The real hardware being simulated

| Function | Real part | In Wokwi |
|---|---|---|
| Microcontroller | ESP32-DevKitC V4 (ESP32-WROOM-32) | `board-esp32-devkit-c-v4` |
| Seat air temperature/RH (1.1 m, in a radiation shield) | Sensirion SHT30, I²C 0x44 (ADDR → GND) | custom chip `chip-sht30` |
| Outside reference temperature/RH (≥ 2 m away) | Sensirion SHT30, I²C 0x45 (ADDR → 3V3) | custom chip `chip-sht30` |
| Roof lining temperature | DS18B20 probe, 1-Wire, 4.7 kΩ pull-up | `wokwi-ds18b20` + `wokwi-resistor` |
| Fan power monitor | TI INA219, I²C 0x40, 0.1 Ω shunt, high side of 12 V fan supply | inside custom chip `chip-saaya-fan` |
| Fan | Arctic P12 Pro 120 mm, 12 V, 4-wire PWM (25 kHz), tach 2 pulses/rev | inside custom chip `chip-saaya-fan` |
| Fan driver | 2N3904 NPN, 1 kΩ base resistor; GPIO HIGH pulls fan PWM LOW (inverted) | inside custom chip `chip-saaya-fan` |
| Display | SSD1306 0.96″ 128×64 OLED, I²C 0x3C | `board-ssd1306` |
| Buttons | 3 × 12 mm IP65 push buttons to GND (MODE, HELP on front; ACK on side wall, for staff) | `wokwi-pushbutton` × 3 |
| Help/fault LED | Red LED + 330 Ω | `wokwi-led` + `wokwi-resistor` |
| Buzzer | SFM-27 12 V active buzzer via 2N3904 | `wokwi-buzzer` (driven directly) |
| Drinking-water level | PP float switch (closed = water OK) + 10 kΩ pull-up | `wokwi-slide-switch` + `wokwi-resistor` |
| Power | 12 V 2 A adapter → 1 A fuse → MP1584 buck to 5 V → board 3.3 V regulator | not simulated (Wokwi powers the board) |

Wokwi has no SHT3x, INA219 or 4-wire fan part. That is why two custom chips are needed. Write them in C with the Wokwi Custom Chips API (`#include "wokwi-api.h"`).

## 3. Pin map (must match exactly)

| ESP32 pin | Signal | Notes |
|---|---|---|
| IO21 | I²C SDA | OLED, both SHT30s, fan chip (INA219) |
| IO22 | I²C SCL | same bus; firmware runs it at 50 kHz |
| IO25 | Fan PWM out | 25 kHz, 8-bit; inverted by the 2N3904 |
| IO34 | Fan tach in | input-only pin: **needs an external 10 kΩ pull-up to 3V3** |
| IO35 | Float switch in | input-only pin: **needs an external 10 kΩ pull-up to 3V3**; switch to GND |
| IO4 | DS18B20 data | 4.7 kΩ pull-up to 3V3 |
| IO32 | MODE button | to GND, internal pull-up |
| IO33 | HELP button | to GND, internal pull-up |
| IO27 | ACK button | to GND, internal pull-up |
| IO26 | LED | through 330 Ω to LED anode, cathode to GND |
| IO14 | Buzzer | buzzer pin 2; buzzer pin 1 to GND |
| 3V3, GND.1 | power | every module’s VCC/GND |

Avoid strapping pins (0, 2, 12, 15) and flash pins (6–11).

## 4. diagram.json requirements

- Part ids: `esp`, `oled`, `seat`, `reference`, `fan`, `roof`, `r_dq`, `btn_mode`, `btn_help`, `btn_ack`, `led`, `r_led`, `buzzer`, `float`, `r_float`, `r_tach`.
- Attributes:
  - `oled`: `{"i2cAddress":"0x3c"}`
  - `seat`: `{"address":"68","temperature":"33.4","humidity":"49"}` (68 = 0x44)
  - `reference`: `{"address":"69","temperature":"35.8","humidity":"44"}` (69 = 0x45)
  - resistors: `r_dq` 4700, `r_led` 330, `r_float` 10000, `r_tach` 10000
  - buttons: colours blue (MODE), red (HELP), black (ACK, label `ACK (side)`)
  - LED: red
  - buzzer: `{"volume":"0.1"}`
- Custom chip part types are `chip-` + the chip file name: `chip-sht30` and `chip-saaya-fan`.
- Connections:
  - Serial: `esp:TX`→`$serialMonitor:RX` and `esp:RX`→`$serialMonitor:TX`.
  - I²C: every I²C device’s SDA→`esp:21` and SCL→`esp:22`.
  - Power: every module’s VCC→`esp:3V3` and GND→`esp:GND.1`.
  - SHT30 addresses: `seat:ADDR`→GND and `reference:ADDR`→`esp:3V3`.
  - Fan: `fan:PWM`→`esp:25`, `fan:TACH`→`esp:34`, `r_tach` between `esp:34` and `esp:3V3`.
  - Roof probe: `roof:DQ`→`esp:4`, `r_dq` between DQ and 3V3.
  - Buttons: `btn_*:1.l`→pin and `btn_*:2.l`→GND.
  - LED: `esp:26`→`r_led:1`, `r_led:2`→`led:A`, `led:C`→GND.
  - Buzzer: `esp:14`→`buzzer:2`, `buzzer:1`→GND.
  - Float: `float:2`→`esp:35`, `float:1`→GND, `r_float` between `esp:35` and 3V3.
- Layout: ESP32 in the centre. The I²C devices (OLED, seat, reference, fan, roof probe) go in a column on the right, and the buttons, LED, buzzer and float switch on the left. Wire colours: blue SDA, gold SCL, red 3V3, black GND, green/orange signals.

## 5. Custom chips (exact behaviour)

### 5.1 `sht30` — Sensirion SHT30

`sht30.chip.json`: name `SHT30`, pins `["VCC","GND","SDA","SCL","ADDR"]`. Three controls (type `range`):

| id | range | step |
|---|---|---|
| `temperature` (°C) | 20 to 47 | 0.1 |
| `humidity` (%RH) | 5 to 95 | 1 |
| `connected` (1 = yes, 0 = unplugged) | 0 to 1 | 1 |

`sht30.chip.c`:
- In `chip_init()`, read these attributes:
  - `attr_init("address", 0x44)`
  - `attr_init_float("temperature", 33.0)`
  - `attr_init_float("humidity", 50.0)`
  - `attr_init("connected", 1)`
- Register one I²C device with `i2c_init` at that address. SDA and SCL use `pin_init(..., INPUT_PULLUP)`.
- `connect(user_data, address, read)` returns **false (NACK) when `connected` is 0**. Otherwise:
  - on a write it resets the command byte counter;
  - on a read it rewinds the output buffer.
- `write` collects 2 bytes into a 16-bit command and then executes it:
  - `0x2400`, `0x240B`, `0x2416`, `0x2C06`, `0x2C0D`, `0x2C10` (single-shot measurement): prepare 6 bytes `[T_msb, T_lsb, CRC, RH_msb, RH_lsb, CRC]`, where
    - `T_raw = round((T + 45) / 175 × 65535)`
    - `RH_raw = round(RH / 100 × 65535)`
    - both are clamped to 0…65535, and RH to 0…100 first.
  - `0xF32D` (status): 3 bytes, `0x0000` (or `0x2000` if the heater is on) + CRC.
  - `0x30A2` soft reset (heater off), `0x306D` heater on, `0x3066` heater off, `0x3041` clear status: no data.
- `read` returns the next prepared byte, or `0xFF` when none is left. Always read the **current** control values with `attr_read_float` when a measurement command arrives, so the sliders work live.
- **CRC-8** per the Sensirion datasheet: polynomial 0x31, initial value 0xFF, no reflection, no final XOR. Check value: CRC(0xBE, 0xEF) = 0x92.
- This must satisfy the Adafruit SHT31 library:
  - `begin()`: an empty write must ACK; soft reset; status must not be 0xFFFF.
  - `readTemperature()` / `readHumidity()`: command 0x2400, 20 ms wait, then read 6 bytes, with both CRCs checked.

### 5.2 `saaya-fan` — 2N3904 + Arctic P12 Pro + INA219

`saaya-fan.chip.json`: name `SAAYA fan branch (2N3904 + P12 Pro + INA219)`, pins `["VCC","GND","SDA","SCL","PWM","TACH"]`. Controls (range 0 to 1, step 1):

| id | label |
|---|---|
| `blocked` | fan blocked, 1 = rotor stalled |
| `tachCut` | tach wire cut |
| `inaConnected` | INA219 connected, 1 = yes |

`saaya-fan.chip.c`:
- **PWM input with inversion:**
  - `PWM` is an INPUT connected to ESP32 IO25.
  - Estimate the GPIO duty by **sampling** the pin with a repeating timer every **997 µs**. Don’t watch 25 kHz edges; that is too slow in the simulator.
  - Average over 200 samples (≈ 0.2 s): `gpio_high = highs / samples`.
  - The fan sees `fan_in = 1 − gpio_high`, because the transistor inverts it.
  - Start with `gpio_high = 1`: at boot the firmware drives IO25 HIGH, so the fan is stopped.
- **Fan physics** (timer every 10 ms):
  - Target speed:
    - `target = 0` if blocked or `fan_in < 0.05` (P12 Pro stops below 5 %);
    - otherwise `target = 450 + 2550 × (fan_in − 0.05) / 0.95` rpm (≈ 3000 rpm at 100 %).
  - First-order response: `rpm += (target − rpm) × (1 − e^(−10/τ))`, with τ = 1200 ms speeding up and 2500 ms slowing down. Blocked means rpm = 0 at once.
  - Current in amps:
    - blocked with `fan_in ≥ 0.05`: 0.05 A (locked-rotor protection);
    - otherwise `(fan_in ≥ 0.05 ? 0.03 : 0.01) + 0.30 × (rpm/3000)²`.
- **Tach output:**
  - `TACH` is OUTPUT, starting HIGH.
  - 2 pulses per revolution, so the toggle frequency is `rpm × 2 / 60 × 2` edges per second.
  - Use a one-shot timer that toggles the pin and re-schedules itself with half-period `1e6 / (2 × pulses_per_s)` µs (minimum 50 µs).
  - If rpm < 1 or `tachCut` = 1: hold HIGH and check again in 20 ms.
- **INA219 at I²C 0x40** (NACK when `inaConnected` = 0). Register file of six 16-bit registers:

  | Register | Contents |
  |---|---|
  | 0x00 config | default 0x399F; writing bit 15 resets it |
  | 0x01 shunt | `round(I × 0.1 Ω / 10 µV)` (signed) |
  | 0x02 bus | `(round(Vbus / 4 mV) << 3) \| 0x02`, where `Vbus = 12.0 − I × 0.1` |
  | 0x03 power | `current_reg × bus_raw / 5000` |
  | 0x04 current | `shunt_raw × CAL / 4096` |
  | 0x05 calibration | written by the library (4096 for the 32 V / 2 A setting); while CAL = 0, current and power read 0, like the real chip |

  - Write transaction: first byte = register pointer, next two bytes = value (MSB first), stored for registers 0x00 and 0x05.
  - Read transaction: return MSB then LSB of the register at the pointer.
  - Recompute all values after every physics step and every register write.
  - Check: 0.12 A gives a power register of about 719, i.e. 719 × 2 mW = 1.44 W.
- Print a status line to the Chips Console every 2 s, e.g. `fan: GPIO high 50% -> fan input 50%, 1658 rpm, 0.121 A`.

Both chips must compile with Wokwi’s flags: `clang --target=wasm32-unknown-wasi -nostartfiles -Wl,--import-memory -Wl,--export-table -Wl,--no-entry -Werror`. That means C only, no unused variables, `calloc` for state, callbacks through `user_data`. Call `attr_init`, `i2c_init`, `pin_init` and `timer_init` **only** inside `chip_init()`.

## 6. Firmware (`sketch.ino` + `controller.h`)

### 6.1 `controller.h` — copy exactly, do not change

```cpp
#pragma once
#include <stdint.h>
#include <math.h>
// Pure control logic, shared by the ESP32 firmware and the native unit test.
constexpr float AUTO_ON_C=32.0f, AUTO_OFF_C=31.0f;
// Fan-benefit screen: Morris et al. 2021 (Lancet Planet Health) 39 C young healthy, 38 C >65 y,
// 37 C >65 y on anticholinergics; WHO: fans heat the body above 40 C.
constexpr float FAN_CAUTION_C=37.0f, FAN_AVOID_C=39.0f, FAN_RESUME_C=38.5f;
enum FanAdvice {FAN_OK=0,FAN_CAUTION=1,FAN_AVOID=2,FAN_UNKNOWN=3};
inline FanAdvice fanAdvice(float airC){
 if(!isfinite(airC))return FAN_UNKNOWN;
 return airC>=FAN_AVOID_C?FAN_AVOID:(airC>=FAN_CAUTION_C?FAN_CAUTION:FAN_OK);
}
struct ControlInput {bool help=false,ack=false,manual=false,automatic=false,sensorFault=false; uint32_t now=0; float rpm=0;};
struct ControlState {bool help=false,fanFault=false; int duty=0;uint32_t started=0;};
// Hysteresis: start at >=32 C, keep running until <31 C; unknown temperature never requests.
// Automatic mode also stops where a fan may add heat (>=39 C) and only restarts below 38.5 C.
// Manual mode is never blocked: the worker decides, the display warns.
inline bool autoRequest(bool wasOn,float temp){
 if(!isfinite(temp))return false;
 return wasOn?(temp>=AUTO_OFF_C&&temp<FAN_AVOID_C):(temp>=AUTO_ON_C&&temp<FAN_RESUME_C);
}
inline ControlState step(ControlState prev,ControlInput in){
 ControlState out;
 out.help=(prev.help&&!in.ack)||in.help;            // help wins over a simultaneous ack
 out.duty=in.manual?70:(in.automatic&&!in.sensorFault?50:0);
 out.started=(prev.duty>0&&out.duty>0)?prev.started:in.now;
 out.fanFault=out.duty>0&&uint32_t(in.now-out.started)>=3000&&in.rpm<100;
 return out;
}
```

### 6.2 `sketch.ino` — required behaviour

- First line: `#define SAAYA_BENCH_AUTO 1` (field build: automatic fan enabled). Then include `Arduino.h`, `Wire.h`, `Adafruit_SHT31.h`, `Adafruit_SSD1306.h`, `Adafruit_INA219.h`, `OneWire.h`, `DallasTemperature.h`, `ArduinoJson.h`, `Preferences.h`, `esp_task_wdt.h`, `"controller.h"`.
- **Support both Arduino-ESP32 core 2 and core 3** (Wokwi may use core 3), with these macros:
  ```cpp
  #if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  #define SAAYA_PWM_SETUP(pin) ledcAttach((pin),25000,8)
  #define SAAYA_PWM_WRITE(pin,v) ledcWrite((pin),(v))
  #define SAAYA_WDT_INIT() do{esp_task_wdt_config_t c={};c.timeout_ms=5000;c.idle_core_mask=0;c.trigger_panic=true;esp_task_wdt_reconfigure(&c);}while(0)
  #else
  #define SAAYA_PWM_SETUP(pin) do{ledcSetup(0,25000,8);ledcAttachPin((pin),0);}while(0)
  #define SAAYA_PWM_WRITE(pin,v) ledcWrite(0,(v))
  #define SAAYA_WDT_INIT() esp_task_wdt_init(5,true)
  #endif
  ```
- Pins: `PWM=25, TACH=34, WATER=35, MODE=32, HELP=33, ACK=27, LED=26, BUZZER=14, ROOF=4`.
- **setup()**, in this order:
  1. `Serial.begin(115200)`; `Wire.begin(21,22)`; `Wire.setClock(50000)`; `Wire.setTimeOut(50)`.
  2. IO25 OUTPUT HIGH, `SAAYA_PWM_SETUP(PWM)`, `SAAYA_PWM_WRITE(PWM,255)` (fan off, because the driver inverts).
  3. MODE/HELP/ACK `INPUT_PULLUP`; TACH and WATER plain `INPUT`.
  4. LED and BUZZER OUTPUT.
  5. `attachInterrupt(digitalPinToInterrupt(TACH), tachRise, RISING)`, where `tachRise` (IRAM_ATTR) increments a volatile counter.
  6. `inside.begin(0x44)` (seat), `outside.begin(0x45)` (reference), `powerMeter.begin()`, `display.begin(SSD1306_SWITCHCAPVCC,0x3C)`.
  7. `roof.begin()`, `setWaitForConversion(false)`, `requestTemperatures()`.
  8. `preferences.begin("saaya")`; restore the help latch with `getBool("help",false)`.
  9. Session id `boot-%08lx-%08lx` from `esp_random()`.
  10. `SAAYA_WDT_INIT()`; `esp_task_wdt_add(NULL)`.
- **loop()**, every iteration:
  1. Reset the watchdog.
  2. Debounce MODE/HELP/ACK: a press is counted when the stable level goes LOW after **35 ms** unchanged. MODE toggles `manual`.
  3. `autoOn = SAAYA_BENCH_AUTO && !manual && !sensorFault && autoRequest(autoOn, temp)`.
  4. Build a `ControlInput` and call `step()`.
  5. If `help` changed, save it with `putBool("help", …)`.
  6. `SAAYA_PWM_WRITE(PWM, 255 - duty*255/100)`.
  7. LED = `help || fanFault || sensorFault`; BUZZER = `help && (millis()%1000 < 120)`.
- **Once per second:**
  - `rpm = pulses × 30000 / elapsed_ms` (2 pulses per revolution).
  - Retry `begin()` for any SHT30 that is not OK.
  - Read both SHT30s; a non-finite value marks that sensor not OK.
  - `sensorFault = !inOK || !outOK || RH out of 0–100`.
  - Roof: read the previous DS18B20 conversion (`DEVICE_DISCONNECTED_C` or outside −40…125 → NaN), then request the next one.
  - `water = digitalRead(WATER) == LOW`.
  - INA219: probe 0x40 with `beginTransmission/endTransmission`; if absent, `powerOK=false`; if it returns, `begin()` again. `watts = getPower_mW()/1000` when OK, else NaN.
- **Print one JSON line** per second (ArduinoJson 7), keys in this order:
  - `schema_version:1`, `device_id:"saaya-esp32"`, `session_id`, `seq`
  - `source:"MEASURED"`, `config_id:"bench-v2-fan-branch-power"`, `calibration_id:"UNVERIFIED"`
  - `acquired_ms`, `emitted_ms`
  - `temp`, `rh`, `outdoor_temp`, `outdoor_rh`, `roof_temp`, `watts` (all **null when NaN, never 0**)
  - `rpm`, `duty`, `water:"available"|"low"`, `help`
  - `quality:"valid"|"invalid"`, `fan_fault`, `fan_advice:"ok"|"caution"|"avoid"|"unknown"` (from `fanAdvice`, unknown if sensorFault)
  - `clock_aligned:false`, `reference_valid:false`, `ref_roof:null`, `ref_air_speed:null`, `air_speed:null`
- **OLED** (text size 1, cursor 0,0), five lines exactly:
  1. `SAAYA NODE / MEASURED` (exactly 21 characters, one 128-pixel line)
  2. `T: %.1f RH: %.0f`
  3. `Fan %d%% %.0f RPM`
  4. `Water available` or `WATER LOW / CHECK`
  5. First match in this order:
     - `HELP REQUEST LATCHED` (help latched)
     - `SENSOR FAULT` (sensorFault)
     - `FAN FEEDBACK FAULT` (fan fault)
     - `HOT: FAN MAY ADD HEAT` (advice = avoid)
     - `FAN: LIMITED BENEFIT` (advice = caution)
     - `Not a safety rating` (otherwise)
- Code style: never put a `//` comment in the middle of a long line that has more code after it. Use `/* */` or a new line.

## 7. libraries.txt

```
Adafruit SHT31 Library@2.2.2
Adafruit SSD1306@2.5.13
Adafruit GFX Library
Adafruit BusIO
Adafruit INA219@1.2.3
DallasTemperature@3.11.0
OneWire@2.3.8
ArduinoJson@7.3.0
```

## 8. Acceptance tests (the simulation must pass all of these)

| # | Action | Expected |
|---|---|---|
| 1 | Start the simulation (seat 33.4 °C, reference 35.8 °C) | Within ~5 s (fan spin-up): automatic fan 50 %, OLED `Fan 50% ~1650 RPM`, JSON `"duty":50`, `"quality":"valid"`, `watts` ≈ 1.4–1.6, Chips Console shows the fan at ≈ 1650 rpm |
| 2 | Set the seat chip temperature to 31.5 °C, then 30.9 °C | Fan keeps running at 31.5 (hysteresis), stops below 31 |
| 3 | Seat 40 °C | Automatic fan stops; OLED line 5 `HOT: FAN MAY ADD HEAT`; JSON `"fan_advice":"avoid"` |
| 4 | Press MODE at 40 °C | Manual fan 70 % (≈ 2200 rpm): manual is never blocked |
| 5 | Press MODE again, seat 38.6 °C, then 38.2 °C | No automatic restart at 38.6; restarts at 50 % below 38.5 |
| 6 | Fan chip `blocked` = 1 | After 3 s: `FAN FEEDBACK FAULT`, LED on, JSON `"fan_fault":true`; back to 0 clears it |
| 7 | Fan chip `tachCut` = 1 | Same fault as test 6 |
| 8 | Press HELP | LED on, buzzer beeps once a second, OLED `HELP REQUEST LATCHED`, `"help":true` |
| 9 | Stop and restart the simulation | Help latch is still on (restored from flash) |
| 10 | Press ACK | Help cleared |
| 11 | Reference chip `connected` = 0 | `SENSOR FAULT`, automatic fan off, `outdoor_temp` null, `"quality":"invalid"`; recovers when set back to 1 |
| 12 | Fan chip `inaConnected` = 0 | `"watts":null` |
| 13 | Slide the float switch to the other side | `WATER LOW / CHECK`, `"water":"low"` |
| 14 | Click the DS18B20 and change its temperature | `roof_temp` follows within 2 s |

## 9. Demo script (3 minutes, for examiners)

1. Point at the circuit: the same ESP32 pins as the real interfacing diagram; the serial monitor shows the same JSON the real node sends.
2. Automatic fan at 33 °C (test 1). Then 40 °C: the fan stops, because research shows fans can add heat in very hot air (test 3). Press MODE: the worker can still choose 70 % (test 4).
3. Block the fan: the system reports a fault instead of claiming cooling (test 6).
4. HELP → restart the simulation → still latched → ACK clears it (tests 8–10).
5. Unplug the reference sensor: data is marked invalid and sent as null, never as a guess (test 11).

## 10. Common pitfalls to avoid

- Custom chip files must be named exactly `sht30.chip.json` / `sht30.chip.c` and `saaya-fan.chip.json` / `saaya-fan.chip.c`. The diagram part types are `chip-sht30` and `chip-saaya-fan`. Do **not** add your own `wokwi-api.h`: Wokwi supplies it.
- IO34 and IO35 have no internal pull-ups. The 10 kΩ resistors to 3V3 must be in the diagram.
- The firmware writes **255 − duty×2.55** because the 2N3904 inverts the PWM. The fan chip must invert it back.
- Seat = 0x44 (ADDR to GND), reference = 0x45 (ADDR to 3V3). Do not swap them.
- `ledcSetup`/`ledcAttachPin` do not exist in core 3; use the macros in Section 6.2.
- Missing data must be `null` in JSON and `nan` on the OLED, never 0.
- Chips must use timers for physics. Never block or busy-wait inside a callback.

When finished, list which acceptance tests you expect to pass and anything you could not verify.
