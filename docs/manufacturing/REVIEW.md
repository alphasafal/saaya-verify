# FS-01 manufacturing review and RFQ dossier — revision A

**Disposition: design review / quotation only. Not released for fabrication or installation.** This package supports professional review; no named CAD firm or manufacturer has reviewed or endorsed it.

## Included and deliberately separate

The model contains structural members, proposed base/connection plates and hole patterns, two roof layers and spacers, bench rails/slats, replaceable shade louvres, a fan cartridge with front/rear guards, a service enclosure/carrier, electronics/probe/sensor references, a separate water vessel, conduit and fastener envelopes. STEP bodies are editable solids, not converted STL triangles. Purchased component details are simplified; threads are omitted from standard fastener envelopes.

The generated BOM contains quantities and idealized solid volumes. The model does not turn an assumed material density into a certified shipping weight. It excludes weld beads, coatings, cable harnesses, sealants, foundations and unselected mounting accessories. Use weighed parts for final resource and transport accounting.

## Fabrication route and tolerances to agree with the supplier

| Family | Proposed process | Review acceptance target | Release check |
|---|---|---|---|
| SHS/RHS steel frame | Saw/laser tube cut, jig, weld, corrosion finish | Cut length ±1 mm; assembled datum-to-datum ±3 mm; frame squareness ≤3 mm diagonal difference | Fabricator confirms steel grade, stock wall tolerance, weld schedule, distortion allowance, coating vent/drain holes and dimensional inspection |
| Flat connection/base plates | Laser/plasma rough cut then drill critical holes | Hole position ±0.25 mm relative to indicated datum; hole size +0.2/0 mm proposal | Actual bolt/anchor selected, edge distances and tear-out designed, burr-free mating faces |
| Roof skins | Cut, form, coat, gasket/fasten | Supplier defines profile, bend allowance and finished pitch | Current broad skin solids are envelopes; seams, hems, laps, gutter, fixing grid and uplift details must be approved before cutting |
| Bench/slats/screens | Saw/machine, radius/deburr, finish | Slat gap checked after coating; no exposed sharp edges | UV/moisture/creep/fire and occupant load specification; repairable fasteners selected |
| Electrical housing | Qualified outdoor enclosure preferred | Verify actual module clearances and service access | Supplier IP rating applies only to approved enclosure/penetrations; modeled shell has no IP claim |
| Polymer shield/fit coupons | FDM prototype, then qualified part choice | Print coupon and measure; do not treat 0.3 mm CAD allowance as a verified tolerance | Radiation response, UV, heat deformation, water ingress and airflow tests |

These are proposed RFQ targets, not blanket ISO tolerances. Do not apply machining tolerances to a welded shelter. No sheet-metal flat pattern is production-ready until the fabricator's bend tooling and K-factor are established. Current DXFs represent unformed flat plates/skin envelopes only.

## Assembly sequence and service access

1. Resolve site load, anchor and foundation design before site work. Survey drainage and unobstructed approach; set datums from the post-centre grid.
2. Make one base/post/beam connection first article. Inspect tube wall, hole centres, squareness, weld quality and finish. Trial-assemble the roof subframe at ground level.
3. Trial-fit roof skin fixing, spacers, water runoff and gutter. The open roof needs checked uplift paths to the foundations. Safe lifting/temporary stability requires the installer's method statement.
4. Assemble bench and replaceable screen modules. Check pinch points, sharp edges, hot surfaces and the free access bay with actual users and the applicable accessibility requirements.
5. Mount the fan cartridge on an approved support, with guards on both sides. Confirm blade clearance, guard deflection, sound and occupied-zone air-speed distribution. The reference PC fan is not an approved outdoor part.
6. Install dry electronics with a fused SELV supply, insulated mounts, strain relief, drip loops and segregated sensor/fan wiring. Keep mains adapters and mains installation outside this prototype scope unless installed by a qualified electrician.
7. Mount shielded outdoor/seated sensors and the roof probe. Seal cable penetrations using the selected enclosure manufacturer's method. Route cables in conduit with removable clips; retain a service loop at the door/carrier.
8. Run bench electrical/fault tests and independent paired thermal/air-speed tests. Record actual part revisions, calibration, power boundary and failures before any performance claim.

The lid, carrier, fan guards, roof layers, slats and screens are separate bodies. CAD inspection can check access envelopes; it cannot certify tool reach, assembly ergonomics or maintenance time. Verify those during the first article.

## Critical unresolved interfaces / release holds

- Structural member sizes are candidates. `feasibility.json` is a transparent elastic screening calculation, not an IS 875/IS 800 design. Roof local pressures, member stability, connections, lateral bracing and foundations remain open.
- Anchor geometry is illustrative. No embedment/capacity, concrete strength or soil bearing value has been established.
- Complete roof forming, sealed laps, water runoff/gutter/downpipe, continuous load path, fatigue and corrosion treatment need supplier/engineer detailing.
- Bolted joint plate patterns are proposed, not an approved connection design. Tube sleeves, crush resistance, washers/nuts, torque, end caps and galvanizing holes must be resolved.
- Fan cartridge support, enclosure mounting brackets, lid hinge/gasket/latch, strain relief, sensor support arms and module-specific carrier drilling require actual component drawings and first-article inspection.
- Full-size fan/weather suitability, supply protection and installation are not inherited from the tabletop firmware. Full-size config/calibration and commissioning are separate; no occupied trials are authorized by this CAD.
- Water experiment remains removable and inactive; no pump, plumbing or potable-water specification is included.

## Reviewer deliverable / RFQ response requested

Ask the reviewer/manufacturer to return a redlined drawing set, interface-clash disposition, revised STEP, process/material substitutions, inspection plan, itemized delivered/installed quote, lead time and exclusions. Request separate prices for one first article and batches of 10/50; do not assume volume discounts. Include tooling, finishing, installation, power, transport, maintenance and tax explicitly.

No manufacturer has been contacted and no supplier quote, independent DFM approval, thermal result, patent clearance or construction certification is represented by this release.

## Primary references consulted

- [CadQuery import/export documentation](https://cadquery.readthedocs.io/en/latest/importexport.html): STEP assemblies and DXF export.
- [Espressif DevKitC V4 dimension drawing](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf): reference PCB outline; procurement must match revision.
- [Noctua NF-A20 PWM specifications](https://www.noctua.at/en/products/nf-a20-pwm/specifications): 200 × 200 × 30 mm, 12 V interface reference; no outdoor suitability inferred.
- [Adafruit SHT31-D](https://www.adafruit.com/product/2857): current breakout differs from historical board; confirm purchased revision.
- [Protolabs sheet-metal design guidelines](https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/): manufacturing constraints need the supplier's process/tooling; not an endorsement or review of SAAYA.
- [BIS structural reference document](https://www.services.bis.gov.in/tmp/WCCED21426932_12032025_1.pdf): references IS 875 Part 3:2015. This is not a substitute for obtaining and applying the governing standards.

Accessed 12 October 2026. Third-party full PDFs/CAD assets are not republished in this package.

## Revision A geometric corrections and cost disposition

The modeled fastener stack was corrected with coordinated 11 mm beam/plate through-holes, a longer bolt envelope and widened beam end allowance. A proposed rear purlin seating relief removes up to 3 mm over 50 mm; the structural engineer must approve or replace this detail before fabrication. Sloping skins, spacer ends and cap surfaces now share a common slope. Water and conduit placement were moved to clear the bench and support rails. Added sensor stems, a reference stand, rear service rail, fan arms and enclosure support members. Support attachment strengths, nuts/washers/sleeves and sealing are still release holds.

The latest solid-intersection report is shipped with the CAD. Zero intersections above its threshold means only that the idealized solid bodies do not occupy the same volume; it does not establish that every fastening or interface is adequately detailed.

The approximately 250 kg idealized assembly is materially larger than the early concept budget assumed. Revised unquoted first-article allowances are approximately INR94,000–171,000, including provisional engineering/site/installation allowances. The below-installed-AC target is **not demonstrated**. A dated installed AC quote is still absent. To reduce cost, review roof area, material/process, component sourcing and connection count against loads and repairability; do not remove structural members solely to match a price.

### Verified full-size fan interface limitation

The current manufacturer specifications list 154 × 154 mm as one NF-A20 mounting pattern, 200 × 200 × 30 mm without pads (32 mm with pads), IP50, and nonzero rotation at 0% PWM. The 30 mm CAD body is the bare reference envelope; pads/guard spacing require allowance. **The tabletop duty-zero command must not be treated as a full-size fan stop.** A suitably rated hardware power-isolation stage and a verified outdoor fan/supply configuration are required before full-size commissioning. IP50 provides no water-protection rating. This is a geometry reference, not an approved outdoor actuator.

Final independent source review corrected the bench support direction by adding three transverse rails underneath all six slats; added a centre hole in each roof cap to match the roof fixing axis; removed the 0.05 mm bounding-box exclusion from the volume-based clash check; and linked CAD regeneration artifacts to the publishing job. Clear contact geometry does not approve bench load capacity or the fastener design.
