# SAAYA panel presentation and gap review

## Five-minute presentation

1. **Purpose, 30 seconds.** SAAYA proposes shade, ventilation and a repairable instrumented shelter. It does not claim room-AC-equivalent cooling, thermal safety, or established novelty.
2. **Architecture, 60 seconds.** Open `/explain.html#architecture`. Follow sensor → ESP32 → PWM signal driver → fan. Follow tach back to ESP32. Identify OLED, assistance controls, separate USB/controller power and fused fan power. The INA219 measures only the fan branch.
3. **Placement, 90 seconds.** Open the labelled CAD. Select ESP32 to reveal the dry enclosure; select seated SHT31 to explain why ambient sensors must avoid controller heat. Inspect the independent reference mast, roof probe, fan, display, assistance button and separate optional water vessel. Each inspector gives role, rationale, connections, coordinates and limitations.
4. **Evidence, 60 seconds.** Describe actual USB serial → laptop bridge → local API/SQLite → dashboard. Public hosting replays synthetic records. Demonstrate fan failure or reference mismatch in the evidence lab; invalid comparisons do not produce a cooling claim.
5. **Next steps, 60 seconds.** Assemble and calibrate the unoccupied bench, verify wiring and faults, run repeated paired trials with position swaps. Complete qualified full-size engineering and supplier checks before fabrication.

## Original presentation gaps and corrections

- The architecture was inside a collapsed homepage disclosure and absent from the full-size review page. The teaching page now displays an interactive diagram and the real local telemetry path prominently.
- Selecting ESP32 showed only name, dimensions and a procurement note. It did not expose the board or explain its role. The inspector now explains every part and instance; selection focuses the camera and reveals internal electronics.
- No visible CAD callouts or presentation sequence existed. Sixteen labelled callouts and a guided tour now cover the core mechanisms and IoT hardware; all 143 instances remain selectable and searchable.
- Full-size geometry and bench firmware could be confused. Every page now separates full-size placement from the implemented bench pin map and its electrical limits.
- AI, internet hosting and actual telemetry were easy to conflate. The diagram and FAQs distinguish static Vercel hosting, USB bench telemetry and optional read-only local AI.

Audit evidence: the current live page was inspected on 12 October 2026, including selecting ESP32. The resulting screen still showed a closed enclosure and one line of dimensions; the source confirmed no role/placement/connection fields. Screenshot retained in `work/saaya/audit-before.png` outside the public package. Screenshot review is not a full accessibility certification.

## Engineering gaps that presentation cannot close

- The near-edge reference mast may remain under the roof overhang. It is not automatically a valid unshaded reference. Use an appropriately positioned matched control and document conditions.
- Air shields are simplified hollow envelopes, not tested radiation/ventilation shields.
- The roof probe envelope ends near the lower skin; thermal coupling and the contact fixture are not complete.
- Discrete PWM/buzzer stages, fuse, supply, connectors and detailed harness are electrical requirements but are not detailed CAD parts. They must be fitted and documented before hardware assembly.
- Bench I²C is a short bus. Full-size cable lengths, interference and suitable remote sensor interfaces need qualification.
- The full-size NF-A20 envelope is a dimensional reference, not an approved outdoor actuator; 0% PWM does not stop it. A true isolation path is needed. The 250 mA bench fuse is not a full-size specification.
- Exact module fit, enclosure seals, cable glands, structural joints, roof weatherproofing, foundations and occupied load capacity remain open.
- Human-scale airflow and cooling cannot be inferred from miniature geometry or RPM. External air-speed instrumentation and appropriate independent thermal measurements are required.
- Installed-cost comparison, patent novelty, sustainability benefit and physical performance are unproven.

## Sources and implementation references

- `firmware/src/main.cpp`: actual GPIOs, bus addresses, serial format and sensor acquisition.
- `firmware/include/controller.h`: deterministic manual/automatic/fault/latch behavior.
- `docs/engineering.md`: bench circuit, power boundary and physical test cautions.
- `cad/fullsize/exports/assembly.json` and `bom.json`: model placement, quantities, envelopes and process notes.
- `docs/manufacturing/REVIEW.md`: full-size release holds and supplier references.
- `docs/physical-protocol.md`: calibration and paired experiment requirements.

The teaching metadata in `site/component-guide.json` is explanatory. CAD source and supplier measurements remain the engineering authority. Exploded coordinates are a viewing aid; the inspector always reports original CAD coordinates.
