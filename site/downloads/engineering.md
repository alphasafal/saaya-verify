# SAAYA v2 engineering package — fabrication candidate

## What is real, and what is not

The repository contains executable firmware, a local telemetry API, source-labelled experiment logic, parametric CSG sources and exported STL meshes. These are engineering artifacts, not evidence of physical assembly. No component has been purchased, no shell has been printed, and no shelter temperature has been measured in this project. Do not describe the prototype as hardware-tested or manufacturing-released.

The original 250 × 200 mm concept remains in `archive/lab-v1`. V2 expands the bench assembly to 300 × 240 mm and the enclosure to 120 × 90 × 45 mm to provide cable and service space. Lower roof bottom Z=194, thickness3; upper roof bottom Z=213; clear air gap16mm. All coordinates are millimetres.

## Selected electrical architecture

Use a classic ESP32-WROOM development board compatible with PlatformIO `esp32dev`, not ESP32-S2/S3/C3. Mechanical reference: Espressif DevKitC V4, nominal48.26×27.94mm PCB outline. The supplier BOM's generic board is not guaranteed identical; measure it before printing. Mount with an insulated adjustable carrier, never assume undocumented PCB mounting holes.

For first bench operation, power the ESP32 via USB from the recording laptop. Power only the fan branch from a commercially enclosed regulated12V adapter. Connect signal grounds together. Do not feed a development board's5V pin while USB is connected. A protected5V conversion option is reserved for later standalone use and is not necessary for this USB bench circuit.

### Pin and connection schedule

| ESP32 pin | Connection | Conditioning / notes |
|---|---|---|
| 3V3 / GND | SHT31, OLED, INA219 logic supply | Check exact carrier voltage requirements; no5V I2C pull-ups |
| GPIO21 | I2C SDA | Outdoor SHT31 0x44; indoor SHT31 0x45 via ADR high; OLED0x3C; INA2190x40 |
| GPIO22 | I2C SCL | Short bench bus; check total parallel pull-up resistance |
| GPIO25 | 4.7k resistor -> Q1 base | Q1=2N3904 or equivalent verified NPN, emitter GND, collector fan PWM.10k base-emitter pull-down. Firmware inverts output for this stage |
| GPIO34 | Fan tach | External10k pull-up to3V3; pin is input-only with no internal pull-up. Verify open-collector tach output; never feed12V |
| GPIO35 | Water float | External10k to3V3; dry-contact switch toGND means available. Open circuit means low/check, including broken wire |
| GPIO32 | Mode button | Active-low toGND; internal pull-up; toggles off/manual70% |
| GPIO33 | Help button | Active-low; latches request in NVS across restart |
| GPIO27 | Acknowledge button | Active-low; deliberate local clear. Help takes priority if both pressed |
| GPIO26 | LED via330ohm | Indicator; LED cathode toGND |
| GPIO14 | Q2 buzzer stage | 4.7k base resistor,10k base-ground; NPN low-side driver for rated low-voltage active buzzer. Flyback diode for inductive buzzer, cathode at positive supply |
| GPIO4 | DS18B20 data |4.7k pull-up to3V3; powered three-wire mode; roof-contact probe |

### Fan branch and current measurement

12V adapter positive -> inline250mA fuse -> switch -> INA219 VIN+ -> INA219 VIN- -> fan12V positive. Adapter negative, fan GND, ESP32 GND and INA219 GND share reference. INA219 VCC is3V3, not12V. Check chosen breakout shunt/current/voltage rating before connecting. Sensor and controller power are excluded from the fan-branch power reading; `config_id=bench-v2-fan-branch-power` records this boundary. Total-system energy requires an additional meter or a relocated correctly rated instrument.

Reference fan: Noctua NF-A4x10 PWM12V, four-wire. Manufacturer lists40×40mm footprint,32×32mm mounting centres,11mm bare depth in extended specifications and12mm with pads; use12mm clearance. Rated max0.48W; this is a datasheet limit, not measured consumption. Pin1 black GND, pin2 yellow12V, pin3 green tach, pin4 blue PWM. Verify harness before energising; do not substitute a two-wire fan. The fan has integrated motor drive; the external NPN controls the PWM signal rather than switching the motor from a GPIO.

Source: https://www.noctua.at/en/products/nf-a4x10-pwm/specifications

### Control and acquisition

Firmware defaults to off/manual only (`SAAYA_BENCH_AUTO=0`). Enabling the compile-time bench-auto option adds a demonstration band (on at ≥32 °C, held until <31 °C to prevent chatter), not an occupational threshold; only use on an unoccupied bench. Automatic mode is disabled by invalid indoor/outdoor readings. Manual operation remains available independently. Help stays latched; neither a network fault nor water state clears it. A five-second watchdog restarts a stalled task; the help latch is restored from NVS.

Sensors sample approximately once per second. Two fan tach pulses per revolution are assumed for the reference fan; verify with manufacturer information and a tachometer before relying on RPM. A three-second startup grace precedes feedback faults. The roof probe uses nonblocking conversions. Missing endpoints remain null. Readings are uncalibrated until the physical calibration protocol is performed.

The serial bridge authenticates locally with `SAAYA_DEVICE_TOKEN`; it never labels simulation as measured. Physical firmware does not invent a paired reference, air velocity or synchronized clock. Such records can be monitored but cannot pass CoolProof comparison until a separate measured reference and calibration/alignment metadata exist.

## Mechanical assembly

Use `cad/parameters.json` and `cad/generate.py` as the authoritative v2 source. Manifold CSG exports closed positive-volume STL meshes. Editable legacy SCAD remains archived; v2 exports do not depend on an unverified OpenSCAD executable.

| Part | Quantity | Assembly note |
|---|---:|---|
| Base quarter150×120×4 |4| Four tiles form300×240; align and clamp before joining |
| Roof quarter160×130×3 |8| Four per layer; white upper surface; keep gap open |
| Pillar12×12×190 |4| Bottom and top pilot bores; no structural certification |
| Roof spacer,16 high |4| M3 clearance; supports upper layer over lower roof |
| Enclosure base / lid |1 each| Shell42.5 high + lid2.5; 2.5mm walls; removable lid |
| Universal carrier |1| M3 floor attachments; insulated standoffs and ties secure electronics |
| OLED bezel |1| Nominal window24×14; measure actual module before printing |
| Fan angle bracket |1| 32mm bolt grid; slotted base attachment |
| Fan guards |2| Front and rear; do not describe as certified finger protection |
| Fan guard spacers |8|4mm nominal; check blades and screw lengths |
| Sensor shield cage |2| Passive slotted cover; reflective finish; validate radiation bias |
| Jaali coupons,8/12 pitch |1 each| Swap during unoccupied airflow tests; clip support needs fitting |
| Join plates |As required| Drill-to-fit attachment method; hole match not fully jigged |

Starting fasteners: M3 machine screws/nuts/washers for panels, M3 self-tapping/plastic-compatible fasteners for documented pilot holes after coupon test, appropriately long fan through-bolts with nuts. Do not force metal threads into an undersized print. Roof-stack screws need3+16+3mm stack plus engagement; select exact lengths after measuring print thickness. No screw may touch fan blades or circuit traces.

Print small fit coupons first. Start with PETG,0.2mm layers,3 perimeters and4 top/bottom layers; these are starting process settings, not validated strength or dimensional tolerances. Nominal0.3mm allowance needs adjustment to printer/material. The large structure is a miniature lab fixture only. Sun-heated roof temperatures can exceed plastic service limits: log surface temperature and stop before material softens. Full-scale structural parts require suitable metal/material selection and qualified wind/anchorage design.

Wet vessel stays on the opposite side of the base from the dry electronics. Use separate non-potable demonstration water when inserting an uncertified float. Provide drip loops and strain relief. Cable-gland apertures are nominal Ø8 and must match purchased glands. No IP rating or potable certification is claimed.

## Manufacturing release gates still open

- Receive and dimension-check exact ESP32, OLED, driver, float and connectors.
- Print fit coupons; check carrier, bezel, glands, screw engagement and lid closure with wiring installed.
- Complete join-plate drilling jig and shelter mounting details; validate frame rigidity.
- Measure fan-guard clearance, sensor-shield bias, noise, vibration and electrical current.
- Complete thermal, rain, UV, cleaning and ingress assessments appropriate to deployment.
- Full-size wind loads, foundations, corrosion, access and electrical review require a specific site.

These gates intentionally prevent the phrase “manufacturing-ready” from hiding missing physical work.
