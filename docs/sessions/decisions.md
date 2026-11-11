# Decisions

From the 2026-10-20 to 2026-11-02 session. "User" means the project owner chose it; "Claude" means it was a design call made while implementing, open to change.

## Scope and electronics architecture

| Decision | By | Why |
| --- | --- | --- |
| Sensing only, no e-stim | User | Anything patient-connected is safety-critical. E-stim stays a future, separate, isolated module. |
| Full build stays sensing only: two PCBs, hinge and thigh | User | Keeps the power design simple. |
| About 12 h per charge | User | A full day of use. |
| MCU, encoder and shin IMU at the lateral hinge; battery on the thigh frame | User | Least mass at the joint. The board rides on the shin side, so it doubles as the shin IMU mount. |
| AS5600 magnet in the Inner Hinge snap post, sensor on the Outer Hinge cap | Claude | Measures thigh-to-shin rotation directly. This is brace rotation, not anatomical knee flexion; check the difference in validation. |
| 8-wire harness across the joint; thigh IMU interrupt not routed | Claude | Keeps the harness at 8 conductors. Firmware polls the thigh IMU. |
| SW1 and a PTC fuse at the cell | User (of three options) | The harness carries no battery voltage when off, and a short in it is current-limited. |
| AS5600 DIR tied to GND | Claude | Datasheet: DIR must sit at GND or VDD, and a GPIO floats during boot. Invert in firmware if needed. |
| 1.5 kΩ series resistor on each FSR line | Claude | Keeps the ADC input at or below 2.87 V, inside the 0–2.9 V range at 12 dB, and limits harness fault current. |
| FSRs give relative contact only | Claude, from the review | FSR 402s are nonlinear with hysteresis; don't report absolute pressure. |
| Charge the cell off the brace, unplugged at J4 | User | The XIAO's charger takes 10–20+ h, and this can't happen while worn. |
| Cell: Adafruit 258, 1200 mAh, 62 × 34 × 5 mm | Claude | Documented, and polarity-matched to the charger. About 22 h at the design load. |
| Charger: Adafruit 4410, jumpered for 500 mA | Claude | Same vendor as the cell. 500 mA is Adafruit's stated maximum for it. |
| Fuse: Littelfuse 1206L050YR; switch: C&K PCM12SMTR | Claude | The fuse trips below the cell's 1.2 A limit. The switch fits the existing footprint. |
| Firmware limits BLE TX to 9 dBm or less | Claude, forced by the parts | 21 dBm peaks at 335 mA, over the switch's 300 mA rating. |

## Mechanical and printing

| Decision | By | Why |
| --- | --- | --- |
| PETG for the first print | User | Tougher than PLA for a worn prototype. |
| All-printed relieved snap hinge for now | User | Printing is a prototype stage; real parts come later. |
| Connectors flat and still modular | User | Parts stay swappable. |
| Frames wrap 180° (half-angle 90°) | Claude | Squares the sockets on the knee axis and removes the twist. **Check fit on the wearer:** the opening now equals the bore. |
| Socket flares removed (`socket_flare_depth = 0`) | Claude | Flat shoulder for the flat connectors. |
| Hinge running clearance 0.016 in (0.41 mm); snap interference 0.030 in | Claude | FDM tolerance. Estimated finger strain about 1.7%, against about 11% for the original snap. These are parameters to tune after a test print. |

## Process

- Commit finished work to `main` and push; update `HANDOFF.md` and add a `docs/progress/` note each session (this repo's `AGENTS.md`).
- Save Fusion work in the *Knee brace Design* project only. Save to Fusion only when the user says to.
