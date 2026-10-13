# SAAYA FS-02: five-person passive-first rest pavilion

Revision: 2026-10-13. Concept only. Original FS-01 and tabletop packages retained.

## Why not just a movable fan?

A portable fan provides the same basic air-movement mechanism at substantially less equipment/construction scope. SAAYA has no demonstrated superiority. Its proposed additional service is a shaded, accessible rest place with recliners, local assistance, independently adjustable airflow and auditable environmental measurements. Compare three cases: fan in comparable shade; an existing shaded-space retrofit; and this new structure. If the simpler retrofit works as well, do not add the new structure or AI merely for novelty.

The 32.4 m² footprint and 47.52 m² roof projection are much larger than FS-01. The previous cost estimate and below-installed-AC target cannot be transferred. No installed cost is quoted for FS-02. Quote foundations/frame, roof weathering, screens, five rated cots, five selected fans, electrical installation, monitoring, transport, labour, cleaning and replacements separately. Prioritize reuse of a suitable existing building for a lower-construction-scope option.

## New layout

- Frame footprint 6000 × 5400 mm; upper/lower roof projection 7200 × 6600 mm.
- Nine perimeter post candidates; no centre post blocks the front approach.
- Five nominal 750 × 1900 mm reclining cots: two front, three rear. Deck 450 mm; conceptual head support inclined 20 degrees.
- Cot envelopes leave y=2100–3400 mm as a 1300 mm transverse clear strip. A 1600 mm central front approach is reserved; clearance is a design reservation, not a formal accessibility claim.
- Five nominal 400 mm fans, each independently adjustable and associated with a local manual fan/help control. A 35-degree downward concept orientation is shown; guard/stand/impeller are schematic.
- Five local air temperature/RH locations, an external reference station, central cabinet, and an external WBGT/air-speed validation reservation.
- Lower roof at 3000 mm, upper roof at 3320 mm, raised ridge cap at 3660 mm. The weather cap sits above central slots in both skins. Drainage, weather baffles and structural supports are not detailed.

CAD represents placements and envelopes. Cot backrest locks, complete fan guarding, controller internals, harness, joints and fixings are not fully engineered. No supplier-specific fan curve, power rating, mass, sound level or outdoor approval has been selected. More fans do not imply a proportional cooling gain.

## Traditional mechanisms adapted cautiously

Deep verandah/chajja-like overhangs reduce direct solar exposure; removable jaali-style screens address side exposure with an airflow penalty to assess. High-level openings and a ventilated roof offer possible exhaust/heat-removal paths, dependent on actual driving pressures. This is inspiration from passive architecture, not a reproduction of a verified palace design or a proven historical temperature drop.

Heavy stone/earth thermal mass is excluded until night-time discharge potential is assessed. In warm nights it can retain heat. Direct evaporative terracotta/pad/mist systems are excluded from core because they add moisture, consume water and need cleaning; consider only a removable, separately monitored experiment where weather supports it. Vellore seasonal hourly analysis and site wind/sun surveys remain required.

If passive shade and air movement do not provide an adequate rest environment under the site's heat-management programme, assess a separate enclosed conditioned refuge. An open pavilion cannot guarantee lower air temperature or humidity and is not equivalent to AC.

## Physiology and AI boundary

This design supports voluntary rest; it does not maintain or treat blood pressure. BP varies with posture, exertion, hydration, medicines and illness and is not an adequate sole feedback signal for a fan controller. There is no automatic BP-to-cooling loop. The reclining posture is not prescribed as medical treatment.

Future physiological monitoring would require consent, validated equipment, an occupational-health/clinical protocol, private handling and human review. Do not use an AI score or a normal-looking measurement to delay assistance or clear someone to return to work. Help requests should be independent of any threshold. Serious illness, collapse or confusion requires prompt emergency assessment; do not leave an ill worker sleeping unattended.

Environmental sensors may support a reviewed comfort/maintenance policy, but the existing firmware is only the original bench implementation. The five-zone electrical system, communications and firmware are not implemented. Do not extend the short bench I²C wiring across this pavilion without redesigning the interface.

Optional existing local AI explains completed experiment evidence. It has no actuator, diagnosis or return-to-work authority. The public page uses fixed explanatory scenarios and collects no health data.

## Validation / release holds

The generator checks each constructed shape is valid with positive volume. STEP and viewing STLs are delivered. This is not an assembly interference report or manufacturing release. Still required:

1. Supplier dimensions, capacity-rated cots and guarded outdoor-suitable fans; reach, transfers, cleanability and maintenance evaluation.
2. Qualified structural/electrical design, drainage and weathering, foundations, connections and fire/material suitability.
3. Paired unoccupied airflow and environmental tests, including appropriate calibrated instruments, energy/noise and fault cases.
4. Comparisons with the same fan in comparable shade and an existing-building retrofit, repeated across weather and swapped positions.
5. Only after those gates, an approved supervised worker study with consent and stopping rules.

## Reproduce

Use CadQuery 2.6.1 (`cad/fullsize/requirements.txt`). Run `python cad/pavilion/build.py`, then `npm run build:pavilion`. Outputs: `cad/pavilion/exports/` and public copies in `site/pavilion/`. Render/selection layer: `site/pavilion-src.js`. All geometry dimensions are mm.

## References reviewed 2026-10-13

- DOE passive principles: https://www.energy.gov/cmei/buildings/zeb-technologies-passive-design-techniques
- DOE ventilation/night cooling: https://bsesc.energy.gov/energy-basics/natural-ventilation-and-cooling
- Australian Government hot-arid cooling: https://www.energy.gov.au/households/household-guides/energy-saving-guide-northern-australia/hot-arid-living
- NIOSH workplace controls: https://www.cdc.gov/niosh/heat-stress/recommendations/index.html
- NIOSH occupational heat standard, including physiological monitoring limitations: https://www.cdc.gov/niosh/docs/2016-106/pdfs/2016-106.pdf
- NIOSH heat-related illnesses: https://www.cdc.gov/niosh/heat-stress/about/illnesses.html

Sources support general mechanisms and health boundaries, not performance validation of this geometry.
