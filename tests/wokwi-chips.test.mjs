// Runs the compiled Wokwi custom chips (firmware/wokwi-full/*.chip.c) inside a minimal stand-in for
// the Wokwi chip host, and drives them exactly the way the firmware's libraries do:
//   Adafruit_SHT31: probe, soft reset 0x30A2, status 0xF32D (3 bytes), measure 0x2400 (6 bytes + CRC)
//   Adafruit_INA219: write CAL (0x05) and CONFIG (0x00), read POWER (0x03)
//   firmware PWM on IO25 (inverted by Q1) and tach counting on IO34 (2 pulses per revolution).
// Needs clang with the wasm32-wasi sysroot (Debian/Ubuntu: wasi-libc, libclang-rt-18-dev-wasm32).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const dir = new URL('../firmware/wokwi-full/', import.meta.url).pathname;
function build(name) {
  const out = join(tmpdir(), `${name}.chip.wasm`);
  execFileSync('clang', ['--target=wasm32-unknown-wasi', '-nostartfiles', '-Wl,--import-memory', '-Wl,--export-table', '-Wl,--no-entry',
    '-Werror', '-Wall', '-Wno-unused-function', '-O2', '-I', join(dir, 'vendor'), '-o', out, join(dir, `${name}.chip.c`)], { stdio: 'pipe' });
  return readFileSync(out);
}
let canBuild = true;
try { build('sht30'); } catch (e) { canBuild = false; console.log('# skipping: wasm32-wasi toolchain not available:', String(e.stderr || e).slice(0, 200)); }

/** Minimal Wokwi chip host: pins, attributes, timers, I2C device registration, printf. */
async function host(wasm, attrs = {}) {
  const memory = new WebAssembly.Memory({ initial: 32, maximum: 32768 });
  const h = { pins: [], attrs: [], timers: [], i2c: null, now: 0, log: [], pinInput: {} };
  const u32 = () => new Uint32Array(memory.buffer), f32 = () => new Float32Array(memory.buffer);
  const cstr = (p) => { const b = new Uint8Array(memory.buffer); let s = ''; while (b[p]) s += String.fromCharCode(b[p++]); return s; };
  let table;
  const call = (idx, ...a) => table.get(idx)(...a);
  const env = {
    pinInit: (name, mode) => { h.pins.push({ name: cstr(name), mode, value: mode === 17 ? 1 : 0, edges: 0 }); return h.pins.length - 1; },
    pinRead: (pin) => { const p = h.pins[pin]; const f = h.pinInput[p.name]; return f ? f(h.now) : p.value; },
    pinWrite: (pin, v) => { const p = h.pins[pin]; if (p.value !== v) p.edges++; p.value = v; },
    pinWatch: () => 1, pinWatchStop: () => {}, pinMode: (pin, m) => { h.pins[pin].mode = m; },
    pinADCRead: () => 0, pinDACWrite: () => 0,
    attrInit: (name, dflt) => { const n = cstr(name); h.attrs.push({ name: n, value: n in attrs ? attrs[n] : dflt }); return h.attrs.length - 1; },
    attrRead: (id) => Math.trunc(h.attrs[id].value) >>> 0, attrReadFloat: (id) => h.attrs[id].value,
    i2cInit: (cfg) => { const w = u32(), i = cfg >> 2; h.i2c = { user: w[i], address: w[i + 1], connect: w[i + 4], read: w[i + 5], write: w[i + 6], disconnect: w[i + 7] }; return 1; },
    uartInit: () => 0, uartWrite: () => 0, spiInit: () => 0, spiStart: () => {}, spiStop: () => {},
    timerInit: (cfg) => { const w = u32(), i = cfg >> 2; h.timers.push({ user: w[i], cb: w[i + 1], next: Infinity, period: 0, repeat: false }); return h.timers.length - 1; },
    timerStart: (t, us, repeat) => { Object.assign(h.timers[t], { next: h.now + us * 1000, period: us * 1000, repeat: !!repeat }); },
    timerStartNanos: (t, ns, repeat) => { Object.assign(h.timers[t], { next: h.now + ns, period: ns, repeat: !!repeat }); },
    timerStop: (t) => { h.timers[t].next = Infinity; },
    getSimNanos: () => h.now,
    framebufferInit: () => 0, bufferRead: () => {}, bufferWrite: () => {},
    memory,
  };
  const wasi = {
    fd_write: (fd, iovs, n, nwritten) => { const w = u32(); let s = '', tot = 0; for (let k = 0; k < n; k++) { const p = w[(iovs >> 2) + 2 * k], l = w[(iovs >> 2) + 2 * k + 1]; s += Buffer.from(memory.buffer, p, l).toString(); tot += l; } h.log.push(s); w[nwritten >> 2] = tot; return 0; },
    fd_close: () => 0, fd_seek: () => 0, fd_fdstat_get: () => 0, proc_exit: () => {}, environ_get: () => 0, environ_sizes_get: (a, b) => { u32()[a >> 2] = 0; u32()[b >> 2] = 0; return 0; },
  };
  const { instance } = await WebAssembly.instantiate(wasm, { env, wasi_snapshot_preview1: new Proxy(wasi, { get: (o, k) => o[k] || (() => 0) }) });
  table = instance.exports.__indirect_function_table;
  instance.exports.chipInit();
  h.setAttr = (name, v) => { h.attrs.find((a) => a.name === name).value = v; };
  h.run = (ns) => { const end = h.now + ns; for (;;) { let t = null; for (const x of h.timers) if (x.next <= end && (!t || x.next < t.next)) t = x; if (!t) break; h.now = t.next; t.next = t.repeat ? t.next + t.period : Infinity; call(t.cb, t.user); } h.now = end; };
  // I2C master helpers (one transaction each, like Wire)
  h.write = (bytes) => { if (!call(h.i2c.connect, h.i2c.user, h.i2c.address, 0)) return false; for (const b of bytes) call(h.i2c.write, h.i2c.user, b); if (h.i2c.disconnect) call(h.i2c.disconnect, h.i2c.user); return true; };
  h.read = (n) => { if (!call(h.i2c.connect, h.i2c.user, h.i2c.address, 1)) return null; const r = []; for (let k = 0; k < n; k++) r.push(call(h.i2c.read, h.i2c.user) & 0xFF); if (h.i2c.disconnect) call(h.i2c.disconnect, h.i2c.user); return r; };
  return h;
}
const crc8 = (d) => { let c = 0xFF; for (const x of d) { c ^= x; for (let b = 0; b < 8; b++) c = c & 0x80 ? ((c << 1) ^ 0x31) & 0xFF : (c << 1) & 0xFF; } return c; };

test('SHT30 chip speaks the Adafruit SHT31 protocol with valid CRCs', { skip: !canBuild }, async () => {
  for (const [addr, t, rh] of [[0x44, 33.4, 49], [0x45, 35.8, 44], [0x44, 40.0, 30]]) {
    const h = await host(build('sht30'), { address: addr, temperature: t, humidity: rh });
    assert.equal(h.i2c.address, addr);
    assert.ok(h.write([]), 'probe ACK');                                  // Adafruit_I2CDevice::begin()
    assert.ok(h.write([0x30, 0xA2]));                                    // soft reset
    assert.ok(h.write([0xF3, 0x2D])); const st = h.read(3);              // status
    assert.notEqual((st[0] << 8) | st[1], 0xFFFF); assert.equal(st[2], crc8(st.slice(0, 2)));
    assert.ok(h.write([0x24, 0x00])); h.run(20e6); const m = h.read(6);  // measure, high repeatability
    assert.equal(m[2], crc8(m.slice(0, 2))); assert.equal(m[5], crc8(m.slice(3, 5)));
    const T = -45 + 175 * ((m[0] << 8) | m[1]) / 65535, H = 100 * ((m[3] << 8) | m[4]) / 65535;
    assert.ok(Math.abs(T - t) < 0.01, `T ${T} vs ${t}`); assert.ok(Math.abs(H - rh) < 0.01, `RH ${H} vs ${rh}`);
    h.setAttr('connected', 0); assert.equal(h.write([]), false, 'unplugged → NACK');
  }
});

test('fan chip: inverted PWM, tach at 2 pulses/rev, stall, cut tach and INA219 power', { skip: !canBuild }, async () => {
  const h = await host(build('saaya-fan'));
  const pwmPeriod = 40000;                                               // 25 kHz in ns
  const gpio = (highFrac) => { h.pinInput.PWM = (now) => ((now % pwmPeriod) < highFrac * pwmPeriod ? 1 : 0); };
  const tach = h.pins.find((p) => p.name === 'TACH');
  const rpmOver = (s) => { const e0 = tach.edges; h.run(s * 1e9); return (tach.edges - e0) / 2 / 2 / s * 60; };   // 2 edges/pulse, 2 pulses/rev
  // INA219 set-up as Adafruit setCalibration_32V_2A(): CAL = 4096, CONFIG = 0x399F
  assert.ok(h.write([0x05, 0x10, 0x00])); assert.ok(h.write([0x00, 0x39, 0x9F]));
  const watts = () => { h.write([0x03]); const r = h.read(2); return ((r[0] << 8) | r[1]) * 2 / 1000; };
  gpio(255 / 256); h.run(2e9); assert.equal(Math.round(rpmOver(1)), 0, 'boot: GPIO high → fan input 0 % → stopped');
  gpio(128 / 256); h.run(8e9); const r50 = rpmOver(2);                   // firmware duty 50 → ledcWrite(128)
  assert.ok(r50 > 1500 && r50 < 1800, `50 % → ${r50} rpm`);
  const w = watts(); assert.ok(w > 1.2 && w < 1.8, `INA219 power ${w} W`);
  gpio(77 / 256); h.run(8e9); const r70 = rpmOver(2);                    // duty 70 → ledcWrite(77)
  assert.ok(r70 > 2000 && r70 < 2400, `70 % → ${r70} rpm`);
  h.setAttr('blocked', 1); h.run(0.5e9); assert.equal(Math.round(rpmOver(1)), 0, 'stalled rotor: no tach pulses');
  h.setAttr('blocked', 0); h.run(6e9); assert.ok(rpmOver(1) > 1800, 'recovers');
  h.setAttr('tachCut', 1); h.run(0.1e9); assert.equal(Math.round(rpmOver(1)), 0, 'cut tach wire: no pulses');
  h.setAttr('inaConnected', 0); assert.equal(h.write([0x03]), false, 'INA219 unplugged → NACK');
});
