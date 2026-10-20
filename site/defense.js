// Renders the design-defense numbers straight from the tested Python sources
// (site/data/thermal-model.json, aggregate-demo.json, costs.json). No numbers are typed here.
const $ = s => document.querySelector(s);
const f1 = x => (x == null ? '—' : Number(x).toFixed(1));
const el = (tag, attrs = {}, text) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
};
const NS = 'http://www.w3.org/2000/svg';
const svg = (tag, attrs = {}, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
};

function table(target, headers, rows) {
  const t = el('table');
  const head = el('tr');
  headers.forEach(h => head.append(el('th', { scope: 'col' }, h)));
  const thead = el('thead');
  thead.append(head);
  t.append(thead);
  const body = el('tbody');
  rows.forEach(r => {
    const tr = el('tr');
    r.forEach((c, i) => tr.append(el(i ? 'td' : 'th', i ? {} : { scope: 'row' }, c)));
    body.append(tr);
  });
  t.append(body);
  target.replaceChildren(t);
}

function bars(target, items, { unit = '°C', min = null, label } = {}) {
  const w = 720, rowH = 34, left = 300, right = 70, h = items.length * rowH + 30;
  const vals = items.map(i => i.value);
  const lo = min ?? Math.floor(Math.min(...vals) / 5) * 5 - 5, hi = Math.ceil(Math.max(...vals) / 5) * 5;
  const x = v => left + (v - lo) / (hi - lo) * (w - left - right);
  const s = svg('svg', { viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': label });
  for (let g = lo; g <= hi; g += 5) {
    s.append(svg('line', { x1: x(g), x2: x(g), y1: 4, y2: h - 22, class: 'grid' }));
    s.append(svg('text', { x: x(g), y: h - 6, 'text-anchor': 'middle', class: 'tick' }, `${g}`));
  }
  items.forEach((it, i) => {
    const y = 8 + i * rowH;
    s.append(svg('text', { x: left - 10, y: y + 17, 'text-anchor': 'end', class: 'bar-label' }, it.name));
    s.append(svg('rect', { x: left, y: y + 3, width: Math.max(2, x(it.value) - left), height: 20, rx: 3, class: it.cls || 'bar' }));
    s.append(svg('text', { x: x(it.value) + 6, y: y + 18, class: 'bar-value' }, `${f1(it.value)} ${unit}`));
  });
  target.replaceChildren(s);
}

async function load(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

async function thermal() {
  const m = await load('data/thermal-model.json');
  const c = m.conditions;
  $('#model-conditions').textContent =
    `Assumed driving conditions: air ${c.ta_c} °C, ${c.ghi} W/m², noon sun ${f1(c.sun_elevation_deg)}° high to the ${c.sun_is_north ? 'north' : 'south'} (day ${c.day_of_year}), wind ${c.wind} m/s, ` +
    `sunlit ground ${c.sunlit_ground_rise} K above air. Seated head ${m.person.head_height} m; local air speed ${m.person.air_speed} m/s.`;
  const d = Object.fromEntries(m.designs.map(x => [x.design, x]));
  const saaya = m.designs.find(x => x.design.startsWith('SAAYA'));
  bars($('#mrt-chart'), m.designs.map(x => ({ name: x.design.replace(/\s*\(.*\)$/, ''), value: x.tmrt_c,
    cls: x.design.startsWith('SAAYA') ? 'bar saaya' : x.design.startsWith('Open') ? 'bar sun' : 'bar' })),
    { label: 'Predicted mean radiant temperature at the seated head for each roof option' });
  table($('#design-table'), ['Option', 'Roof underside', 'Upper skin', 'Seated MRT (harder seat)', 'Black globe 150 mm (predicted)', 'Sun on head?'],
    m.designs.map(x => [x.design, x.underside_c == null ? 'no roof' : `${f1(x.underside_c)} °C`, x.upper_c == null ? '—' : `${f1(x.upper_c)} °C`,
      `${f1(x.tmrt_c)} °C`, `${f1(x.globe_150mm_c)} °C`, x.sun_on_head ? 'yes' : 'no']));
  const hl = m.headline;
  $('#k-shade').textContent = `${f1(hl.shade_alone_k)} K`;
  $('#k-roof').textContent = `${f1(hl.roof_treatment_k)} K`;
  $('#k-underside').textContent = `${f1(hl.underside_cooler_k)} K`;
  const vf = saaya.view_fractions;
  $('#k-view').textContent = `${Math.round(vf.roof * 100)} %`;
  $('#view-note').textContent = `What the seated head "sees" (share of the full sphere): roof ${Math.round(vf.roof * 100)} %, sky ${Math.round(vf.sky * 100)} %, ` +
    `shaded ground ${Math.round(vf.shaded_ground * 100)} %, sunlit ground ${Math.round(vf.sunlit_ground * 100)} %.`;
  const ss = m.second_skin;
  table($('#skin-table'), ['Top coat condition', 'Underside: single sheet', 'Underside: double roof', 'Seated MRT saved by 2nd skin'],
    ss.map(r => [r.top_coat, `${f1(r.single_underside_c)} °C`, `${f1(r.double_underside_c)} °C`, `${r.tmrt_saved_by_second_skin_k.toFixed(2)} K`]));
  table($('#overhang-table'), ['Extra overhang each side', 'Roof area', 'Seated MRT', 'Roof share of view'],
    m.overhang.map(r => [`${r.extra_overhang_m.toFixed(1)} m`, `${r.roof_area_m2.toFixed(1)} m²`, `${f1(r.tmrt_c)} °C`, `${Math.round(r.roof_view_fraction * 100)} %`]));
  table($('#ground-table'), ['Surroundings (sunlit part)', 'Surface above air', 'Albedo', 'Seated MRT'],
    m.ground.map(r => [r.surround, `+${r.sunlit_ground_rise_k} K`, r.albedo.toFixed(2), `${f1(r.tmrt_c)} °C`]));
  table($('#sensitivity-table'), ['Parameter varied', 'Value', 'MRT under existing shed', 'MRT under SAAYA', 'Benefit'],
    m.sensitivity.map(r => [r.parameter, String(r.value), `${f1(r.tmrt_existing_shed_c)} °C`, `${f1(r.tmrt_saaya_c)} °C`, `${f1(r.benefit_k)} K`]));
  table($('#band-table'), ['Prediction target', 'Roof underside band', 'Black globe band'],
    m.prediction_bands.map(b => [b.target, `${f1(b.underside_c[0])}–${f1(b.underside_c[1])} °C`, `${f1(b.globe_150mm_c[0])}–${f1(b.globe_150mm_c[1])} °C`]));
  const ul = $('#falsify');
  ul.replaceChildren(...m.falsification.map(t => el('li', {}, t)));
}

async function evidence() {
  const a = await load('data/aggregate-demo.json');
  const r = a.results.roof_temp;
  const w = 720, h = 170, lo = Math.min(...r.run_deltas, r.ci95[0]) - 1, hi = 1.5;
  const x = v => 40 + (v - lo) / (hi - lo) * (w - 80);
  const s = svg('svg', { viewBox: `0 0 ${w} ${h}`, role: 'img', 'aria-label': 'Five synthetic run differences, their mean and 95 percent confidence interval against the predeclared margin' });
  const m = r.declaration.margin;
  s.append(svg('rect', { x: x(-m), y: 18, width: x(m) - x(-m), height: 110, class: 'margin-band' }));
  s.append(svg('text', { x: (x(-m) + x(m)) / 2, y: 14, 'text-anchor': 'middle', class: 'tick' }, `± ${m} °C "no meaningful difference" band`));
  s.append(svg('line', { x1: x(0), x2: x(0), y1: 18, y2: 128, class: 'zero' }));
  r.run_deltas.forEach((d, i) => s.append(svg('circle', { cx: x(d), cy: 40 + i * 12, r: 5, class: 'run' })));
  s.append(svg('line', { x1: x(r.ci95[0]), x2: x(r.ci95[1]), y1: 112, y2: 112, class: 'ci' }));
  s.append(svg('circle', { cx: x(r.mean), cy: 112, r: 6, class: 'mean' }));
  s.append(svg('text', { x: x(r.mean), y: 150, 'text-anchor': 'middle', class: 'bar-value' }, `mean ${r.mean.toFixed(2)} °C, 95 % CI ${r.ci95[0].toFixed(2)} to ${r.ci95[1].toFixed(2)}`));
  for (let g = Math.ceil(lo); g <= hi; g++) s.append(svg('text', { x: x(g), y: h - 2, 'text-anchor': 'middle', class: 'tick' }, `${g}`));
  $('#aggregate-chart').replaceChildren(s);
  const o = r.outcome.replaceAll('_', ' ').toLowerCase();
  $('#aggregate-outcome').textContent = `Outcome: ${o}. ${r.runs_valid} ${a.source.toLowerCase()} runs (seeds ${a.seeds.join(', ')}). ${r.warning}.`;
}

async function cost() {
  const c = await load('data/costs.json');
  const tab = c.tabletop.reduce((s, x) => s + x.quantity * x.unit_price, 0);
  const lo = c.full_size.reduce((s, x) => s + x.estimate_low, 0), hi = c.full_size.reduce((s, x) => s + x.estimate_high, 0);
  const inr = v => '₹' + Math.round(v).toLocaleString('en-IN');
  $('#cost-tabletop').textContent = inr(tab);
  $('#cost-fullsize').textContent = `${inr(lo)}–${inr(hi)}`;
  $('#cost-ac').textContent = inr(c.ac.price);
  table($('#fullsize-cost-table'), ['Full-size line (allowance, not a quote)', 'Low', 'High'],
    c.full_size.map(x => [x.item, inr(x.estimate_low), inr(x.estimate_high)]));
}

for (const [fn, id] of [[thermal, '#model-conditions'], [evidence, '#aggregate-outcome'], [cost, '#cost-tabletop']]) {
  fn().catch(e => { const t = $(id); if (t) t.textContent = `Could not load data: ${e.message}`; });
}
