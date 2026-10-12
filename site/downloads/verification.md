# Verification status — 12 October 2026

This file is updated with executed checks before publication. No physical fabrication or testing was performed.

| Area | Status | Evidence / limit |
|---|---|---|
| Local telemetry API | Implemented and automated tests run | Extended Python tests cover API, evidence, analysis and CAD; includes stale backlog and burst-sampling regressions |
| CoolProof simulation | Implemented and tested | Fixed synthetic60-sample scenarios; not a physical thermal model |
| Physical-data evaluator | Implemented and tested with fixtures | Measured-path fixtures are synthetic; no measured trial exists |
| Interactive site | Browser checked | Scenario controls, invalid/valid comparison, export, missing power, mobile layout and JS errors |
| CAD |15 STL exports checked | Closed meshes after reloading; positive volume; intended enclosure dimensions; <=220mm envelope per printable piece |
| Manufacturing fit | NOT VERIFIED | Purchased module dimensions, tolerances, joins, wiring clearance, printer process and assembly inspection remain open |
| Firmware controller | Native C++ tests run | Latch, manual override, startup grace, feedback and timer wrap |
| ESP32 firmware build | PASS, local and GitHub Actions | esp32dev / espressif32 6.10.0; 22,880 bytes RAM and 334,801 bytes flash in hosted build; not flashed to physical hardware |
| Physical electronics | NOT ASSEMBLED / NOT TESTED | No device, wiring, power, sensor calibration or serial hardware validation |
| Optional AI | Disabled by default; adapter/unit tests implemented | No local model installed or actual model output evaluated |
| Research |13 records, all8 dossier references covered | Full-text access varies per source; unavailable text not represented as reviewed |
| Vellore climate | Historical IMD normals transcribed |1981–2010 baseline; current site humidity/wind and1991–2020 detailed extraction remain missing |
| Installed cost vs AC | NOT VERIFIED | Web equipment price is not a Vellore installation quote; shelter costs are allowances |
| Novelty / certification | NOT ESTABLISHED | No exhaustive patent search, human-scale thermal proof, structural approval or medical claim |
| Public deployment | Vercel production and GitHub Pages deployed | https://saaya-verify.vercel.app/ is primary; https://alphasafal.github.io/saaya-verify/ remains a static mirror. Browser checks cover public interaction, not physical telemetry |

CAD limitation: mesh validity does not prove printability at arbitrary settings or mechanical fit. The model includes envelopes for off-the-shelf parts whose supplier-specific dimensions still require measurement. The join-plate drilling and replaceable OLED bezel are fabrication candidates, not production tooling.

## FS-01 full-size revision A

44 valid STEP part definitions and 143 placed instances. Re-imported STEP solids are valid; the final modeled assembly has no solid intersections above 1 mm³ in the generated check. This does not prove manufacturability, joint strength, weather protection, tool access or physical fit. STEP assembly, individual parts, STL meshes, flat-profile DXFs, three dimensioned SVG review sheets, BOM, transparent screening calculations and review/RFQ notes are included.

The approximately 250 kg modeled mass uses idealized material densities and simplified purchased parts. The updated INR94,000–171,000 first-article budget is an unquoted allowance and does not demonstrate the below-installed-AC goal. Structural design, foundations, roof forming/joints, outdoor components and full-size commissioning remain release holds.

Firmware verification evidence: https://github.com/alphasafal/saaya-verify/actions/runs/38157427602 . Local Python 3.13.5; hosted Python 3.11; full-size CAD uses CadQuery 2.6.1 on Python 3.11.
