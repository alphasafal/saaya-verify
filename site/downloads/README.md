# SAAYA VERIFY

**Shade with evidence.** A Vellore-oriented tabletop shelter research prototype with an interactive public demo, local ESP32 telemetry, fault-aware comparison records and editable fabrication candidates.

**Live demo:** https://saaya-verify.vercel.app/

**Full-size CAD review:** https://saaya-verify.vercel.app/fullsize.html

**Secondary static mirror:** https://alphasafal.github.io/saaya-verify/

**Status:** software demonstrator and engineering package. No physical build, calibrated measurements, manufacturing release or safety certification is claimed. See [verification](docs/verification.md).

**Teacher presentation:** https://saaya-verify.vercel.app/explain.html — interactive IoT diagram, labelled CAD, placement rationales, bench pin map and current engineering gaps.

**Operational CAD:** open [the worker / fan / sensor view](https://saaya-verify.vercel.app/fullsize-model.html) and change synthetic parameters. [Layer scope and control rules](docs/operational-cad.md).

**New FS-02:** [five-person rest pavilion](https://saaya-verify.vercel.app/rest-pavilion.html), a separate concept with five reclining cots and independently directed fan locations. [Design and physiology boundaries](docs/FS02-design-review.md).

## Explore

[Two-minute presentation and workshop handoff](docs/demo-guide.md).

- Interactive model, seven reproducible scenarios, evidence exports, research, costs and drawbacks: `site/`.
- All eight dossier references plus traditional-design and climate sources: [research review](research/REVIEW.md).
- Full-size STEP assembly, editable source, DXFs, drawings and checks: [FS-01](cad/fullsize/) / [review and RFQ](docs/manufacturing/REVIEW.md).
- Current sensors, control and telemetry block diagram: [IoT architecture](docs/architecture-v2.svg).
- Electrical pin map, motor conditioning, parts and manufacturing gates: [engineering](docs/engineering.md).
- Parametric CSG, printable STL parts and dimensioned enclosure drawing: [CAD](cad/exports/).
- Physical experiment design and calibration: [protocol](docs/physical-protocol.md).
- Repairability, resource accounting and novelty limits: [sustainability](docs/sustainability.md).
- Original three-sheet lab pack and concept model: [preserved archive](archive/lab-v1/).

## Quick start — local bench

Python3.11+ and Node20+ are supported targets; tested versions are recorded in verification. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_site.py
python -m uvicorn api.main:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765 . API documentation is at `/docs`. The checked-in model bundle and exported parts make rebuilding the CAD/3D bundle unnecessary for a basic run.

### Real USB telemetry

Set the same private `SAAYA_DEVICE_TOKEN` environment variable in the API and bridge terminals. Generate your own value; never commit it. Restart the API after setting the token. Flash the firmware only after checking the wiring notes and chosen board. Then:

```sh
python scripts/serial_bridge.py /dev/ttyUSB0
```

Replace the port with the actual USB serial device (`/dev/cu...` on macOS). Use the local site's **Check local device** button. Measurement credentials stay on the laptop; the public site cannot ingest or control devices. Serial bridge loss drops and reports frames; missing intervals are never silently filled.

The physical firmware emits unverified calibration, null reference/air-speed and unsynchronized-clock fields. These are honest measured records but are not sufficient for comparative cooling evidence. Follow the physical protocol and use paired instrument records before invoking the physical evaluator.

## Reproducible demonstration

```sh
curl -X POST http://127.0.0.1:8765/sim/scenario -H 'Content-Type: application/json' -d '{"name":"fan_failure","seed":1}'
```

Use its `run_id` to predeclare `/experiments` with endpoint `air_speed` or `roof_temp`, advance `/sim/step`, finish `/experiments/{id}/finish`, then retrieve `/experiments/{id}/export?format=json` or `csv`. An experiment must be declared before samples are collected. Finished records are immutable snapshots; a scenario reset creates a new run.

Scenarios: `normal`, `humid`, `fan_failure`, `sensor_failure`, `low_water`, `no_power`, `reference_mismatch`. Their60 samples are illustrative synthetic values, not a Vellore thermal simulation. Public replay runs accelerated and uses the same generated records as the Python evaluator.

## Optional read-only AI

AI is not required for controls or evidence evaluation. To use a local Ollama server, install a model yourself and set `SAAYA_AI_MODEL` to its name before starting the API. The server is fixed to loopback port11434; it does not forward records to an external model provider. POST `/experiments/{id}/explain` after finishing a run. The response is explicitly an **unverified model explanation**, not evidence; it cannot change records or actuators. Actual model generation is unverified until a model is installed and exercised. No model or API credits are bundled.

## Engineering builds and tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
c++ -std=c++11 tests/controller_test.cpp -o /tmp/saaya-controller-test
/tmp/saaya-controller-test
pio run -d firmware
python cad/generate.py
npm ci
npm run build:model
python scripts/build_site.py
npx playwright install chromium
npm run test:browser
```

Start the local API before the browser check. `CHROME_CHANNEL=chrome` uses an installed Chrome instead. `TEST_URL` can target the deployed public site. `requirements-lock.txt` records the tested development environment; it is not required for the basic API.

For measured600-second paired trials:

```sh
python scripts/evaluate_physical.py paired-records.json declared-metadata.json --output physical-result.json
```

The metadata template is in `experiments/`. It deliberately contains unverified fields and cannot produce valid evidence unchanged. Software fixtures in tests are synthetic even when testing the MEASURED path; they are not physical results.

## Deployment

GitHub Actions builds and tests the static site, then deploys `site/` to GitHub Pages on pushes to `main`. Pages hosts static files only. The SQLite database and device API remain local and are excluded from publication. No customer accounts, paid services, hardware purchases or external telemetry are provisioned.

## Cost boundary

Current numbers are supplier web observations plus explicitly labelled allowances; see `research/costs.json`. Full-size costs are conceptual and span the AC equipment price. A dated Vellore installed quote for both designs is missing. SAAYA has not met the “below installed AC cost” goal, and an open shelter does not offer equivalent cooling/dehumidification.

## Reuse and attribution

Original project source is public for inspection. No additional licence grant is implied; third-party libraries retain their respective licences. Literature is linked and summarized, not redistributed as full paper PDFs. `site/model.bundle.js` includes third-party notices generated by the bundler. Do not copy a safety or performance claim from a simulation screenshot.

## Full-size CAD review build

This is a review/quotation package, not a manufacturing or construction release. The full-size model is separate from the tabletop firmware configuration. Purchased parts, outdoor qualification, connections, foundations and first-article tests remain release gates.

```sh
python3.11 -m venv .cadvenv
.cadvenv/bin/python -m pip install -r cad/fullsize/requirements.txt
.cadvenv/bin/python cad/fullsize/build.py
.cadvenv/bin/python cad/fullsize/validate.py
.cadvenv/bin/python cad/fullsize/feasibility.py
.cadvenv/bin/python cad/fullsize/drawings.py
.cadvenv/bin/python cad/fullsize/cost.py
python scripts/build_fullsize_assets.py
npm run build:fullsize
```

`cost.py` updates the full-size allowance table from current model quantities; original concept allowances are retained as superseded. Zero solid intersections does not establish joint strength, missing supports, manufacturing tolerances or tool access.

## Vercel production publishing

The Vercel project is `alphasafals-projects/saaya-verify`. Deploy **only `site/`** so the local Python API/database are not deployed as cloud functions:

```sh
python scripts/build_site.py
python scripts/build_fullsize_assets.py
npm run build:model
npm run build:fullsize
vercel link --yes --project saaya-verify --scope alphasafals-projects --cwd site
vercel project inspect saaya-verify --scope alphasafals-projects --cwd site
vercel deploy --prod --yes --scope alphasafals-projects --cwd site
```

Vercel credentials and project-link state are ignored by Git. This release uses an explicit CLI deployment; an automatic Git-to-Vercel integration is not claimed. GitHub Actions continues validating and publishing the secondary Pages mirror.
