# Operational CAD teaching layer

This layer addresses the visual review finding that bought-out part envelopes looked like anonymous blocks and the assembly did not explain the worker cooling path.

## What is now visible

- A seated reference person on the existing bench, for spatial explanation only.
- Seven schematic fan blades and hub inside the existing 200 mm reference fan envelope. These are not Noctua impeller geometry.
- SHT31 board/chip details, ESP32 shield/header details, INA219 board and OLED face details at the original component transforms. Detailed mesh features are illustrative, not supplier-approved outlines.
- Colour-coded hardware and sensor-location rings; click shortcuts or labels to focus on small electronics. No physical component is secretly scaled up.
- The current horizontal fan axis in amber. Dashed blue curves identify a desired delivery zone, not the flow that this fan has been shown to produce.
- Solar exposure intercepted by the roof and intended ventilation through the roof gap, as qualitative arrows.
- Synthetic temperature, RH and roof-temperature readings attached to component labels. No live device data is used.

Cooling view makes structure/guards transparent for inspection. Solid CAD view removes the presentation meshes. The original STEP, STL, BOM and manufacturing checks retain their existing scope; decorative detail meshes and the human reference are excluded from them.

## Parameter response

The controls reproduce the steady-state bench decision rules after the three-second fan-start grace period. They are not a new full-size controller or a physiological model.

| Input | Response shown | Implementation boundary |
|---|---|---|
| Manual mode | 70% PWM command | Existing bench firmware allows manual mode despite an air-sensor fault |
| Optional bench auto | 50% at air temperature >=32°C with valid air sensors; otherwise 0% | Compile-time feature disabled by default; trigger is not a safety threshold |
| Relative humidity | Changes evaporation explanation and sensor label | Current firmware does not use RH to optimize PWM |
| Roof temperature | Local roof-minus-air difference, not a cooling benefit | Logged observation; no roof actuator or radiant-temperature inference |
| Tach feedback | Rotation animation / feedback fault below 100 RPM when duty >0 | Independent synthetic input; RPM does not prove airflow |
| Fan power loss | Stops rotor and moving particles; feedback fault when commanded | Separate USB supply can still power controller |
| Water availability | Available/low indication | No pump, mister or evaporative actuator in core design |

The NF-A20 full-size dimensional reference is IP50 and can continue rotating at 0% PWM. A zero command is not hardware isolation. Do not infer bench NF-A4x10 behaviour or a fan-speed curve from this overlay.

## Design gap exposed by the human reference

Existing fan axis: X=970, Y approximately 1900, Z=1520 mm. The reference worker's torso and head are below that axis. A revised mount/location and a selected outdoor-rated actuator require design review and seated air-speed mapping. The dashed path bends toward a target zone deliberately: it is an aspiration, not a solved flow field. No aiming bracket, revised fan purchase or cooling capability is claimed by this release.

The reference SHT31 location is also not proven to be an unshaded ambient reference. Roof probe contact, radiation shields, harness and weather sealing remain open issues described in the manufacturing review.

## Export and reproduction

`site/cooling-scene.js` contains editable Three.js geometry and `site/cooling-logic.js` contains the parameter explanation rules. Build with `npm run build:fullsize`. The viewer's Download operational 3D button exports GLB for viewing/editing in tools that support glTF; it is marked ILLUSTRATIVE and is not a substitute for the assembly STEP. It includes the current presentation state, so reset Cooling view before exporting an overview.

Run `node --test tests/cooling.test.mjs`. With the local server running, run `npm run test:cooling` for browser actions and GLB file validation.

## Mechanism sources

Reviewed 2026-10-12:

- [NIOSH workplace recommendations](https://www.cdc.gov/niosh/heat-stress/recommendations/): environmental controls, shade/rest and air movement within a wider occupational heat programme.
- [NIOSH PPE heat burden](https://www.cdc.gov/niosh/heat-stress/recommendations/ppe.html): air temperature, humidity, radiant heat, airflow and clothing affect heat exchange.
- [Noctua NF-A20 PWM specifications](https://www.noctua.at/en/products/nf-a20-pwm/specifications): purchased-reference envelope and limitations; no outdoor approval implied.

No CFD, net physiological heat-balance calculation, measured airflow, thermal experiment or safety assessment is produced by this layer.

## Adjustable-mount and AI explanation update (2026-10-13)

The viewer now includes an opt-in 0–40 degree downward-tilt preview. It rotates the reference fan, cartridge and guards about the fan-centre pivot and adds schematic side-pivot details. The amber axis follows the pose; blue curves remain a desired delivery zone, not a computed jet. This is a mechanical design proposal only. Detailed hinge fasteners, locking torque, load capacity, travel stops, finger access, adjustment ergonomics and interference/airflow checks are not complete. Solid CAD view restores the original mount, and the manufacturing STEP is unchanged.

The AI explanation explicitly separates optional local model analysis from a public fixed-rule evidence brief. The public scenario brief includes synthetic source, measured-data gaps and withheld comparison status; it is not represented as model output. Actual optional AI is implemented through the local `/experiments/{id}/explain` endpoint and `SAAYA_AI_MODEL`, using a local Ollama server. No model service has been installed or demonstrated here, and nothing in the AI path controls actuators.

The comparison asks whether SAAYA adds measurable value over the same fan with comparable shade. Complexity, a different angle, or an AI label alone cannot establish that value. Exported operational GLB units are metres; the original engineering coordinate convention is millimetres.
