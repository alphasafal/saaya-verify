# SAAYA evidence and feasibility review

Checked 11 October 2026. Research and design assessment, not physical validation. This review is a bounded corpus: all eight dossier references were checked, supplemented by traditional-mechanism studies, official climate information, manufacturer documents and supplier listings. It is not an exhaustive literature search, systematic-review claim, patent opinion, or evidence that SAAYA is unprecedented.

## Evidence ledger and search method

[evidence.json](evidence.json) is the canonical source-by-source review. Every record gives access status, method, climate, scale, findings, limitation and resulting SAAYA decision. R1 and R6 PDFs were inspected for methods; R2 publication overview and R8 official guidance were inspected. R3/R4/R7 publisher metadata or abstracts were available but complete texts could not be retrieved. R5 indexing and abstract were verified, but repeated full-text access returned a browser challenge. These access limits mean the detailed review remains incomplete for those records; the dossier's assertions were not silently promoted to verified findings.

Queries included exact DOI strings for R1–R7, WHO document title, IMD Vellore station43303, windcatcher experimental passive cooling, jaali shading/ventilation, wetted-clay evaporative cooling, and named component model/dimensions/India price. Primary publishers, manufacturers, IMD and WHO were preferred. Supplier listings support purchase observations only; they do not certify engineering suitability.

The R1 simulation is useful for choosing experiments, not for predicting this prototype. The R6 manikin study cannot establish worker recovery or cooling from an open shelter. A suitable next review pass should obtain accessible full texts of R3/R4/R5/R7, extract primary studies most similar to an open-sided Vellore shelter, and check supplementary assumptions. No third-party PDFs are included in the public repository.

## Traditional architecture translated into experiments

| Mechanism | Tabletop implementation | Measurement and failure to look for |
|---|---|---|
| Deep shade/verandah | Roof overhang; seat fully inside projected shade | Photograph shade coverage through day. Low-angle sunlight may reach the seat. |
| Ventilated double roof | Removable reflective top panel and unobstructed gap | Compare top and underside surface temperatures and radiant proxy. Restriction/debris can defeat ventilation. |
| Jaali | Interchangeable perforated screen; always preserve open exits | Compare screen-on/off seated air speed and shade. A screen can improve shade while reducing flow. |
| Windcatcher/high outlet | Removable scoop/outlet experimental module | Test multiple wind directions and calm condition. Do not assume stack effect in a miniature model matches full scale. |
| Terracotta evaporation | Deferred removable module with independent non-potable tray | Measure mass loss, humidity, air speed and local conditions; cleaning/hygiene can outweigh benefit. |
| Thermal mass/night cooling | Deferred removable mass sample, not an uncosted heavy roof | Compare overnight reset and next-day temperature. Stored heat and weight can make it unsuitable. |

These are engineering hypotheses, not verified performance assertions. T1–T3 in the ledger provide traceable literature connections. Reflective roof and shade are baseline hypotheses supported in the dossier corpus; a dedicated quantitative ventilated-double-roof experiment paper was not fully reviewed in this pass. Do not advertise an optimum vent gap or historic form based on these sources.

## Vellore climate and data gap

[IMD1991–2020 tables](https://www.imdpune.gov.in/library/public/Climatological%20Tables%201991-2020.pdf) identify Vellore station43303 at station table398. Indexed wind rows were accessible; the complete PDF repeatedly timed out. Temperature, humidity and rainfall month-by-month values therefore remain unverified in this release. No secondary weather site's numerical series has been copied into controller thresholds.

Before full-size design freeze, obtain the complete table and an hourly weather file with explicit station, period and gaps. Add at least several days of co-located T/RH,wind and rainfall observations in each relevant season. A fixed wind-facing design is inappropriate without site wind/obstruction measurements. Rain protection, drainage and humidity testing remain mandatory project requirements even though seasonal sizing is pending. Demonstration scenarios are synthetic stress cases, not a Vellore forecast or measured typical day.

## Component geometry and substitution rules

- **ESP32:** [Espressif DevKitC V4 documentation](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) includes dimensions and source drawings. Overall outline is54.4×27.9mm;48.2mm is a partial dimension, not overall clearance. DOIT DevKit V1 and generic38-pin boards are different products. The costed Robocraze board is a generic candidate, not a verified exact mechanical match. Use an adjustable tray until the received PCB and connectors are measured; record board revision.
- **SHT31:** [Adafruit2857](https://www.adafruit.com/product/2857) lists12.7×18×2.6mm for its current carrier. Do not substitute the bare Sensirion IC dimension or assume another breakout matches its mounting pattern. Two sensors require different addresses0x44/0x45. Quote is sold out; procurement is unresolved.
- **Fan:** [Noctua NF-A4x10 PWM](https://noctua.at/en/nf-a4x10-pwm/buy) is12V,4-pin,40×40×10mm with32×32mm hole centres. Budget12mm thickness with pads and additional connector/bend clearance. Manufacturer maximum input0.48W is not total-system consumption or measured useful airflow. Do not confuse the5V,24V,FLX and PWM versions.
- **OLED:** A0.96inch diagonal does not specify carrier size or aperture. Supplier reference is in the BOM; exact PCB dimensions and hole centres must be checked before the front panel is released. [Example carrier drawing](https://www.electrokit.com/upload/quick/42/32/fb04_41035586-tds.pdf) is27.4×27.8mm with23.7mm hole-centre spans and1.9mm holes, but is NOT proof that the costed module has this geometry.
- **Power/probe:** INA219 breakout rating/shunt value and DS18B20 mechanical dimensions vary by vendor. Verify low-current accuracy and roof-contact installation against a reference instrument. A contact probe is not a globe thermometer. A float indicates level, not potability.

Production release requires receipt inspection, documented measured dimensions, component-specific drawings, trial assembly and electrical testing. This package does not establish production fit or environmental certification.

## Cost result

[costs.json](costs.json) separates supplier observations from planning allowances. The current mixed tabletop subtotal is **₹10,408.64**. It includes a documented premium tachometer/PWM fan and branded sensor carriers. Several parts need quotes and the sensor listing is sold out. Shipping, tools, calibrated air-speed/WBGT equipment and assembly labour are excluded. Thus it is not a purchasable guaranteed basket and the original₹2,150–4,200 miniature estimate is not supported for this configuration.

The conceptual full-size installed range is **₹30,500–52,500**, excluding PV/battery, land, unanticipated civil works and certification. Each line is an engineering planning allowance, not a supplier quote. Annual maintenance allowance is₹1,500–3,500, excluding energy,water and major damage. Site-specific structural design may change the range materially.

[Blue Star IA318TXU](https://consumer.bluestarindia.com/products/inverter-ac-t-series-1-5-ton-3-star-2026-bee-label-copy) lists₹36,990 for a1.5-ton3-star inverter unit. Standard installation and Vellore availability were not confirmed. Obtain a dated local installed quote with copper length,brackets,drain,electrical work and taxes before making the target comparison. The shelter range overlaps and exceeds the equipment listing; **below-installed-AC cost is unproven**. AC conditions an enclosed room; SAAYA shades and ventilates an outdoor rest space, so price does not imply equivalent cooling.

Cost reduction candidates: borrow validation instruments; use a locally available documented tach fan after re-testing; procure supported SHT31 breakouts with measured carriers; reuse modular frame stock. Removing actuator feedback or sensor calibration merely to hit a number would undermine CoolProof.

## Sustainability and novelty accounting

Use a repairable bolted frame, replaceable roof/screen panels and detachable electronics. Record actual material mass, supplier, recycled content evidence, service intervals and end-of-life separation; do not convert a material name into a sustainability claim. Count fan/controller energy at the input, including losses. Keep drinking water accounting separate from optional evaporative water. Establish a reference shelter and service life before carbon comparisons.

Prior art P1 rules out a broad solar-cooling-shelter novelty claim. The bounded contribution to test is an inspectable chain from intervention command to measured actuator response, resource use and uncertainty-aware evidence. A formal patent search and freedom-to-operate review are not completed. AI explanations must cite recorded evidence and this ledger; no model output is a new experimental measurement.

## Evidence needed for the next release

1. Receive exact parts; capture dimensions and calibrations; reprice the purchased configuration.
2. Compare sensor pairs side-by-side before deployment; swap positions to estimate bias.
3. Run simultaneous unoccupied reference/intervention tests, recording weather, geometry, exposure, source and exclusions. Repeat on several days.
4. Measure air speed at multiple defined points, roof contact temperature, a properly documented radiant proxy, and electricalWh. Borrow calibrated occupational instruments for any future exposure assessment.
5. Test fan failure, disconnection, reboot, communication loss, assistance persistence and stale data. Preserve invalid runs rather than delete adverse outcomes.
6. Obtain structural, electrical and hygiene review plus a local fabrication quote before human-scale installation.

## Additional local climate check

The IMD city table provides a1981–2010 baseline: May mean daily maximum39.1°C; September mean rainfall195.2mm; October158.1mm. These are historical normals, not October2026 observations. Monthly values are transcribed in `vellore-climate.json`. Humidity and wind are not supplied by this city table; obtain station data or log local conditions before assigning evaporation/windcatcher performance. The1991–2020 PDF fetch timed out, so its detailed extraction remains open.

Source: https://city.imd.gov.in/citywx/extreme/OCT/vellore2.htm
