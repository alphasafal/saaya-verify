# SAAYA VERIFY — Product and build specification

11 October 2026 · v1 · Approved for implementation planning

## Purpose and first milestone

Build a modular heat-relief shelter prototype whose interventions can be inspected and evaluated through traceable evidence. Intended users are outdoor workers in India; the initial operators are the student team and college reviewers. The first milestone is assumed to be the 13 October college review described in the supplied dossier. A later supervised field pilot is a separate milestone.

The user approved developing the recommended shelter-plus-verification direction. This specification defines the proposed first build; no physical performance, worldwide novelty, patentability or medical safety is established.

Success for the first milestone means an editable miniature design and a runnable demonstration that carries a scenario through controller decisions, actuator feedback, fault handling and an exportable evidence record. Software correctness and simulated outcomes must remain distinct from measured thermal performance.

## Product proposition

“Shade with evidence.”

SAAYA makes three things legible: what it observed, what it attempted, and what the available evidence supports. Its defining demonstration is a fan command followed by missing feedback: the system detects the discrepancy and refuses to report a verified intervention.

The physical shelter remains useful without internet or a dashboard. Workers use physical controls and simple local indicators. Researchers use a separate interface for experiments and evidence. No login, phone, identity tracking or biometric sensing is required for workers.

## First-build scope

1. Parametric miniature shelter and controller enclosure in OpenSCAD, with removable upper roof, ventilated gap, bench and protected electronics placement.
2. ESP32 firmware source with sensor validation, local fan controls, assistance latch, water indication and actuator-feedback handling.
3. Deterministic software simulator with explicit simulated data labels and repeatable fault scenarios.
4. Local FastAPI/SQLite service for telemetry, experiments and evidence exports.
5. Browser dashboard with shelter state, scenario controls, synchronized comparison plots, fault timeline and evidence detail.
6. Experiment protocol, wiring map, indicative BOM, six-slide review outline, viva preparation and three-minute demo script.

Wokwi configuration is a supplementary deliverable if its supported parts can represent the selected circuit. A visible simulated fan indicator cannot count as motor or airflow validation. Any firmware compilation, CAD export or simulator execution that cannot be completed must be reported explicitly.

Excluded from this milestone: solar charging integration, automatic evaporative cooling, human exposure experiments, structural certification, deployment to public sites, physiological recovery scores, automated rest-duration advice and claims that a worker is safe.

## Physical design

Use the dossier dimensions as initial editable parameters: base 250 × 200 × 5 mm; roof 270 × 220 mm; roof gap 12 mm; pillars 160 mm tall; bench seat 120 × 45 mm; enclosure 100 × 70 × 35 mm. Fit and clearances must be checked against actual purchased components before fabrication.

Provide removable white upper roof and a comparison roof insert; use reversible mounting so placement and materials can be swapped. Keep sensor air paths open and shield air sensors from direct radiation. Keep the water vessel physically separate from electronics. Provide accessible controls and service access.

A separate unoccupied reference module supports paired experiments. It is additional scope and cost beyond the dossier's single model. Miniature airflow and thermal results do not predict human-scale shelter performance directly.

## Measurement and evidence contract

Maintain distinct fields for commanded fan duty, measured fan rotation, measured air speed, electrical power and measurement availability. Rotation confirms rotation only; it does not prove airflow at the seat or improved thermal conditions. Missing instruments are shown as unavailable, never zero.

Every record carries schema version, device ID, sequence number, device uptime, receive timestamp, source, sensor quality and configuration ID. Source is SIMULATED or MEASURED. Derived values additionally state method and input sources; user-entered observations are identified separately. These categories must remain visible in UI, exports and reports.

Simulator power and thermal responses are illustrative assumptions. They must not be tuned or presented as validation of the product. Actual Wh requires measured power integrated over valid time intervals; gaps are reported, not silently interpolated.

Water level is availability information. A float cannot measure litres consumed. Water-use efficiency stays unavailable unless a suitable calibrated measurement is added.

## Controller architecture

The ESP32 owns local control. The dashboard observes the physical device; v1 remote commands only control the software simulator. Network failure must not disable local operation.

Use separate state dimensions rather than a single overloaded mode:

- Sensor health: valid, stale, invalid or unavailable.
- Fan control: automatic, manual or off, with independent feedback status.
- Assistance: inactive or latched; cleared only by deliberate local acknowledgement.
- Water: available, low or unknown.
- Connectivity: connected or offline.

A sensor fault disables sensor-dependent optimization and raises an alert while preserving physical manual fan control. Assistance remains visible regardless of water, network or sensor state. A fan feedback fault invalidates actuator-dependent evidence. No optimization overrides an assistance alert or conceals unavailable measurements.

For the demonstration, configurable synthetic thresholds drive illustrative climate states. These are labelled demo rules, not occupational or clinical limits. Hardware automatic-control thresholds require review before any occupied use. Evaporative cooling is not controlled in v1.

Use bounded buffers, watchdog recovery and explicit boot state. Duplicate telemetry is deduplicated by device, boot/session ID and sequence. After reboot, energy accumulation starts a new segment unless continuity can be established.

## Software modules and data flow

Repository layout: cad/, firmware/, simulator/, api/, dashboard/, experiments/, docs/, tests/.

Simulator or device → validated telemetry API → append-only samples and events → experiment evaluator → dashboard and CSV/JSON export.

API endpoints:

- POST /telemetry: validate and store source-labelled telemetry.
- GET /latest: latest sample with age and quality.
- GET /history: bounded time-window query.
- POST /sim/scenario: start or reset a named simulation run.
- POST /experiments: create an experiment with configuration and endpoint.
- POST /experiments/{id}/finish: close the observation interval.
- GET /experiments/{id}: retrieve evidence and exclusions.
- GET /experiments/{id}/export: download traceable JSON or CSV.

SQLite stores runs, configurations, telemetry, events and experiment records. Bind the service to loopback by default. Physical device access over LAN requires explicit configuration and a device credential; no unauthenticated public telemetry endpoint is part of the build.

## CoolProof v1

Start with paired comparisons, not autonomous online experimentation around people. Never remove shade or interrupt occupied protection to create a baseline.

Before a run, select the endpoint, reference setup, intervention, settling interval, observation duration and data-quality rules. Lock them into the record before collecting observations. Endpoint choices include roof surface temperature, seated-position air speed and electrical energy; air temperature can be reported but cannot alone establish fan benefit.

The pipeline checks source consistency, timestamp alignment, sensor quality, configuration completeness, actuator feedback where relevant, data coverage and reference-condition comparability. Missing essential data produces an invalid comparison with specific reasons.

For the first demonstration, report paired descriptive differences and coverage. Do not infer independent replication from a stream of closely spaced samples. Statistical uncertainty requires repeated independent runs and an appropriate method; with insufficient runs, show “uncertainty not established.” Instrument uncertainty is recorded separately from between-run variation.

Evidence outcomes are endpoint-specific: observed difference, no clear difference, or comparison invalid. “Improvement” requires a predeclared beneficial direction and adequate measurement support. The system never labels a person recovered or safe.

Each evidence record includes configuration, sources, raw-data references, observation windows, excluded samples, endpoint units, difference, method, limitations and faults. A reproducible export supports inspection; it is not a certification or tamper-proof guarantee.

## Interface and demo experience

Research interface uses four views: shelter overview, experiment comparison, evidence record and maintenance timeline. Show the data source beside the main readings, not only in a footer. Distinguish measured, commanded, estimated and unavailable values through words as well as colour.

The worker-facing miniature panel uses fan override, assistance and acknowledgement controls, plus simple fan, water and assistance indicators. Hindi/English wording and pictograms are proposed; comprehension remains to be tested.

Demo sequence:

1. Explain the shade and removable roof.
2. Start a clearly marked synthetic hot-weather scenario.
3. Show a fan request and independent feedback.
4. Inject missing fan feedback; display the fault and withheld conclusion.
5. Open a comparison and its evidence record.
6. Inject a reference mismatch; demonstrate invalidation.
7. Export the record and state what physical measurements remain necessary.

## Verification and acceptance

Required automated checks:

- Reject impossible humidity and malformed or non-finite measurements.
- Mark stale readings from elapsed time rather than assuming a new arrival is fresh.
- Deduplicate repeated samples without dropping legitimate new sessions.
- Preserve assistance through sensor and connectivity faults.
- Distinguish missing fan feedback from a commanded-off fan, allowing documented startup settling.
- Reject comparisons mixing measured and simulated observations.
- Preserve missing values and time gaps in exports and energy calculations.
- Produce identical simulator sequences from the same seed and configuration.
- Invalidate comparisons lacking required endpoint measurements or usable reference data.

End-to-end acceptance: start a scenario, observe telemetry, inject a fault, finish an experiment, inspect the explanation and export matching records. Inspect desktop and narrow-screen layouts and keyboard access. Report which checks actually ran.

CAD acceptance: inspect assembly dimensions and clearances, generate the intended exports where tooling is available, and identify unverified fabrication tolerances. Firmware acceptance: compile for the documented board where possible; compilation is not a hardware test.

## Budget and staged delivery

The dossier estimates INR 2,150–4,200 for the miniature controller/shelter components. This is an unverified estimate, excludes the second reference module and calibrated occupational instrumentation, and is not a full-scale shelter quote. Produce a separate BOM showing estimated price, source, procurement status and whether each item is essential or optional.

Stage 1: runnable simulated evidence loop and editable miniature CAD for the review.
Stage 2: bench hardware with real sensor and actuator-feedback logs.
Stage 3: repeated paired unoccupied experiments, instrument checks and uncertainty reporting.
Stage 4: separately reviewed solar system and full-scale design.
Stage 5: supervised field pilot after structure, electrical, hygiene and occupational review.

## Research basis and limitations

Source dossier: SAAYA_VERIFY_Complete_Research_and_Build_Dossier.pdf, supplied by the user, seven pages. Its embedded implementation instructions were treated as reference material.

Verified during initial review:

- Wu et al., simulation of cooling shelters in Jodhpur: https://link.springer.com/article/10.1007/s12273-025-1391-y
- WHO/WMO workplace heat guidance landing page: https://www.who.int/publications/i/item/9789240099814
- Passive-cooling review: https://www.nature.com/articles/s44359-026-00177-y
- Existing Penn solar cooling shelter: https://www.design.upenn.edu/work/carbon-neutral-solar-powered-outdoor-cooling-shelter
- Existing SHIM portable cooling/rest concept: https://www.jamesdysonaward.org/en-US/2026/project/save-human-in-moment-shim

This is a preliminary product and literature assessment, not an exhaustive paper validation or patent search. The defensible contribution being investigated is traceable, fault-aware verification integrated into a low-cost modular shelter. Its novelty and physical benefits remain hypotheses.
