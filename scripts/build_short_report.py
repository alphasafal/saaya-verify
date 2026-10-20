"""Concise 8-page version of the SAAYA cool shelter report (A4).
python scripts/build_short_report.py -> docs/report/SAAYA_Cool_Shelter_Report_Concise.pdf
"""
from pathlib import Path
import html, json, runpy, subprocess, io, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report'
IMG = OUT / 'img'
e = html.escape
g = runpy.run_path(str(ROOT / 'scripts' / 'build_node_pdf.py'))
T = json.loads((ROOT / 'site/data/thermal-model.json').read_text())
H = T['headline']
D = {d['design']: d for d in T['designs']}
costs = json.loads((ROOT / 'research/costs.json').read_text())
FL = sum(x['estimate_low'] for x in costs['full_size']); FH = sum(x['estimate_high'] for x in costs['full_size'])

STUDENT, REGNO, GUIDE = 'Safal Gupta', '23BCT0237', ''
COURSE, MONTH = '[Course Code – Course Title]', 'October 2026'

# references, numbered in order of first use
REFS = {
    'imd': 'India Meteorological Department, climatological normals for Vellore (station 43303), 1991–2020.',
    'ilo': 'International Labour Organization, <i>Working on a Warmer Planet: The Impact of Heat Stress on Labour Productivity and Decent Work</i>, Geneva, 2019.',
    'ndma': 'National Disaster Management Authority, <i>Guidelines for Cooling Centers</i> (draft), New Delhi, 2025.',
    'swinbank': 'W. C. Swinbank, “Long-wave radiation from clear skies,” <i>Q. J. R. Meteorol. Soc.</i>, vol. 89, pp. 339–348, 1963.',
    'watmuff': 'J. H. Watmuff, W. W. S. Charters and D. Proctor, “Solar and wind induced external coefficients for solar collectors,” <i>COMPLES</i>, no. 2, 1977.',
    'morris21': 'N. B. Morris <i>et al.</i>, “Electric fan use for cooling during hot weather: a biophysical modelling study,” <i>Lancet Planet. Health</i>, vol. 5, no. 6, 2021.',
    'who': 'World Health Organization, “Climate change, heat and health,” fact sheet, 2024.',
    'esp32': 'Espressif Systems, <i>ESP32 Series Datasheet</i> v5.3 and <i>ESP32-DevKitC V4 User Guide</i>.',
    'sht3x': 'Sensirion AG, <i>Datasheet SHT3x-DIS</i>, v7, 2022.',
    'ds18b20': 'Analog Devices, <i>DS18B20 1-Wire Digital Thermometer</i>, datasheet.',
    'ina219': 'Texas Instruments, <i>INA219 Current/Power Monitor with I²C Interface</i>, SBOS448.',
    'intel': 'Intel Corporation, <i>4-Wire PWM Controlled Fans Specification</i>, Rev. 1.2, 2004.',
}
order = []


def c(*keys):
    for k in keys:
        if k not in order:
            order.append(k)
    return '[' + ', '.join(str(order.index(k) + 1) for k in keys) + ']'


fig_n = 0
tab_n = 0


def fig(src, cap, width='100%'):
    global fig_n
    fig_n += 1
    return f'<figure><img src="{(IMG / src).as_uri()}" style="width:{width}" alt="{e(cap)}"><figcaption><b>Fig. {fig_n}:</b> {e(cap)}</figcaption></figure>'


def tbl(cap, headers, rows, widths):
    global tab_n
    tab_n += 1
    cg = ''.join(f'<col style="width:{w}">' for w in widths)
    return (f'<div class="tbl"><div class="tcap"><b>Table {tab_n}:</b> {e(cap)}</div><table><colgroup>{cg}</colgroup><thead><tr>'
            + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows) + '</tbody></table></div>')


m = lambda k: D[k]['tmrt_c']
open_sun, shed, white, saaya = m('Open sun (no shelter)'), m('Weathered GI / cement sheet (typical existing shed)'), m('Single sheet, white both faces'), m('SAAYA double roof (white top, ventilated gap, bare low-e lining)')
shed_u = D['Weathered GI / cement sheet (typical existing shed)']['underside_c']
bare_u = D['Single bare galvanised sheet']['underside_c']
saaya_u = D['SAAYA double roof (white top, ventilated gap, bare low-e lining)']['underside_c']
ov = {round(x['extra_overhang_m'], 1): x['tmrt_c'] for x in T['overhang']}
gr = {x['surround']: x['tmrt_c'] for x in T['ground']}

body = f"""
<div class="title">
<div class="t1">SAAYA: AN IoT-ENABLED COOL SHELTER FOR OUTDOOR WORKERS</div>
<div class="t2">Project Report (concise version)</div>
<div class="t3">{e(STUDENT)} ({e(REGNO)})<br>School of Computer Science and Engineering, Vellore Institute of Technology, Vellore · {MONTH}</div>
</div>

<div class="abs"><b>Abstract.</b> Outdoor workers in Vellore rest under bare metal sheets that become radiant heaters in the afternoon. Nobody measures whether these shades help, fans fail unnoticed and there is no reliable way to call for help. SAAYA is a demountable cool shelter for four to six workers: a 2.4 m × 2.0 m steel frame with a reflective upper roof skin, a ventilated 120 mm gap, a painted lining, a 200 mm overhang, a louvred screen and a bench. An ESP32-based node reads seat and outdoor air (two SHT30), roof lining temperature (DS18B20), fan speed (tachometer) and fan power (INA219); it runs a 12 V PWM fan only when moving air helps, stops automatic operation at 39 °C, detects fan faults and latches help requests. A screening heat model predicts that shade reduces mean radiant temperature at the seat by {H['shade_alone_k']:.1f} °C and the cool roof by a further {H['roof_treatment_k']:.1f} °C, with the lining {H['underside_cooler_k']:.0f} °C cooler than a weathered sheet. The node costs ₹{g['total']:,} and draws {g['w_typ']:.1f} W. Firmware compiles and passes automated tests; fabrication and field testing are next.</div>

<h2>1. Introduction</h2>
<p>Vellore’s mean daily maximum in May is about 39 °C, with a record of 45 °C {c('imd')}. The ILO projects that India will lose 5.8 % of working hours to heat stress by 2030, mostly in agriculture and construction {c('ilo')}. Rest breaks are the main protection workers have, yet they are usually taken under galvanised or cement sheets whose undersides reach 60–80 °C at noon and radiate that heat onto people’s heads. NDMA’s draft guidance on cooling centres treats shaded rest areas as an essential first step {c('ndma')}.</p>
<p><b>Problem.</b> Existing shades have three gaps: (1) the roof itself is hot; (2) there is no feedback on whether the shade or fan works, so a stalled fan looks the same as a running one; (3) a worker who feels unwell has no signal that cannot be missed.</p>
<p><b>Objectives.</b> (a) Design a low-cost, demountable shelter that reduces radiant heat by passive means; (b) build an IoT node that controls a fan safely, detects faults and provides a latched help request; (c) make every cooling claim depend on paired, repeated measurement; (d) keep the electronics under ₹6,000 and below 10 W.</p>

<h2>2. Shelter Design</h2>
<div class="side">{fig('shelter-iso.png', 'SAAYA cool shelter (CadQuery 3D model)', '100%')}
<p>The shelter is designed to block sun first and then to keep the surface above people’s heads cool. Six layers are used in order of cost: <b>shade</b> (the largest single effect), a <b>white upper skin</b> that reflects most sunlight, a <b>ventilated gap</b> of about 120 mm through which wind carries away the heat the top skin absorbs, a <b>painted aluminium lining</b> that stays close to air temperature even as the white coat soils, a <b>200 mm overhang and removable timber jaali louvres</b> that cut low-angle sun while keeping breeze, and finally a <b>controlled fan</b>, the only part that uses electricity.</p></div>
{tbl('Main dimensions and members of the shelter (from the 3D model)', ['Item', 'Value', 'Reason'], [
    ('Post centres / roof', '2400 × 2000 mm / 2800 × 2400 mm', 'Bench for 4–6 people; 200 mm overhang widens the shadow'),
    ('Clear height', '2310 mm', 'Standing headroom with margin'),
    ('Roof fall', '120 mm over 2000 mm (3.4°)', 'Rain run-off to the rear'),
    ('Roof gap', '≈ 120 mm (SHS 30 × 30 spacers)', 'Enough for wind-driven ventilation'),
    ('Posts / beams / purlins', 'SHS 60×60×3 / RHS 80×60×3 / RHS 60×40×3', 'Standard sections, locally fabricated'),
    ('Base', '200 × 200 × 10 plates, 4 anchors each', 'Bolted, so the shelter can move with the site'),
    ('Bench', '1400 × 450 mm timber slats, seat 450 mm', 'Drains and stays cooler than steel'),
    ('Mass / parts', '≈ 250 kg, 44 distinct parts, 143 instances', 'Clash check: zero intersections'),
], ['24%', '38%', '38%'])}
{tbl('Material choices and rejected alternatives', ['Choice', 'Why', 'Rejected alternative'], [
    ('Steel SHS/RHS, bolted', 'Predictable strength, demountable, repairable', 'Bamboo (variable, termites); timber (rot); aluminium (cost, welding)'),
    ('White upper skin', 'Reflects sunlight; cheap; repaintable', f'Bare GI: modelled underside ≈ {bare_u:.0f} °C; polycarbonate transmits heat'),
    ('Ventilated gap', 'Lining stays cool as paint ages', 'Sealed gap (hotter); sandwich panel (cost, stores heat into evening)'),
    ('Jaali louvres', 'Block low sun, keep airflow', 'Solid wall (blocks breeze); fabric (UV wear)'),
    ('No AC / no air cooler', 'Open shelter cannot hold cooled air', 'AC 1.4–1.6 kW wasted; evaporative cooler weak in humid monsoon'),
], ['22%', '36%', '42%'])}

<h2>3. Heat Model and Results</h2>
<p>A screening model was written (api/thermal.py) to compare roof options before building anything. It balances solar gain, convection (h = 2.8 + 3.0v) {c('watmuff')}, long-wave exchange with a clear sky {c('swinbank')} and view factors from the seated head (1.1 m) to roof, sky and ground, for Vellore at solar noon in mid-May (38 °C air, 45 % RH, 900 W/m², 1 m/s wind). Its output is the mean radiant temperature (MRT), the single number that captures how much heat surfaces radiate onto a person. The energy balance closes to zero and the model has 17 automated tests; it is a screening tool, not yet validated.</p>
{tbl('Predicted MRT at the seated head and roof underside temperature', ['Design', 'MRT (°C)', 'Roof underside (°C)'], [
    ('Open sun, no shelter', f'{open_sun:.1f}', '—'),
    ('Weathered GI / cement shed (typical today)', f'{shed:.1f}', f'{shed_u:.1f}'),
    ('Single bare galvanised sheet', f'{m("Single bare galvanised sheet"):.1f}', f'{bare_u:.1f}'),
    ('Single sheet, white both faces', f'{white:.1f}', f'{D["Single sheet, white both faces"]["underside_c"]:.1f}'),
    ('<b>SAAYA ventilated double roof</b>', f'<b>{saaya:.1f}</b>', f'<b>{saaya_u:.1f}</b>'),
], ['56%', '20%', '24%'])}
<p><b>Findings.</b> (1) Shade alone lowers MRT by {H['shade_alone_k']:.1f} °C; this is the main benefit of any shelter. (2) The SAAYA roof adds a further {H['roof_treatment_k']:.1f} °C at the seat, because the roof fills only about {H['roof_view_fraction']*100:.0f} % of the seated person’s view; but its underside is {H['underside_cooler_k']:.0f} °C cooler than a weathered sheet ({saaya_u:.0f} vs {shed_u:.0f} °C), which matters for standing workers and keeps working as the top coat soils. (3) Layout matters as much as the roof: +0.3 m of overhang gives −{ov[0.0]-ov[0.3]:.1f} °C, irrigated ground cover around the shelter gives −{gr['typical dry ground']-gr['irrigated grass / ground cover']:.1f} °C, while light paving raises MRT by +{gr['light paving']-gr['typical dry ground']:.1f} °C by reflecting sun into the shelter. (4) The model makes falsifiable predictions: roof underside {T['prediction_bands'][0]['underside_c'][0]:.0f}–{T['prediction_bands'][0]['underside_c'][1]:.0f} °C and 150 mm globe {T['prediction_bands'][0]['globe_150mm_c'][0]:.0f}–{T['prediction_bands'][0]['globe_150mm_c'][1]:.0f} °C; it is rejected if measurements fall outside on two of three clear days.</p>
{tbl('SAAYA compared with normal cooling options', ['Criterion', 'Tin shed', 'AC (1.5 t)', 'Air cooler', 'SAAYA'], [
    ('Power', 'None', '1.4–1.6 kW', '100–200 W + water', f'{g["w_typ"]:.1f} W typical'),
    ('Works in an open shelter', 'Yes, hot roof', 'No', 'Partly', 'Yes'),
    ('Humid monsoon', '—', 'Works', 'Weak, adds humidity', 'Works'),
    ('Knows if it is working', 'No', 'No', 'No', 'Yes (paired sensors)'),
    ('Fan fault / help request', 'No', 'No', 'No', 'Yes / latched'),
    ('Equipment cost', 'Low', '≈ ₹36,990 + wiring', '₹8–15k', f'₹{g["total"]:,} node'),
], ['24%', '15%', '18%', '19%', '24%'])}

<h2>4. IoT System: Architecture and Control</h2>
<p>The SAAYA Node has three blocks. <b>Sense:</b> SHT30 at the seat (1.1 m, in a radiation shield), SHT30 outside as a reference (≥ 2 m away, same height), DS18B20 bonded to the roof lining, INA219 on the 12 V fan supply, the fan tachometer, a float switch in the drinking-water can, and MODE, HELP and ACK buttons. <b>Decide:</b> an ESP32 runs the control loop on one core with the rules kept in a single header that is unit-tested on a PC; a Wi-Fi uplink task runs on the other core; a 5 s watchdog restarts the board if anything hangs; the help latch is stored in flash. <b>Act:</b> 12 V PWM fan, OLED display, LED and buzzer; one JSON record per second goes over USB or Wi-Fi to a FastAPI/SQLite logger. Control never depends on the network.</p>
{tbl('Control rules implemented in firmware (controller.h)', ['Rule', 'Behaviour', 'Reason'], [
    ('Auto fan', 'ON at 50 % when seat air ≥ 32 °C; OFF below 31 °C', 'Hysteresis prevents on/off flicker'),
    ('Heat cut-off', 'Caution ≥ 37 °C; auto stop ≥ 39 °C; restart < 38.5 °C', f'Fans can add heat in very hot air {c("morris21", "who")}'),
    ('Manual', 'MODE gives 70 %; never blocked, warning shown', 'The worker decides'),
    ('Fan fault', 'Duty > 0 but < 100 rpm after 3 s → FAULT', 'A stalled fan must not be reported as cooling'),
    ('Help', 'HELP latches LED, buzzer, OLED; saved in flash; only ACK (side) clears', 'Cannot be lost by reboot or accidental press'),
    ('Sensor loss', 'Reading shown as unavailable, never as 0', 'Missing data is not evidence'),
    ('Fail-safe', 'If the ESP32 stops, PWM floats and the fan runs at 100 %', f'4-wire fan standard {c("intel")}'),
], ['16%', '48%', '36%'])}

<h2>5. Component Selection and Justification</h2>
{tbl('Components, reasons and rejected alternatives (prices: Indian online retail, Oct 2026)', ['Component', 'Why chosen', 'Rejected, and why', '₹'], [
    ('ESP32-DevKitC (WROOM-32)', f'Wi-Fi, 16 PWM channels, interrupt input for tach, flash, watchdog, instant boot, −40 to 85 °C {c("esp32")}', 'Arduino Uno: no Wi-Fi, 2 kB RAM. Raspberry Pi: SD card corrupts on power cuts, ~10× power', '499'),
    ('SHT30 × 2', f'±0.2 °C, ±2 %RH typ.; addresses 0x44/0x45 share one bus {c("sht3x")}', 'DHT22: slow, RH drift. BME280: self-heating. SHT31: 2× price, same accuracy in 0–65 °C', '358'),
    ('DS18B20 probe', f'Waterproof, 1 m cable, one GPIO, ±0.5 °C {c("ds18b20")}', 'IR sensor: wrong on low-emissivity metal. NTC: needs calibration', '49'),
    ('INA219', f'Measures real fan voltage and current on I²C {c("ina219")}', 'ACS712: ≈ 60 mV signal at 0.33 A, noisy. Datasheet watts: not a measurement', '89'),
    ('Arctic P12 Pro 4-wire fan', '25 kHz PWM, tach 2 pulses/rev, fails ON if PWM lost, 0.33 A', '2-wire fan: no feedback. 230 V pedestal fan: shock risk, 55–125 W', '910'),
    ('SSD1306 OLED', 'Readable without a phone; shares I²C (0x3C)', '16×2 LCD: 5 V, 6 pins. Phone app: workers may not carry phones', '130'),
    ('3 × 12 mm IP65 buttons', 'Rain-proof; HELP front, ACK on side for staff', 'Touch sensors: false triggers from sweat and rain', '477'),
    ('SFM-27 buzzer + LED', '> 95 dB at < 12 mA', 'Passive piezo: quieter, needs tone generation', '64'),
    ('PP float switch', 'Dry contact; broken wire reads “low water” (fail-safe)', 'Ultrasonic: cost, condensation errors', '175'),
    ('12 V 2 A SMPS + MP1584 + 1 A fuse', '12 V drives fan directly; efficient buck to 5 V', '7805 linear: > 50 % lost as heat in a sealed box', '257'),
    ('ProtechT WPE16 IP65 ABS box', '175 × 100 × 60 mm, rain-rated, purchasable', '3D-printed PETG: softens at 60–70 °C, not rain-rated', '949'),
], ['19%', '36%', '37%', '8%'])}
<p><b>Compatibility.</b> All sensors and the OLED run at 3.3 V from the ESP32’s regulator, so no level shifting is needed; the fan’s PWM line is pulled down by a 2N3904 and its open-collector tachometer is pulled up to 3.3 V, so no GPIO ever sees 12 V. The four I²C devices have four different addresses (0x44, 0x45, 0x3C, 0x40) and the bus runs at 50 kHz for the longer reference cable. Input-only pins IO34/IO35 are used only as inputs with external 10 kΩ pull-ups; strapping pins (0, 2, 12, 15) and flash pins (6–11) are avoided. Peak current is {g['in_pk']:.0f} mA against the 2 A adapter, and the 3.3 V rail carries about 25 mA of its ≈ 500 mA budget. The 750 ms DS18B20 conversion runs asynchronously, so the loop is never blocked.</p>

<h2>6. Interfacing Diagram</h2>
{fig('interfacing-diagram.png', 'SAAYA Node interfacing diagram (ESP32-DevKitC V4, 3.3 V logic)', '100%')}
{tbl('Pin assignment', ['Signal', 'ESP32 pin', 'Interface detail'], [
    ('I²C SDA / SCL', 'IO21 / IO22', 'SHT30 ×2, OLED, INA219; 4.7 kΩ pull-ups on modules; 50 kHz'),
    ('Fan PWM', 'IO25', '25 kHz via 2N3904 (inverted in firmware)'),
    ('Fan tachometer', 'IO34 (input only)', '10 kΩ to 3.3 V; interrupt, 2 pulses per revolution'),
    ('Roof probe', 'IO4', '1-Wire, 4.7 kΩ pull-up'),
    ('Float switch', 'IO35 (input only)', '10 kΩ pull-up; open = low water'),
    ('MODE / HELP / ACK', 'IO32 / IO33 / IO27', 'To GND, internal pull-ups, debounced'),
    ('LED / buzzer', 'IO26 / IO14', '330 Ω (≈ 8 mA) / 2N3904 low-side switch on 12 V'),
    ('Power', '5V pin, GND', '12 V → 1 A fuse → MP1584 (5 V) → on-board 3.3 V LDO; never USB and 5V pin together'),
], ['20%', '22%', '58%'])}

<h2>7. 3D Model, Technical Specifications and Deployment</h2>
<div class="pair">{fig('render-internals.png', 'Node enclosure, lid removed', '100%')}{fig('render-assembly.png', 'Radiation shield, enclosure front and 120 mm fan', '100%')}</div>
{tbl('Technical specifications of the SAAYA Node', ['Parameter', 'Value'], [
    ('Enclosure', '175 × 100 × 60 mm IP65 ABS; 5 × PG7 glands on the bottom at 30 mm pitch; M12 breather vent'),
    ('Front panel / side', 'OLED, HELP Ø12 mm, MODE Ø12 mm, LED Ø8 mm / ACK Ø12 mm on right wall'),
    ('Mounting', '3 mm aluminium bracket 215 × 110 mm on a 60 mm SHS post (hose clamps), box at 1.4 m'),
    ('Supply / consumption', f'12 V DC 2 A; {g["w_typ"]:.1f} W typical, {g["w_pk"]:.1f} W peak, ≈ {g["wh_day"]:.0f} Wh/day'),
    ('Measurement', 'Air T/RH ±0.2 °C/±2 %RH (two points); roof ±0.5 °C; fan rpm, V, I'),
    ('Sampling / output', '1 Hz control; one JSON record per second over USB or Wi-Fi'),
    ('Operating range', '0–60 °C ambient inside the box; 5 s watchdog'),
    ('Verification', 'Four firmware builds compile in CI (bench, field, Wi-Fi, core 3); native controller tests; hardware simulation tests; 23-solid clash check'),
], ['26%', '74%'])}
{fig('installation-elevation.png', 'Installation in the SAAYA cool shelter (side elevation, mm)', '70%')}
<p><b>Deployment at a Vellore worksite.</b> The open front faces away from the afternoon sun and the louvre screen is placed on the west side. The node is fixed to a rear post at 1.4 m with glands facing down and drip loops on every cable; the seat sensor hangs at 1.1 m in its shield; the reference sensor stands ≥ 2 m outside at the same height so that both see the same weather; the roof probe is bonded to the centre of the lining. Power comes from a 12 V mains adapter, or off-grid from a 20 W panel with a 12 V 7 Ah battery covering the ≈ {g['wh_day']:.0f} Wh daily need. On an existing shed the node can be retrofitted alone. In a typical day, the fan starts automatically around late morning when seat air crosses 32 °C, the OLED shows temperatures and fan state, the system stops automatic fan operation if seat air passes 39 °C, and a worker who feels unwell presses HELP, which keeps the light and buzzer on until a supervisor presses ACK.</p>

<h2>8. Cost, Verification Plan and Conclusion</h2>
<p><b>Cost.</b> The node costs ₹{g['total']:,} including cables, shields and mounting (₹{g['listed']:,} for listed parts). The first shelter is estimated at ₹{FL:,}–₹{FH:,} including foundations, fabrication, transport and contingency; this is an estimate from the CAD quantities, not a quotation. Cost falls with repeated production of standard bolted sections, use of existing slabs, an optional upper skin where a clean white roof is maintained, ground cover before a larger roof, and retrofitting the node onto existing sheds.</p>
<p><b>Verification plan.</b> No cooling claim is made from the design alone. The margin is declared before data is collected (1.0 °C for roof temperature, because two ±0.5 °C sensors may disagree by up to 1 °C; 0.2 m/s for air speed). Seat readings are always paired with the outdoor reference taken at the same moment. A single run is reported only as a point estimate; a result requires at least three valid runs on three different days, and a direction is claimed only if the whole 95 % confidence interval clears the margin. Runs with a fan or sensor fault are withheld automatically. The website’s evidence lab demonstrates this with replayed data.</p>
<p><b>Hardware simulation.</b> Before soldering, the whole node was simulated. The project website has an interactive simulator (Fig. 6) that shows every part wired to the real ESP32 pins and runs the firmware’s own control header compiled to WebAssembly (identical to the native C++ on 5,000 random test cases). Sensors are set with sliders and the fan follows a speed and current model. Automated tests confirm the 32 °C start, the 39 °C stop and 38.5 °C restart, manual 70 % at any temperature, the fan-feedback fault for a stalled fan or a cut tach wire, the help latch surviving a power cut, and null values for missing sensors. A complete Wokwi project also runs the actual firmware on an emulated ESP32, with custom SHT30 and fan/INA219 chips written in C. The simulation found and fixed three firmware faults: swapped sensor addresses, the automatic fan switched off in the only build, and an OLED line one character too long.</p>
{fig('simulator-board.png', 'Hardware simulator: field build at 34.2 °C seat air, fan at 50 % with tach feedback, INA219 reading 1.45 W', '88%')}
<p><b>Limitations.</b> The shelter has not yet been built or measured; the heat model is unvalidated; steel sections, foundations and wind loads require a structural engineer’s approval; costs are estimates.</p>
<p><b>Conclusion.</b> SAAYA combines a passive cool shelter, chosen with the help of a heat model, with a ₹{g['total']:,} IoT node that runs a fan only when it helps, stops at 39 °C, detects faults, latches help requests and refuses to claim cooling without paired, repeated measurement. The next steps are structural approval, building one shelter with two nodes, co-locating sensors to correct offsets, and a three-day paired test comparing single and double roofs.</p>
<p class="links">Project files: github.com/alphasafal/saaya-verify · Live site and 3D models: saaya-verify.vercel.app</p>

<h2>References</h2>
<ol class="refs">@@REFS@@</ol>
"""
body = body.replace('@@REFS@@', ''.join(f'<li><span class="rn">[{i}]</span>{REFS[k]}</li>' for i, k in enumerate(order, 1)))

CSS = """
@page{size:A4;margin:18mm 18mm 20mm 22mm}
*{box-sizing:border-box}
html{font-family:'Times New Roman','Liberation Serif',serif;font-size:11pt;color:#000}
body{margin:0;line-height:1.38;text-align:justify;hyphens:auto}
p{margin:0 0 6pt}
.title{text-align:center;border-bottom:1.2pt solid #000;padding-bottom:4mm;margin-bottom:4mm}
.t1{font-size:16pt;font-weight:bold;line-height:1.3}
.t2{font-size:12pt;font-weight:bold;margin-top:2mm}
.t3{font-size:11pt;margin-top:2mm;line-height:1.4}
.abs{font-size:10.5pt;border:.6pt solid #000;padding:3mm 4mm;margin-bottom:4mm;line-height:1.35}
h2{font-size:13pt;margin:10pt 0 5pt;break-after:avoid;text-align:left}
figure{margin:5pt 0 7pt;text-align:center;break-inside:avoid}
figure img{display:block;margin:0 auto}
figcaption{font-size:10pt;margin-top:3pt}
.pair{display:flex;gap:5mm;align-items:flex-end}.pair figure{flex:1}.pair img{max-height:52mm;width:auto!important;max-width:100%}
.side{display:flex;gap:5mm;align-items:center}.side figure{flex:0 0 46%;margin:0}.side p{flex:1;margin:0}
.tbl{margin:5pt 0 8pt}
.tcap{text-align:center;font-size:10pt;margin-bottom:3pt;break-after:avoid}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:9.4pt;line-height:1.28;text-align:left}
th,td{border:.6pt solid #000;padding:2pt 3.5pt;vertical-align:top;word-wrap:break-word}
th{background:#e6e6e6}
thead{display:table-header-group}tr{break-inside:avoid}
.refs{list-style:none;padding-left:8mm;font-size:9.6pt;text-align:left;margin:0}.refs li{margin-bottom:2pt;position:relative}.refs .rn{position:absolute;left:-8mm}
.links{font-size:10pt;text-align:left}
"""

if __name__ == '__main__':
    src = OUT / 'concise.html'
    src.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>SAAYA concise report</title><style>{CSS}</style></head><body>{body}</body></html>")
    raw = OUT / 'concise-raw.pdf'
    subprocess.run(['node', str(ROOT / 'scripts' / 'print_report.cjs'), str(src), str(raw)], check=True)
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    r = PdfReader(str(raw)); w = PdfWriter(); n = len(r.pages)
    for i, pg in enumerate(r.pages):
        buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=A4); cv.setFont('Times-Roman', 10)
        cv.drawCentredString(A4[0] / 2, 10 * 72 / 25.4, f'{i + 1}'); cv.save(); buf.seek(0)
        pg.merge_page(PdfReader(buf).pages[0]); w.add_page(pg)
    w.add_metadata({'/Title': 'SAAYA: An IoT-Enabled Cool Shelter for Outdoor Workers (concise report)', '/Author': STUDENT})
    final = OUT / 'SAAYA_Cool_Shelter_Report_Concise.pdf'
    with open(final, 'wb') as f:
        w.write(f)
    raw.unlink(); src.unlink()
    print('Concise report:', final, n, 'pages')
