# SAAYA VERIFY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution or superpowers:subagent-driven-development if the user selects delegation. Complete tasks in order using the checkboxes below.

**Goal:** Deliver a runnable local shelter simulator with a fault-aware evidence workflow, editable miniature CAD, and ESP32 firmware source.

**Architecture:** A local FastAPI service owns validated telemetry, deterministic simulation runs, SQLite persistence and experiment evaluation. A React browser interface displays the same stored records used for evidence exports. Independent ESP32 firmware controls physical hardware locally and emits the documented telemetry contract; it never depends on the web interface for local controls.

**Tech stack:** Python, FastAPI, Pydantic, SQLite, pytest; React, TypeScript, Vite; PlatformIO/Arduino ESP32; OpenSCAD. Use available stable compatible dependencies and save resolved versions and lockfiles during implementation.

**Spec:** [Approved product specification](SAAYA_Product_and_Build_Specification.md).

**Execution recommendation:** Native execution in this chat. The modules share one telemetry and evidence contract, so sequential implementation provides a useful integration check after each task. A final independent review checks the completed implementation.

## Global constraints

- Source is SIMULATED or MEASURED.
- Missing instruments are shown as unavailable, never zero.
- The ESP32 owns local control.
- Network failure must not disable local operation.
- No optimization overrides an assistance alert or conceals unavailable measurements.
- Water-use efficiency stays unavailable unless a suitable calibrated measurement is added.
- Bind the service to loopback by default.
- Statistical uncertainty requires repeated independent runs and an appropriate method; with insufficient runs, show “uncertainty not established.”
- The system never labels a person recovered or safe.
- Physical testing, fabrication, sourcing and field deployment are not accomplished by software execution.

## Review focus

1. Device restarts and duplicated transmissions must not merge sessions or double-count energy: tests in Tasks 1–2.
2. Delayed packets and missing power samples must remain stale or incomplete: tests in Tasks 1–2.
3. Scenario resets during active experiments must not silently change their data: tests in Tasks 2–3.
4. API loss and empty datasets must not leave apparently current readings on screen: tests in Task 4.
5. Missing feedback, manual controls and assistance must behave independently, including at boot: tests in Tasks 1 and 5.

## Delivery layout

Place the deliverable project in `outputs/saaya-verify/`. Use `work/` for intermediate screenshots and scratch assets. Each path below is relative to that project.

- `api/models.py`: shared validation schemas.
- `api/control.py`: pure reference control logic.
- `api/store.py`: database persistence and bounded queries.
- `api/evidence.py`: comparison eligibility, descriptive results and energy accounting.
- `api/main.py`: HTTP routes and application lifecycle.
- `simulator/scenarios.py`: deterministic synthetic sequences and injected failures.
- `dashboard/src/`: React application and visual components.
- `firmware/src/`: ESP32 controller and board integration.
- `cad/`: editable shelter, enclosure and export instructions.
- `experiments/`: protocol, schema and sample synthetic records.
- `docs/`: wiring, BOM, demo, review material and verification status.
- `tests/`: backend and integration tests; browser tests live under `dashboard/tests/`.

## Task 1 — Telemetry and reference controller

**Files:** `api/__init__.py`, `api/models.py`, `api/control.py`, `tests/test_models.py`, `tests/test_control.py`, `pyproject.toml`.

**Interfaces:** `Telemetry`, `ControlState`, `ControlInput`, `ControlConfig`; `step_control(previous: ControlState, inputs: ControlInput, config: ControlConfig) -> ControlState`.

Telemetry includes schema version, device/session/configuration IDs, sequence, source, acquisition uptime, emission uptime, nullable sensor values, explicit sensor quality, fan command, nullable rotation/air-speed/power values, assistance state and water state. Server receive time is assigned by the service. Reading age accounts for acquisition age at emission and time elapsed after reception. Cross-device experiment pairing also requires an explicit synchronized observation timestamp; unknown clock alignment invalidates measured comparisons.

- [ ] Write failing tests for RH outside 0–100, NaN/infinity, negative sequence, invalid source and valid null measurements.
- [ ] Write failing control tests for assistance latching, deliberate acknowledgement, stale inputs, manual fan operation during sensor failure, off-state feedback and startup grace.
- [ ] Run `python -m pytest tests/test_models.py tests/test_control.py -q`; confirm missing implementation is the failure.
- [ ] Implement the schemas and pure state transitions. Keep illustrative automatic thresholds in named demo configuration. Assistance and water are independent of fan mode.
- [ ] Run the same tests; require all passing. Record configuration and startup-grace values in documentation.

## Task 2 — Simulator, persistence and evidence evaluator

**Files:** `simulator/__init__.py`, `simulator/scenarios.py`, `api/store.py`, `api/evidence.py`, `tests/test_simulator.py`, `tests/test_store.py`, `tests/test_evidence.py`.

**Interfaces:** `generate_scenario(name: str, seed: int, count: int) -> list[Telemetry]`; `Store.insert(sample: Telemetry) -> bool`; `Store.history(device_id: str, session_id: str, limit: int) -> list[Telemetry]`; `evaluate_experiment(spec: ExperimentSpec, samples: list[Telemetry]) -> EvidenceRecord`.

Use unique `(device_id, session_id, sequence)` keys. Persist run/configuration metadata. ExperimentSpec captures endpoint, source, device/session pairs, configuration IDs, start/end, settling period, expected cadence, tolerances and minimum coverage before observation begins. EvidenceRecord includes exclusions, raw sample references, source, endpoint units, descriptive difference, coverage, energy completeness, faults and limitations.

- [ ] Write failing tests asserting identical scenario values for identical seeds; isolated sessions for resets; reproducible fan fault, low-water, stale-sensor and reference-mismatch scenarios.
- [ ] Write failing tests asserting duplicate insertion returns false, a new session accepts sequence zero, invalid comparisons cannot report improvement, mixed sources are rejected and unavailable power remains null.
- [ ] Add tests for cross-session energy boundaries, time gaps, minimum coverage, clock misalignment, missing endpoints and fan-dependent comparisons with failed feedback. Report valid-duration Wh and coverage separately; never present incomplete duration as full-run consumption.
- [ ] Run `python -m pytest tests/test_simulator.py tests/test_store.py tests/test_evidence.py -q` and confirm the intended failures.
- [ ] Implement deterministic synthetic generation, parameterized SQL storage and paired descriptive evaluation. Independent-run uncertainty stays unestablished in the single-run demo.
- [ ] Run the tests again and require all passing.

## Task 3 — API and complete programmatic demonstration

**Files:** `api/main.py`, `api/exports.py`, `tests/test_api.py`, `tests/test_workflow.py`, `.env.example`, `README.md`.

**Interfaces:** Implement the eight endpoints listed in the approved specification. Add `GET /health`, `GET /events` and `POST /sim/step` for health, timeline and deterministic progression. A scenario starts a named run; stepping advances that run explicitly. Finished experiments are immutable snapshots.

- [ ] Write failing HTTP tests for invalid payloads, bounded history, unknown IDs, duplicate samples, finished-experiment immutability and JSON/CSV null/source preservation.
- [ ] Add one workflow test: create run → predeclare experiment → advance samples → inject fan fault → finish → retrieve/export. Assert fault-dependent evidence is withheld and exported samples match stored references.
- [ ] Add a reset test proving active experiments stay tied to their original sessions and cannot acquire replacement-run samples.
- [ ] Run `python -m pytest tests/test_api.py tests/test_workflow.py -q`; confirm intended failures.
- [ ] Implement routes, explicit simulator actions, export serialization and local configuration. Require a configured credential for measured ingestion; document deliberate LAN opt-in.
- [ ] Run all backend tests and start the service on `127.0.0.1`. Verify the complete workflow through HTTP as well as the test client.

## Task 4 — Research dashboard

**Files:** `dashboard/package.json`, `dashboard/index.html`, `dashboard/vite.config.ts`, `dashboard/tsconfig.json`, `dashboard/src/{main.tsx,App.tsx,api.ts,types.ts,styles.css}`, `dashboard/src/components/{ShelterView.tsx,TelemetryCards.tsx,ComparisonChart.tsx,EvidencePanel.tsx,EventTimeline.tsx}`, `dashboard/tests/workflow.spec.ts`.

**Interfaces:** Typed client for Task 3 endpoints. UI state always derives from API records; visual animation cannot create evidence values.

Visual direction: warm ivory, charcoal, restrained leaf green, amber for attention; architectural shelter illustration; clear instrument-style readings; prominent SIMULATED labels. Four views: overview, experiment, evidence and maintenance. This is a research tool with usable controls, not a promotional landing page.

- [ ] Write browser acceptance tests for empty state, API failure, scenario start, experiment creation, fan fault, finish, evidence inspection and export. Assert stale/disconnected copy replaces apparent freshness after API loss.
- [ ] Implement responsive navigation, accessible form controls and inline validation. Preserve experiment parameters after creation; show command and feedback separately.
- [ ] Implement synchronized reference/intervention plots with explicit units, missing-data gaps and source labels. Expose raw evidence and limitations without hiding them behind decorative scores.
- [ ] Run typecheck, production build and browser tests. Check the actual UI at desktop and mobile widths, keyboard navigation, chart legends and download content. Save screenshots as verification evidence.

## Task 5 — ESP32 firmware and wiring

**Files:** `firmware/platformio.ini`, `firmware/src/main.cpp`, `firmware/include/control.h`, `firmware/src/control.cpp`, `firmware/test/test_control/test_main.cpp`, `docs/wiring.md`, `docs/firmware.md`.

**Interfaces:** Emit Task 1 telemetry as serial JSON with a new boot/session ID. Native C++ control fixtures must match Python reference decisions for shared input sequences. Real hardware automatic mode is disabled until explicitly enabled for unoccupied bench work; physical manual operation remains available.

- [ ] Write failing native tests for boot state, assistance latch, sensor failure, manual override, tach startup grace and millis rollover.
- [ ] Implement two SHT31 inputs, OLED state, debounced controls, fan PWM via an external driver, tach input, water float and optional power monitor. Reserve pins after checking board and library documentation; document I2C addresses and voltage constraints.
- [ ] Add sensor acquisition timestamps, bounded logging, watchdog recovery and unavailable fields for absent instruments. Do not fabricate air speed from fan RPM.
- [ ] Run native tests and attempt the documented ESP32 compilation. Record exact outcomes; no hardware-tested claim without hardware.
- [ ] Produce an explicit pin/wiring table, external motor-driver/protection requirements and physical water/electrical separation notes. If Wokwi substitutions are feasible, add a separate documented simulation configuration and identify unsupported physical effects.

## Task 6 — Editable CAD and review package

**Files:** `cad/saaya_shelter.scad`, `cad/controller_box.scad`, `cad/README.md`, `experiments/protocol.md`, `experiments/schema.csv`, `docs/bom.csv`, `docs/review-outline.md`, `docs/viva.md`, `docs/demo-script.md`, `docs/verification.md`.

**Interfaces:** Dimension parameters match the specification; the project README links all deliverables and run commands.

- [ ] Create the shelter with base 250 × 200 × 5 mm, roof 270 × 220 mm, gap 12 mm, 160 mm pillars and 120 × 45 mm bench. Keep roof inserts removable and the reference module explicit.
- [ ] Create the 100 × 70 × 35 mm enclosure with accessible lid and parameterized component apertures. Mark component fit as unverified until checked against purchased parts.
- [ ] Export shelter assembly, roof insert and enclosure STL if OpenSCAD is available; inspect renders and provide dimensioned front/top/isometric views. Record any unavailable export or unverified fabrication detail.
- [ ] Write the paired unoccupied protocol, calibration/placement record, CSV schema and indicative BOM with procurement status. Do not turn the dossier estimates into supplier quotes.
- [ ] Write six-slide content, 20 viva questions with answers, a three-minute script and a verification matrix distinguishing implemented, executed and physically untested work.

## Task 7 — Integration, independent review and delivery

**Files:** `README.md`, `docs/verification.md`, relevant corrections and lockfiles.

- [ ] Run the documented clean-start installation and launch steps against the finished project.
- [ ] Run backend tests, frontend typecheck/build/browser workflow and available firmware/CAD checks. Fix failures and rerun affected checks.
- [ ] Request a final independent review of source provenance, evidence validity, controller faults, persistence and UI correctness using the available review capability. Resolve actionable findings and report any review limitation.
- [ ] Open the running app in Codex. Deliver the project, launch command, verification results and remaining physical tasks. Describe only checks actually executed.

## Plan self-review

The tasks cover all first-build specification deliverables. Solar, evaporative control, occupied testing and full-scale deployment remain outside the first milestone. Software simulation is the acceptance path when physical equipment is absent. Statistical uncertainty is deliberately not estimated from consecutive simulator samples. All five review-focus conditions have explicit owning tests above.

Implementation has not started. The approved specification and this plan are the current deliverables.
