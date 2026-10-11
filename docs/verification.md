# Verification status — 11 October 2026

This file is updated with executed checks before publication. No physical fabrication or testing was performed.

| Area | Status | Evidence / limit |
|---|---|---|
| Local telemetry API | Implemented and automated tests run | 43 Python tests pass across API, evidence, analysis and CAD; includes stale backlog and burst-sampling regressions |
| CoolProof simulation | Implemented and tested | Fixed synthetic60-sample scenarios; not a physical thermal model |
| Physical-data evaluator | Implemented and tested with fixtures | Measured-path fixtures are synthetic; no measured trial exists |
| Interactive site | Browser checked | Scenario controls, invalid/valid comparison, export, missing power, mobile layout and JS errors |
| CAD |15 STL exports checked | Closed meshes after reloading; positive volume; intended enclosure dimensions; <=220mm envelope per printable piece |
| Manufacturing fit | NOT VERIFIED | Purchased module dimensions, tolerances, joins, wiring clearance, printer process and assembly inspection remain open |
| Firmware controller | Native C++ tests run | Latch, manual override, startup grace, feedback and timer wrap |
| ESP32 firmware build | In progress | Toolchain installation/build result will be recorded before final publication |
| Physical electronics | NOT ASSEMBLED / NOT TESTED | No device, wiring, power, sensor calibration or serial hardware validation |
| Optional AI | Disabled by default; adapter/unit tests implemented | No local model installed or actual model output evaluated |
| Research |13 records, all8 dossier references covered | Full-text access varies per source; unavailable text not represented as reviewed |
| Vellore climate | Historical IMD normals transcribed |1981–2010 baseline; current site humidity/wind and1991–2020 detailed extraction remain missing |
| Installed cost vs AC | NOT VERIFIED | Web equipment price is not a Vellore installation quote; shelter costs are allowances |
| Novelty / certification | NOT ESTABLISHED | No exhaustive patent search, human-scale thermal proof, structural approval or medical claim |
| Public deployment | Pending release | Live URL and actual deployment result recorded at release |

CAD limitation: mesh validity does not prove printability at arbitrary settings or mechanical fit. The model includes envelopes for off-the-shelf parts whose supplier-specific dimensions still require measurement. The join-plate drilling and replaceable OLED bezel are fabrication candidates, not production tooling.
