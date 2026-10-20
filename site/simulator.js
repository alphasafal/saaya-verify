/* SAAYA Node hardware simulator.
 * Control rules: firmware/include/controller.h compiled to sim/controller.wasm (see scripts/build_sim_wasm.sh).
 * Loop: mirrors firmware/src/main.cpp line by line (debounce, 1 s sampling, tach maths, JSON, OLED text).
 * Physics (sensors, fan, INA219) is modelled and labelled as such on the page. */
(() => {
'use strict';
const NS = 'http://www.w3.org/2000/svg';
const $ = (s) => document.querySelector(s);
const svg = $('#board');
const STEP = 10;                       // ms of simulated time per firmware loop iteration
const PINS_L = ['3V3', 'EN', 'VP', 'VN', 'IO34', 'IO35', 'IO32', 'IO33', 'IO25', 'IO26', 'IO27', 'IO14', 'IO12', 'GND', 'IO13', 'SD2', 'SD3', 'CMD', '5V'];
const PINS_R = ['GND', 'IO23', 'IO22', 'TX', 'RX', 'IO21', 'GND', 'IO19', 'IO18', 'IO5', 'IO17', 'IO16', 'IO4', 'IO0', 'IO2', 'IO15', 'SD1', 'SD0', 'CLK'];
const PX_L = 492, PX_R = 648, pinY = (i) => 170 + 24 * i;
const PY = (name) => { let i = PINS_L.indexOf(name); if (i >= 0) return pinY(i); i = PINS_R.indexOf(name); return pinY(i); };

/* ------------------------------------------------------------------ SVG helpers */
function el(tag, attrs = {}, parent = svg) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; }
function txt(x, y, s, cls = '', parent = svg, anchor) { const t = el('text', { x, y, class: cls }, parent); if (anchor) t.setAttribute('text-anchor', anchor); t.textContent = s; return t; }
function wire(points, cls, id) { const p = el('polyline', { points: points.map((q) => q.join(',')).join(' '), class: `wire ${cls}` }); if (id) p.id = id; return p; }
function dot(x, y, color) { return el('circle', { cx: x, cy: y, r: 3.6, fill: color }); }
function card(x, y, w, h, title, sub) {
  const g = el('g');
  const r = el('rect', { x, y, width: w, height: h, rx: 8, class: 'card' }, g);
  txt(x + 12, y + 20, title, 'title', g); if (sub) txt(x + 12, y + 35, sub, 'sub', g);
  const badge = txt(x + w - 10, y + 19, '', 'badge', g, 'end');
  return { g, r, badge };
}
const W = {};   // wires by id
const V = {};   // live text by id

/* ------------------------------------------------------------------ draw the board */
function drawBoard() {
  // 12 V rail and fan feed (drawn first, under everything)
  W.feedFan = wire([[1170, 525], [1186, 525], [1186, 96], [180, 96], [180, 120]], 'w12');
  W.rail = wire([[160, 690], [950, 690]], 'w12');
  W.railIn = wire([[370, 735], [395, 735], [395, 690]], 'w12');
  W.buzz12 = wire([[160, 690], [160, 676]], 'w12');
  W.inaIn = wire([[950, 690], [950, 575]], 'w12');
  W.buckIn = wire([[600, 690], [600, 705]], 'w12');
  W.chain1 = wire([[150, 735], [175, 735]], 'w12'); W.chain2 = wire([[255, 735], [280, 735]], 'w12');
  W.v5 = wire([[520, 735], [470, 735], [470, PY('5V')], [PX_L, PY('5V')]], 'w5');
  [[395, 690], [600, 690], [160, 690], [950, 690]].forEach(([x, y]) => dot(x, y, '#c43c2c'));

  // left-side signal wires (lanes chosen so that none cross)
  const L = (pin, lane, ty, id) => { W[id] = wire([[PX_L, PY(pin)], [lane, PY(pin)], [lane, ty], [330, ty]], 'wsig', id); };
  L('IO34', 345, 200, 'tach'); L('IO25', 357, 300, 'pwm'); L('IO35', 372, 375, 'float');
  L('IO32', 387, 458, 'mode'); L('IO33', 402, 485, 'help'); L('IO26', 417, 540, 'led');
  L('IO27', 432, 600, 'ack'); L('IO14', 447, 655, 'buzz');

  // right-side buses
  W.scl = wire([[PX_R, PY('IO22')], [710, PY('IO22')], [710, 515]], 'wscl');
  W.sda = wire([[PX_R, PY('IO21')], [690, PY('IO21')], [690, 235], [690, 500]], 'wsda');
  const taps = [['oled', 235, 250], ['seat', 315, 330], ['ref', 410, 425], ['ina', 500, 515]];
  taps.forEach(([id, ys, yc]) => { W[id + 'Sda'] = wire([[690, ys], [870, ys]], 'wsda'); W[id + 'Scl'] = wire([[710, yc], [870, yc]], 'wscl'); dot(690, ys, '#2b6cb0'); dot(710, yc, '#b7950b'); });
  W.ow = wire([[PX_R, PY('IO4')], [670, PY('IO4')], [670, 625], [870, 625]], 'wsig');

  // ESP32-DevKitC V4
  el('rect', { x: 480, y: 120, width: 180, height: 540, rx: 10, fill: '#1d2b29' });
  el('rect', { x: 540, y: 128, width: 60, height: 112, rx: 4, fill: '#b8bdc0' });
  el('rect', { x: 546, y: 134, width: 48, height: 30, rx: 2, fill: '#9aa0a4' });
  txt(570, 190, 'ESP32', 'pinlbl', undefined, 'middle').setAttribute('fill', '#2a3333');
  txt(570, 204, 'WROOM-32', 'pin', undefined, 'middle').setAttribute('fill', '#2a3333');
  el('rect', { x: 550, y: 652, width: 40, height: 16, rx: 3, fill: '#a9afb3' });
  const lbl = txt(570, 420, 'ESP32-DevKitC V4', 'pinlbl', undefined, 'middle'); lbl.setAttribute('fill', '#9fb7ae'); lbl.setAttribute('transform', 'rotate(-90 570 420)');
  const used = new Set(['IO34', 'IO35', 'IO32', 'IO33', 'IO25', 'IO26', 'IO27', 'IO14', '5V', 'IO21', 'IO22', 'IO4', '3V3', 'GND']);
  PINS_L.forEach((n, i) => { el('rect', { x: PX_L - 5, y: pinY(i) - 5, width: 10, height: 10, rx: 2, fill: used.has(n) ? '#e0b64a' : '#77706a' }); const t = txt(PX_L + 10, pinY(i) + 4, n.replace('IO', ''), used.has(n) ? 'pinlbl' : 'pin'); if (used.has(n)) t.setAttribute('fill', '#f4e7c1'); });
  PINS_R.forEach((n, i) => { el('rect', { x: PX_R - 5, y: pinY(i) - 5, width: 10, height: 10, rx: 2, fill: used.has(n) ? '#e0b64a' : '#77706a' }); const t = txt(PX_R - 10, pinY(i) + 4, n.replace('IO', ''), used.has(n) ? 'pinlbl' : 'pin', undefined, 'end'); if (used.has(n)) t.setAttribute('fill', '#f4e7c1'); });
  V.esp = txt(570, 640, '', 'pin', undefined, 'middle'); V.esp.setAttribute('fill', '#cfe8d9');

  // ---------------- left cards
  const fan = card(30, 120, 300, 210, 'PWM fan + 2N3904 driver', 'Arctic P12 Pro 120 mm · 4-wire · 12 V');
  V.fanCard = fan;
  const rotor = el('g', { transform: 'translate(95 238)' }, fan.g);
  el('rect', { x: -58, y: -58, width: 116, height: 116, rx: 10, fill: '#2a3331' }, rotor);
  el('circle', { r: 52, fill: '#1a201f' }, rotor);
  V.blades = el('g', {}, rotor);
  for (let k = 0; k < 7; k++) el('path', { d: 'M0 0 C 12 -10, 40 -18, 46 -6 C 40 2, 20 4, 0 0 Z', fill: '#6f7b78', transform: `rotate(${k * 360 / 7})` }, V.blades);
  el('circle', { r: 12, fill: '#3b4643' }, rotor);
  V.fanVal = txt(170, 175, '', 'val', fan.g); V.fanSub = txt(170, 195, '', 'sub', fan.g); V.fanSub2 = txt(170, 212, '', 'sub', fan.g);
  txt(170, 250, 'Tach → IO34, 10 kΩ to 3V3', 'sub', fan.g); txt(170, 266, '+12 V via INA219 (top wire)', 'sub', fan.g);
  // Q1 symbol
  const q = el('g', { transform: 'translate(300 300)' }, fan.g);
  el('circle', { r: 13, fill: 'none', stroke: '#1c3832', 'stroke-width': 1.4 }, q);
  el('path', { d: 'M-4 -8 V8 M-4 -3 L6 -10 M-4 3 L6 10 M30 0 H-4', fill: 'none', stroke: '#1c3832', 'stroke-width': 1.4 }, q);
  txt(262, 324, 'Q1 2N3904', 'sub', fan.g);
  txt(170, 282, 'IO25 → 1 kΩ → Q1 (inverts)', 'sub', fan.g);

  const fl = card(30, 345, 300, 60, 'Float switch · water can', 'PP reed, NO · IO35 + 10 kΩ pull-up'); V.floatCard = fl; V.floatVal = txt(318, 395, '', 'val', fl.g, 'end');

  const bt = card(30, 418, 300, 82, 'Front buttons · IP65 12 mm, to GND');
  V.btnMode = button(bt.g, 290, 458, 'MODE', '#3d5f7a', 'IO32 · manual / auto'); V.btnHelp = button(bt.g, 290, 485, 'HELP', '#c0392b', 'IO33 · latched request');

  const ld = card(30, 515, 300, 50, 'Help / fault LED', 'IO26 · 330 Ω · ≈ 8 mA');
  V.ledGlow = el('circle', { cx: 290, cy: 540, r: 16, fill: '#ff4a3a', opacity: 0, class: 'ledglow' }, ld.g);
  V.led = el('circle', { cx: 290, cy: 540, r: 8, fill: '#6b2620', stroke: '#3a1512' }, ld.g);

  const ak = card(30, 578, 300, 44, 'ACK button · side wall', 'IO27 · staff only'); V.btnAck = button(ak.g, 290, 600, 'ACK', '#5b6466', '', true);

  const bz = card(30, 632, 300, 44, 'Buzzer SFM-27', 'IO14 → Q2 2N3904 → 12 V · > 95 dB'); V.bzCard = bz;
  V.bzWaves = el('g', { opacity: 0 }, bz.g);
  [8, 14, 20].forEach((r) => el('path', { d: `M${296 + r * .3} ${654 - r} A ${r} ${r} 0 0 1 ${296 + r * .3} ${654 + r}`, fill: 'none', stroke: '#c0392b', 'stroke-width': 2 }, V.bzWaves));
  el('circle', { cx: 290, cy: 654, r: 9, fill: '#222' }, bz.g);

  // ---------------- right cards
  const ol = card(870, 110, 300, 160, 'SSD1306 OLED 128×64', 'I²C 0x3C'); V.oledCard = ol;
  el('rect', { x: 920, y: 146, width: 213, height: 112, rx: 6, fill: '#0b0f12' }, ol.g);
  V.oled = el('image', { x: 924, y: 150, width: 205, height: 102, preserveAspectRatio: 'none', style: 'image-rendering:pixelated' }, ol.g);

  const se = card(870, 285, 300, 80, 'SHT30 · seat air (1.1 m)', '0x44 · ADDR → GND · in radiation shield'); V.seatCard = se; V.seatVal = txt(882, 357, '', 'val', se.g);
  const re = card(870, 380, 300, 80, 'SHT30 · outside reference', '0x45 · ADDR → 3V3 · 10 m Cat5e, ≥ 2 m out'); V.refCard = re; V.refVal = txt(882, 452, '', 'val', re.g);
  const ina = card(870, 475, 300, 100, 'INA219 · fan power', '0x40 · high side of the 12 V fan branch'); V.inaCard = ina; V.inaVal = txt(882, 545, '', 'val', ina.g);
  txt(882, 563, 'VIN+ from 12 V rail · VIN− to fan +12 V', 'sub', ina.g);
  const ds = card(870, 595, 300, 70, 'DS18B20 · roof lining', '1-Wire on IO4 · 4.7 kΩ pull-up'); V.roofCard = ds; V.roofVal = txt(882, 655, '', 'val', ds.g);

  // ---------------- power row
  const ad = card(30, 705, 120, 60, '12 V 2 A', 'SMPS adapter'); V.adCard = ad;
  card(175, 705, 80, 60, 'Fuse', '1 A slow');
  const sw = card(280, 705, 90, 60, 'Switch', 'rocker'); V.swCard = sw;
  const bk = card(520, 705, 160, 60, 'MP1584 buck', '12 V → 5.0 V'); V.bkCard = bk;
  V.power = txt(700, 742, '', 'sub'); V.power.setAttribute('font-size', '12');
}

function button(parent, x, y, label, color, sub, small) {
  const g = el('g', { class: 'btn', tabindex: 0, role: 'button', 'aria-label': `${label} button` }, parent);
  el('circle', { cx: x, cy: y, r: small ? 13 : 14, fill: '#d9ddd8', stroke: '#9aa29c' }, g);
  el('circle', { cx: x, cy: y, r: small ? 9 : 10, fill: color, class: 'cap' }, g);
  txt(x - 22, y + 4, label, 'title', g, 'end').setAttribute('font-size', '12');
  if (sub) txt(x - 72, y + 4, sub, 'sub', g, 'end');
  const name = label;
  const down = (e) => { e.preventDefault(); pressButton(name, true); g.classList.add('down'); };
  const up = () => { pressButton(name, false); g.classList.remove('down'); };
  g.addEventListener('pointerdown', down); g.addEventListener('pointerup', up); g.addEventListener('pointerleave', up);
  g.addEventListener('keydown', (e) => { if ((e.key === 'Enter' || e.key === ' ') && !e.repeat) { e.preventDefault(); tapButton(name); } });
  return g;
}

/* ------------------------------------------------------------------ firmware rules (WASM) */
let C = null;   // wasm exports
async function loadRules() {
  const buf = await (await fetch('sim/controller.wasm')).arrayBuffer();
  C = (await WebAssembly.instantiate(buf)).instance.exports;
}
const stepRules = (s, i) => {
  C.step(+s.help, +s.fanFault, s.duty, s.started >>> 0, +i.help, +i.ack, +i.manual, +i.automatic, +i.sensorFault, i.now >>> 0, Math.fround(i.rpm));
  return { help: !!C.outHelp(), fanFault: !!C.outFault(), duty: C.outDuty(), started: C.outStarted() >>> 0 };
};

/* ------------------------------------------------------------------ simulated world */
const sim = {
  build: 'field', speed: 1, paused: false, sound: false,
  wallMs: 11 * 3600e3,                  // time of day shown in the log
  env: { seatT: 33, seatRH: 50, outT: 35.5, outRH: 45, roofT: 41, waterLow: false },
  faults: { fanBlocked: false, tachCut: false, seatOff: false, refOff: false, roofOff: false, inaOff: false },
  nvs: { help: false },                 // ESP32 flash (Preferences "saaya")
  phys: { rpm: 0, pulseAcc: 0, fanDuty: 0, amps: 0.01 },
  pins: { MODE: false, HELP: false, ACK: false },   // true = pressed (pin pulled LOW)
  release: { MODE: Infinity, HELP: Infinity, ACK: Infinity }, pressT: { MODE: 0, HELP: 0, ACK: 0 },
  powered: true, offUntil: 0, day: null, fw: null,
  trace: [], serial: [], events: [],
};

class Button {   // firmware/src/main.cpp struct Button, verbatim logic
  constructor(name) { this.name = name; this.last = true; this.stable = true; this.changed = 0; }
  press(now) { const v = !sim.pins[this.name]; if (v !== this.last) { this.last = v; this.changed = now; } if (v !== this.stable && ((now - this.changed) >>> 0) >= 35) { this.stable = v; return !v; } return false; }
}
const hex8 = () => Math.floor(Math.random() * 2 ** 32).toString(16).padStart(8, '0');
const noise = (a) => (Math.random() - 0.5) * 2 * a;
const f32 = (x) => Number(Math.fround(x).toPrecision(7));
const shtQuant = (t, rh) => { const st = Math.round((t + 45) / 175 * 65535), srh = Math.round(rh / 100 * 65535); return [Math.fround(-45 + 175 * st / 65535), Math.fround(100 * srh / 65535)]; };

function setup() {                     // main.cpp setup()
  const fw = {
    t: 0, state: { help: false, fanFault: false, duty: 0, started: 0 }, autoOn: false, manual: false,
    inOK: !sim.faults.seatOff, outOK: !sim.faults.refOff, powerOK: !sim.faults.inaOff, displayOK: true,
    tachPulses: 0, lastSample: 0, seq: 0, session: `boot-${hex8()}-${hex8()}`, uptimeMs: 0,
    rpm: 0, temp: NaN, rh: NaN, ot: NaN, orr: NaN, roofTemp: NaN, sensorFault: true, haveRoofConversion: false,
    roofScratch: NaN, buttons: { MODE: new Button('MODE'), HELP: new Button('HELP'), ACK: new Button('ACK') },
    pwmVal: 255, led: false, buzzer: false, lines: [], i2cFlash: 0, watts: NaN, water: true,
  };
  fw.state.help = sim.nvs.help;        // preferences.getBool("help")
  fw.roofScratch = sim.faults.roofOff ? NaN : sim.env.roofT;   // roof.requestTemperatures()
  sim.fw = fw;
  log(`Node booted (${fw.session}). Help latch read from flash: ${fw.state.help ? 'ON' : 'off'}. Found: seat SHT30 ${fw.inOK ? '✓' : '✗'}, reference SHT30 ${fw.outOK ? '✓' : '✗'}, INA219 ${fw.powerOK ? '✓' : '✗'}, OLED ✓.`, fw.state.help ? 'alert' : '');
}

function loop(fw) {                    // main.cpp loop(), one iteration
  const now = fw.t;
  const prev = { ...fw.state }, prevAuto = fw.autoOn, prevManual = fw.manual;
  if (fw.buttons.MODE.press(now)) fw.manual = !fw.manual;
  const helpPressed = fw.buttons.HELP.press(now), ackPressed = fw.buttons.ACK.press(now);
  const benchAuto = sim.build === 'field';
  fw.autoOn = benchAuto && !fw.manual && !fw.sensorFault && !!C.autoRequest(+fw.autoOn, Math.fround(fw.temp));
  fw.state = stepRules(fw.state, { help: helpPressed, ack: ackPressed, manual: fw.manual, automatic: fw.autoOn, sensorFault: fw.sensorFault, now, rpm: fw.rpm });
  if (prev.help !== fw.state.help) sim.nvs.help = fw.state.help;          // preferences.putBool
  fw.pwmVal = 255 - Math.trunc(fw.state.duty * 255 / 100);                // ledcWrite (inverted by Q1)
  fw.led = fw.state.help || fw.state.fanFault || fw.sensorFault;
  fw.buzzer = fw.state.help && (now % 1000 < 120);
  narrate(fw, prev, prevAuto, prevManual, helpPressed, ackPressed);
  if (((now - fw.lastSample) >>> 0) < 1000) return;
  const elapsed = now - fw.lastSample; fw.lastSample = now;
  const pulses = fw.tachPulses; fw.tachPulses = 0; fw.rpm = Math.fround(pulses * 30000 / elapsed);
  const seatPresent = !sim.faults.seatOff, refPresent = !sim.faults.refOff;
  if (!fw.inOK) fw.inOK = seatPresent; if (!fw.outOK) fw.outOK = refPresent;
  const [st, srh] = shtQuant(sim.env.seatT + noise(0.04), Math.min(100, Math.max(0, sim.env.seatRH + noise(0.3))));
  const [ot, orh] = shtQuant(sim.env.outT + noise(0.04), Math.min(100, Math.max(0, sim.env.outRH + noise(0.3))));
  fw.ot = fw.outOK && refPresent ? ot : NaN; fw.orr = fw.outOK && refPresent ? orh : NaN;
  fw.temp = fw.inOK && seatPresent ? st : NaN; fw.rh = fw.inOK && seatPresent ? srh : NaN;
  if (!Number.isFinite(fw.ot) || !Number.isFinite(fw.orr)) fw.outOK = false; if (!Number.isFinite(fw.temp) || !Number.isFinite(fw.rh)) fw.inOK = false;
  fw.sensorFault = !fw.outOK || !fw.inOK || fw.rh < 0 || fw.rh > 100 || fw.orr < 0 || fw.orr > 100;
  if (fw.haveRoofConversion) fw.roofTemp = sim.faults.roofOff || !Number.isFinite(fw.roofScratch) ? NaN : Math.round(fw.roofScratch * 16) / 16;   // 12-bit, 0.0625 °C
  fw.haveRoofConversion = true; fw.roofScratch = sim.faults.roofOff ? NaN : sim.env.roofT + noise(0.05);
  fw.water = !sim.env.waterLow;        // float closed -> LOW -> available
  const powerPresent = !sim.faults.inaOff;
  if (!powerPresent) fw.powerOK = false; else if (!fw.powerOK) fw.powerOK = true;
  fw.watts = NaN;
  if (fw.powerOK) { const mw = 12.0 * sim.phys.amps * 1000; fw.watts = Math.fround(Math.round(mw / 2) * 2 / 1000); }   // power LSB 2 mW
  fw.i2cFlash = 220;
  const advice = C.fanAdvice(fw.sensorFault ? NaN : Math.fround(fw.temp));
  const fin = (v) => (Number.isFinite(v) ? f32(v) : null);
  const d = { schema_version: 1, device_id: 'saaya-esp32', session_id: fw.session, seq: fw.seq++, source: 'MEASURED', config_id: 'bench-v2-fan-branch-power', calibration_id: 'UNVERIFIED', acquired_ms: fw.uptimeMs, emitted_ms: fw.uptimeMs,
    temp: fin(fw.temp), rh: fin(fw.rh), outdoor_temp: fin(fw.ot), outdoor_rh: fin(fw.orr), roof_temp: fin(fw.roofTemp), watts: fin(fw.watts), rpm: f32(fw.rpm), duty: fw.state.duty, water: fw.water ? 'available' : 'low', help: fw.state.help,
    quality: fw.sensorFault ? 'invalid' : 'valid', fan_fault: fw.state.fanFault, fan_advice: ['ok', 'caution', 'avoid', 'unknown'][advice], clock_aligned: false, reference_valid: false, ref_roof: null, ref_air_speed: null, air_speed: null };
  serial(JSON.stringify(d));
  const p = (v, n) => (Number.isFinite(v) ? v.toFixed(n) : 'nan');
  fw.lines = ['SAAYA NODE / MEASURED', `T: ${p(fw.temp, 1)} RH: ${p(fw.rh, 0)}`, `Fan ${fw.state.duty}% ${p(fw.rpm, 0)} RPM`, fw.water ? 'Water available' : 'WATER LOW / CHECK',
    fw.state.help ? 'HELP REQUEST LATCHED' : fw.sensorFault ? 'SENSOR FAULT' : fw.state.fanFault ? 'FAN FEEDBACK FAULT' : advice === 2 ? 'HOT: FAN MAY ADD HEAT' : advice === 1 ? 'FAN: LIMITED BENEFIT' : 'Not a safety rating'];
  drawOled(fw.lines);
  sim.trace.push({ w: sim.wallMs, t: fw.temp, d: fw.state.duty, r: fw.rpm }); if (sim.trace.length > 5000) sim.trace.shift();
  narrateSample(fw, advice);
}

/* fan + tach + INA219 physics, one STEP */
function physics(fw) {
  const ph = sim.phys;
  const pwmIn = sim.powered && fw ? 1 - fw.pwmVal / 256 : 0;            // Q1 inverts the GPIO
  ph.fanDuty = sim.powered ? pwmIn : 0;
  const target = !sim.powered || sim.faults.fanBlocked || ph.fanDuty < 0.05 ? 0 : 450 + 2550 * (ph.fanDuty - 0.05) / 0.95;
  if (sim.faults.fanBlocked) ph.rpm = 0;
  else { const tau = target > ph.rpm ? 1200 : 2500; ph.rpm += (target - ph.rpm) * (1 - Math.exp(-STEP / tau)); if (ph.rpm < 1) ph.rpm = 0; }
  ph.amps = !sim.powered ? 0 : sim.faults.fanBlocked && ph.fanDuty >= 0.05 ? 0.05 : (ph.fanDuty >= 0.05 ? 0.03 : 0.01) + 0.30 * (ph.rpm / 3000) ** 2;
  ph.pulseAcc += ph.rpm / 60 * 2 * STEP / 1000;
  const whole = Math.floor(ph.pulseAcc); ph.pulseAcc -= whole;
  if (fw && sim.powered && !sim.faults.tachCut) fw.tachPulses += whole;
}

function tick(ms) {   // advance simulated time
  const n = Math.max(1, Math.round(ms / STEP));
  for (let k = 0; k < n; k++) {
    sim.wallMs += STEP;
    if (sim.day) dayStep();
    for (const b of ['MODE', 'HELP', 'ACK']) if (sim.pins[b] && sim.wallMs >= sim.release[b]) sim.pins[b] = false;
    if (!sim.powered) { physics(null); if (sim.wallMs >= sim.offUntil) { sim.powered = true; setup(); } continue; }
    const fw = sim.fw;
    physics(fw);
    loop(fw);
    fw.t += STEP; fw.uptimeMs += STEP;
    if (fw.i2cFlash > 0) fw.i2cFlash -= STEP;
  }
}

/* ------------------------------------------------------------------ narration */
const clock = (ms) => { const s = Math.floor(ms / 1000) % 86400; return `${String(Math.floor(s / 3600)).padStart(2, '0')}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`; };
function log(msg, cls = '') { sim.events.unshift({ t: clock(sim.wallMs), msg, cls }); if (sim.events.length > 80) sim.events.pop(); dirty.events = true; }
function serial(line) { sim.serial.push(line); if (sim.serial.length > 120) sim.serial.shift(); dirty.serial = true; }
function narrate(fw, prev, prevAuto, prevManual, helpPressed, ackPressed) {
  const s = fw.state, t = Number.isFinite(fw.temp) ? fw.temp.toFixed(1) : '—';
  if (fw.manual !== prevManual) log(fw.manual ? 'MODE pressed → manual fan at 70 % (never blocked by temperature).' : `MODE pressed → back to ${sim.build === 'field' ? 'automatic' : 'off (default build has no automatic mode)'}.`);
  if (fw.autoOn && !prevAuto) log(`Seat ${t} °C ≥ 32 °C → automatic fan ON at 50 %.`, 'good');
  if (!fw.autoOn && prevAuto && !fw.manual) {
    if (fw.sensorFault) log('Sensor fault → automatic fan inhibited.', 'alert');
    else if (fw.temp >= 39) log(`Seat ${t} °C ≥ 39 °C → automatic fan STOPPED: in air this hot a fan may add heat. MODE still gives manual 70 %.`, 'alert');
    else log(`Seat ${t} °C < 31 °C → automatic fan off.`);
  }
  if (s.help && !prev.help) log('HELP pressed → request LATCHED: LED on, buzzer beeping, OLED shows HELP. Saved to flash.', 'alert');
  if (!s.help && prev.help) log('ACK pressed on the side wall → help request cleared and flash updated.', 'good');
  if (ackPressed && !prev.help) log('ACK pressed (no help request was active).');
  if (helpPressed && prev.help) log('HELP pressed again (already latched).');
  if (s.fanFault && !prev.fanFault) log(`Fan commanded at ${s.duty} % but tach shows ${Math.round(fw.rpm)} rpm for 3 s → FAN FEEDBACK FAULT. No cooling is claimed.`, 'alert');
  if (!s.fanFault && prev.fanFault && s.duty > 0) log('Tach pulses back → fan fault cleared.', 'good');
}
let lastSample = null;
function narrateSample(fw, advice) {
  const L = lastSample; lastSample = { sf: fw.sensorFault, inOK: fw.inOK, outOK: fw.outOK, adv: advice, water: fw.water, power: fw.powerOK, roof: Number.isFinite(fw.roofTemp) };
  if (!L) return;
  if (fw.sensorFault && !L.sf) log(`${!fw.inOK ? 'Seat' : ''}${!fw.inOK && !fw.outOK ? ' and ' : ''}${!fw.outOK ? 'reference' : ''} SHT30 not answering → SENSOR FAULT: values sent as null, automatic fan inhibited.`, 'alert');
  if (!fw.sensorFault && L.sf) log('Both SHT30 sensors answering again → readings valid.', 'good');
  if (advice !== L.adv && !fw.sensorFault) { if (advice === 1) log('Seat ≥ 37 °C → OLED: “FAN: LIMITED BENEFIT”.'); if (advice === 2) log('Seat ≥ 39 °C → OLED: “HOT: FAN MAY ADD HEAT”.', 'alert'); }
  if (fw.water !== L.water) log(fw.water ? 'Float up → water available.' : 'Float dropped → OLED: “WATER LOW / CHECK”, record water = "low".', fw.water ? 'good' : 'alert');
  if (fw.powerOK !== L.power) log(fw.powerOK ? 'INA219 found again → fan power measured.' : 'INA219 not answering → watts sent as null (never guessed).', fw.powerOK ? 'good' : 'alert');
  if (L.roof && !Number.isFinite(fw.roofTemp)) log('Roof probe disconnected → roof_temp null.', 'alert');
  if (!L.roof && Number.isFinite(fw.roofTemp) && sim.trace.length > 2) log('Roof probe reading again.', 'good');
}

/* ------------------------------------------------------------------ OLED */
const oc = document.createElement('canvas'); oc.width = 128; oc.height = 64; const ox = oc.getContext('2d');
function drawOled(lines) {
  ox.fillStyle = '#000'; ox.fillRect(0, 0, 128, 64);
  ox.fillStyle = '#fff'; ox.font = '8px "DejaVu Sans Mono", Menlo, Consolas, monospace'; ox.textBaseline = 'alphabetic';
  let cx = 0, cy = 0;   // Adafruit GFX cursor, setTextWrap(true): println() of each line
  lines.forEach((s) => { for (const ch of s) { if (cx + 6 > 128) { cx = 0; cy += 8; } if (cy < 64) ox.fillText(ch, cx, cy + 7); cx += 6; } cx = 0; cy += 8; });
  const img = ox.getImageData(0, 0, 128, 64), px = img.data;
  for (let i = 0; i < px.length; i += 4) { const on = px[i] > 110; px[i] = on ? 214 : 4; px[i + 1] = on ? 236 : 6; px[i + 2] = on ? 255 : 10; px[i + 3] = 255; }
  ox.putImageData(img, 0, 0);
  V.oled.setAttribute('href', oc.toDataURL());
}

/* ------------------------------------------------------------------ inputs */
function pressButton(name, down) {
  if (down) { sim.pins[name] = true; sim.pressT[name] = sim.wallMs; sim.release[name] = Infinity; }
  else if (sim.pins[name] && sim.release[name] === Infinity) sim.release[name] = Math.max(sim.wallMs, sim.pressT[name] + 80);
}
function tapButton(name) { sim.pins[name] = true; sim.pressT[name] = sim.wallMs; sim.release[name] = sim.wallMs + 150; }
function powerCut() { if (!sim.powered) return; sim.powered = false; sim.offUntil = sim.wallMs + 1500; log('POWER CUT → node off, fan spinning down. Help latch is kept in flash.', 'alert'); V.oled.setAttribute('href', blankOled); lastSample = null; }
let blankOled = '';

const SCN = {
  morning: { seatT: 30, seatRH: 58, outT: 31.5, outRH: 55, roofT: 34 },
  warm: { seatT: 34, seatRH: 48, outT: 36.5, outRH: 42, roofT: 42 },
  extreme: { seatT: 40, seatRH: 32, outT: 42.5, outRH: 28, roofT: 47 },
};
function applyEnv(e) { Object.assign(sim.env, e); syncSliders(); }
function syncSliders() { for (const k of ['seatT', 'seatRH', 'outT', 'outRH', 'roofT']) { const i = $('#' + k); i.value = sim.env[k]; out(k); } $('#waterLow').checked = sim.env.waterLow; }
function out(k) { const v = sim.env[k]; $('#o-' + k).textContent = k.endsWith('RH') ? `${Math.round(v)} %` : `${(+v).toFixed(1)} °C`; }
function dayCurve(h) {   // representative Vellore May day at the seat (modelled)
  const x = Math.max(0, Math.sin(Math.PI * (h - 6) / 16));
  const seat = 28 + 12.2 * x ** 1.4;
  return { seatT: +seat.toFixed(2), seatRH: Math.round(70 - 38 * x), outT: +(seat + 1.5 + 1.2 * x).toFixed(2), outRH: Math.round(66 - 38 * x), roofT: +(30 + 13 * x).toFixed(2) };
}
function startDay() { sim.wallMs = 6 * 3600e3; sim.day = { end: 18 * 3600e3, last: 0 }; setSpeed(600); log('Playing a modelled Vellore May day, 06:00 → 18:00, at 600× speed.'); }
function dayStep() {
  if (sim.wallMs - sim.day.last >= 30e3) { sim.day.last = sim.wallMs; Object.assign(sim.env, dayCurve(sim.wallMs / 3600e3)); dirty.sliders = true; }
  if (sim.wallMs >= sim.day.end) { sim.day = null; setSpeed(1); log('Day finished at 18:00.'); }
}
function setSpeed(s) { sim.speed = s; document.querySelectorAll('[data-speed]').forEach((b) => b.setAttribute('aria-pressed', String(+b.dataset.speed === s))); $('#clock-chip').dataset.speed = s; }

function bindUI() {
  for (const k of ['seatT', 'seatRH', 'outT', 'outRH', 'roofT']) $('#' + k).addEventListener('input', (e) => { sim.env[k] = +e.target.value; out(k); });
  $('#waterLow').addEventListener('change', (e) => { sim.env.waterLow = e.target.checked; });
  document.querySelectorAll('[data-fault]').forEach((c) => c.addEventListener('change', () => { sim.faults[c.dataset.fault] = c.checked; log(`${c.checked ? 'Injected' : 'Removed'}: ${c.parentElement.textContent.trim()}.`, c.checked ? 'alert' : ''); }));
  document.querySelectorAll('[name=build]').forEach((r) => r.addEventListener('change', () => { sim.build = r.value; log(r.value === 'field' ? 'Firmware build: field (automatic fan band enabled).' : 'Firmware build: default (manual only, as shipped for bench use).'); }));
  document.querySelectorAll('[data-scn]').forEach((b) => b.addEventListener('click', () => { const s = b.dataset.scn; if (s === 'day') return startDay(); sim.day = null; applyEnv(SCN[s]); log(`Scenario: ${b.textContent}.`); }));
  document.querySelectorAll('[data-speed]').forEach((b) => b.addEventListener('click', () => { sim.day = null; setSpeed(+b.dataset.speed); }));
  $('#pause').addEventListener('click', (e) => { sim.paused = !sim.paused; e.target.setAttribute('aria-pressed', String(sim.paused)); e.target.textContent = sim.paused ? 'Run' : 'Pause'; });
  $('#powerCut').addEventListener('click', powerCut);
  $('#sound').addEventListener('change', (e) => { sim.sound = e.target.checked; });
  document.addEventListener('keydown', (e) => { if (e.target.closest('input,select,textarea')) return; const m = { m: 'MODE', h: 'HELP', a: 'ACK' }[e.key.toLowerCase()]; if (m && !e.repeat) tapButton(m); });
}

/* ------------------------------------------------------------------ render */
const dirty = { events: true, serial: true, sliders: false };
let angle = 0, audio = null, beepOn = false;
function setWire(w, mode) { if (!w) return; w.classList.toggle('live', mode === 'live'); w.classList.toggle('dead', mode === 'dead'); w.classList.toggle('flash', mode === 'flash'); }
function badge(c, text, color) { c.badge.textContent = text; c.badge.setAttribute('fill', color); }
function render(dtReal) {
  const fw = sim.fw, on = sim.powered, ph = sim.phys;
  angle = (angle + Math.min(ph.rpm, 3000) * 0.06 * dtReal / 1000 * 6) % 360;
  V.blades.setAttribute('transform', `rotate(${angle})`);
  const duty = on ? fw.state.duty : 0;
  V.fanVal.textContent = `${Math.round(ph.rpm)} rpm`;
  V.fanSub.textContent = on ? `Set ${duty} % · fan sees ${(ph.fanDuty * 100).toFixed(0)} %` : 'No power';
  V.fanSub2.textContent = on ? `IO25 high ${(100 * fw.pwmVal / 256).toFixed(0)} % · tach ${sim.faults.tachCut ? 'cut' : (ph.rpm / 30).toFixed(0) + ' Hz'}` : '';
  const fanState = !on ? ['OFF', '#63726a'] : sim.faults.fanBlocked && duty ? ['STALLED', '#b2461b'] : fw.state.fanFault ? ['FAULT', '#b2461b'] : ph.rpm > 50 ? ['RUNNING', '#2f7d5b'] : ['STOPPED', '#63726a'];
  badge(V.fanCard, ...fanState); V.fanCard.r.classList.toggle('fault', on && fw.state.fanFault);
  setWire(W.pwm, on && duty ? 'live' : '');
  setWire(W.tach, sim.faults.tachCut ? 'dead' : on && ph.rpm > 50 ? 'live' : '');
  setWire(W.feedFan, on && ph.amps > 0.02 ? 'live' : '');
  // float
  V.floatVal.textContent = sim.env.waterLow ? 'WATER LOW' : 'Water OK'; V.floatVal.setAttribute('fill', sim.env.waterLow ? '#b2461b' : '#1f5039');
  // LED, buzzer
  const led = on && fw.led; V.led.setAttribute('fill', led ? '#ff5b4a' : '#6b2620'); V.ledGlow.setAttribute('opacity', led ? 0.55 : 0);
  setWire(W.led, led ? 'live' : '');
  const bz = on && fw.buzzer; V.bzWaves.setAttribute('opacity', bz ? 1 : 0); setWire(W.buzz, bz ? 'flash' : '');
  beep(bz && sim.sound);
  ['mode', 'help', 'ack'].forEach((k) => setWire(W[k], sim.pins[k.toUpperCase()] ? 'flash' : ''));
  // sensors
  const sv = (t, rh) => (Number.isFinite(t) ? `${t.toFixed(2)} °C · ${rh.toFixed(1)} %RH` : 'no data (null)');
  V.seatVal.textContent = on ? sv(fw.temp, fw.rh) : '—'; V.refVal.textContent = on ? sv(fw.ot, fw.orr) : '—';
  V.roofVal.textContent = on ? (Number.isFinite(fw.roofTemp) ? `${fw.roofTemp.toFixed(2)} °C` : 'no data (null)') : '—';
  V.inaVal.textContent = on ? (Number.isFinite(fw.watts) ? `12.0 V · ${(fw.watts / 12).toFixed(3)} A · ${fw.watts.toFixed(2)} W` : 'no data (null)') : '—';
  const st = (c, off, ok) => { c.r.classList.toggle('off', off); badge(c, off ? 'UNPLUGGED' : !on ? '' : ok ? 'OK' : 'FAULT', off || !ok ? '#b2461b' : '#2f7d5b'); };
  st(V.seatCard, sim.faults.seatOff, on && fw.inOK); st(V.refCard, sim.faults.refOff, on && fw.outOK); st(V.inaCard, sim.faults.inaOff, on && fw.powerOK);
  st(V.roofCard, sim.faults.roofOff, on && Number.isFinite(fw.roofTemp)); badge(V.oledCard, on ? 'OK' : '', '#2f7d5b');
  const flash = on && fw.i2cFlash > 0 ? 'flash' : '';
  setWire(W.sda, flash); setWire(W.scl, flash);
  [['oled', false], ['seat', sim.faults.seatOff], ['ref', sim.faults.refOff], ['ina', sim.faults.inaOff]].forEach(([id, off]) => { setWire(W[id + 'Sda'], off ? 'dead' : flash); setWire(W[id + 'Scl'], off ? 'dead' : flash); });
  setWire(W.ow, sim.faults.roofOff ? 'dead' : flash);
  // power
  const pw = on ? ['live', ''] : ['dead', 'dead'];
  [W.rail, W.railIn, W.buzz12, W.inaIn, W.buckIn, W.chain1, W.chain2].forEach((w) => setWire(w, on ? '' : 'dead')); setWire(W.v5, on ? '' : pw[1]);
  V.power.textContent = on ? `Node ≈ ${(0.9 + 12 * ph.amps).toFixed(1)} W (fan ${(12 * ph.amps).toFixed(2)} W)` : 'Rebooting…';
  V.esp.textContent = on ? `up ${(fw.uptimeMs / 1000).toFixed(0)} s · ${fw.manual ? 'MANUAL' : sim.build === 'field' ? 'AUTO' : 'OFF'}` : 'power off';
  badge(V.swCard, on ? 'ON' : 'OFF', on ? '#2f7d5b' : '#b2461b');
  $('#clock-chip').textContent = `${clock(sim.wallMs)} · ${sim.paused ? 'paused' : sim.speed + '×'}`;
  if (dirty.sliders) { syncSliders(); dirty.sliders = false; }
  if (dirty.events) { $('#events').innerHTML = sim.events.map((e) => `<li class="${e.cls}"><time>${e.t}</time><span>${escapeHtml(e.msg)}</span></li>`).join(''); dirty.events = false; }
  if (dirty.serial) { const s = $('#serial'); const atEnd = s.scrollTop + s.clientHeight >= s.scrollHeight - 30; s.textContent = sim.serial.join('\n'); if (atEnd) s.scrollTop = s.scrollHeight; dirty.serial = false; drawTrace(); }
}
const escapeHtml = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function beep(on) {
  if (on === beepOn) return; beepOn = on;
  try {
    if (!audio && on) { const ctx = new (window.AudioContext || window.webkitAudioContext)(); const o = ctx.createOscillator(); const g = ctx.createGain(); o.frequency.value = 2800; g.gain.value = 0; o.connect(g).connect(ctx.destination); o.start(); audio = { ctx, g }; }
    if (audio) audio.g.gain.value = on ? 0.05 : 0;
  } catch (_) { /* audio unavailable */ }
}
function drawTrace() {
  const cv = $('#trace'), g = cv.getContext('2d'), Wd = cv.width, Hd = cv.height, padL = 34, padB = 22;
  g.clearRect(0, 0, Wd, Hd); g.font = '11px DM Sans, sans-serif'; g.fillStyle = '#63726a';
  const pts = sim.trace.slice(sim.day || sim.trace.length > 600 && sim.speed > 20 ? -5000 : -300);
  const y = (v, lo, hi) => Hd - padB - (v - lo) / (hi - lo) * (Hd - padB - 10);
  [[32, 'auto on 32'], [39, 'auto stop 39']].forEach(([v, s]) => { g.strokeStyle = '#d7dfd3'; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(padL, y(v, 20, 45)); g.lineTo(Wd, y(v, 20, 45)); g.stroke(); g.setLineDash([]); g.fillText(s, Wd - 74, y(v, 20, 45) - 3); });
  [20, 25, 30, 35, 40, 45].forEach((v) => g.fillText(v, 6, y(v, 20, 45) + 4));
  if (pts.length < 2) return;
  const x = (i) => padL + i / (pts.length - 1) * (Wd - padL - 6);
  const line = (key, lo, hi, color) => { g.strokeStyle = color; g.lineWidth = 2; g.beginPath(); let pen = false; pts.forEach((p, i) => { const v = p[key]; if (!Number.isFinite(v)) { pen = false; return; } const yy = y(v, lo, hi); if (pen) g.lineTo(x(i), yy); else { g.moveTo(x(i), yy); pen = true; } }); g.stroke(); };
  line('t', 20, 45, '#c4572c'); line('d', 0, 100, '#275c49'); line('r', 0, 3000, '#2b6cb0');
  g.fillStyle = '#63726a'; g.fillText(clock(pts[0].w), padL, Hd - 6); g.fillText(clock(pts[pts.length - 1].w), Wd - 54, Hd - 6);
}

let lastFrame = performance.now();
function frame(now) {
  const dt = Math.min(100, now - lastFrame); lastFrame = now;
  if (!sim.paused) tick(dt * sim.speed);
  render(sim.paused ? 0 : dt);
  requestAnimationFrame(frame);
}

/* ------------------------------------------------------------------ start */
const ready = (async () => {
  drawBoard();
  drawOled([]); blankOled = oc.toDataURL();
  bindUI();
  try { await loadRules(); } catch (e) { $('#wasm-chip').textContent = 'Could not load firmware rules (WebAssembly)'; $('#wasm-chip').classList.add('bad'); throw e; }
  $('#wasm-chip').textContent = 'Firmware rules: controller.h → WebAssembly ✓'; $('#wasm-chip').classList.add('ok');
  setup();
  requestAnimationFrame(frame);
})();

// Hooks for automated tests and for driving a demo from the console.
window.saayaSim = {
  ready,
  advance(ms) { tick(ms); render(0); },
  press(name) { tapButton(name); },
  set(env) { applyEnv(env); },
  fault(name, on) { sim.faults[name] = on; const c = document.querySelector(`[data-fault="${name}"]`); if (c) c.checked = on; },
  build(b) { sim.build = b; document.querySelector(`[name=build][value=${b}]`).checked = true; },
  pause(p) { sim.paused = p; },
  powerCut,
  state() { const fw = sim.fw; return { powered: sim.powered, duty: fw.state.duty, help: fw.state.help, fanFault: fw.state.fanFault, manual: fw.manual, autoOn: fw.autoOn, sensorFault: fw.sensorFault, rpm: fw.rpm, physRpm: sim.phys.rpm, led: fw.led, oled: fw.lines.slice(), nvsHelp: sim.nvs.help, lastJson: sim.serial[sim.serial.length - 1] ? JSON.parse(sim.serial[sim.serial.length - 1]) : null, events: sim.events.map((e) => e.msg) }; },
};
})();
