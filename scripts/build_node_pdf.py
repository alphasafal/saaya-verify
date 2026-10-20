"""Build docs/node/SAAYA_Node_IoT_Design.html (printed to PDF by scripts/print_pdf.cjs).
Dimensions come from cad/node/exports/node.json; prices/specs from the sourced tables below.
Run: python scripts/build_node_pdf.py && node scripts/print_pdf.cjs
"""
from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / 'docs' / 'node'
P = json.loads((ROOT / 'cad/node/exports/node.json').read_text())['parameters']
E = P['enclosure']
e = html.escape

# ---------------- bill of materials (INR incl. GST where shown; checked 20 Oct 2026) ----------------
# (item, model, qty, unit price, status, source key)
BOM = [
    ('Microcontroller', 'ESP32-DevKitC, 38-pin, ESP32-WROOM-32', 1, 499, 'listed', 'probots-esp32'),
    ('Air T/RH (seat + reference)', 'GY-SHT30-D module, Sensirion SHT30', 2, 179, 'listed', 'probots-sht30'),
    ('Roof surface temperature', 'DS18B20 waterproof probe, 1 m', 1, 49, 'listed', 'probots-ds18b20'),
    ('Fan power monitor', 'INA219 module (0.1 Ω shunt class)', 1, 89, 'listed', 'hubtronics-ina219'),
    ('Local display', 'SSD1306 0.96" 128×64 I²C OLED', 1, 130, 'listed', 'robu-oled'),
    ('Actuator', 'Arctic P12 Pro 120 mm 4-wire PWM fan', 1, 910, 'listed', 'md-p12pro'),
    ('PWM + buzzer drivers', '2N3904 NPN, TO-92', 2, 6, 'listed', 'probots-2n3904'),
    ('MODE / HELP / ACK', '12 mm IP65 metal momentary (ProMax)', 3, 159, 'listed', 'probots-btn'),
    ('Status light', '5 mm red LED + 8 mm bezel', 1, 4, 'listed', 'probots-led'),
    ('Help sounder', 'SFM-27 active buzzer, 3–24 V', 1, 60, 'allowance', 'robu-sfm27'),
    ('Water availability', 'PP float switch, reed, NO', 1, 175, 'listed', 'probots-float'),
    ('Power supply', '12 V 2 A SMPS adapter', 1, 189, 'listed', 'probots-smps'),
    ('5 V rail', 'MP1584EN buck module', 1, 49, 'listed', 'robu-mp1584'),
    ('Enclosure', 'ProtechT WPE16 IP65 ABS 175×100×60', 1, 949, 'listed', 'probots-wpe16'),
    ('Cable entries', 'PG7 nylon cable gland', 5, 15, 'listed', 'probots-pg7'),
    ('Protection', '5×20 fuse holder + 1 A T fuse', 1, 19, 'allowance (listed items out of stock)', 'hubtronics-fuse'),
    ('Board + passives', 'perfboard 90×70, headers, resistors, terminal blocks', 1, 150, 'allowance', None),
    ('Power switch / vent', 'rocker switch + M12 breathable vent', 1, 120, 'allowance', None),
    ('Field cable', 'Cat5e STP 10 m (sensor runs)', 1, 250, 'allowance', None),
    ('Radiation shields', '2 × DIY 5-plate PP shield on M5 rods', 1, 300, 'allowance', None),
    ('Mounting', '3 mm Al bracket, M6 anchors / 2 hose clamps, UV conduit', 1, 450, 'allowance', None),
]
total = sum(q * u for _, _, q, u, _, _ in BOM)
listed = sum(q * u for _, _, q, u, s, _ in BOM if s == 'listed')

SRC = {
    'probots-esp32': 'https://probots.co.in/esp32-wroom-32-nodemcu-38-pin-micro-usb-development-board.html',
    'probots-sht30': 'https://probots.co.in/gy-sht30-d-digital-temperature-humidity-sensor-module-i2c.html',
    'probots-ds18b20': 'https://probots.co.in/ds18b20-waterproof-temperature-sensor-for-arduino-raspberry.html',
    'hubtronics-ina219': 'https://hubtronics.in/ina219-m',
    'robu-oled': 'https://st.robu.in/product/0-96-inch-oled',
    'md-p12pro': 'https://mdcomputers.in/product/arctic-p12-pro-120mm-cabinet-fan-acfan00305a',
    'probots-2n3904': 'https://probots.co.in/2n3904-npn-transistor-40v-0-2a-to92.html',
    'probots-btn': 'https://probots.co.in/12mm-promax-pps12005rpm-metal-push-button-switch-waterproof-momentary-red.html',
    'probots-led': 'https://probots.co.in/5mm-red-led-diffused.html',
    'robu-sfm27': 'https://st.robu.in/product/continuous-sound-electronic-active-buzzer-sfm-27-dc-3-24v',
    'probots-float': 'https://probots.co.in/water-level-float-sensor-switch-with-digital-output.html',
    'probots-smps': 'https://probots.co.in/12v-2a-power-supply-smps-adaptor-premium.html',
    'robu-mp1584': 'https://aws.robu.in/?p=2275994',
    'probots-wpe16': 'https://probots.co.in/protecht-ip65-waterproof-plastic-enclosure-wpe16.html',
    'probots-pg7': 'https://probots.co.in/polymide-cable-glands-pg-07.html',
    'hubtronics-fuse': 'https://hubtronics.in/5x20mm-glass-fuse-holder',
}
DS = {
    'ESP32-WROOM-32E datasheet (Espressif)': 'https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
    'ESP32 series datasheet (Espressif)': 'https://documentation.espressif.com/esp32_datasheet_en.pdf',
    'ESP32-DevKitC V4 user guide': 'https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html',
    'SHT3x-DIS datasheet (Sensirion)': 'https://sensirion.com/file/datasheet_sht3x_digital',
    'DS18B20 datasheet (Analog Devices)': 'https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf',
    'INA219 datasheet (TI)': 'https://www.ti.com/lit/ds/symlink/ina219.pdf',
    'SSD1306 controller datasheet': 'https://academy.cba.mit.edu/classes/output_devices/OLED/SSD1306.pdf',
    '2N3904 datasheet (onsemi)': 'https://pages.hmc.edu/mspencer/e151/datasheets/2N3904.pdf',
    'MP1584 datasheet (MPS)': 'https://www.monolithicpower.com/pub/media/document/MP1584_r1.1.pdf',
    'Intel 4-wire PWM fan specification rev 1.2': 'https://www.mikrocontroller.net/attachment/670442/4-Wire_PWM_Controlled_Fans.pdf',
    'Noctua PWM white paper': 'https://cdn.noctua.at/preview/media/Noctua_PWM_specifications_white_paper.pdf',
    'Arctic P12 Pro listing (specs)': 'https://mdcomputers.in/product/arctic-p12-pro-120mm-cabinet-fan-acfan00305a',
    'Wokwi parts / ESP32 simulation docs': 'https://docs.wokwi.com/guides/esp32',
}

SEL = [  # component, chosen, criteria met, rejected alternatives
    ('Microcontroller', 'ESP32-DevKitC (WROOM-32)', '₹499; 2 × I²C, 16 LEDC PWM channels (25 kHz fan PWM), interrupt tach input, Wi-Fi built in, flash for the help latch, hardware watchdog, −40…85 °C', 'Arduino Uno (no Wi-Fi, 2 kB RAM), Raspberry Pi (SD-card corruption on power loss, ~10× power, no hard real-time), ESP8266 (one ADC, fewer GPIO, no 2nd core for the Wi-Fi task)'),
    ('Air temperature / RH (×2)', 'Sensirion SHT30 on GY-SHT30-D', 'Same typical accuracy as SHT31 (±0.2 °C over 0–65 °C, ±2 %RH) at less than half the price (₹179 vs ₹399); digital I²C; 0x44/0x45 lets two share one bus; 0.6 mA while measuring', 'DHT22 (slower, timing-critical 1-wire, poorer RH stability), BME280 (self-heating, pressure not needed), SHT31 (no accuracy gain in our 25–45 °C range)'),
    ('Roof underside temperature', 'DS18B20 waterproof probe', '₹49; ±0.5 °C (−10…85 °C); stainless, sealed; 1-Wire runs on long cable; one GPIO', 'IR thermometer (needs emissivity correction on a metal roof), NTC thermistor (needs ADC calibration, lead resistance)'),
    ('Energy measurement', 'INA219 breakout', '₹89; high-side current + bus voltage 0–26 V on I²C; 0.5 % class; measures the fan branch so energy is measured, not estimated', 'ACS712-5A Hall sensor (185 mV/A: only ≈ 60 mV signal at the 0.33 A fan load, noisy), datasheet power figures (not a measurement)'),
    ('Actuator', 'Arctic P12 Pro, 120 mm, 12 V, 4-wire', 'Tach feedback (2 pulses/rev) proves the fan turns; 25 kHz PWM speed control; 0 rpm below 5 % PWM gives a true off; 77 CFM at 0.33 A (~4 W)', '2-wire fans (no feedback: a stalled fan looks like a running one), 230 V pedestal fan (shock risk in a wet outdoor space, no feedback, 55–125 W)'),
    ('Display', 'SSD1306 0.96" I²C OLED', '₹130; readable status without a phone; shares the I²C bus; ~20 mA', 'LCD 16×2 (needs 5 V and 6 GPIO or an extra I²C backpack), phone app only (workers may not carry phones)'),
    ('Controls', '3 × 12 mm IP65 metal momentary buttons', 'Weatherproof, gloved-hand usable; HELP on the front, ACK on the side so only staff clear a request', 'Membrane keypad (UV/ heat ageing), touch sensor (false triggers with sweat/rain)'),
    ('Alert', 'SFM-27 active buzzer + 5 mm LED', '>95 dB, <12 mA from 12 V via 2N3904; visible + audible help/fault state', 'Passive piezo (needs tone generation, quieter)'),
    ('Water status', 'PP reed float switch', 'Dry contact, no power, cheap; open circuit (incl. broken wire) reads “low / check”', 'Ultrasonic level sensor (cost, condensation errors), capacitive probe (fouling)'),
    ('Power', '12 V 2 A SMPS + MP1584 buck to 5 V + 1 A fuse', '12 V feeds the fan directly; buck gives 5 V for the board at high efficiency; fuse protects the field wiring; ~3.6× current margin', 'Linear 7805 (≈60 % loss at 12→5 V), USB power bank (not for continuous outdoor use)'),
    ('Enclosure', 'ProtechT WPE16 IP65 ABS, 175×100×60', 'Purchasable, IP65, room for the 90×70 board + modules; cable glands down + breathable vent manage monsoon rain and condensation', '3D-printed PETG box (UV and heat creep near 60–70 °C roof air, not IP-rated)'),
]

SPEC = [  # component, supply, current, range, accuracy, interface, size, source key
    ('ESP32-WROOM-32E (DevKitC)', '3.0–3.6 V module; 5 V via board LDO', '20–68 mA modem-sleep; Wi-Fi TX 239 mA avg / 379 mA peak; 10 µA deep sleep', '−40…85 °C', '—', '2 × I²C, LEDC PWM, GPIO, Wi-Fi 802.11 b/g/n', 'board 54.4 × 27.9; module 18 × 25.5 × 3.1', 'ESP32-WROOM-32E datasheet (Espressif)'),
    ('SHT30 (×2)', '2.15–5.5 V (3.3 V used)', '0.6 mA measuring; 0.2 µA idle', '0–100 %RH; −40…125 °C', '±0.2 °C (0–65 °C), ±2 %RH typ; τ63 RH 8 s', 'I²C 0x44 / 0x45', 'small breakout; measure before fixing', 'SHT3x-DIS datasheet (Sensirion)'),
    ('DS18B20 probe', '3.0–5.5 V', '1 mA active; 0.75 µA standby', '−55…125 °C', '±0.5 °C (−10…85 °C); 12-bit, 750 ms', '1-Wire, 4.7 kΩ pull-up', 'Ø6 × 50 mm probe, 1 m lead', 'DS18B20 datasheet (Analog Devices)'),
    ('INA219', '3–5.5 V logic; bus 0–26 V', '0.7 mA', '±3.2 A with 0.1 Ω shunt', '0.5 % max (B grade); 0.8 mA LSB', 'I²C 0x40', '≈ 25 × 22 mm', 'INA219 datasheet (TI)'),
    ('SSD1306 OLED', '3.3–5 V module', '≈ 20 mA fully lit, < 5 mA text', '−40…85 °C', '128 × 64 px, active 21.7 × 10.9 mm', 'I²C 0x3C', '27.5 × 27.5 × 11 mm', 'SSD1306 controller datasheet'),
    ('Arctic P12 Pro fan', '12 V', '0.33 A (~4 W)', '600–3000 rpm; 0 rpm < 5 % PWM', '77 CFM / 131 m³/h; 6.9 mmH₂O', '4-wire: PWM 25 kHz, tach 2 p/rev', '120 × 120 × 25 mm', 'Arctic P12 Pro listing (specs)'),
    ('2N3904 (Q1, Q2)', 'VCEO 40 V', 'IC 200 mA max', '—', 'hFE 100–300 @ 10 mA; VCE(sat) 0.2 V', '4.7 kΩ base, 10 kΩ B-E', 'TO-92', '2N3904 datasheet (onsemi)'),
    ('MP1584EN buck', '4.5–28 V in', '3 A out', '0.8–20 V out (set 5.0 V)', 'IC marked NRND → MP2338 for production', '—', '22 × 17 × 4 mm', 'MP1584 datasheet (MPS)'),
    ('SFM-27 buzzer', '3–24 V (12 V used)', '< 12 mA', '—', '> 95 dB', 'via Q2 on IO14', 'measure before drilling', None),
    ('12 mm IP65 button (×3)', '—', '3 A / 250 V AC contact', '—', 'IP65', 'to GND, internal pull-up', '12 mm panel hole', None),
    ('PP float switch', '—', '0.5 A switching', '−10…60 °C', 'NO reed', 'IO35 + 10 kΩ pull-up', 'measure before fitting', None),
    ('Enclosure WPE16', '—', '—', 'outdoor, shaded mount', 'IP65', '5 × PG7 + M12 vent', f"{E['W']} × {E['H']} × {E['D']} mm", None),
]

PINS = [
    ('IO21 / IO22', 'I²C SDA / SCL @ 50 kHz', 'bidir', '4.7 kΩ to 3V3', 'SHT30 seat 0x44, SHT30 reference 0x45, OLED 0x3C, INA219 0x40'),
    ('IO25', 'Fan PWM 25 kHz (LEDC ch 0)', 'out', '4.7 kΩ → Q1 2N3904, 10 kΩ B-E; output inverted in firmware', 'Fan pin 4 (PWM). ESP32 reset → line floats → fan full speed'),
    ('IO34', 'Fan tach', 'in only', '10 kΩ to 3V3 (no internal pull-up)', 'Fan pin 3, 2 pulses/rev'),
    ('IO4', 'DS18B20 1-Wire', 'bidir', '4.7 kΩ to 3V3', 'Roof underside probe'),
    ('IO35', 'Float switch', 'in only', '10 kΩ to 3V3; closed = water OK', 'Float in water can'),
    ('IO32', 'MODE button', 'in', 'INPUT_PULLUP, 35 ms debounce', 'Front panel'),
    ('IO33', 'HELP button', 'in', 'INPUT_PULLUP; latch stored in flash', 'Front panel (red)'),
    ('IO27', 'ACK button', 'in', 'INPUT_PULLUP', 'Right side wall (staff)'),
    ('IO26', 'Status LED', 'out', '330 Ω (≈ 8 mA)', 'Front panel'),
    ('IO14', 'Buzzer', 'out', '4.7 kΩ → Q2 2N3904 low side', 'SFM-27 on 12 V'),
    ('5V / GND', 'Board supply', 'power', 'MP1584 5.0 V; never with USB connected', 'Common GND star at buck'),
    ('3V3', 'Sensor/logic supply', 'power', 'DevKitC LDO', 'All I²C modules, DS18B20, pull-ups'),
]

POWER = [  # load, rail, typical mA, peak mA, note
    ('ESP32-DevKitC (Wi-Fi off)', '5 V', 70, 70, 'modem-sleep 20–68 mA + LDO'),
    ('ESP32 Wi-Fi uplink (optional)', '5 V', 0, 380, 'TX peak 379 mA'),
    ('OLED', '3.3 V', 10, 20, ''),
    ('SHT30 ×2 + DS18B20 + INA219', '3.3 V', 3, 4, ''),
    ('LED', '3.3 V', 0, 8, 'only on help/fault'),
    ('Fan, Arctic P12 Pro', '12 V', 230, 330, '70 % / 100 % PWM'),
    ('Buzzer', '12 V', 0, 12, 'only on help'),
]


def table(headers, rows, cls=''):
    h = ''.join(f'<th>{e(x)}</th>' for x in headers)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


bom_rows = [(e(a), e(m), q, f'₹{u:,}', f'<b>₹{q * u:,}</b>', e(s)) for a, m, q, u, s, _ in BOM]
bom_rows.append(('<b>Total</b>', f'listed shop prices ₹{listed:,} + allowances ₹{total - listed:,}', '', '', f'<b>₹{total:,}</b>', 'excl. shipping, tools, labour'))

# Power budget numbers
eff = 0.85
r5_typ = sum(t for _, r, t, _, _ in POWER if r in ('5 V', '3.3 V'))
r5_pk = sum(p for _, r, _, p, _ in POWER if r in ('5 V', '3.3 V'))
r12_typ = sum(t for _, r, t, _, _ in POWER if r == '12 V')
r12_pk = sum(p for _, r, _, p, _ in POWER if r == '12 V')
in_typ = r12_typ + 5 * r5_typ / 12 / eff
in_pk = r12_pk + 5 * r5_pk / 12 / eff
w_typ = 12 * in_typ / 1000
w_pk = 12 * in_pk / 1000
wh_day = 12 * r12_typ / 1000 * 8 + 5 * r5_typ / eff / 1000 * 24

CSS = """
@page{size:A4 landscape;margin:12mm 13mm 13mm}
*{box-sizing:border-box}
body{font:9.6pt/1.42 'Helvetica Neue',Helvetica,Arial,sans-serif;color:#1d2622;margin:0}
h1{font-size:25pt;margin:0 0 2mm;letter-spacing:-.02em;color:#17392f}
h2{font-size:15pt;margin:0 0 2.5mm;color:#17392f;border-bottom:1.5px solid #17392f;padding-bottom:1.2mm}
h3{font-size:10.5pt;margin:3mm 0 1mm;color:#17392f}
p{margin:0 0 2mm}
.page{page-break-after:always;break-after:page}
.page:last-child{page-break-after:auto}
.sub{color:#56645d;font-size:10.5pt;margin-bottom:4mm}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.grid3{display:grid;grid-template-columns:1.15fr 1fr;gap:6mm;align-items:start}
table{border-collapse:collapse;width:100%;font-size:8.3pt;margin:1mm 0 2mm}
th{background:#17392f;color:#fff;text-align:left;padding:1.4mm 1.6mm;font-weight:600}
td{border-bottom:.6px solid #c9d2cc;padding:1.2mm 1.6mm;vertical-align:top}
tr:nth-child(even) td{background:#f4f7f4}
.small td,.small th{font-size:7.6pt;padding:.9mm 1.3mm}
.box{border:1px solid #c9d2cc;border-left:3.5px solid #17392f;padding:2.5mm 3.5mm;margin:2mm 0;background:#f8faf8}
.warn{border-left-color:#b5651d;background:#fdf6ee}
.kpi{display:flex;gap:6mm;margin:3mm 0}
.kpi div{border-top:2.5px solid #17392f;padding-top:1.5mm;flex:1}
.kpi b{display:block;font-size:17pt;color:#17392f;letter-spacing:-.02em}
.kpi span{font-size:8.3pt;color:#56645d}
img.full{width:100%;display:block}
img.fit{max-width:100%;max-height:150mm;display:block;margin:0 auto}
.cap{font-size:8pt;color:#56645d;margin-top:1mm}
ul,ol{margin:0 0 2mm;padding-left:5mm}
li{margin:.6mm 0}
.src{font-size:7.4pt;color:#3c4a44;word-break:break-all}
.foot{font-size:7.5pt;color:#7b8a83;margin-top:2mm}
"""

img = lambda name: (N / name).resolve().as_uri()

body = f"""
<section class="page">
<h1>SAAYA Node v1 — IoT heat-rest monitor and fan controller</h1>
<div class="sub">Retrofit IoT product for outdoor-worker rest shades · Vellore, Tamil Nadu · VIT B.Tech CSE project · October 2026</div>
<div class="grid3">
<div>
<h2>1. Real-life scenario</h2>
<p><b>Problem.</b> Construction, road and farm workers in Vellore rest outdoors in pre-monsoon heat (May mean maximum ≈ 39 °C, record 45 °C). Typical rest sheds are bare GI or cement sheets that themselves run 55–70 °C, nobody knows whether the shelter actually helps, and a worker who feels unwell has no reliable way to call for help. India's NDMA draft cooling-centre guidelines (2025) ask for shaded rest structures for outdoor workers; SAAYA Node makes any such shade measurable and safer.</p>
<p><b>Users.</b> Workers (press buttons, read the display), site supervisor / safety officer (receives help requests, acknowledges), site engineer (reviews logged evidence).</p>
<p><b>How it operates.</b> The node bolts to the post of an existing shade. Every second it reads seat-zone air (SHT30 in a radiation shield), an outdoor reference (second SHT30), roof underside temperature (DS18B20), water availability (float) and the fan's real speed (tach) and energy (INA219). A worker presses <b>MODE</b> for the fan. In automatic mode the fan runs from 32 °C and <b>stops at ≥ 39 °C</b>, where published studies show a fan can add heat, and the display says so; manual control is never blocked. <b>HELP</b> latches a request (LED + 95 dB buzzer + OLED), survives power cuts, and can only be cleared by the staff <b>ACK</b> button on the side. Data go to a laptop over USB, or optionally over site Wi-Fi to the supervisor's dashboard.</p>
<p><b>Expected benefits.</b> (1) A help request that cannot be lost or silently cleared. (2) Fault awareness: a stalled fan, dead sensor or stale data is reported, never shown as “cooling”. (3) Evidence: paired seat-vs-reference and roof readings prove whether a shade upgrade worked. (4) Very low energy: ≈ {wh_day:.0f} Wh/day versus 11–13 kWh per shift for a 1.5-ton AC. (5) ≈ ₹{total:,} per site instead of building a new ₹94k–1.7 lakh shelter.</p>
<p><b>Why this design fits.</b> An open shade cannot hold AC-cooled air; shade + air movement + monitoring is the realistic intervention. The node is offline-first (control runs on the ESP32, not the cloud), cheap, weatherproof and retrofittable.</p>
</div>
<div>
<img class="full" src="{img('render-assembly.png')}" alt="SAAYA Node 3D model">
<div class="cap">3D model (CadQuery → STEP): IP65 controller box on aluminium bracket, 5-plate radiation shield with SHT30, 120 mm PWM fan with guards.</div>
<div class="kpi"><div><b>₹{total:,}</b><span>complete node, listed prices + allowances</span></div><div><b>{w_typ:.1f} W</b><span>typical draw (fan 70 %)</span></div><div><b>6</b><span>measured quantities, 1 actuator, 3 controls</span></div></div>
<div class="box">Status: design, firmware, CAD and simulation package. Firmware compiles in CI and its control logic has native tests; <b>no unit has been assembled or field-tested yet</b>. Prices checked online on 20 Oct 2026.</div>
</div></div></section>

<section class="page">
<h2>2. Component selection and justification</h2>
<p>Selection criteria, in order: <b>(a) evidence capability</b> (feedback and measurement, not just control), <b>(b) cost</b>, <b>(c) accuracy adequate for a 1 °C decision margin</b>, <b>(d) power</b>, <b>(e) operating range for 25–45 °C shaded outdoor air and monsoon humidity</b>, <b>(f) 3.3 V / I²C compatibility</b>, <b>(g) Indian availability</b>.</p>
{table(['Function', 'Selected', 'Why it meets the criteria', 'Rejected alternatives and why'], [(e(a), f'<b>{e(b)}</b>', e(c), e(d)) for a, b, c, d in SEL], 'small')}
</section>

<section class="page">
<h2>3. Technical specification sheet</h2>
{table(['Component', 'Supply', 'Current', 'Range', 'Accuracy / rating', 'Interface', 'Dimensions', 'Datasheet'], [(f'<b>{e(a)}</b>', e(b), e(c), e(d), e(f_), e(g), e(h), e(k or 'shop listing')) for a, b, c, d, f_, g, h, k in SPEC], 'small')}
</section>

<section class="page">
<h2>3b. Power budget and datasheet design rules</h2>
<div class="grid2">
<div><h3>Power budget (12 V input)</h3>
{table(['Load', 'Rail', 'Typical mA', 'Peak mA', 'Note'], [(e(a), e(b), c, d, e(n)) for a, b, c, d, n in POWER], 'small')}
<p>12 V input ≈ <b>{in_typ:.0f} mA typical ({w_typ:.1f} W)</b>, <b>{in_pk:.0f} mA peak ({w_pk:.1f} W)</b>, assuming 85 % buck efficiency. The 12 V 2 A adapter gives &gt; 3× margin; the 1 A slow fuse clears a wiring short. Daily energy, fan 8 h + controller 24 h ≈ <b>{wh_day:.0f} Wh</b> — a 20 W panel + 12 V 7 Ah battery could run it off-grid (option, not costed).</p></div>
<div><h3>Design rules taken from the datasheets</h3>
<ul>
<li>IO34–IO39 are input-only with no internal pull-ups → external 10 kΩ on tach (IO34) and float (IO35).</li>
<li>4-wire fan spec (Intel rev 1.2, Noctua): 25 kHz PWM; fan runs at <b>full speed if the PWM line is undriven</b>; tach 2 pulses/rev open collector → if the ESP32 crashes the fan fails <i>on</i>, not off.</li>
<li>DevKitC: power from USB <i>or</i> 5V pin, never both → USB only for programming.</li>
<li>INA219 bus ≤ 26 V; placed high-side in the 12 V fan branch only.</li>
<li>Two SHT30 share one bus via ADDR (0x44 low, 0x45 high); ADDR never left floating.</li>
<li>MP1584 IC is “not recommended for new designs” → fine for the prototype; MP2338 for production.</li>
</ul></div></div>
</section>

<section class="page">
<h2>4. Interfacing diagram</h2>
<img class="fit" src="{img('interfacing-diagram.svg')}" alt="Interfacing diagram" style="max-height:168mm">
</section>

<section class="page">
<h2>4b. ESP32 pin map</h2>
{table(['ESP32 pin', 'Function', 'Dir', 'Conditioning', 'Connected to'], [(f'<b>{e(a)}</b>', e(b), e(c), e(d), e(f_)) for a, b, c, d, f_ in PINS])}
<p class="cap">Unused: strapping pins IO0/IO2/IO12/IO15 avoided; IO6–IO11 reserved for flash. Firmware: <code>firmware/src/main.cpp</code>, control logic <code>firmware/include/controller.h</code>. Bus wiring: one Cat5e STP pair per signal with its own ground (SDA+GND, SCL+GND, 3V3+GND).</p>
</section>

<section class="page">
<h2>4c. Bill of materials and cost (₹, checked 20 Oct 2026)</h2>
{table(['Function', 'Part', 'Qty', 'Unit', 'Line', 'Status'], bom_rows, 'small')}
<p class="cap">“listed” = price read on the linked Indian shop page; “allowance” = estimate. Cheaper options: P12 PWM PST fan (≈ ₹568 each in a 5-pack, 56 CFM) instead of P12 Pro; generic IP65 box instead of WPE16. Not cut: the tach fan, the paired reference sensor and calibration time — without them the node can no longer prove anything.</p>
</section>

<section class="page">
<h2>5. 3D model design (CadQuery, STEP + STL)</h2>
<div class="grid2">
<div><img class="full" src="{img('render-internals.png')}" alt="Internals">
<div class="cap">Lid removed: 90×70 perfboard with ESP32-DevKitC and field terminals (left); INA219, MP1584 and fuse (right); M12 vent on the left wall; ACK button on the right wall; 5 PG7 glands underneath.</div></div>
<div>{table(['Feature', 'Dimension (mm)', 'Reason'], [
    ('Enclosure', f"{E['W']} × {E['H']} × {E['D']}, wall {E['wall']}, lid depth {E['lid_depth']}", 'Purchased IP65 box; fits board + modules with ≥ 10 mm wiring space'),
    ('OLED window', f"{P['oled_window']['w']} × {P['oled_window']['h']} at x {P['oled_window']['x']}, z {P['oled_window']['z']}", 'Covers the 21.7 × 10.9 active area with margin; top-left = first thing read'),
    ('HELP / MODE / LED', f"Ø12 / Ø12 / Ø8 on x = {P['help_button']['x']}, z = {P['help_button']['z']} / {P['mode_button']['z']} / {P['status_led']['z']}", 'One vertical column at the right hand; LED above HELP so the request state is next to the button'),
    ('ACK (side)', f"Ø12 on right wall, y {P['ack_button']['y']}, z {P['ack_button']['z']}", 'Deliberate staff action; not reachable by accident from the front'),
    ('Buzzer grille', '5 × Ø2, pitch 5, at x 27.5, z 32', 'Sound path without a large water entry'),
    ('Cable glands', f"5 × PG7 Ø12.5, x = {', '.join(map(str, P['glands_bottom']['xs']))}, y {P['glands_bottom']['y']}", 'All entries face down → rain drains away; 30 mm pitch leaves spanner room'),
    ('Breather vent', f"M12 Ø12.5 left wall, y {P['vent_side']['y']}, z {P['vent_side']['z']}", 'Equalises pressure, prevents condensation pumping in day/night cycles'),
    ('Back bracket', f"{P['bracket']['W']} × {P['bracket']['H']} × 3 Al; 4 × Ø6.5 on 194 × 90; 4 slots 8 × 16", 'M6 anchors to wall, or two hose clamps round a 40–90 mm post'),
    ('Radiation shield', '5 plates Ø110, 14 pitch, 3 × M5 rods; SHT30 at centre', 'Blocks sun and hot-roof radiation while letting air through'),
    ('Fan', '120 × 120 × 25, wire guards both faces', 'Aimed at the seated torso from ≈ 1 m, 30–45° down'),
], 'small')}
<div class="grid2" style="gap:3mm;margin-top:2mm"><div><img class="full" src="{img('render-front.png')}" alt="Front panel"><div class="cap">Front panel</div></div><div><img class="full" src="{img('render-bottom.png')}" alt="Cable entries"><div class="cap">Underside: 5 PG7 glands, vent on the left wall</div></div></div>
<p class="cap">Interference check over all 23 solids: none above 1 mm³. Interactive model: <b>saaya-verify.vercel.app/node.html</b>; files: <code>cad/node/</code>.</p></div>
</div>
</section>

<section class="page">
<h2>5b. Dimensioned enclosure drawing</h2>
<img class="fit" src="{img('enclosure-drawing.svg')}" alt="Enclosure drawing" style="max-height:170mm">
</section>

<section class="page" style="font-size:8.9pt">
<h2>6. Deployment capability</h2>
<div class="grid3">
<div><img class="full" src="{img('installation-elevation.svg')}" alt="Installation elevation">
<div class="cap">Retrofit to an existing shade. Box centre 1400 mm (reachable seated or standing, above splash); seat sensor 1100 mm (seated head height); reference ≥ 2 m outside the shade at the same height; roof probe bonded to the underside centre.</div>
{table(['Item', 'Placement'], [
    ('Node box', 'Shaded side of a post or wall, 1400 mm, glands down, drip loop under the box'),
    ('Seat sensor', 'In shield beside the bench, 1100 mm, ≈ 0.4 m from the head, ≤ 2 m cable'),
    ('Reference sensor', 'In shield on its own pole, ≥ 2 m from the shade edge, same height, ≤ 5 m STP cable'),
    ('Roof probe', 'Bonded with thermal tape to the roof underside centre, shielded from direct sun'),
    ('Fan', 'On the post or a roof member, ≈ 1 m from the seat, 30–45° down'),
    ('Float', 'Inside the drinking-water can; wire leaves through the lid'),
], 'small')}</div>
<div>
<h3>Installation area</h3><p>Construction or road-work site, farm, bus-stop or factory yard with an existing shade of ≈ 2.4 × 2 m for 4–6 seated workers; one node per rest shade. Larger rest areas (e.g. a 30–60 worker site with several sheds) use one node per shed.</p>
<h3>Mounting</h3><p>Four M6 anchors into a wall or two stainless hose clamps on a 40–90 mm post; no welding or drilling of the structure. Cables run in UV-stabilised conduit.</p>
<h3>Power availability</h3><p>Site 230 V socket → 12 V 2 A adapter kept in shade (≤ {w_pk:.0f} W peak). Off-grid option: 20 W panel + 12 V 7 Ah battery (daily need ≈ {wh_day:.0f} Wh).</p>
<h3>Connectivity</h3><p>Offline-first: all control on the ESP32. Data: USB serial to a laptop running the local API, or the optional Wi-Fi build (env <code>esp32dev_wifi</code>) posting each frame to the supervisor's laptop on site Wi-Fi with a device token; Wi-Fi runs in a separate task so a weak signal can never delay buttons or the fan. No cloud account or SIM needed; GSM/LoRa is a later option.</p>
<h3>Environmental conditions</h3><p>Shaded air 25–45 °C, monsoon rain, dust, 43–51 % afternoon RH in hot months. All parts rated ≥ 60 °C (ESP32, OLED −40…85 °C); IP65 box, glands down, breather vent; box and adapter kept out of direct sun.</p>
<h3>Maintenance</h3><ul>
<li><b>Weekly:</b> wipe radiation shields and fan guard; check float and water can.</li>
<li><b>Monthly:</b> check gland tightness, cable chafe, fan tach vs. command on the display.</li>
<li><b>Quarterly:</b> co-locate the two SHT30s for 20 min and record the offset; repaint/clean the roof top coat if soiled.</li>
<li><b>On fault:</b> OLED states the fault (sensor / fan feedback / water); parts are plug-in and swap in minutes.</li></ul>
</div></div>
</section>

<section class="page">
<h2>7. Operating logic, verification and online tools</h2>
<div class="grid2"><div>
{table(['State / event', 'System response'], [
    ('Air < 32 °C, AUTO', 'Fan off (hysteresis: starts ≥ 32 °C, stops < 31 °C)'),
    ('32–37 °C, AUTO', 'Fan 50 % PWM; display normal'),
    ('37–39 °C', 'Fan allowed; display “FAN: LIMITED BENEFIT” (older / medicated users)'),
    ('≥ 39 °C', 'AUTO fan stops (restarts < 38.5 °C); display “HOT: FAN MAY ADD HEAT”; MANUAL still allowed'),
    ('MODE pressed', 'Toggle manual 70 % ↔ off'),
    ('HELP pressed', 'Latch → LED + buzzer + OLED; stored in flash; survives reboot'),
    ('ACK (staff)', 'Clears the latch; HELP wins if pressed together'),
    ('Fan commanded, tach < 100 rpm after 3 s', '“FAN FEEDBACK FAULT”; any cooling claim invalidated'),
    ('Sensor missing / invalid', '“SENSOR FAULT”; readings unavailable (never zero); AUTO inhibited'),
    ('Float open (or wire broken)', '“WATER LOW / CHECK”'),
    ('Firmware stall', '5 s hardware watchdog restart; help latch restored'),
], 'small')}
</div><div>
<h3>What has been verified</h3><ul>
<li>ESP32 firmware compiles in GitHub Actions (PlatformIO, espressif32 6.10.0).</li>
<li>Control logic: native C++ tests (latch, manual, fault, start-up grace, timer rollover, hysteresis, fan-benefit screen); identical rules tested in Python and JavaScript.</li>
<li>CAD: 23 solids valid, no interference &gt; 1 mm³; STEP/STL exported.</li>
<li>Evidence API: 89 Python tests; browser tests on the public site.</li></ul>
<h3>Online tools used</h3><ul>
<li><b>Wokwi</b> (ESP32 simulator): <code>firmware/diagram.json</code> wires the same pins to an ESP32-DevKitC V4, SSD1306, DS18B20, buttons, LED, buzzer and float switch. Wokwi has no SHT3x/INA219/fan part, so the simulation exercises the fault paths (sensor fault, fan-feedback fault, help latch). Prepared, not yet run.</li>
<li><b>GitHub Actions</b> (CI compile + tests), <b>Vercel</b> and GitHub Pages (live 3D model and documentation), manufacturer datasheets and Indian shop listings (linked below).</li></ul>
<div class="box warn"><b>Not yet proven:</b> real air speed at the seat, sensor-shield bias, buck efficiency in heat, IP rating after drilling, and any health benefit. Next step: build two units, co-locate sensors, then run paired trials on three clear days.</div>
</div></div>
</section>

<section class="page">
<h2>Sources</h2>
<div class="src" style="font-size:8.2pt;line-height:1.7">{'<br>'.join(f'<b>{e(k)}</b>: {e(v)}' for k, v in DS.items())}<br><br>{'<br>'.join(f'<b>{e(k)}</b>: {e(v)}' for k, v in SRC.items())}<br><br>Other figures: Vellore climate (IMD normals via Wikipedia), NDMA draft Guidelines for Cooling Centers (2025), fan-use thresholds (Morris et al. 2021, WHO), AC input power (Blue Star / Voltas spec pages) — full citations in docs/DEFENSE.md.</div>
<div class="foot">SAAYA VERIFY · github.com/alphasafal/saaya-verify · saaya-verify.vercel.app · All dimensions in mm.</div>
</section>
"""

doc = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>SAAYA Node v1 - IoT design document</title><style>{CSS}</style></head><body>{body}</body></html>"
(N / 'SAAYA_Node_IoT_Design.html').write_text(doc)
print('HTML written; BOM total', total, 'listed', listed, f'power typ {w_typ:.1f} W peak {w_pk:.1f} W, {wh_day:.0f} Wh/day')
