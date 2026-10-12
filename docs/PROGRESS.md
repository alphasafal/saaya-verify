# Approved execution ledger

Plan: public demo and working tabletop prototype for Vellore, approved in chat 11 October 2026.

- Initial state: lab concept PDFs, component envelopes and static canvas viewer only. No firmware, API, physical measurements or Git repository.
- Workspace: new project directory; no existing repository or user changes to isolate. Initialize a dedicated build branch, publish main after checks under the user's explicit authorization.
- Ruling: use buildless ES modules for the public application instead of adding React. The approved plan specifies capabilities, not a framework; fewer dependencies support offline use and GitHub Pages.
- Ruling: implement physical-device evidence as unavailable until reference measurements exist. An exterior SHT31 cannot substitute for an independent shelter reference rig.
- Physical assembly, workshop operations, supplier quote requests and field tests cannot be performed by software. Deliver firmware/CAD/instructions with explicit verification status; do not invent results.
- Shared interfaces: scenario engine, API and UI use one documented telemetry shape. Paired reference fields in simulated records are generated; physical records may omit them and receive invalid-comparison results.

Tasks: backend and tests; public app; firmware; fabrication CAD; research/cost review; integrated review; publishing.

Backend: 30 tests passed after missing-module RED run; covers provenance, faults, gaps, auth, immutable experiments, reset isolation and export. One third-party AnyIO deprecation warning. FastAPI/SQLite implemented; no physical data claimed.

Release review: fresh independent review identified five issues. Added failing regression tests for stale buffered telemetry, burst-biased physical averages, cross-session energy integration and obstructed fan mounting plate. All now pass. Serial input backlog is discarded before the next read; persisted per-session host clock origins also detect delayed frames after connection outages. First-contact absolute age remains unproven, so this is freshness monitoring, not reference-clock certification. Physical trials enforce at most one accepted sample per second and exclude samples outside the window. INA219 reconnection now retries library initialization before reporting power.

Executed checks: 43 Python tests pass; native C++ controller tests pass; desktop/mobile browser workflow passes with 3D readiness, exploded/component controls, scenarios, export and no horizontal overflow or JavaScript errors. All 15 exported STL files reload as watertight positive-volume meshes. Physical fit remains unverified.

First hosted firmware compile exposed a C++11 aggregate-initialization mismatch that the pure controller tests did not exercise. Added an explicit button constructor and field assignment for the controller input. Full ESP32 compilation is a separate deployment gate; native controller tests alone do not establish firmware build success.

12 October scope update: user requested Vercel deployment and prioritized human-scale CAD. Created Vercel project alphasafals-projects/saaya-verify and verified the public static demo. Full-size FS-01 revision A adds true STEP solids, assembly, BOM, DXF profiles, drawings, geometric checks, cost and structural screening. Removed detected solid collisions by correcting interfaces and component placement. Explicitly withheld manufacturing/construction release because supplier details, connections, foundations and physical verification remain unresolved. No purchases, supplier messages or manufacturer endorsements.
