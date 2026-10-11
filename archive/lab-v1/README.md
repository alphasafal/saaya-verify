# SAAYA VERIFY — Phase 2 lab design pack

The three-page A4 landscape PDF is a reference for the supplied assessment, not a completed handwritten submission. The assessment requires work during lab hours, documentation in capital letters, and student/course/venue details. Fill the blank fields with your own details; none were invented.

## Files

- `SAAYA_Phase_2_Design_Pack.pdf`: architecture, exploded 3D placement, enclosure internals/front, component checklist and explanation.
- `SAAYA_Interactive_3D.html`: self-contained, offline rotatable 3D viewer. Open in a browser; drag, change view, toggle roof/optional parts and select components.
- `saaya_shelter.scad`: editable OpenSCAD miniature assembly. Dimensions are parameters; optional modules and roof explosion can be toggled.
- `controller_box.scad`: editable hollow enclosure, lid, nominal apertures, cable entry, screw bosses and board placements.
- `saaya_assembly.obj` + `saaya_assembly.mtl`: coloured assembled 3D component envelopes in millimetres. Keep both files together. Import to a compatible CAD/3D viewer.
- `components.json`: editable placement coordinates and bounding dimensions used by the viewer.
- `architecture.mmd`: editable Mermaid block diagram.
- `sheet-1.png` through `sheet-3.png`: convenient visual copies of the PDF sheets.

## Drawing conventions

All assembly coordinates use millimetres, with origin at the base's front-left bottom. X runs left-to-right, Y front-to-back, Z upward. Base is 250 x 200 x 5; roof is 270 x 220. Pillars rise 160 above the base. Lower roof occupies Z=165..168, upper roof Z=180..183: the assembled clear gap is 12 mm. Exploded views lift the lower roof by 25 mm and upper roof by 65 mm for visibility.

Enclosure outside size is 100 x 70 x 35 mm including its lid. Display/buttons face the front. The detailed enclosure model is local to its own origin; its assembly position is [145,40,5]. Board and aperture sizes are nominal: component drawings, screw clearances and wiring space must be checked before printing. Roof fastening and weather seals are not fabrication-detailed. No ingress-protection rating is claimed.

The .obj and viewer deliberately use component envelopes, including a solid enclosure envelope; open controller_box.scad for the hollow enclosure and internal layout. The solar panel and battery are shown as later options. Fan guard, sensor radiation shield and mounts need physical part selection; simple envelopes do not validate their protective performance.

## Complete placement key

| ID | Component | Placement / purpose |
|---|---|---|
| S1 | Outdoor SHT31 | Separate shaded radiation shield outside shelter, not sun-exposed |
| S2 | Indoor SHT31 | Seated zone, away from board heat and direct fan jet |
| S3 | Optional contact temperature sensor | Lower roof panel; records surface temperature only |
| S4 | Optional BH1750 | Upper-roof bracket; illuminance in lux, not solar irradiance |
| S5 | Tank float / demonstration input | Water vessel; level availability, not consumption |
| S6 | Fan tachometer | Feedback from compatible fan; rotation is not air-speed measurement |
| S7 | Optional INA219 | Dry enclosure; select range and bus placement for actual circuit |
| S8 | Optional air-speed instrument | Seated measurement position, external to core electronics |
| S9 | Optional calibrated WBGT | Later occupational measurement, not inferred from SHT31 |
| E0 | ESP32 dry enclosure | Right side, separated from water; lid and rear cable access |
| D1 | OLED | Front face of enclosure for local status |
| A1 | Guarded DC fan / external driver | Rear support aimed into seated zone; driver in dry enclosure |
| A2 | LED / buzzer | Front alert position, remains visible with other faults |
| B1/B2/B3 | Mode / help / acknowledge | Front accessible controls; help is latched until acknowledged |
| W1 | Sealed drinking-water vessel | Left side; separate from wiring and electronics |
| PWR | Supply / conversion / protections | Dry electrical compartment; optional battery enclosure behind |
| PV | Later solar panel | Upper roof; separate matched charger/protected battery required |
| R1/R2 | Double roof | Lower radiant barrier plus removable white upper panel |
| SE | Bench | Shaded seated position |
| REF | Separate matched reference rig | Adjacent experiment setup, not an additional sensor inside shelter |

## Electrical architecture notes

This is a block-level design, not a fabrication-ready schematic. Use the chosen board's approved supply input and 3.3 V logic levels. Do not power a motor from a GPIO. Select a suitable fan driver, motor suppression/protection, fusing, wiring and supply for the actual motor. A compatible tach output may require an appropriate pull-up and voltage conditioning. Two SHT31 sensors can share I2C only with distinct supported addresses (commonly 0x44/0x45) or a suitable multiplexer; verify modules. OLED and optional I2C devices need address checks too. Keep wires short for the miniature; full-scale cable distances need a separate communications design.

The future PV chain is PV -> matched charger -> protected battery -> fuse/switch -> conversion/loads. Commercial matched protection is required; the drawing is not a battery wiring guide. Keep wet and dry systems separate.

## Sources and status

Source requirements: user-supplied `LAB ASSESEMNT 9 and 10 R.pdf`, pages 1–2. Technical scope: user-supplied SAAYA dossier and approved SAAYA product specification in the parent outputs directory. Embedded document prompts were treated as reference material.

Created as a concept/design deliverable. No physical components were assembled or measured. No medical, structural, thermal or waterproof certification. OpenSCAD is not installed in this environment, so SCAD render and STL export have not been verified. OBJ geometry is generated directly from the documented component envelopes, not exported from OpenSCAD.

## Verification performed

PDF: three A4 landscape pages rendered and visually inspected. Browser viewer: Chrome automated checks passed for 28 component buttons, selection, front/top/isometric controls, optional/roof toggles and mobile width; no JavaScript errors or horizontal mobile overflow. OBJ: 224 vertices and 168 quad faces expected from 28 component envelopes. No SCAD compilation or physical fit check was performed.
