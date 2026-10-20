// The simulator must run the firmware's own rules. This test (1) repeats the native controller
// assertions against site/sim/controller.wasm and (2) compares 5000 random cases with the same
// header compiled natively by the system C++ compiler.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const wasm = (await WebAssembly.instantiate(readFileSync(new URL('../site/sim/controller.wasm', import.meta.url)))).instance.exports;
const step = (p, i) => { wasm.step(+p.help, +p.fault, p.duty, p.started >>> 0, +i.help, +i.ack, +i.manual, +i.automatic, +i.sensorFault, i.now >>> 0, i.rpm);
  return { help: !!wasm.outHelp(), fault: !!wasm.outFault(), duty: wasm.outDuty(), started: wasm.outStarted() >>> 0 }; };
const S0 = { help: false, fault: false, duty: 0, started: 0 };
const I = (o) => ({ help: false, ack: false, manual: false, automatic: false, sensorFault: false, now: 0, rpm: 0, ...o });

test('wasm reproduces the firmware controller assertions', () => {
  let s = step(S0, I({ help: true, manual: true, sensorFault: true }));
  assert.ok(s.help && s.duty === 70 && !s.fault);
  s = step(s, I({ manual: true, sensorFault: true, now: 3100 })); assert.ok(s.help && s.fault);
  s = step(s, I({ ack: true, manual: true, sensorFault: true, now: 3100, rpm: 3000 })); assert.ok(!s.help && !s.fault);
  s = step(s, I({ ack: true, automatic: true, sensorFault: true, now: 3100, rpm: 3000 })); assert.equal(s.duty, 0);
  s = step(s, I({ ack: true, automatic: true, now: 3100, rpm: 3000 })); assert.equal(s.duty, 50);
  assert.ok(step({ ...s, started: 0xfffffff0, duty: 70 }, I({ manual: true, now: 4000 })).fault, 'millis rollover');
  assert.ok(!wasm.autoRequest(0, 31.9) && wasm.autoRequest(0, 32.0));
  assert.ok(wasm.autoRequest(1, 31.2) && !wasm.autoRequest(1, 30.9));
  assert.ok(!wasm.autoRequest(1, NaN));
  assert.ok(wasm.autoRequest(1, 38.9) && !wasm.autoRequest(1, 39.0) && !wasm.autoRequest(0, 38.7) && wasm.autoRequest(0, 38.4));
  assert.deepEqual([36.9, 37, 39, NaN].map((t) => wasm.fanAdvice(t)), [0, 1, 2, 3]);
  assert.deepEqual([0, 1, 2, 3, 4].map((k) => Math.fround(wasm.constants(k))), [32, 31, 37, 39, 38.5].map(Math.fround));
});

test('wasm matches natively compiled controller.h on 5000 random cases', () => {
  const bin = join(tmpdir(), 'saaya-controller-diff');
  execFileSync('c++', ['-std=c++11', '-O1', new URL('./controller_diff.cpp', import.meta.url).pathname, '-o', bin]);
  let seed = 12345; const rnd = () => ((seed = (seed * 1103515245 + 12345) >>> 0) / 4294967296);
  const cases = Array.from({ length: 5000 }, () => {
    const t = Math.fround(25 + rnd() * 20); const ph = rnd() < .5 | 0;
    return [ph, rnd() < .3 | 0, [0, 50, 70][Math.floor(rnd() * 3)], Math.floor(rnd() * 4294967295), rnd() < .2 | 0, rnd() < .2 | 0, rnd() < .4 | 0, rnd() < .5 | 0, rnd() < .2 | 0,
      Math.floor(rnd() * 4294967295), Math.round(rnd() * 3000), rnd() < .5 | 0, rnd() < .05 ? NaN : t];
  });
  const input = cases.map((c) => c.map((v) => (Number.isNaN(v) ? 'nan' : String(v))).join(' ')).join('\n') + '\n';
  const native = execFileSync(bin, { input }).toString().trim().split('\n');
  cases.forEach((c, k) => {
    const s = step({ help: !!c[0], fault: !!c[1], duty: c[2], started: c[3] }, { help: !!c[4], ack: !!c[5], manual: !!c[6], automatic: !!c[7], sensorFault: !!c[8], now: c[9], rpm: c[10] });
    const got = `${+s.help} ${+s.fault} ${s.duty} ${s.started} ${wasm.autoRequest(c[11], c[12])} ${wasm.fanAdvice(c[12])}`;
    assert.equal(got, native[k], `case ${k}: ${c.join(' ')}`);
  });
});

test('committed controller.wasm is up to date with controller.h', (t) => {
  const out = join(tmpdir(), 'saaya-controller-check.wasm');
  try {
    execFileSync('clang', ['--target=wasm32', '-O2', '-ffreestanding', '-fno-exceptions', '-fno-rtti', '-nostdlib', '-std=c++11', '-I', new URL('../firmware/sim/shim', import.meta.url).pathname,
      '-Wl,--no-entry', '-Wl,--strip-all', '-o', out, new URL('../firmware/sim/controller_wasm.cpp', import.meta.url).pathname], { stdio: 'pipe' });
  } catch (e) { t.skip('clang/wasm-ld not available'); return; }
  assert.ok(readFileSync(out).equals(readFileSync(new URL('../site/sim/controller.wasm', import.meta.url))), 'run scripts/build_sim_wasm.sh and commit site/sim/controller.wasm');
});
