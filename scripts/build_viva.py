"""Viva / defence and presentation guide (separate from the report).
python scripts/build_viva.py  ->  docs/report/SAAYA_Viva_and_Presentation_Guide.pdf
"""
from pathlib import Path
import html, json, runpy, subprocess, io

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report'
e = html.escape
g = runpy.run_path(str(ROOT / 'scripts' / 'build_node_pdf.py'))
T = json.loads((ROOT / 'site/data/thermal-model.json').read_text())
H = T['headline']
costs = json.loads((ROOT / 'research/costs.json').read_text())
FL = sum(x['estimate_low'] for x in costs['full_size']); FH = sum(x['estimate_high'] for x in costs['full_size'])
SITE = 'https://saaya-verify.vercel.app'
MIRROR = 'https://alphasafal.github.io/saaya-verify'


def tbl(headers, rows, widths=None):
    cg = ''.join(f'<col style="width:{w}">' for w in widths) if widths else ''
    return ('<table><colgroup>' + cg + '</colgroup><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>')


def qa(items):
    return ''.join(f'<div class="qa"><div class="q">Q. {e(q)}</div><div class="a">{a}</div></div>' for q, a in items)


slides = [
    ('1', 'Title', '0:20', 'Name and register number (23BCT0237). “SAAYA is a cool shelter for outdoor workers; passive design cools, the IoT system controls and proves.”'),
    ('2', 'The problem', '0:50', '39 °C May, 67 °C modelled shed roof underside, ILO 5.8 % hours lost. Three gaps: hot roof, no feedback, no help signal.'),
    ('3', 'Our idea', '0:40', 'Shelter + node + evidence rules. Point at the roofless render: bench, fan, sensors, box.'),
    ('4', 'Six layers', '0:50', 'Shade → white top → ventilated gap → cool lining → overhang + jaali → smart fan. Only the last uses power.'),
    ('5', 'Heat model', '1:10', f'Shade −{H["shade_alone_k"]:.1f} °C, roof extra −{H["roof_treatment_k"]:.1f} °C, underside ≈ {H["underside_cooler_k"]:.0f} °C cooler. Say “screening model, not validated”.'),
    ('6', 'Vs AC / cooler', '0:50', 'AC wastes 1.4–1.6 kW in an open shelter; cooler adds humidity, weak in monsoon. SAAYA ≈ 3 W and the only one that knows if it works.'),
    ('7', 'Shelter decisions', '0:50', 'Read two rows aloud (white skin, ventilated gap); the rest is on the slide.'),
    ('8', 'Fan rules', '0:50', 'Auto on 32 / off 31, caution 37, stop 39, restart 38.5; manual never blocked; fault < 100 rpm after 3 s; HELP latch.'),
    ('9', 'Architecture', '0:40', 'Sense → decide → act; logging optional; network failure changes nothing for the worker.'),
    ('10', 'Devices 1', '1:00', 'ESP32 vs Uno/Pi; SHT30 vs DHT22/BME280; tach fan vs 2-wire. Stress “why not”.'),
    ('11', 'Devices 2', '0:40', 'OLED, IP65 buttons, float switch fail-safe, buck not 7805, bought IP65 box not 3D print.'),
    ('12', 'Compatibility', '0:50', '3.3 V logic, 4 I²C addresses, safe pins, 578 mA of 2 A, non-blocking loop, fits the plate.'),
    ('13', 'Interfacing', '0:50', 'Trace one path with a pointer: 12 V → fuse → buck → ESP32; then fan PWM and tach.'),
    ('14', 'Shelter CAD', '0:40', '2400 × 2000 posts, 2800 × 2400 roof, 2310 clear, 120 mm gap, ≈ 250 kg; engineer approval needed.'),
    ('15', 'Node CAD', '0:30', '175 × 100 × 60 IP65; glands down; ACK on side; vent.'),
    ('16', 'Deployment', '0:30', 'Front away from afternoon sun, box 1.4 m, seat 1.1 m, reference ≥ 2 m outside, mains or 20 W solar.'),
    ('17', 'Cost', '0:40', f'Node ₹{g["total"]:,}; shelter ₹94k–₹1.71 lakh estimate; 3.2 W vs ≈ 1,500 W AC; how cost drops.'),
    ('18', 'Evidence rules', '0:50', 'Declare, pair, repeat 3 days, claim only if the 95 % interval clears the margin.'),
    ('19', 'Hardware simulation', '0:40', 'Whole node simulated; rules are the firmware’s own code compiled to WebAssembly (identical on 5,000 cases); 9 behaviours tested; Wokwi runs the real firmware; found 3 bugs before soldering.'),
    ('20', 'Live demo', '5:00', 'Switch to the website (script in section 3).'),
    ('21', 'Honest status', '0:40', 'Done and tested / not yet proven / next steps. End calmly.'),
    ('22', 'Thank you', '—', 'Leave it up during questions.'),
]

demo = [
    ('designs.html', 'Open the design gallery. “Everything I will show is live and open: CAD, firmware and data.”'),
    ('fullsize-model.html', 'Click <b>Whole shelter</b>, then untick <b>Roof</b> to show the frame and devices; tick <b>Section</b>; click <b>Worker + airflow</b>. Type <i>ESP32</i> in the search box and press <b>Focus selected component</b>.'),
    ('simulator.html', 'The whole node circuit running the firmware’s own rules (compiled to WebAssembly). Click <b>Afternoon 34 °C</b>: fan starts at 50 %. Click <b>Extreme 40 °C</b>: automatic stops, OLED says HOT. Press <b>MODE</b> on the circuit: manual 70 % still works. Tick <b>Fan blocked</b>: FAN FEEDBACK FAULT after 3 s. Press <b>HELP</b>, then <b>Power cut</b>: the latch comes back after reboot; <b>ACK</b> clears it. Point at the serial monitor: the same JSON the real node sends.'),
    ('node.html', 'Click <b>Lid off</b>, then <b>Front panel</b>, then <b>Cable entries</b>. Point out glands facing down and ACK on the side.'),
    ('explain.html', 'Click a sensor on the IoT diagram; it opens that part in 3D. Scroll to <b>3 · Wiring & working</b>.'),
    ('index.html#lab', 'Choose <b>Normal operation</b>, endpoint <b>Roof surface temperature</b>, <b>Start replay</b>, then <b>Complete replay</b>: the record shows a single-run estimate and says replication is needed. Press <b>Reset</b>, choose <b>Fan feedback failure</b> with endpoint <b>Seated air speed</b>, run again: the claim is withheld with the reason. This is the key moment of the demo.'),
    ('defense.html', 'Scroll to the MRT chart and the decision table. End the demo here.'),
]

numbers = [
    ('Shelter post grid / roof', '2400 × 2000 mm / 2800 × 2400 mm (200 mm overhang)'),
    ('Clear height / roof fall / roof gap', '2310 mm / 120 mm over 2000 (3.4°) / ≈ 120 mm'),
    ('Bench', '1400 × 450 mm, seat 450 mm high, 4–6 people'),
    ('Steel sections', 'Posts SHS 60×60×3, beams RHS 80×60×3, purlins RHS 60×40×3'),
    ('Model: shade alone / cool roof extra', f'−{H["shade_alone_k"]:.1f} °C / −{H["roof_treatment_k"]:.1f} °C MRT at seated head'),
    ('Model: roof underside vs weathered sheet', f'≈ {H["underside_cooler_k"]:.0f} °C cooler'),
    ('Fan rules', 'Auto on ≥ 32 °C, off < 31 °C; auto stops ≥ 39 °C, restarts < 38.5 °C; manual 70 %, auto 50 %'),
    ('Fan fault', 'Commanded but < 100 rpm after 3 s'),
    ('I²C addresses', 'SHT30 seat 0x44, SHT30 reference 0x45, OLED 0x3C, INA219 0x40; bus 50 kHz'),
    ('Pins', 'SDA 21, SCL 22, PWM 25, tach 34, float 35, roof 4, MODE 32, HELP 33, ACK 27, LED 26, buzzer 14'),
    ('Power', f'≈ {g["w_typ"]:.1f} W typical, {g["w_pk"]:.1f} W peak, ≈ {g["wh_day"]:.0f} Wh/day; 12 V 2 A adapter, 1 A fuse'),
    ('Enclosure', '175 × 100 × 60 IP65 ABS (ProtechT WPE16), 5 × PG7 glands down, M12 vent'),
    ('Cost', f'Electronics ₹{g["total"]:,} (₹{g["listed"]:,} listed); shelter ₹{FL:,}–₹{FH:,} estimate'),
    ('Tests', '89 Python tests, C++ controller tests, 4 firmware builds in CI, 9 simulator behaviour tests, WebAssembly = native C++ on 5,000 cases, 143-instance and 23-solid clash checks'),
]

shelter_why = [
    ('Steel SHS/RHS frame', 'Standard sections, bolted plates → demountable, repairable, locally fabricated.', 'Bamboo: variable strength, termites. Timber: rot, fire. Aluminium: cost, local welding.'),
    ('White upper skin', 'Reflects most sunlight; cheap; repaintable.', 'Bare GI: hot underside (model ≈ 80 °C). Cement sheet: heavy, brittle. Polycarbonate: transmits heat.'),
    ('Ventilated gap ≈ 120 mm', 'Carries away heat absorbed by the top skin; lining stays near air temp even when the top gets dirty.', 'Sealed gap: hotter lining. Sandwich panel: cost, releases heat into the evening.'),
    ('Painted aluminium lining', 'Cool surface above heads; paint resists corrosion; model shows finish matters little once cool.', 'No lining: hot top skin faces people. False ceiling: moisture.'),
    ('200 mm overhang', 'Wider shadow at the bench without bigger post grid.', 'Bigger overhang: more wind uplift and cost (upgrade option; +0.3 m ≈ −1.4 °C).'),
    ('Removable jaali louvres', 'Cut low-angle sun, keep airflow.', 'Solid wall: blocks breeze. Fabric: UV wear.'),
    ('Slatted bench 450 high', 'Comfortable, drains, stays cooler than metal.', 'Steel bench: too hot. Concrete: fixed.'),
    ('Base plates + anchors', 'Can be lifted and moved with the site.', 'Embedded posts: permanent.'),
    ('No AC / no evaporative cooler', 'Open shelter cannot hold cool air; coolers need water, add humidity, weak in monsoon.', 'For enclosed cooling, NDMA treats a cooling room as a separate facility.'),
]

elec_why = [
    ('ESP32-DevKitC', '₹499; 2×I²C, 16 PWM, interrupt tach input, Wi-Fi, flash, watchdog, −40…85 °C.', 'Arduino Uno: no Wi-Fi, 2 kB RAM. Raspberry Pi: SD corruption on power cuts, ~10× power. ESP8266: one ADC, fewer pins.', '3.3 V logic matches all sensors; 5 V input from buck.'),
    ('SHT30 ×2', '±0.2 °C, ±2 %RH typ, same as SHT31 in 0–65 °C, ₹179 each; addresses 0x44/0x45 share one bus.', 'DHT22: slower, timing-critical, RH drift. BME280: self-heating, pressure not needed. SHT31: ₹399 for no gain in our range.', '2.15–5.5 V → 3.3 V OK; I²C.'),
    ('DS18B20 probe', '₹49, ±0.5 °C, waterproof, long cable, 1 GPIO.', 'IR sensor: needs emissivity, wrong on metal. NTC: calibration, lead resistance.', '3.0–5.5 V; 1-Wire + 4.7 kΩ.'),
    ('INA219', '₹89, high-side V and I on I²C, 0.5 % class → measured energy.', 'ACS712: only ≈ 60 mV signal at 0.33 A, noisy. Datasheet watts: not a measurement.', 'Logic 3.3 V; bus ≤ 26 V (12 V used).'),
    ('Arctic P12 Pro fan', '4-wire: tach proves rotation; 25 kHz PWM; 0 rpm < 5 %; fails ON if PWM floats; 0.33 A.', '2-wire fan: no feedback. 230 V pedestal fan: shock risk, no feedback, 55–125 W.', '12 V supply; PWM pulled low by 2N3904; tach open-collector → 10 kΩ to 3.3 V.'),
    ('SSD1306 OLED', '₹130, readable without a phone, shares I²C.', 'LCD 16×2: needs 5 V and more pins. Phone app only: workers may not carry phones.', '3.3–5 V; 0x3C.'),
    ('3 × 12 mm IP65 buttons', 'Weatherproof; HELP front, ACK side (staff only).', 'Touch sensors: false triggers with sweat/rain. Membrane: UV ageing.', 'To GND, internal pull-ups.'),
    ('SFM-27 buzzer + LED', '>95 dB at <12 mA; visible + audible.', 'Passive piezo: quieter, needs tone code.', '12 V via 2N3904; LED 330 Ω at 3.3 V ≈ 8 mA.'),
    ('PP float switch', 'Dry contact; broken wire reads “low” (fail-safe).', 'Ultrasonic: cost, condensation. Capacitive: fouling.', 'IO35 input-only + 10 kΩ pull-up.'),
    ('12 V 2 A + MP1584 + 1 A fuse', '12 V feeds fan; buck is efficient; >3× margin.', '7805 linear: >50 % lost as heat in a sealed box.', 'Never USB and 5 V pin together.'),
    ('IP65 ABS box', 'Purchasable, rain-rated, glands down + vent.', '3D-printed PETG: softens near 60–70 °C, not rain-rated.', '175 × 100 × 60 fits 90 × 70 board + modules.'),
]

compat = [
    ('Logic levels', 'All sensors and the OLED run at 3.3 V on the ESP32’s own 3.3 V rail, so no level shifters are needed. The fan’s PWM and tach lines never see 12 V: PWM is pulled down by a transistor and tach is an open collector pulled up to 3.3 V.'),
    ('I²C address map', 'Four devices, four different addresses: 0x44, 0x45, 0x3C, 0x40. No clash. Bus at 50 kHz for the longer reference cable.'),
    ('Pins', 'Input-only pins (IO34, IO35) used only as inputs with external pull-ups. Strapping pins (0, 2, 12, 15) and flash pins (6–11) avoided. Every peripheral has its own GPIO.'),
    ('Current', f'3.3 V rail ≈ 25 mA typical vs ≈ 500 mA LDO budget. 12 V adapter ≈ {g["in_pk"]:.0f} mA peak vs 2000 mA rating.'),
    ('Timing', 'DS18B20 750 ms conversion runs in the background; Wi-Fi runs on the other core with a queue; the control loop is never blocked; 5 s watchdog.'),
    ('Mechanical', 'Every module fits the 160 × 86 mounting plate; clash check passes; glands spaced 30 mm for spanner access; box fits on a 60 mm SHS post with hose clamps.'),
]

questions = [
    ('What is new in your project? Shade shelters already exist.', 'Shade and cool roofs are not new and I do not claim them. What is new is the combination: a demountable cool shelter whose own sensors tell you whether it works, a fan controller that stops at 39 °C because research shows fans can add heat there, and a help request that cannot be lost.'),
    ('Why not just put an air conditioner?', 'An open shelter cannot hold cooled air, so most of the AC’s 1.4–1.6 kW would be wasted, and it needs mains power and servicing. If a site needs truly cooled air, NDMA treats an enclosed cooling room as a separate facility.'),
    ('Why not an evaporative cooler or mist fan?', 'They need water and cleaning, add humidity, and lose their effect in Vellore’s humid monsoon months. Hygiene of standing water is also a concern.'),
    ('Your model says the double roof adds only 2.6 °C. Why build it?', f'Because the seated MRT is dominated by shade, but the double roof keeps the underside ≈ {H["underside_cooler_k"]:.0f} °C cooler, which matters for anyone standing close to it, keeps working as the white coat gets dirty, and the upper skin is removable so we can test both on site.'),
    ('Is your model validated?', 'No, it is a screening model. It uses standard relations, its energy balance closes, and it has 17 tests. It makes predictions with tolerance bands for the roof underside and a globe thermometer, which we will check on three clear days.'),
    ('Why 39 °C as the fan cut-off?', 'Morris et al. 2021 propose 39 °C for young healthy adults, 38 °C for over-65s, 37 °C for older people on certain medicines; WHO says below 40 °C. We stop auto at 39 °C, warn from 37 °C, and leave manual to the worker.'),
    ('Why ESP32 and not Raspberry Pi?', 'The controller must survive power cuts and network loss. ESP32 boots instantly, has a hardware watchdog, PWM, flash for the help latch and costs ₹499. A Pi boots Linux from an SD card that can corrupt on power loss and uses far more power.'),
    ('Why two temperature sensors?', 'One at the seat, one outside as a reference at the same height. Weather changes affect both, so the difference shows what the shelter does. With one sensor you cannot separate the shelter from the weather.'),
    ('Why SHT30 and not DHT22?', 'SHT30 is digital I²C, faster and more accurate (±0.2 °C, ±2 %RH), and two can share one bus. DHT22 uses a timing-critical one-wire protocol and drifts in humidity.'),
    ('The website says SHT31 but the report says SHT30. Which?', 'SHT30 is the final choice: same typical accuracy in our range, same footprint and same addresses, at less than half the price. SHT31 is a drop-in upgrade if a wider accurate range is needed.'),
    ('Why does the fan need a tachometer?', 'Without it, a stalled or unplugged fan looks exactly like a running one. The tach lets the system say “fan fault” instead of claiming cooling.'),
    ('What happens if the ESP32 crashes?', 'The watchdog restarts it within 5 s and the help latch is restored from flash. Meanwhile the fan’s PWM line floats and, by the four-wire fan standard, the fan runs at full speed: it fails on, not off.'),
    ('What if Wi-Fi is down?', 'Nothing changes for the worker. All control is on the ESP32; Wi-Fi is only for logging and runs on a separate core.'),
    ('How does HELP work and why is ACK on the side?', 'HELP latches LED, buzzer and display and is saved in flash. Only ACK clears it. ACK is on the side so it is pressed deliberately by staff, not by accident.'),
    ('How did you choose the 1 °C margin?', 'Two ±0.5 °C sensors could disagree by up to about 1 °C before we correct their offset, so smaller differences cannot be trusted.'),
    ('How do you compare results across days?', 'One run is never a result. We need at least three valid runs on three different days, then a 95 % confidence interval; a direction is claimed only if the whole interval clears the margin.'),
    ('How much does it cost?', f'Electronics ≈ ₹{g["total"]:,}. The first shelter is estimated at ₹{FL:,}–₹{FH:,} including foundations, fabrication, transport and contingency. It is an estimate, not a quote. The retrofit option costs only the electronics.'),
    ('How will you reduce the shelter cost?', 'Repeated production, bolted standard sections, using an existing slab, optional upper skin, ground cover instead of bigger roof, and retrofitting existing sheds where possible.'),
    ('Is the structure safe?', 'The sections are candidates. Foundations, connections and wind loads must be designed and approved by a structural engineer before anyone sits under it. I state this in the report.'),
    ('How is it powered off-grid?', f'Daily need ≈ {g["wh_day"]:.0f} Wh; a 20 W panel with a 12 V 7 Ah battery would cover it. Not costed yet.'),
    ('Where exactly do sensors go and why?', 'Seat sensor at 1.1 m (seated head height) in a radiation shield; reference ≥ 2 m outside at the same height; roof probe on the lining centre; box at 1.4 m on a rear post.'),
    ('Why a radiation shield?', 'Sun or a hot roof shining on a sensor makes it read high. The plates block radiation while letting air through.'),
    ('Why glands at the bottom?', 'Rain runs off rather than into the box; drip loops make water drop before reaching the gland. The vent stops condensation being sucked in at night.'),
    ('What did you actually test?', 'Firmware compiles in CI (including Wi-Fi build); control logic has native C++ tests; 89 Python tests; both CAD models clash-checked; website browser-tested. Not yet: assembly and field measurement.'),
    ('What is the role of AI in this project?', 'None in control. There is an optional local explainer for finished data records that cannot change data or control anything.'),
    ('Why Vellore?', 'Hot pre-monsoon (May mean max ≈ 39 °C) and humid monsoon: a demanding test for both fan rules and weatherproofing, and it is where VIT is.'),
    ('Can it scale to a big site?', 'Yes, by placing one shelter per 4–6 resting workers near the work fronts, each with its node; data can go to one supervisor laptop over Wi-Fi.'),
    ('Is the simulator real or just an animation?', 'The decisions are real: the firmware’s own control header is compiled to WebAssembly and called directly, and a test shows identical results to the normal C++ build on 5,000 random cases. The loop around it copies main.cpp: debounce, 1 s sampling, tach maths, inverted PWM, flash latch. What is modelled is the sensor readings (sliders) and the fan’s speed and current, and the page says so.'),
    ('Why not just simulate everything in Wokwi?', 'I did build a Wokwi project that runs the real firmware binary. But Wokwi has no SHT30, INA219 or 4-wire fan, so I had to write those as custom chips in C, and it needs an account. The website simulator works anywhere without login, which is safer for a live demo.'),
    ('How did you test your custom Wokwi chips?', 'I compiled them with Wokwi’s exact compiler flags and ran them in a small stand-in for the Wokwi host, sending the same I²C bytes the Adafruit libraries send: SHT30 reset, status and measurement with CRC checks, and INA219 calibration and power reads; and driving the fan with the firmware’s 25 kHz PWM to check rpm, tach pulses and stall detection.'),
    ('Did the simulation find anything?', 'Yes, three real bugs: the seat and reference SHT30 addresses were swapped in the code compared with the design, the only firmware build had automatic mode switched off, and the first OLED line was 22 characters on a 21-character display. All fixed and re-tested.'),
    ('What would you do with more time?', 'Structural approval, build one shelter and two nodes, co-locate sensors, 3-day paired tests, compare single vs double roof, add GSM/LoRa for help alerts, design a PCB.'),
]

hard = [
    ('“So you haven’t built anything?”', 'Say calmly: “Not yet. This stage is a complete, tested design: CAD, circuit, firmware that compiles, and a test plan. I deliberately do not claim any cooling result until we measure it.” Then show the demo where the system refuses to claim.'),
    ('“This is just a fan under a roof.”', '“The roof and fan are standard. The contribution is how they are combined and checked: the roof chosen by a heat model, a fan that stops when it would add heat, fault detection, and evidence rules.”'),
    ('“Your numbers are from a model.”', '“Yes, and I label them as screening estimates with tolerance bands. The roof underside prediction is the cheapest thing to verify, with a ₹49 probe.”'),
    ('“Why not a cheaper fan?”', '“Cheap Indian 40/120 mm fans are 2-wire with no tachometer. Without feedback the system cannot detect a stalled fan, which is one of the problems we set out to solve.”'),
]

dont = [
    'Do not say the shelter “cools the air” or is “as good as AC”. Say it reduces radiant heat and moves air.',
    'Do not say it is “tested” or “proven”. Say firmware and logic are tested in software; field testing is next.',
    'Do not say “safe for workers” or mention medical benefits.',
    'Do not claim it is the first in the world or patentable.',
    'If you do not know an answer, say: “I have not checked that; I would find out by …”. Examiners respect that more than guessing.',
]

check = [
    'Print two copies of the report.',
    'Open every demo page once on the presentation laptop the day before (Vercel can be slow the first time).',
    'Keep the GitHub Pages mirror open in a second tab in case Vercel is blocked on the college network.',
    'Download the report PDF and slide deck to the laptop for offline use; take screenshots of each demo page as a last resort.',
    'Rehearse the 14-minute talk twice with a timer; the demo should be 5 minutes.',
    'Carry the numbers page printed or memorised.',
]

body = f"""
<h1>SAAYA Cool Shelter — Viva and Presentation Guide</h1>
<p class="sub">For Safal’s personal preparation. Not part of the submitted report.</p>

<h2>1. Your one-minute pitch (learn this by heart)</h2>
<div class="box">“Outdoor workers in Vellore rest under hot metal sheets in 39 °C heat. Nobody knows if these shades help, fans fail without anyone noticing, and there is no reliable way to call for help. SAAYA is a demountable cool shelter: a reflective, ventilated double roof with a deep overhang and a jaali screen does most of the cooling passively. An ESP32-based system measures the seat and outdoor air, the roof and the fan, runs the fan only when it helps, stops it above 39 °C where research shows fans add heat, detects faults, and gives workers a help button that cannot be lost. It costs about ₹{g["total"]:,} in electronics and every claim it makes must be backed by measurement.”</div>

<h2>2. Presentation plan — follows the slide deck (≈ 14 min talk + 5 min demo)</h2>
{tbl(['Slide', 'Content', 'Time', 'What to say'], [(a, e(bb), c, e(d)) for a, bb, c, d in slides], ['7%', '18%', '8%', '67%'])}
<p><b>Delivery tips.</b> Stand beside the screen, not in front of it. Point at the diagram while you talk about pins. Say numbers slowly. When you switch to the demo, say what you are about to show before clicking. Finish on the “what is proven / not yet proven” slide: honesty at the end leaves a strong impression.</p>

<h2>3. Live demo script — {e(SITE)}</h2>
{tbl(['Page', 'What to click and say'], [(f'<b>{e(p)}</b>', s) for p, s in demo], ['22%', '78%'])}
<p><b>Backup.</b> If Vercel does not load, use the mirror {e(MIRROR)}/ with the same page names. If there is no internet, open the report PDF and the slide deck offline.</p>

<h2>4. Numbers to remember</h2>
{tbl(['Item', 'Value'], [(e(a), e(bb)) for a, bb in numbers], ['34%', '66%'])}

<h2>5. Why every shelter decision — and why not the alternatives</h2>
{tbl(['Decision', 'Why', 'Why not the alternatives'], [(f'<b>{e(a)}</b>', e(bb), e(c)) for a, bb, c in shelter_why], ['20%', '40%', '40%'])}

<h2>6. Why every device — alternatives and compatibility</h2>
{tbl(['Device', 'Why chosen', 'Why not others', 'Compatibility'], [(f'<b>{e(a)}</b>', e(bb), e(c), e(d)) for a, bb, c, d in elec_why], ['14%', '31%', '31%', '24%'])}

<h2>7. How to prove the parts are compatible</h2>
{tbl(['Check', 'Explanation'], [(f'<b>{e(a)}</b>', e(bb)) for a, bb in compat], ['18%', '82%'])}

<h2>8. Explaining the firmware in 30 seconds</h2>
<p>“The ESP32 runs a loop. Every cycle it reads the buttons and applies the control rules; once a second it reads the sensors, updates the display and sends one record. The rules live in one header file that we test on a computer: HELP latches and only ACK clears it; manual fan is 70 %; auto fan is 50 % between 32 °C and 39 °C with hysteresis; if the fan is commanded but the tachometer shows under 100 rpm after 3 seconds it is a fault; a missing sensor is shown as unavailable, never as zero. A watchdog restarts the board in 5 seconds if anything hangs.”</p>

<h2>9. Questions examiners are likely to ask</h2>
{qa(questions)}

<h2>10. Hard questions and how to handle them</h2>
{qa(hard)}

<h2>11. Things not to say</h2>
<ul>{''.join(f'<li>{e(x)}</li>' for x in dont)}</ul>

<h2>12. Day-before checklist</h2>
<ul>{''.join(f'<li>{e(x)}</li>' for x in check)}</ul>
"""

CSS = """
@page{size:A4;margin:18mm 18mm 20mm 18mm}
html{font-family:'Liberation Sans',Arial,sans-serif;font-size:10.5pt;color:#111}
body{margin:0;line-height:1.45}
h1{font-size:20pt;margin:0 0 2mm;color:#173f33}
.sub{color:#555;margin:0 0 6mm}
h2{font-size:13.5pt;color:#173f33;border-bottom:1.5px solid #173f33;padding-bottom:1mm;margin:7mm 0 3mm;break-after:avoid}
p{margin:0 0 3mm}
.box{border-left:4px solid #173f33;background:#f2f6f3;padding:3mm 4mm;font-size:11pt;line-height:1.55}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:9.3pt;line-height:1.35;margin:1mm 0 3mm}
th{background:#173f33;color:#fff;text-align:left;padding:1.6mm 2mm}
td{border-bottom:.6pt solid #c8d1cc;padding:1.5mm 2mm;vertical-align:top}
tr{break-inside:avoid}thead{display:table-header-group}
tr:nth-child(even) td{background:#f6f8f6}
.qa{margin:0 0 3mm;break-inside:avoid}
.q{font-weight:bold;color:#173f33}
.a{margin-left:5mm}
ul{margin:0 0 3mm;padding-left:6mm}li{margin:0 0 1.5mm}
"""

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    src = OUT / 'viva.html'
    src.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>SAAYA viva guide</title><style>{CSS}</style></head><body>{body}</body></html>")
    tmp = OUT / 'viva-raw.pdf'
    subprocess.run(['node', str(ROOT / 'scripts' / 'print_report.cjs'), str(src), str(tmp)], check=True)
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    r = PdfReader(str(tmp)); w = PdfWriter(); n = len(r.pages)
    for i, pg in enumerate(r.pages):
        buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4); c.setFont('Helvetica', 8.5)
        c.drawCentredString(A4[0] / 2, 10 * 72 / 25.4, f'SAAYA cool shelter - viva and presentation guide - page {i + 1} of {n}'); c.save(); buf.seek(0)
        pg.merge_page(PdfReader(buf).pages[0]); w.add_page(pg)
    w.add_metadata({'/Title': 'SAAYA Cool Shelter - Viva and Presentation Guide', '/Author': 'Safal Gupta'})
    final = OUT / 'SAAYA_Viva_and_Presentation_Guide.pdf'
    with open(final, 'wb') as f:
        w.write(f)
    tmp.unlink(); src.unlink()
    print('Guide:', final, n, 'pages')
