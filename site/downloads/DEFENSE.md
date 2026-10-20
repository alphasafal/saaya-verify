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

## 3. Radiant screening model (`api/thermal.py`, 17 test cases)

Steady-state thin-skin roof balance with a convection-only wind coefficient h = 2.8 + 3.0v (Watmuff 1977; radiation explicit), Swinbank clear sky (optimistic), ventilated-gap air at ambient (optimistic) or sealed-gap natural convection, roof underside viewing shaded and sunlit ground by view factor, and sphere mean radiant temperature at a seated head from exact rectangle solid angles. Person α 0.7 / ε 0.97 (VDI 3787 convention); black globe α = ε = 0.95 with the ASHRAE/ISO 7726 forced-convection relation (biased below ≈1 m/s, [Teitelbaum et al. 2022](https://link.springer.com/10.1038/s41598-022-10172-5)). Noon sun from latitude and date: on 15 May at Vellore it is 84° high and **north** of the zenith. Conditions: 38 °C air, 900 W/m², wind 1 m/s, sunlit ground +15 K, FS-01 roof 2.8 × 2.4 m at 2.37 m, head 1.1 m. Each design is reported at its less favourable seat (the rear bench).

| Option | Roof underside | Seated MRT | 150 mm black globe (pred.) |
|---|---|---|---|
| Open sun (no shelter) | — | 73.6 °C | 64.7 °C |
| Weathered GI / cement sheet (typical existing shed) | 67.0 °C | 57.8 °C | 51.2 °C |
| Single bare galvanised sheet | 79.5 °C | 56.7 °C | 50.5 °C |
| Single sheet, white both faces | 48.9 °C | 55.4 °C | 49.8 °C |
| Single sheet, white top / bare underside | 48.8 °C | 55.4 °C | 49.9 °C |
| SAAYA double roof (white top, ventilated gap, bare low-e lining) | 41.0 °C | 55.2 °C | 49.7 °C |
| Double roof, sealed (unventilated) gap | 44.3 °C | 55.3 °C | 49.8 °C |

Findings that changed the design:

1. Shade alone (open sun → typical shed) removes ≈15.9 K of seated MRT; SAAYA's roof removes a further ≈2.6 K (total 18.5 K). The roof fills only ≈15 % of the seated view.
2. The second skin cuts lining temperature ≈8–22 K (more as the top coat soils) but seated MRT by only 0.3–0.8 K → **second skin becomes an optional, removable experiment**.
3. Lining finish barely matters once the lining is cool; counting reflected hot ground, a painted lining is marginally better than bare low-e metal → **paint the lining** (also better against corrosion).
4. +0.3 m overhang each side: −1.4 K for +52 % roof area. Irrigated ground cover: ≈−4 K at no structural cost. Light paving: ≈+5 K (reflected sun).

Declared prediction bands (2⁵ corner cases of irradiance 800–1000 W/m², wind 0.5–2 m/s, diffuse fraction 0.15–0.3, sunlit ground +10–20 K, lining ε 0.25–0.5):

| Target | Roof underside | Black globe |
|---|---|---|
| SAAYA double roof | 39.6–44.5 °C | 46.3–54.6 °C |
| Weathered shed sheet | 59.3–73.8 °C | 47.5–56.3 °C |

The underside bands do not overlap, so a roof-lining probe discriminates the designs; the globe bands overlap, so the globe tests the model's absolute level. Reject the model if measurements under logged conditions fall outside the band on 2 or more of 3 clear days.

Field context: tree shade lowered afternoon MRT by up to 33.4 °C in Tempe, Arizona while air temperature varied ≤4.4 °C across sites ([Middel & Krayenhoff 2019](https://par.nsf.gov/servlets/purl/10099415)) — shade acts on radiation, not air temperature. Indian cool-roof pilots report 1–5 °C indoor reductions ([MHT Ahmedabad](https://www.mahilahousingtrust.org/wp-content/uploads/2022/09/MHT_Combating-Climate-Change‑induced-Heatstress-2.pdf), [NRDC](https://www.nrdc.org/experts/anjali-jaiswal/cool-roofs-community-led-initiatives-four-indian-cities)).

## 4. Fan-benefit screen

Evidence: Ravanelli et al., JAMA 2015 (fans help at 42 °C in young men only below ≈47 % RH); Gagnon et al., JAMA 2016 (no benefit, slight harm, adults ≈68 y at 42 °C); Morris et al., Annals Int Med 2019 (fan worse in very hot dry, better in hot humid); Morris et al., Lancet Planet Health 2021 (ceilings 39 °C young, 38 °C >65 y, 37 °C >65 y on anticholinergics; fans alone not routinely advised in northern India); WHO fact sheet (fans only below 40 °C).

Implementation (identical in `controller.h`, `api/core.py`, `site/cooling-logic.js`; tested in all three): advice `ok` < 37 °C ≤ `caution` < 39 °C ≤ `avoid`. Automatic mode stops at ≥39 °C, restarts < 38.5 °C; normal on/off band 32/31 °C. Manual is never blocked; the OLED warns. A conservative screen on air temperature only; humidity-dependent limits await extraction of the full Morris 2021 tables.

## 5. Architecture decisions

| Topic | Chosen | Rejected | Why |
|---|---|---|---|
| Strategy | Passive shade + cool roof, small fan add-on | AC, evaporative, misting, bare fan | No enclosure; humidity; water/hygiene; model shows shade dominates |
| Roof | White top, ventilated gap, cool painted lining; 2nd skin removable | Single painted sheet, sandwich panel, green roof, slab | A cool lining is what the seated person feels; finish barely matters once cool |
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

Predeclared endpoint, beneficial direction and margin (1.0 °C roof — set above the possible disagreement of two ±0.5 °C probes before offset correction; 0.2 m/s air speed) locked at declaration; simultaneous paired reference; explicit invalidation reasons. A single run reports only a point estimate (`POINT_ESTIMATE_IN_DECLARED_DIRECTION` / `…_AGAINST_…` / `…_WITHIN_MARGIN`) or `INVALID`, with lag-1 autocorrelation and effective n. Claims (`DIFFERENCE_IN_DECLARED_DIRECTION`, `DIFFERENCE_AGAINST_DECLARED_DIRECTION`, `EQUIVALENT_WITHIN_MARGIN`, `INCONCLUSIVE`) come only from `aggregate()`: ≥3 valid runs on ≥3 distinct days, two-sided 95 % Student-t CI of run means (stricter than TOST's 90 %), equivalence-style decision (`POST /evidence/aggregate`, `scripts/evaluate_physical.py --aggregate`). Invalid runs are reported (`runs_invalid`, `valid_fraction`), not dropped.

## 7. Cost

- Bench today: ₹10,408.64 (mixed quotes/allowances). Budget profile in `research/costs.json`: ≈₹4,661 by replacing two Adafruit SHT31 carriers (₹3,066) with GY-SHT30 modules (₹179 each, Probots) and the Noctua (₹3,130) with a generic 4-wire PWM+tach fan (≈₹300 allowance; Waveshare US$2.69, no verified Indian listing), DS18B20 at ₹49. Not cut: tach feedback, the paired sensor, calibration.
- Full-size FS-01 first article: ₹94,134–1,70,771 unquoted allowance (the earlier ₹30,500–52,500 is superseded). AC equipment reference ₹36,990 (not installed). Levers: optional second skin (≈half of the ₹9,000–16,000 roof-materials line; 0.3–0.8 K at the seat), painted lining, ground treatment before more overhang, retrofit existing shade first (avoids the largest lines: steel and foundations), bolted repeated sections.
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
10. Adversarial review of the first model version found eight errors, all fixed with tests: globe predicted with a person's absorptance (2.5–6.6 K low); lining assumed to see only shaded ground (flattered low-e lining); McAdams combined coefficient double-counted radiation; May sun placed south of zenith; headline double-counted shade and roof; no falsification tolerance; single runs labelled "difference"; same-afternoon runs could count as independent days.

Each has a regression test (`tests/test_hardening_v3.py`, `tests/test_thermal.py`, `tests/controller_test.cpp`, `tests/cooling.test.mjs`, `tests/defense-browser.cjs`).

## 9. Not verified / open

ILO India figures only via secondary source; Lancet India per-person hours conflict in press; Morris 2021 humidity tables not extracted; ISO 7243/7726 texts not opened (formulas via NCAR and Teitelbaum 2022); BEE label pages not opened; no Indian listing for a 4-wire PWM+tach 40 mm fan; Vellore IMD primary page; no measured shade-vs-sun globe data in India; and, above all, no physical measurement of SAAYA.
