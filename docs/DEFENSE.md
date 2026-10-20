# SAAYA VERIFY — design defense (v0.3, 20 October 2026)

Interactive version with live charts: [`site/defense.html`](../site/defense.html) (deployed at `/defense.html`). This file is the citable text. Nothing here has been built or measured; every number is a cited source, a costed allowance or a model prediction written so that a measurement can refute it.

## 1. Problem

- ILO (2019) projects heat stress will cost India about 5.8 % of working hours by 2030, ≈34 million full-time jobs (as reported by [Down To Earth](https://www.downtoearth.org.in/news/india/heat-stress-singes-india-most-ilo-pegs-cost-at-34-mn-jobs-in-2030-65380); verify against ILO Table 6.2 before quoting). Southern Asia: 5.3 % of hours, ≈43 million jobs ([ILO PDF](https://www.ilo.org/sites/default/files/wcmsp5/groups/public/@dgreports/@dcomm/@publ/documents/publication/wcms_711919.pdf)).
- Lancet Countdown 2025: ≈247 billion potential labour hours lost in India in 2024 (press reports of the [Lancet report](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)01919-1/abstract)).
- Vellore: May mean daily maximum ≈39 °C, record 45 °C, afternoon RH 43–51 % in hot months (IMD normals relayed by [Wikipedia](https://en.wikipedia.org/wiki/Vellore); IMD primary page still to obtain).
- NDMA draft *Guidelines for Cooling Centers* (May 2025) call for temporary shaded structures for outdoor workers, high-reflectance roofs, no bare GI roofing, shaded/green unpaved ground, cross-ventilation ([PDF](https://heathealth.info/wp-content/uploads/NDMA-Cooling-centre-guidelines.pdf)). SAAYA is a testable, low-cost version of that structure plus an evidence layer.

## 2. How it differs from conventional cooling

| | Room AC (1.5 t) | Evaporative cooler / mister | Pedestal fan in open | SAAYA |
|---|---|---|---|---|
| Works open-sided | No | Partly | Yes | Yes |
| Attacks | Air temp + humidity | Air temp by adding moisture | Sweat evaporation | Radiant load first, then air movement |
| Power | ≈1.4–1.6 kW | Fan + pump | 35 W BLDC to 55–125 W | Bench fan 0.32 W typ. |
| Water | — | Continuous, hygiene | — | None for cooling |
| Failure | Silent | Silent | Silent | Detects stalled fan, dead sensor, stale data; help latch survives reboot |
| Knows if it worked | No | No | No | Only after predeclared, paired, replicated comparison |

Power sources: Blue Star 5-star 1395 W, Voltas 3-star 1615 W (aggregator spec pages); Atomberg Efficio 35 W; Usha 55 W, Crompton Torpedo 125 W (retail specs); Noctua NF-A4x10 PWM 0.32 W typ / 0.48 W max. An open shelter is not equivalent to AC.

## 3. Radiant screening model (`api/thermal.py`, 11 tests)

Steady-state thin-skin roof balance (Swinbank clear sky, McAdams h = 5.7 + 3.8v, grey-body gap exchange, sealed-gap natural convection) and sphere mean radiant temperature at a seated head from exact rectangle solid angles; ISO 7730 operative weighting; ISO 7726 globe inversion. Conditions: 38 °C air, 900 W/m², sun 78°, wind 1 m/s, sunlit ground +15 K, FS-01 roof 2.8 × 2.4 m at 2.37 m, head 1.1 m.

| Option | Roof underside | Seated MRT | 150 mm globe (pred.) |
|---|---|---|---|
| Open sun (no shelter) | — | 73.9 °C | 58.3 °C |
| Weathered GI / cement sheet (typical existing shed) | 58.8 °C | 55.4 °C | 47.2 °C |
| Single bare galvanised sheet | 65.4 °C | 53.9 °C | 46.4 °C |
| Single sheet, white both faces | 44.3 °C | 53.5 °C | 46.2 °C |
| Single sheet, white top / bare underside | 45.1 °C | 53.2 °C | 46.0 °C |
| SAAYA double roof (white top, ventilated gap, bare low-e lining) | 38.6 °C | 53.0 °C | 45.9 °C |
| Double roof, sealed gap | 40.4 °C | 53.0 °C | 45.9 °C |

Findings that changed the design:

1. Shade itself removes ≈21 K of radiant load; roof treatment adds ≈2.4 K versus a weathered shed; the roof fills only ≈15 % of the seated view.
2. The second skin cuts underside temperature 6–18 K (more as the top coat soils) but seated MRT by only 0.2–0.6 K → **second skin becomes an optional, removable experiment**.
3. +0.3 m overhang each side: −1.4 K for +52 % roof area. Planted/shaded ground: −2.7 K at no structural cost. Light paving *raises* MRT (reflected sun).
4. Falsification: roof-underside DS18B20 and a 150 mm globe at seat height across ≥3 clear days; reject the model if outside the declared margin. Note the globe relation has known error below ≈1 m/s air speed ([Teitelbaum et al. 2022](https://link.springer.com/10.1038/s41598-022-10172-5)); record air speed alongside.

Field context: tree shade lowered afternoon MRT by up to 33.4 °C in Tempe, Arizona while air temperature varied ≤4.4 °C across sites ([Middel & Krayenhoff 2019](https://par.nsf.gov/servlets/purl/10099415)) — shade acts on radiation, not air temperature. Indian cool-roof pilots report 1–5 °C indoor reductions ([MHT Ahmedabad](https://www.mahilahousingtrust.org/wp-content/uploads/2022/09/MHT_Combating-Climate-Change‑induced-Heatstress-2.pdf), [NRDC](https://www.nrdc.org/experts/anjali-jaiswal/cool-roofs-community-led-initiatives-four-indian-cities)).

## 4. Fan-benefit screen

Evidence: Ravanelli et al., JAMA 2015 (fans help at 42 °C in young men only below ≈47 % RH); Gagnon et al., JAMA 2016 (no benefit, slight harm, adults ≈68 y at 42 °C); Morris et al., Annals Int Med 2019 (fan worse in very hot dry, better in hot humid); Morris et al., Lancet Planet Health 2021 (ceilings 39 °C young, 38 °C >65 y, 37 °C >65 y on anticholinergics; fans alone not routinely advised in northern India); WHO fact sheet (fans only below 40 °C).

Implementation (identical in `controller.h`, `api/core.py`, `site/cooling-logic.js`; tested in all three): advice `ok` < 37 °C ≤ `caution` < 39 °C ≤ `avoid`. Automatic mode stops at ≥39 °C, restarts < 38.5 °C; normal on/off band 32/31 °C. Manual is never blocked; the OLED warns. A conservative screen on air temperature only; humidity-dependent limits await extraction of the full Morris 2021 tables.

## 5. Architecture decisions

| Topic | Chosen | Rejected | Why |
|---|---|---|---|
| Strategy | Passive shade + low-e roof, small fan add-on | AC, evaporative, misting, bare fan | No enclosure; humidity; water/hygiene; model shows shade dominates |
| Roof | White top, ventilated gap, bare low-e lining; 2nd skin removable | Single painted sheet, sandwich panel, green roof, slab | Underside temp × emissivity is what the seated person feels |
| Controller | ESP32-WROOM, local control | Uno, Raspberry Pi, PLC | Watchdog, LEDC PWM, NVS latch, instant boot, ₹425–499; network loss never stops control |
| Air sensors | 2 × SHT31 (0x44/0x45) | DHT22, BME280, thermistors | Digital, ±0.2 °C typ., identical pair swappable for bias |
| Feedback | Tach interrupt; DS18B20 roof probe | Open loop, current only, IR | Proves the fan turns; IR fails on low-e surfaces |
| Energy | INA219 on fan branch, gap-aware integration | Datasheet watts, smart plug | Missing ≠ zero |
| Fan drive | 4-wire PWM via NPN; fails to full speed | MOSFET-switched 2-wire; relay mains fan | Floating PWM → 100 % (Intel 4-wire convention); no mains in wet area |
| Help | Flash-latched, separate local acknowledge | Momentary, phone alert | Survives reboot, independent of thresholds |
| Data | USB → bridge → loopback FastAPI → SQLite WAL | MQTT, cloud IoT, Influx | Zero recurring cost, no internet dependency, no data leaves laptop |
| Analysis | Deterministic evaluator; optional local read-only AI | Cloud LLM in loop, ML | Auditable invalidation; AI never controls |
| Web | Buildless ES modules, static hosting | React/Next, server dashboard | No server to attack; public site cannot ingest/control |
| CAD | CadQuery/Manifold with CI interference checks | Proprietary-only CAD | Diffable, regenerated in CI, STEP/STL/DXF exports |

## 6. Evidence engine

Predeclared endpoint, beneficial direction and margin (1.0 °C roof; 0.2 m/s air speed) locked at declaration; simultaneous paired reference; explicit invalidation reasons; outcomes `DIFFERENCE_IN_DECLARED_DIRECTION` / `DIFFERENCE_AGAINST_DECLARED_DIRECTION` / `NO_CLEAR_DIFFERENCE` / `INVALID`; lag-1 autocorrelation and effective n reported per run; cross-run Student-t 95 % CI over ≥3 independent runs with an equivalence-style decision (`POST /evidence/aggregate`, `scripts/evaluate_physical.py --aggregate`). Invalid runs are counted, not dropped.

## 7. Cost

- Bench today: ₹10,408.64 (mixed quotes/allowances). Budget profile in `research/costs.json`: ≈₹4,661 by replacing two Adafruit SHT31 carriers (₹3,066) with GY-SHT30 modules (₹179 each, Probots) and the Noctua (₹3,130) with a generic 4-wire PWM+tach fan (≈₹300 allowance; Waveshare US$2.69, no verified Indian listing), DS18B20 at ₹49. Not cut: tach feedback, the paired sensor, calibration.
- Full-size FS-01 first article: ₹94,134–1,70,771 unquoted allowance (the earlier ₹30,500–52,500 is superseded). AC equipment reference ₹36,990 (not installed). Levers: optional second skin (≈half of the ₹9,000–16,000 roof-materials line), ground treatment before more overhang, retrofit existing shade first (avoids the largest lines: steel and foundations), bolted repeated sections.
- Running: AC ≈11–13 kWh per 8 h shift; 35 W BLDC fan ≈0.3 kWh; bench fan a few Wh. Maintenance allowance ₹1,500–3,500/yr.

## 8. Flaws found and fixed in the v0.3 review

1. SQLite connection leak on every request (27 ResourceWarnings in one test file) → closing context manager, WAL, indexes, schema migration.
2. No predeclared direction or "no clear difference" outcome → declarations + outcomes.
3. No way to establish uncertainty → cross-run aggregation.
4. Device endpoint accepted `SIMULATED` rows → `MEASURED` only.
5. Unbounded roof/outdoor/reference/air-speed/power/RPM fields → sensor-range bounds.
6. Auto fan without hysteresis → 32/31 °C band (C++, Python, JS).
7. Auto fan ran in conditions where fans may add heat → fan-benefit screen.
8. Contradictory full-size cost figures → corrected.
9. Design priorities asserted rather than derived → screening model and reprioritisation.

Each has a regression test (`tests/test_hardening_v3.py`, `tests/test_thermal.py`, `tests/controller_test.cpp`, `tests/cooling.test.mjs`, `tests/defense-browser.cjs`).

## 9. Not verified / open

ILO India figures only via secondary source; Lancet India per-person hours conflict in press; Morris 2021 humidity tables not extracted; ISO 7243/7726 texts not opened (formulas via NCAR and Teitelbaum 2022); BEE label pages not opened; no Indian listing for a 4-wire PWM+tach 40 mm fan; Vellore IMD primary page; no measured shade-vs-sun globe data in India; and, above all, no physical measurement of SAAYA.
