# Physical bench and thermal protocol

## Preconditions

No human exposure testing in this phase. Use protected low-voltage supplies, guarded fans, separate wet/dry areas, and a competent electrical inspection before energising. Verify polarity with power disconnected. Use a current-limited supply for initial fan tests. No purchase, assembly or measured result is implied by this protocol.

## Bench sequence

1. Compare component markings and pinouts with the engineering schedule. Verify fan four-wire variant and INA219 shunt limits.
2. Inspect printed clearances; remove burrs and trapped cables. Confirm guards cannot contact the rotor.
3. Power controller over USB with fan adapter disconnected. Check help and acknowledgement, including reboot while help is latched.
4. Confirm the two sensor addresses and roof probe. Disconnect/reconnect each; output must become unavailable/invalid and recover without clearing help.
5. Energise fan branch, command manual mode and compare observed rotation with tach reading. Simulate feedback disconnection instead of touching/stalling a spinning fan. Verify grace period then fault indication.
6. Open water float circuit; verify low/check indication. Check disconnected wire behaviour.
7. Start local API and serial bridge. Verify MEASURED tags, UNVERIFIED calibration ID, null air-speed/reference fields and timestamps. Interrupt API: local controls must continue. The bridge reports dropped frames; no hidden gap filling.
8. Confirm input power against a reference meter. The INA219 here measures only the fan branch, not total system energy. Record shunt, range, offset and uncertainty.

## Calibration and paired experiment

Create a calibration sheet with instrument model/serial, method, reference instrument, date, offsets, uncertainty and operator. Co-locate both air sensors in equivalent shaded airflow for at least20 minutes and across at least two stable conditions; do not assume co-location establishes traceable absolute calibration. A calibrated external air-speed instrument is required for fan-benefit endpoints. WBGT cannot be reconstructed from these sensors alone.

Build two matched unoccupied rigs at equal heights and comparable exposure. Log orientation, obstructions, roof material, distances, sun/wind changes, sensor positions and shade. Randomize which rig receives the intervention; swap positions between runs. Use a minimum10-minute settling period, then a10-minute observation window sampled at1Hz. Predeclare an endpoint, beneficial direction, synchronization tolerance, minimum90% paired coverage and exclusion rules before starting. Repeat at least three independent runs on each of three separate days; describe uncertainty with the actual independent units, not600 consecutive readings treated as600 experiments.

A pair must have matching physical times within1second, valid instrument state and a recorded reference configuration. Mark cloud/wind shifts and other confounding changes. The public60-second replay is a separate software demonstration and does not meet this physical protocol.

## Experiment matrix

| Comparison | Endpoint | Limitation |
|---|---|---|
| Single vs ventilated double roof | Roof surface and air temperature; radiant instrument if available | A contact probe is not mean radiant temperature |
| Fixed vs adaptive fan | Seated air speed and electrical Wh | Same air-speed service must be defined before claiming energy savings |
| Jaali8 vs12 pitch vs no screen | Air-speed distribution, shade and fan power | Avoid selecting a screen from appearance alone |
| Clean vs dusty roof | Surface response under matched conditions | Document contamination method and cleaning |
| Dry vs humid weather | Repeat identical geometry/configurations | Distinct weather runs cannot be pooled without accounting for conditions |

Evaporative experiments are excluded from core tests. If later added, use a separate non-potable reservoir, measured water consumption, maintenance/hygiene protocol and independent justification from wet-bulb depression; humidity alone is not a universal threshold for suitability.

## Data and reporting

The public/local demo evaluator requires48/60 contiguous samples for its fixed1Hz replay. For real10-minute trials, use `scripts/evaluate_physical.py` with a predeclared metadata file and600 paired observations. It produces descriptive differences, coverage, exclusions and energy completeness. Missing evidence blocks interpretation. Null means unavailable, not zero. Field uncertainty and safety certification are never synthesized.

Retain raw CSV/JSON, calibration metadata, configuration revision and photographs. Report deviations and failed runs, not just successful ones. Archive before/after data instead of overwriting. Release measured results only after reviewing the actual physical records.

The evaluator rejects more than one valid observation in a one-second bin. Keep the declared 1 Hz cadence; do not append high-frequency bursts to a trial. Values outside the 600-second observation window are excluded. Energy is integrated separately per device/session and excludes sequence discontinuities.

USB bridge freshness: the bridge discards pending serial bytes before awaiting a new frame. The API retains the earliest inferred host origin per boot session to detect transport backlog. This is not calibrated cross-instrument clock alignment; paired physical trials still require independently aligned reference timestamps. Host wall-clock changes can affect freshness estimates.
