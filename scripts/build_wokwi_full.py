"""Generate firmware/wokwi-full/: the complete SAAYA Node in Wokwi, running the real firmware.

    python scripts/build_wokwi_full.py

sketch.ino is firmware/src/main.cpp with the field build flag defined, controller.h is copied, and
diagram.json wires every part to the same ESP32 pins as the hardware. Also writes a zip of the
project for the website (site/downloads/saaya-node-wokwi.zip).
"""
from pathlib import Path
import json, zipfile

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / 'firmware'
OUT = FW / 'wokwi-full'

sketch = ('// SAAYA Node firmware for Wokwi. GENERATED from firmware/src/main.cpp by scripts/build_wokwi_full.py.\n'
          '// Field build: automatic fan band enabled (same as `pio run -e esp32dev_field`).\n'
          '#define SAAYA_BENCH_AUTO 1\n' + (FW / 'src' / 'main.cpp').read_text())
(OUT / 'sketch.ino').write_text(sketch)
(OUT / 'controller.h').write_text((FW / 'include' / 'controller.h').read_text())

(OUT / 'libraries.txt').write_text("""# Wokwi Library List (same versions as firmware/platformio.ini)
Adafruit SHT31 Library@2.2.2
Adafruit SSD1306@2.5.13
Adafruit GFX Library
Adafruit BusIO
Adafruit INA219@1.2.3
DallasTemperature@3.11.0
OneWire@2.3.8
ArduinoJson@7.3.0
""")

P = lambda t, i, top, left, attrs=None: {'type': t, 'id': i, 'top': top, 'left': left, 'attrs': attrs or {}}
parts = [
    P('board-esp32-devkit-c-v4', 'esp', 0, 0),
    # right: I2C bus
    P('board-ssd1306', 'oled', -150, 230, {'i2cAddress': '0x3c'}),
    P('chip-sht30', 'seat', -40, 260, {'address': '68', 'temperature': '33.4', 'humidity': '49'}),
    P('chip-sht30', 'reference', 60, 260, {'address': '69', 'temperature': '35.8', 'humidity': '44'}),
    P('chip-saaya-fan', 'fan', 170, 250),
    P('wokwi-ds18b20', 'roof', 280, 250),
    P('wokwi-resistor', 'r_dq', 290, 160, {'value': '4700'}),
    # left: operator interface
    P('wokwi-pushbutton', 'btn_mode', 40, -230, {'color': 'blue', 'label': 'MODE'}),
    P('wokwi-pushbutton', 'btn_help', 110, -230, {'color': 'red', 'label': 'HELP'}),
    P('wokwi-pushbutton', 'btn_ack', 180, -230, {'color': 'black', 'label': 'ACK (side)'}),
    P('wokwi-led', 'led', -60, -150, {'color': 'red', 'label': 'HELP/FAULT'}),
    P('wokwi-resistor', 'r_led', 0, -170, {'value': '330'}),
    P('wokwi-buzzer', 'buzzer', 250, -190, {'volume': '0.1'}),
    P('wokwi-slide-switch', 'float', -120, -60, {'label': 'FLOAT: left = water OK'}),
    P('wokwi-resistor', 'r_float', -70, -120, {'value': '10000'}),
    P('wokwi-resistor', 'r_tach', 230, 140, {'value': '10000'}),
]
G, V3 = 'esp:GND.1', 'esp:3V3'
C = lambda a, b, color='green': [a, b, color, []]
conns = [
    ['esp:TX', '$serialMonitor:RX', '', []], ['esp:RX', '$serialMonitor:TX', '', []],
    C('oled:SDA', 'esp:21', 'blue'), C('oled:SCL', 'esp:22', 'gold'), C('oled:VCC', V3, 'red'), C('oled:GND', G, 'black'),
    C('seat:SDA', 'esp:21', 'blue'), C('seat:SCL', 'esp:22', 'gold'), C('seat:VCC', V3, 'red'), C('seat:GND', G, 'black'), C('seat:ADDR', G, 'black'),
    C('reference:SDA', 'esp:21', 'blue'), C('reference:SCL', 'esp:22', 'gold'), C('reference:VCC', V3, 'red'), C('reference:GND', G, 'black'), C('reference:ADDR', V3, 'red'),
    C('fan:SDA', 'esp:21', 'blue'), C('fan:SCL', 'esp:22', 'gold'), C('fan:VCC', V3, 'red'), C('fan:GND', G, 'black'),
    C('fan:PWM', 'esp:25', 'green'), C('fan:TACH', 'esp:34', 'orange'), C('r_tach:1', 'esp:34', 'orange'), C('r_tach:2', V3, 'red'),
    C('roof:DQ', 'esp:4', 'green'), C('roof:VCC', V3, 'red'), C('roof:GND', G, 'black'), C('r_dq:1', 'roof:DQ', 'green'), C('r_dq:2', V3, 'red'),
    C('btn_mode:1.l', 'esp:32'), C('btn_mode:2.l', G, 'black'),
    C('btn_help:1.l', 'esp:33'), C('btn_help:2.l', G, 'black'),
    C('btn_ack:1.l', 'esp:27'), C('btn_ack:2.l', G, 'black'),
    C('esp:26', 'r_led:1'), C('r_led:2', 'led:A'), C('led:C', G, 'black'),
    C('esp:14', 'buzzer:2'), C('buzzer:1', G, 'black'),
    C('float:2', 'esp:35'), C('float:1', G, 'black'), C('r_float:1', 'esp:35'), C('r_float:2', V3, 'red'),
]
diagram = {'version': 1, 'author': 'Safal Gupta (23BCT0237) - SAAYA Node', 'editor': 'wokwi', 'parts': parts, 'connections': conns, 'dependencies': {}}
(OUT / 'diagram.json').write_text(json.dumps(diagram, indent=1) + '\n')

# VS Code / wokwi-cli: build the chips with `make -C firmware/wokwi-full`, firmware with `pio run -e esp32dev_field`
(OUT / 'wokwi.toml').write_text("""# Wokwi for VS Code / wokwi-cli. First: `pio run -d firmware -e esp32dev_field` and `make -C firmware/wokwi-full`.
[wokwi]
version = 1
firmware = '../.pio/build/esp32dev_field/firmware.bin'
elf = '../.pio/build/esp32dev_field/firmware.elf'

[[chip]]
name = 'sht30'
binary = 'dist/sht30.chip.wasm'

[[chip]]
name = 'saaya-fan'
binary = 'dist/saaya-fan.chip.wasm'
""")
(OUT / 'Makefile').write_text("""# Build the Wokwi custom chips (needs clang with the wasm32-wasi sysroot).
CFLAGS = --target=wasm32-unknown-wasi -nostartfiles -Wl,--import-memory -Wl,--export-table -Wl,--no-entry -Werror -O2 -I vendor
all: dist/sht30.chip.wasm dist/saaya-fan.chip.wasm
dist/%.chip.wasm: %.chip.c %.chip.json vendor/wokwi-api.h
\tmkdir -p dist && clang $(CFLAGS) -o $@ $< && cp $*.chip.json dist/
clean:
\trm -rf dist
""")

web_files = ['sketch.ino', 'controller.h', 'diagram.json', 'libraries.txt', 'sht30.chip.json', 'sht30.chip.c', 'saaya-fan.chip.json', 'saaya-fan.chip.c', 'README.md']
dl = ROOT / 'site' / 'downloads' / 'saaya-node-wokwi.zip'
with zipfile.ZipFile(dl, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in web_files:
        z.write(OUT / f, f'saaya-node-wokwi/{f}')
print('wrote', OUT, 'and', dl)
