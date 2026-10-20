"""Body text of the VIT report (cool shelter). Imported by build_report.py, which supplies the helpers."""


def build(chapter, section, sub, para, figure, rotated_figure, table, ref, R, g, P, E, H, T, e):
    b = []
    FS = {  # FS-01 cool shelter key dimensions (cad/fullsize, design-basis.md)
        'post_x': 2400, 'post_y': 2000, 'roof_x': 2800, 'roof_y': 2400, 'clear': 2310, 'fall': 120, 'gap': 120,
        'bench': '1400 × 450', 'seat_h': 450,
    }
    ov = {r['extra_overhang_m']: r for r in T['overhang']}
    gr = {r['surround']: r for r in T['ground']}
    ss = T['second_skin']
    bands = {x['target']: x for x in T['prediction_bands']}
    full_lo = sum(x[1] for x in g['FULL']); full_hi = sum(x[2] for x in g['FULL'])

    # ------------------------------------------------------------------ 1
    b.append(chapter('Introduction'))
    b.append(section('Background'))
    b.append(para(
        f'Outdoor work in India does not stop for the summer. Masons, road crews, farm labourers and delivery riders keep working through April and May, when the afternoon air in Vellore regularly sits close to 39 °C and has touched 45 °C {ref(R["imd"])}. The International Labour Organization estimates that heat stress could cost India about 5.8 percent of its working hours by 2030, roughly 34 million full-time jobs {ref(R["ilo"])}. The 2025 Lancet Countdown put the potential labour lost to heat in India in 2024 at 247 billion hours {ref(R["lancet"])}.',
        f'For most of these workers the only relief during a break is whatever shade happens to be on site: a sheet of galvanised iron on four poles, a cement-sheet lean-to, or the shadow of a parked truck. In 2025 the National Disaster Management Authority published draft guidelines asking for proper shaded rest structures for outdoor workers, with reflective roofs instead of bare metal sheets, cross-ventilation and shaded, unpaved ground around them {ref(R["ndma"])}. This project takes those guidelines as a starting point and asks what a cool shelter for a worksite should look like, and how it can show that it is actually working.'))
    b.append(section('Problem statement'))
    b.append(para(
        'Three problems were identified with the rest shades found on typical worksites. The roof itself is often the worst part: a bare or weathered metal sheet absorbs sunlight and its underside becomes a radiant heater above the people sitting below it. There is no feedback of any kind, so if a fan has been fitted, nobody notices when it stalls or loses its supply. And a worker who starts to feel unwell has no dependable way to call for help other than shouting or walking to find a supervisor.',
        'The problem addressed here is to design a low-cost cool shelter for outdoor workers that reduces radiant heat by passive means, moves air only when that is useful, measures the conditions it actually produces, refuses to report a benefit it cannot demonstrate, and gives workers a help request that cannot be lost.'))
    b.append(section('Objectives'))
    b.append('<ol>' + ''.join(f'<li>{x}</li>' for x in [
        'To design a demountable cool shelter of about 2.4 m × 2.0 m for four to six seated workers, with a reflective ventilated double roof, a deep overhang, a side screen and a bench.',
        'To select sensors, a controller and an actuator that measure seat-level air, an outdoor reference, roof temperature, water availability, fan speed and fan energy, at around ₹5,000 for the electronics.',
        'To design the interfacing circuit for an ESP32 microcontroller, with every pin, bus address and supply rail documented.',
        'To develop dimensioned 3D models of the shelter and of the weatherproof electronics enclosure, with sensor positions, from parts and sections available in India.',
        'To write firmware that keeps working without a network, detects sensor and fan faults, latches help requests and avoids running the fan in conditions where it may add heat.',
        'To plan the installation, power, connectivity and maintenance of the shelter on a worksite in Vellore.']) + '</ol>')
    b.append(section('Scope and limitations'))
    b.append(para(
        'The report covers the design of the shelter structure, its passive cooling features, the electronic system (called SAAYA Node), the firmware, the 3D models and the deployment plan. The firmware compiles and its control logic has been tested in software, and both 3D models have been checked for clashes between parts. The shelter has not been fabricated and nothing has been measured outdoors, so no measured cooling benefit or health effect is claimed. The structural sections are candidates that still need approval by a qualified structural engineer, and the shelter cost is a planning estimate, not a quotation.'))
    b.append(section('Organisation of the report'))
    b.append(para(
        'Chapter 2 reviews the literature behind the design. Chapter 3 describes the proposed cool shelter, the real-life scenario and how it operates. Chapters 4 and 5 justify the choice of materials and components and list their specifications. Chapter 6 presents the interfacing diagram. Chapter 7 describes the 3D models of the shelter and the electronics enclosure. Chapter 8 explains deployment, Chapter 9 the implementation and testing, and Chapter 10 concludes the report.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 2
    b.append(chapter('Literature Survey'))
    b.append(section('Heat exposure in a shaded rest area'))
    b.append(para(
        f'The heat a resting person feels outdoors depends on air temperature, humidity and air speed, and also on radiation from the sun, the sky, the ground and any roof overhead. This radiant part is usually expressed as the mean radiant temperature (MRT). Measurements during a record heatwave in Tempe, Arizona, found that tree shade lowered afternoon MRT by up to 33 °C while air temperature across the same sites varied by less than 4.5 °C {ref(R["middel"])}. For a shelter the message is clear: blocking radiation matters far more than trying to cool the air, which an open structure cannot hold anyway.'))
    b.append(section('Cool roofs in India'))
    b.append(para(
        f'Indian pilots show that roof treatment makes a measurable difference. In an Ahmedabad trial by the Mahila Housing Trust, a white solar-reflective coating on a tin roof lowered the daytime indoor temperature by about 1 °C, and modular roofs and false ceilings did somewhat better {ref(R["mht"])}. These were closed rooms rather than open shelters, but they confirm that the finish and the underside temperature of a roof are worth designing for and worth measuring.'))
    b.append(section('Lessons from traditional Indian buildings'))
    b.append(para(
        'Traditional buildings in hot parts of India handle heat with a few simple ideas: deep verandahs and chajjas that keep the sun off walls and people, jaali screens that cut low-angle sun while letting air through, and roofs with an air space that carries heat away before it reaches the room. The shelter borrows these ideas in a light, demountable form: a 200 mm roof overhang on every side, a removable louvred screen on the sun-facing side and a two-layer roof with a ventilated gap. Heavy thermal mass and evaporative cooling were deliberately left out, because a warm night stops thermal mass from recovering and evaporative systems need water and cleaning and lose their effect in humid monsoon weather.'))
    b.append(section('When does a fan help?'))
    b.append(para(
        f'A fan cools by speeding up the evaporation of sweat, but when the air is hotter than the skin it also blows heat onto the body. Ravanelli <i>et al.</i> found that at 42 °C a fan still helped young men, but only up to a limited humidity {ref(R["ravanelli"])}. Gagnon <i>et al.</i> repeated a similar test with adults around 68 years old and found no benefit, with heart rate and core temperature slightly higher with the fan on {ref(R["gagnon"])}. A clinical trial by Morris <i>et al.</i> found fans helping in hot, humid conditions and making things worse in very hot, dry conditions {ref(R["morris19"])}. A later model by the same group proposed upper air-temperature limits for fan use of 39 °C for young healthy adults, 38 °C for people over 65 and 37 °C for older people on anticholinergic medication, and advised against relying on fans alone in northern India {ref(R["morris21"])}. The WHO recommends using fans only below 40 °C {ref(R["who"])}.',
        'This research is the reason the shelter’s controller does not behave like a thermostat. Above about 39 °C it stops running the fan automatically and tells the worker why, while leaving manual control in their hands.'))
    b.append(section('Measuring radiant heat cheaply'))
    b.append(para(
        f'MRT is normally estimated from a black globe thermometer together with air temperature and air speed. Teitelbaum <i>et al.</i> showed that the standard correction becomes inaccurate below about 1 m/s {ref(R["teitelbaum"])}, which is typical under a shelter. The design therefore measures what can be measured reliably and cheaply (air temperature and humidity at the seat and outside, and the temperature of the roof underside) and keeps globe measurements as a separate validation step.'))
    b.append(section('Research gap'))
    b.append(para(
        'Shade structures and cool roofs are well understood, and fans are known to help only within limits. What is missing at worksite level is a cheap shelter that combines passive cooling with measurement, controls its fan within safe limits and is honest about what it does not know. The SAAYA cool shelter is an attempt to fill that gap.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 3
    b.append(chapter('Proposed Cool Shelter and Real-Life Scenario'))
    b.append(section('The practical problem'))
    b.append(para(
        'Consider a building site on the outskirts of Vellore in May. Around fifteen workers take their afternoon break under a galvanised sheet on four poles. The sheet is old and grey, and by 1 p.m. its underside is hotter than the air. A pedestal fan was once tied to a pole but stopped working weeks ago and nobody noticed. When one of the workers feels dizzy, the others have to find the supervisor on foot.'))
    b.append(section('Overview of the cool shelter'))
    b.append(para(
        f'The SAAYA cool shelter is a four-post steel frame with post centres of {FS["post_x"]} × {FS["post_y"]} mm and a roof that projects {FS["roof_x"]} × {FS["roof_y"]} mm, giving a 200 mm overhang on every side. The roof is made of two skins: a white, reflective upper sheet that sends most of the sunlight back to the sky, and a lower lining about {FS["gap"]} mm below it. The gap between them is open at the edges so that wind and rising warm air carry away the heat absorbed by the upper sheet before it reaches the lining. The roof falls {FS["fall"]} mm towards the front for drainage. A {FS["bench"]} mm bench sits at the rear, a removable louvred screen shades the sun-facing side, and the front stays open for access. Clear height under the front of the roof is {FS["clear"]} mm (Fig. 3.1).',
        'The smart part of the shelter, called SAAYA Node, is a weatherproof electronics box fixed to a rear post. It reads the conditions under and outside the shelter, drives a small fan, shows the status on a display and handles help requests.'))
    b.append(figure('shelter-iso.png', 'The SAAYA cool shelter: steel frame, ventilated double roof, louvred side screen, bench, SAAYA Node enclosure on the rear post, seat sensor stand and water can', '92%'))
    b.append(section('Intended users'))
    b.append(para(
        'Workers use the shelter during breaks: they read the display, press MODE to switch the fan and press HELP if someone needs assistance. The site supervisor or safety officer receives help requests and acknowledges them with a separate button. The site engineer looks at the logged data to decide whether, for example, repainting the roof or planting the surrounding ground has made a difference.'))
    b.append(section('How the shelter keeps people cool'))
    b.append(para(
        'Most of the cooling is passive. The roof blocks direct sun from the seated area; the reflective upper skin keeps the roof itself from becoming a heater; the ventilated gap and the lining keep the surface that people see close to air temperature; the overhang widens the shadow; and the louvred screen cuts low-angle sun from the side while letting air through. The fan is a small addition that increases air movement over seated workers when the air is warm but not yet hot enough for a fan to become counter-productive.'))
    b.append(section('How the smart system operates'))
    b.append(para(
        'Once a second, the ESP32 inside SAAYA Node reads the air temperature and humidity at seat height, a matching reference sensor placed outside the shelter, the temperature of the roof underside, a float switch in the drinking-water can, the actual speed of the fan from its tachometer signal and the electrical power drawn by the fan.',
        'When a worker presses MODE, the fan runs at 70 percent. In automatic mode it starts at 32 °C and stops below 31 °C, so it does not switch on and off around a single threshold. If the seat-level air reaches 39 °C, automatic operation stops and the display reads “HOT: FAN MAY ADD HEAT”, although the worker can still switch the fan on manually. If the fan is commanded but its tachometer shows no rotation after three seconds, the display shows a fan fault and no cooling is reported for that period.',
        'Pressing HELP latches a request: the red LED lights, the buzzer sounds and the display shows the request. The latch is kept in flash memory, so it survives a power cut or a reset, and it can only be cleared with the ACK button, which sits on the side of the box so that it is pressed deliberately by staff. Readings go to a laptop over USB, or optionally over the site Wi-Fi to the supervisor.'))
    b.append(section('Design reasoning from a heat model'))
    b.append(para(
        f'Before fixing the roof design, a small steady-state model was written to see which features actually reduce the heat felt by a seated worker {ref(R["swinbank"], R["watmuff"])}. It balances sunlight, sky and ground radiation and wind on each roof skin and computes the MRT at the head of a seated worker from the exact solid angle of the roof, sky and ground. For a clear 38 °C noon in mid-May in Vellore it predicts that moving from open sun into the shade of a weathered metal shed lowers MRT by about {H["shade_alone_k"]:.0f} °C, and that the SAAYA cool roof lowers it by a further {H["roof_treatment_k"]:.1f} °C (Fig. 3.2). The bigger difference is in the roof underside, which the model expects to run about {H["underside_cooler_k"]:.0f} °C cooler than the weathered sheet, so the surface just above people’s heads stays close to air temperature.'))
    b.append(figure('mrt-chart.png', 'Predicted mean radiant temperature at a seated worker’s head for different roof options (screening model, clear 38 °C noon in mid-May, Vellore)', '74%'))
    b.append(para(
        f'The model also showed what else is worth spending on. Adding 0.3 m of overhang on every side lowers the seated MRT by about {ov[0.0]["tmrt_c"] - ov[0.3]["tmrt_c"]:.1f} °C, and replacing dry bare ground around the shelter with irrigated ground cover lowers it by about {gr["typical dry ground"]["tmrt_c"] - gr["irrigated grass / ground cover"]["tmrt_c"]:.0f} °C, because a seated person sees far more ground and sky than roof. Light-coloured paving does the opposite: it reflects sunlight back up and raises MRT by about {gr["light paving"]["tmrt_c"] - gr["typical dry ground"]["tmrt_c"]:.0f} °C. The upper skin of the double roof cuts the lining temperature by {ss[0]["single_underside_c"] - ss[0]["double_underside_c"]:.0f} to {ss[-1]["single_underside_c"] - ss[-1]["double_underside_c"]:.0f} °C, and its value grows as the white top coat gets dirty. These results set the priorities in the design: shade and overhang first, then the cool roof, then the ground around the shelter.'))
    b.append(section('Expected benefits'))
    b.append('<ul>' + ''.join(f'<li>{x}</li>' for x in [
        'A rest place where direct sun and the hot-roof effect are removed, with the roof underside kept near air temperature.',
        'A help request that cannot be lost or silently cleared, and that still works when the network or the laptop is down.',
        'Immediate notice of a stalled fan, a disconnected sensor or an empty water can.',
        'Paired readings from the seat and from outside the shelter, so the site can see whether the shelter, or a later improvement, actually helped.',
        f'Very low energy use: about {g["wh_day"]:.0f} Wh a day for the electronics and fan, compared with 11 to 13 kWh in one shift for a 1.5-ton air conditioner.']) + '</ul>')
    b.append(section('Why the design suits this application'))
    b.append(para(
        'An open shelter cannot keep air-conditioned air in, so cooling the air is not a realistic goal. What can be done is to block radiation, move air sensibly and keep watch. The frame is bolted from repeated steel sections so it can be moved when the site moves; the electronics run entirely on the microcontroller so they do not depend on the internet; and the same electronics can be fitted to an existing shed when a new shelter is not affordable.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 4
    b.append(chapter('Component Selection and Justification'))
    b.append(section('Selection criteria'))
    b.append(para(
        'Every material and component was judged against the same criteria: whether it contributes to cooling or to measurement rather than only appearance; cost; accuracy adequate for a 1 °C decision margin; power consumption; an operating range covering shaded outdoor air between 25 °C and 45 °C and monsoon rain; compatibility with the rest of the system (3.3 V logic and the I²C bus for the electronics, bolted connections for the structure); and availability from Indian suppliers.'))
    b.append(section('Shelter structure and passive cooling elements'))
    b.append(table('Selection of the shelter structure and passive cooling elements', ['Element', 'Selected', 'Reasons for selection', 'Alternatives considered'], [
        ('Frame', '<b>Steel SHS 60×60×3 posts, RHS 80×60×3 beams, RHS 60×40×3 purlins</b>', 'Standard sections stocked across India; bolted plate connections make the shelter demountable; galvanised or painted for corrosion', 'Bamboo (variable strength, termites, hard to bolt), timber (rot, fire), aluminium extrusions (higher cost, harder to weld locally)'),
        ('Upper roof skin', '<b>White coated steel sheet</b>', 'Reflects most sunlight; cheap and replaceable; the white top coat can be repainted when dirty', 'Bare galvanised sheet (hot underside), cement sheet (heavy, brittle), polycarbonate (lets light and heat through)'),
        ('Roof gap', '<b>About 120 mm, open at the edges</b>', 'Wind and rising air carry heat away before it reaches the lining; the gap is set by 30×30 spacers that also carry the upper skin', 'Sealed gap (traps heat), insulated sandwich panel (cost, holds heat into the evening)'),
        ('Lower lining', '<b>Painted aluminium sheet</b>', 'Stays near air temperature behind the ventilated gap; paint resists corrosion and the model shows the finish matters little once the lining is cool', 'No lining (the hot upper skin faces people), false ceiling boards (moisture, fixings)'),
        ('Overhang', '<b>200 mm on every side</b>', 'Widens the shadow at the bench without enlarging the post grid', 'Larger overhang (more wind uplift and cost; considered as an upgrade)'),
        ('Side screen', '<b>Removable timber louvres 20×40, on two rails</b>', 'Cuts low-angle sun from the side while letting air through, like a jaali', 'Solid wall (blocks breeze), fabric (wears out quickly in UV)'),
        ('Bench', '<b>1400×450, seat height 450, timber or recycled-plastic slats</b>', 'Comfortable seated height; slats drain rain and do not get as hot as metal', 'Steel bench (too hot to touch), concrete (fixed, heavy)'),
        ('Foundation', '<b>200×200×10 base plates with 4 anchors each</b>', 'Bolts to a slab or footing and can be lifted and moved', 'Embedded posts (permanent; cannot be relocated)'),
    ], ['13%', '23%', '35%', '29%'], 'small'))
    b.append(section('Electronic components'))
    b.append(table('Selection of the electronic components', ['Function', 'Selected part', 'Reasons for selection', 'Alternatives considered'],
                   [(e(a), f'<b>{e(bb)}</b>', e(c), e(d)) for a, bb, c, d in g['SEL']], ['14%', '16%', '38%', '32%'], 'small'))
    b.append(section('Discussion of key choices'))
    b.append(sub('Why a ventilated double roof instead of a single cool sheet'))
    b.append(para(
        'A single sheet painted white on top already removes much of the solar heat, but its underside still runs well above air temperature on a clear day, and the difference grows as the coating gets dirty. A second skin with a ventilated gap keeps the lining close to air temperature even when the top coat has aged, protects the white coating from being scratched from below, and gives a cool surface just above the heads of standing workers. The upper skin is bolted on spacers so it can be removed, which also allows a site to compare the single and double roof directly with the shelter’s own sensors.'))
    b.append(sub('Microcontroller'))
    b.append(para(
        f'The ESP32 combines two I²C controllers, sixteen PWM channels, interrupt-capable inputs for the fan tachometer, Wi-Fi, flash storage and a hardware watchdog on a ₹499 board {ref(R["esp32"])}. An Arduino Uno would need extra hardware for networking and has very little memory for the telemetry records. A Raspberry Pi was rejected because it boots an operating system from an SD card that can be corrupted by the frequent power cuts on worksites.'))
    b.append(sub('Temperature and humidity sensors'))
    b.append(para(
        f'The SHT31 was the first choice, but the cheaper SHT30 has the same typical accuracy of ±0.2 °C between 0 °C and 65 °C and ±2 percent relative humidity {ref(R["sht3x"])}, which covers the range under a shelter. Two SHT30 modules save about ₹440, and they share one bus because one is set to address 0x44 and the other to 0x45.'))
    b.append(sub('Fan'))
    b.append(para(
        f'A four-wire PWM fan was essential because its tachometer output proves that the fan is actually turning. The four-wire specification also requires such fans to run at full speed when the PWM line is not driven {ref(R["intel"], R["noctua"])}, so if the controller fails the fan fails on rather than off. The Arctic P12 Pro delivers 77 CFM at 0.33 A and stops completely below 5 percent PWM, which gives a genuine off state. A 230 V pedestal fan was rejected because it brings mains voltage into a wet outdoor space and gives no feedback.'))
    b.append(sub('Power'))
    b.append(para(
        f'A 12 V, 2 A adapter feeds the fan directly, and an MP1584 buck module produces 5 V for the board. A linear regulator would waste more than half of the power as heat inside a closed box. The MP1584 chip is marked as not recommended for new designs by its maker {ref(R["mp1584"])}, which is acceptable for a prototype; the MP2338 is noted as its replacement for production.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 5
    b.append(chapter('Technical Specifications'))
    b.append(section('Shelter specification'))
    b.append(table('Specification of the cool shelter structure', ['Item', 'Specification'], [(e(a), e(bb)) for a, bb in [
        ('Plan size', f'Post centres {FS["post_x"]} × {FS["post_y"]} mm; roof projection {FS["roof_x"]} × {FS["roof_y"]} mm (200 mm overhang each side)'),
        ('Height', f'Front clear height {FS["clear"]} mm; roof falls {FS["fall"]} mm over 2000 mm (3.4°) towards the front gutter'),
        ('Capacity', '4 to 6 seated workers on a 1400 mm bench, plus standing space and an open access bay'),
        ('Posts', 'SHS 60 × 60 × 3 mm; front 2300 mm, rear 2420 mm long; 200 × 200 × 10 mm base plates, 4 anchors each'),
        ('Beams and purlins', 'Two RHS 80 × 60 × 3 mm crossbeams, 2580 mm; three RHS 60 × 40 × 3 mm purlins at 2000 mm span; two 6 mm knee gussets'),
        ('Roof', 'White coated steel upper skin; painted aluminium lower lining; nine SHS 30 × 30 × 2 spacers, about 118 mm, with bolted caps'),
        ('Side screen', '14 timber louvres 20 × 40 × 1070 mm on two RHS 30 × 30 × 2 mm rails, 1400 mm long, removable'),
        ('Bench', '1400 × 450 mm, seat height 450 mm, six 70 × 25 mm slats on SHS 40 × 40 × 2 mm legs and rails'),
        ('Connections', 'M10 bolts at roof connection plates, M6 at spacer caps; weld and bolt schedule subject to structural approval'),
        ('Modelled mass', 'About 250 kg using idealised material densities'),
    ]], ['22%', '78%'], 'small'))
    b.append(section('Electronic component specifications'))
    spec_rows = []
    for a, sup, cur, rng, acc, itf, size, src in g['SPEC']:
        rk = {'ESP32-WROOM-32E datasheet (Espressif)': R['esp32e'], 'SHT3x-DIS datasheet (Sensirion)': R['sht3x'], 'DS18B20 datasheet (Analog Devices)': R['ds18b20'],
              'INA219 datasheet (TI)': R['ina219'], 'SSD1306 controller datasheet': R['ssd1306'], '2N3904 datasheet (onsemi)': R['2n3904'], 'MP1584 datasheet (MPS)': R['mp1584']}.get(src)
        spec_rows.append((f'<b>{e(a)}</b>', e(sup) + '<br>' + e(cur), e(rng) + '<br>' + e(acc), e(itf), e(size), ref(rk) if rk else 'supplier'))
    b.append(table('Technical specifications of the electronic components', ['Component', 'Supply and current', 'Range and accuracy', 'Interface', 'Dimensions', 'Source'], spec_rows, ['17%', '22%', '24%', '15%', '14%', '8%'], 'small'))
    b.append(section('Power budget'))
    b.append(para(
        f'Table 5.3 adds up the expected current on each supply rail. With the fan at 70 percent and Wi-Fi off, the system draws about {g["in_typ"]:.0f} mA from the 12 V adapter, about {g["w_typ"]:.1f} W. In the worst case, with the fan at full speed, the Wi-Fi radio transmitting and the buzzer on, it draws about {g["in_pk"]:.0f} mA or {g["w_pk"]:.1f} W, assuming an 85 percent efficient buck converter. The 2 A adapter has a margin of more than three times, and a 1 A slow-blow fuse protects the field wiring.'))
    b.append(table('Power budget per supply rail', ['Load', 'Rail', 'Typical (mA)', 'Peak (mA)', 'Note'],
                   [(e(a), e(rr), str(t), str(p), e(n)) for a, rr, t, p, n in g['POWER']], ['36%', '10%', '14%', '14%', '26%'], 'small'))
    b.append(para(
        f'Running the fan for eight hours and the controller for twenty-four hours uses about {g["wh_day"]:.0f} Wh a day. A 20 W solar panel on the roof with a 12 V, 7 Ah battery could therefore power the shelter on sites without mains, although that option has not been costed here.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 6
    b.append(chapter('Interfacing Design'))
    b.append(section('Circuit overview'))
    b.append(para(
        'Fig. 6.1 shows every connection between the ESP32-DevKitC, the sensors, the fan, the user controls and the power supply. All signals use 3.3 V logic. The four I²C devices share one bus on GPIO21 and GPIO22, run at 50 kHz rather than the usual 100 kHz to give extra margin on the several metres of cable to the reference sensor outside the shelter. The fan is controlled through a 2N3904 transistor so that the ESP32 never connects directly to the fan’s own circuitry, and a second transistor drives the 12 V buzzer.'))
    b.append(rotated_figure('interfacing-diagram-rot.png', 'Interfacing diagram of the SAAYA Node electronics showing all pins, bus addresses, pull-up resistors, driver stages and supply rails'))
    b.append(section('Pin assignment'))
    b.append(table('ESP32 pin assignment', ['ESP32 pin', 'Function', 'Direction', 'Conditioning', 'Connected to'],
                   [(f'<b>{e(a)}</b>', e(bb), e(c), e(d), e(f_)) for a, bb, c, d, f_ in g['PINS']], ['12%', '20%', '10%', '30%', '28%'], 'small'))
    b.append(para('The strapping pins GPIO0, GPIO2, GPIO12 and GPIO15 were avoided because their state at power-up decides how the chip boots, and GPIO6 to GPIO11 are connected to the on-board flash memory.'))
    b.append(section('Design rules taken from the datasheets'))
    b.append('<ul>' + ''.join(f'<li>{x}</li>' for x in [
        f'GPIO34 to GPIO39 are input-only and have no internal pull-up resistors {ref(R["esp32"])}, so the fan tachometer and the float switch use GPIO34 and GPIO35 with external 10 kΩ pull-ups to 3.3 V.',
        f'The fan PWM signal is generated at 25 kHz, the frequency required by the four-wire fan specification, and the tachometer gives two pulses per revolution {ref(R["intel"])}.',
        f'The DevKitC must be powered from either USB or its 5 V pin, never both at once {ref(R["esp32"])}. In the shelter it runs from the buck converter, and USB is used only for programming.',
        f'The INA219 can sense up to 26 V {ref(R["ina219"])}; it sits on the high side of the 12 V fan supply and measures the fan’s energy only.',
        f'The DS18B20 needs a 4.7 kΩ pull-up on its data line {ref(R["ds18b20"])}, and its 750 ms conversion is started in the background so it never delays the control loop.']) + '</ul>')
    b.append('</section>')

    # ------------------------------------------------------------------ 7
    b.append(chapter('3D Model Design'))
    b.append(section('Modelling approach'))
    b.append(para(
        'Both models were built in CadQuery, a Python library for parametric CAD, so every dimension lives in code and the drawings, renders and this report all read the same numbers. The shelter model contains 44 part definitions and 143 placed instances; the electronics enclosure model contains 23 solids. Both are exported as STEP files for use in any CAD package and as STL meshes for the web viewer, and an automatic check confirms that no two solids overlap by more than 1 mm³ in either model.'))
    b.append(section('Shelter structure'))
    b.append(para(
        'The frame is made of welded side frames and a bolted roof module so that it can be transported in pieces and assembled with hand tools. Fig. 7.1 shows the frame with the roof removed: the two crossbeams sit on the posts with knee gussets at the front, and three purlins carry the roof skins. Fig. 7.2 is the general arrangement drawing with the post grid, roof outline, bench and clear height.'))
    b.append(figure('shelter-open.png', 'Shelter frame with the roof skins removed, showing posts, crossbeams, knee gussets, purlins, louvred screen, bench, electronics enclosure and sensor stands', '82%'))
    b.append(rotated_figure('general-arrangement-rot.png', 'General arrangement of the cool shelter: plan with post grid, roof outline and bench, and front elevation with frame, double roof and clear height'))
    b.append(section('Placement of devices in the shelter'))
    b.append(table('Positions of the smart-system devices in the shelter model (datum: front-left post centre at floor level, mm)', ['Device', 'Position (x, y, z)', 'Reason'], [(e(a), e(bb), e(c)) for a, bb, c in [
        ('SAAYA Node enclosure', 'rear right post, z ≈ 950–1200', 'Shaded, within reach of a seated or standing person, close to the cable route'),
        ('Fan', '(850, 1880, 1400) on a rear service rail', 'Above and behind the bench, aimed down at seated workers'),
        ('Seat T/RH sensor', '(1450, 1750, 1100) on a stem by the bench', 'Seated head height, in the occupied zone, in a radiation shield'),
        ('Roof probe', '(1300, 1000, under the lining)', 'Centre of the roof underside, the surface people see'),
        ('Reference T/RH sensor', 'own stand; moved ≥ 2 m outside the roof edge in use', 'Measures outdoor air at the same height for a fair comparison'),
        ('Water can and float', '(0, 1640, 0), rear left', 'Away from the electronics; easy to refill'),
    ]], ['24%', '34%', '42%'], 'small'))
    b.append(section('Electronics enclosure'))
    b.append(para(
        f'The electronics live in a purchased IP65 ABS box of {E["W"]} × {E["H"]} × {E["D"]} mm, which the model treats as a box to be drilled rather than a part to be printed. A 3D-printed housing was rejected because PETG can soften in the 60 to 70 °C air just below a sunlit roof and is not rated for rain. Inside, a 90 × 70 mm perforated board carries the ESP32, the two driver transistors, the pull-up resistors and pluggable terminal blocks for the field wiring, with the INA219, buck converter and fuse holder beside it on a metal plate (Fig. 7.3).',
        'The display window is at the top left, where people look first. The HELP button, the status LED and the MODE button form one column on the right, with the LED directly above HELP so the state of a request is shown next to the button that made it. All five cable glands face the ground so that rain runs off rather than in, and a breathable vent on the left wall stops condensation being drawn in as the box cools every night (Figs. 7.4 and 7.5). An aluminium back bracket clamps to the shelter post with two hose clamps or screws to a wall.'))
    b.append(figure('render-internals.png', 'Electronics enclosure with the lid removed: ESP32 board and terminals (left), INA219, buck converter and fuse (right), vent and side ACK button', '78%'))
    b.append(f'<div class="pair">{figure("render-front.png", "Enclosure front panel", "100%", "half")}{figure("render-bottom.png", "Underside with five PG7 glands", "100%", "half")}</div>')
    dims = [
        ('Enclosure', f"{E['W']} × {E['H']} × {E['D']}, wall {E['wall']}, lid depth {E['lid_depth']}", 'Purchasable IP65 box with at least 10 mm of wiring space'),
        ('OLED window', f"{P['oled_window']['w']} × {P['oled_window']['h']} at x = {P['oled_window']['x']}, z = {P['oled_window']['z']}", 'Clears the 21.7 × 10.9 mm active area'),
        ('HELP, MODE, LED', f"Ø12, Ø12, Ø8 on x = {P['help_button']['x']}; z = {P['help_button']['z']}, {P['mode_button']['z']}, {P['status_led']['z']}", 'One column for the right hand; LED above HELP'),
        ('ACK button', f"Ø12 on right wall, y = {P['ack_button']['y']}, z = {P['ack_button']['z']}", 'Reached only on purpose, by staff'),
        ('Cable glands', f"5 × PG7 (Ø12.5) at x = {', '.join(map(str, P['glands_bottom']['xs']))}, y = {P['glands_bottom']['y']}", 'Face down; 30 mm pitch leaves room for a spanner'),
        ('Vent', f"M12 (Ø12.5) on left wall, y = {P['vent_side']['y']}, z = {P['vent_side']['z']}", 'Equalises pressure, limits condensation'),
        ('Back bracket', f"{P['bracket']['W']} × {P['bracket']['H']} × 3 aluminium; 4 × Ø6.5 on 194 × 90; 4 slots 8 × 16", 'Hose clamps on a 40–90 mm post, or wall anchors'),
        ('Radiation shield', '5 plates Ø110 at 14 mm pitch on three M5 rods', 'Shades the air sensor while letting air pass'),
        ('Fan', '120 × 120 × 25 with guards on both faces', 'Mounted on the rear rail with an adapter plate'),
    ]
    b.append(table('Principal dimensions of the electronics enclosure (mm, datum at front-left-bottom corner)', ['Feature', 'Dimension', 'Reason'], [(e(a), e(bb), e(c)) for a, bb, c in dims], ['18%', '44%', '38%'], 'small'))
    b.append(rotated_figure('enclosure-drawing-rot.png', 'Dimensioned drilling and mounting drawing of the electronics enclosure, back bracket and internal layout'))
    b.append('</section>')

    # ------------------------------------------------------------------ 8
    b.append(chapter('Deployment Capability'))
    b.append(section('Installation area and orientation'))
    b.append(para(
        'The shelter is meant for construction sites, road projects, farms and factory yards where workers rest outdoors, with one shelter for every four to six people on break at the same time. A larger site with thirty to sixty workers would place several shelters near the work fronts rather than one large one, so that nobody has to walk far in the heat. The open front faces away from the afternoon sun, and the louvred screen goes on the west or south-west side, which takes the low afternoon sun in Vellore. The shelter should stand on shaded or planted ground where possible, not on light paving.'))
    b.append(section('Foundation and erection'))
    b.append(para(
        'Each post stands on a 200 × 200 × 10 mm base plate with four anchors into a small concrete footing or an existing slab. The side frames are welded in a workshop, carried to site and bolted to the crossbeams and purlins; the roof skins and spacers are then bolted on and the screen and bench fitted. The size of the footings and anchors depends on the soil and the local wind load and must be designed by a structural engineer for each site.'))
    b.append(section('Mounting the smart system'))
    b.append(para(
        'The electronics box is clamped to a rear post with its centre about 1.4 m above the floor, within easy reach and well above splashing water. The seat sensor stands beside the bench at 1.1 m, the head height of a seated person, and the reference sensor stands at least 2 m outside the roof edge at the same height so that the two readings can be compared fairly. The roof probe is fixed to the centre of the lining with thermal tape, and the fan is mounted on the rear rail about 1 m from the seat, tilted 30 to 45 degrees down (Fig. 8.1). Cables run in UV-stabilised conduit along the post and the purlins.'))
    b.append(rotated_figure('installation-elevation-rot.png', 'Side elevation of the shelter showing mounting heights and sensor positions'))
    b.append(section('Power availability'))
    b.append(para(
        f'Most sites have a 230 V socket in the site office or on a distribution board. The 12 V adapter is kept in the dry and only safe low voltage is run to the shelter. Peak demand is under {g["w_pk"]:.0f} W. For sites without mains, the {g["wh_day"]:.0f} Wh daily need can be met by a small solar panel on the roof and a battery.'))
    b.append(section('Connectivity'))
    b.append(para(
        'The system is offline-first: every control decision is made on the ESP32. Data can be collected in two ways. In the basic setup a laptop connected by USB runs the local logging software. In the Wi-Fi build, the node posts each reading to the supervisor’s laptop over the site network, authenticated with a device token. The Wi-Fi code runs as a separate task on the second processor core, so a weak signal can never delay the buttons, the help alarm or the fan. No cloud account or SIM card is needed, although a GSM or LoRa link could be added for remote sites.'))
    b.append(section('Environmental conditions'))
    b.append(para(
        'In Vellore the shaded air ranges from about 25 °C to 45 °C, afternoon humidity in the hot months is around 43 to 51 percent, and the north-east monsoon brings heavy rain from October to December. The roof falls towards a front gutter, the steel is galvanised or painted, the electronics are rated well above 60 °C, the enclosure is IP65 with its cable entries facing down and a vent for condensation, and the adapter is kept out of the sun and rain.'))
    b.append(section('Maintenance'))
    b.append(table('Maintenance schedule', ['Interval', 'Task'], [(e(a), e(bb)) for a, bb in [
        ('Weekly', 'Wipe the radiation shields and fan guard; check the float switch and refill the water can; clear leaves from the roof gap'),
        ('Monthly', 'Check glands, cables and conduit; compare commanded and measured fan speed on the display; clean the gutter'),
        ('Every three months', 'Place the two SHT30 sensors side by side for 20 minutes and record their offset; check bolt tightness and touch up paint'),
        ('Yearly or when dirty', 'Wash or repaint the white top coat of the upper skin; inspect base plates and anchors for corrosion'),
        ('On a fault message', 'The display names the fault (sensor, fan feedback or water); every electronic part is plugged in and can be replaced in minutes')]], ['22%', '78%'], 'small'))
    b.append(section('Retrofit option'))
    b.append(para(
        'Where a site already has a sound shed and cannot afford a new shelter, the same SAAYA Node can be clamped to an existing post and the roof underside painted. This brings the help request, fault detection and measurement to the existing shade for the cost of the electronics alone, and the measurements can later show whether a full cool shelter is worth building.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 9
    b.append(chapter('Implementation and Testing'))
    b.append(section('Firmware structure'))
    b.append(para(
        'The firmware is written in C++ for the Arduino framework and built with PlatformIO. The decision logic (help latch, fan duty, start-up grace period and fault detection) is kept in a single header file with no hardware dependencies, so the same code can be compiled and tested on a computer. The main loop polls the buttons every cycle, applies the control logic and, once a second, reads the sensors, updates the display and prints one JSON record. A five-second hardware watchdog restarts the board if the loop hangs.'))
    b.append(section('Operating states'))
    b.append(table('Response of the system to each operating state', ['State or event', 'System response'], [(e(a), e(bb)) for a, bb in [
        ('Air below 32 °C, automatic mode', 'Fan off; it starts at 32 °C and stops below 31 °C'),
        ('32 °C to 37 °C, automatic mode', 'Fan at 50 percent; normal display'),
        ('37 °C to 39 °C', 'Fan allowed; display warns that benefit is limited for older or medicated people'),
        ('39 °C or above', 'Automatic fan stops and restarts below 38.5 °C; display reads “HOT: FAN MAY ADD HEAT”; manual still allowed'),
        ('MODE pressed', 'Switches between manual 70 percent and off'),
        ('HELP pressed', 'Request latched; LED, buzzer and display; kept in flash through a reset'),
        ('ACK pressed by staff', 'Clears the request; HELP wins if both are pressed together'),
        ('Fan commanded, tachometer below 100 rpm after 3 s', 'Fan feedback fault shown; any cooling claim for the period is withdrawn'),
        ('Sensor missing or invalid', 'Sensor fault shown; readings marked unavailable, never zero; automatic mode disabled'),
        ('Float switch open or wire broken', '“WATER LOW / CHECK” shown'),
        ('Firmware stalls', 'Watchdog restarts the board within 5 s; the help latch is restored')]], ['38%', '62%'], 'small'))
    b.append(section('Verification carried out'))
    b.append(para(
        'The firmware, including the optional Wi-Fi version, is compiled automatically on GitHub Actions for the esp32dev board. The control logic passes native C++ tests covering the help latch, manual override, fault detection, start-up grace, timer roll-over, hysteresis and the fan-benefit limit, and the same rules are tested in the Python data service and in the web demonstration. The data service has 89 automated tests. The shelter model passes the clash check over all 143 instances, the enclosure model over all 23 solids, and the public website is tested in a browser at desktop and phone widths.',
        f'A circuit for the online Wokwi ESP32 simulator has been prepared with the same pin assignment {ref(R["wokwi"])}. Wokwi does not provide models of the SHT3x, the INA219 or a PWM fan, so the simulation is mainly useful for the help latch and the fault messages; it has been set up but not yet run.'))
    b.append(section('Cost summary'))
    b.append(para(
        f'The electronics cost about ₹{g["total"]:,}, of which ₹{g["listed"]:,} comes from prices listed on Indian supplier websites and the rest is estimated (Appendix A). The first shelter is estimated at ₹{full_lo:,} to ₹{full_hi:,}, including steel, roof, fabrication, finishing, bench and screen, electronics allowance, foundations, transport, engineering review and a 15 percent contingency (Appendix B). This is a planning estimate, not a quotation. Repeated production, bolted standard sections and sites with an existing slab would bring the figure down, and the retrofit option costs only the electronics.'))
    b.append(section('Limitations'))
    b.append(para(
        'Several things have not yet been demonstrated: the real temperature of the roof underside and the air speed at the seat, the error introduced by the home-made radiation shields, the efficiency of the buck converter in a hot box, whether the enclosure stays watertight after drilling, the strength of the frame and its connections, and any effect on how workers feel. The structural sections need approval by a qualified engineer before anyone sits under a full-size shelter.'))
    b.append('</section>')

    # ------------------------------------------------------------------ 10
    b.append(chapter('Conclusion and Future Work'))
    b.append(section('Conclusion'))
    b.append(para(
        f'This project designed the SAAYA cool shelter, a demountable rest shelter for outdoor workers that keeps people cool mainly by passive means and uses a low-cost IoT system to control a fan sensibly, detect faults, handle help requests and measure the conditions it produces. The {FS["post_x"]} × {FS["post_y"]} mm steel frame carries a reflective, ventilated double roof with a 200 mm overhang, a louvred side screen and a bench for four to six people. The smart system uses an ESP32 with two SHT30 sensors, a DS18B20 roof probe, an INA219 power monitor, a four-wire PWM fan, an OLED display and three weatherproof buttons in a {E["W"]} × {E["H"]} × {E["D"]} mm IP65 box.',
        'Two findings shaped the design more than anything else. A heat model showed that shade removes most of the radiant heat and that a cool, ventilated roof keeps the surface above people’s heads near air temperature, which set the order of priorities: shade and overhang, then the cool roof, then the ground around the shelter. Studies of fan use showed that a fan can add heat above about 39 °C, which led to a controller that steps back from automatic operation at that point instead of running harder.'))
    b.append(section('Future work'))
    b.append('<ol>' + ''.join(f'<li>{x}</li>' for x in [
        'Have the frame and connections designed and approved by a structural engineer, and obtain a fabrication quotation in Vellore.',
        'Build one shelter and two electronics units, place the sensors side by side to measure their offsets, and compare the roof underside and seat conditions with the model on at least three clear days.',
        'Compare the single and double roof directly by removing the upper skin for some of the test days.',
        'Add a GSM or LoRa link so that help requests reach a supervisor’s phone on sites without Wi-Fi, and design a small printed circuit board for the electronics.',
        'Carry out a supervised field trial with worker consent and a proper safety protocol, and only then report any effect on comfort.']) + '</ol>')
    b.append('</section>')
    return b
