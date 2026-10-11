# Approved execution ledger

Plan: public demo and working tabletop prototype for Vellore, approved in chat 11 October 2026.

- Initial state: lab concept PDFs, component envelopes and static canvas viewer only. No firmware, API, physical measurements or Git repository.
- Workspace: new project directory; no existing repository or user changes to isolate. Initialize a dedicated build branch, publish main after checks under the user's explicit authorization.
- Ruling: use buildless ES modules for the public application instead of adding React. The approved plan specifies capabilities, not a framework; fewer dependencies support offline use and GitHub Pages.
- Ruling: implement physical-device evidence as unavailable until reference measurements exist. An exterior SHT31 cannot substitute for an independent shelter reference rig.
- Physical assembly, workshop operations, supplier quote requests and field tests cannot be performed by software. Deliver firmware/CAD/instructions with explicit verification status; do not invent results.
- Shared interfaces: scenario engine, API and UI use one documented telemetry shape. Paired reference fields in simulated records are generated; physical records may omit them and receive invalid-comparison results.

Tasks: backend and tests; public app; firmware; fabrication CAD; research/cost review; integrated review; publishing.
