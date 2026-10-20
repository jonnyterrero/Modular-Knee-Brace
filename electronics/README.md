# Electronics — Phase 2 (sensing)

Parts selection, architecture and power budget for the first sensing build. Schematics (KiCad) and firmware come next and go in this folder.

## Scope decisions (2026-10-20)

| Decision | Choice |
| --- | --- |
| E-stim | **Out of scope.** Sensing only. Leave room for a future, separately powered and isolated module; nothing patient-connected in this build. |
| Runtime | **~12 h** per charge (full day) with BLE streaming |
| Placement | **Split:** MCU + encoder + shin IMU in one enclosure at the lateral hinge; LiPo on the thigh frame |
| Prototype material | PETG |

## Architecture

```
            THIGH SEGMENT                    │ joint │            SHIN SEGMENT
                                             │       │
  [1S LiPo 1000 mAh, PCM] ──BAT+/GND─────────┼──┐    │
  [Thigh IMU LSM6DSOX 0x6A] ──3V3/GND/SDA/SCL┼──┤    │  Hinge enclosure (on Outer Hinge cap)
  [FSR T1] [FSR T2] ──FSR_EN/T1/T2───────────┼──┤    │   ├─ XIAO ESP32-S3 (MCU, BLE, USB-C, charger)
                                             │  └────┼──►├─ AS5600 encoder (on hinge axis)
  Inner Hinge boss: Ø6×2.5 mm diametric      │       │   ├─ Shin IMU LSM6DSOX 0x6B (on board)
  magnet (rotates with the thigh)            │       │   └─ VBAT divider
                                             │       │  [FSR C1] [FSR C2] ── local wiring
```

- **Knee angle** comes straight from the encoder: the magnet turns with the thigh side (Inner Hinge), and the sensor rides on the shin side (Outer Hinge).
- **The shin IMU sits on the hinge board.** The Outer Hinge is rigid with the calf frame, so the board's orientation is the shin's orientation, and one cable run goes away.
- **8 conductors cross the joint:** BAT+, GND, 3V3, SDA, SCL, FSR_EN, FSR_T1, FSR_T2. Route them as one silicone-jacketed bundle with a service loop close to the hinge axis, where flexion changes cable length least.

## Bill of materials (prototype)

| Ref | Part | Qty | Role / notes |
| --- | --- | --- | --- |
| U1 | Seeed XIAO ESP32-S3 | 1 | MCU, BLE 5, native USB-C, onboard 1S LiPo charger. 21 × 17.8 mm. |
| U2 | ams AS5600 breakout (or bare SOIC-8 on the hinge board) | 1 | 12-bit magnetic angle sensor, I2C 0x36. Run at 3.3 V (VDD5V tied to VDD3V3). |
| M1 | Diametric NdFeB magnet, Ø6 × 2.5 mm | 1 | Pressed into the Inner Hinge boss tip, centred on the axis. |
| U3, U4 | ST LSM6DSOX 6-axis IMU breakout | 2 | Thigh (SA0 = 0 → 0x6A, remote) and shin (SA0 = 1 → 0x6B, on the hinge board). |
| S1–S4 | Interlink FSR 402 (Ø12.7 mm active) | 4 | Fit/load pads: 2 on the thigh band inner face, 2 on the calf band. |
| R1–R4 | 10 kΩ | 4 | FSR divider legs to GND. |
| R5, R6 | 220 kΩ | 2 | VBAT divider (½ scale), ~10 µA drain. 100 nF from the midpoint to GND. |
| R7, R8 | 2.2 kΩ | 2 | I2C pull-ups (cable to the thigh IMU adds capacitance; 400 kHz). |
| BT1 | 1S LiPo 1000 mAh with protection circuit (PCM), ~50 × 34 × 5 mm (503450 size) | 1 | **Must** have a PCM. ~20 g. |
| J1 | JST-PH 2-pin | 1 | Battery disconnect at the hinge enclosure. |
| SW1 | Slide switch in BAT+ | 1 | Hard power-off for storage and transport. |
| — | 8-core silicone ribbon or 28 AWG silicone wire | ~0.5 m | Thigh-to-hinge bundle. |

## Pin map (XIAO ESP32-S3)

| XIAO pin | GPIO | Signal |
| --- | --- | --- |
| D0 / A0 | 1 | FSR_T1 (ADC1) |
| D1 / A1 | 2 | FSR_T2 (ADC1) |
| D2 / A2 | 3 | VBAT sense (ADC1). The divider holds the GPIO3 strap pin at a defined level at boot. |
| D3 / A3 | 4 | FSR_C1 (ADC1) |
| D4 | 5 | I2C SDA |
| D5 | 6 | I2C SCL |
| D6 | 43 | FSR_EN: powers the FSR dividers only while sampling |
| D7 | 44 | AS5600 DIR (or spare) |
| D8 / A8 | 7 | FSR_C2 (ADC1) |
| D9 | 8 | Thigh IMU INT1 |
| D10 | 9 | Shin IMU INT1 |

All analog inputs are on ADC1, which keeps working while BLE is active. ADC2 conflicts with the radio.

## Power budget

Sample plan: IMUs at 104 Hz, encoder at 100 Hz, FSRs at 20 Hz, BLE notifications at ~50 Hz.

| Load | Mode | Current (mA) | Source |
| --- | --- | --- | --- |
| ESP32-S3 + BLE | 80 MHz, auto light-sleep between samples, connected and notifying | 35 | **Estimate.** Measure on the bench (PPK2 or USB meter) before trusting it. |
| AS5600 | NOM power mode | 6.5 | Datasheet typ. LPM1 (5 ms polling) is 3.4 mA if 200 Hz updates are enough. |
| LSM6DSOX ×2 | Accel + gyro, high-performance | 1.1 | Datasheet typ, 0.55 mA each |
| FSR ×4 | Gated by FSR_EN at ~10 % duty | 0.15 | 4 × 0.33 mA worst case × 0.1 |
| VBAT divider + regulator Iq + misc | — | 0.5 | Allowance |
| **Total (design value)** | | **≈ 43** | |

Sizing:

- 43 mA × 12 h = 520 mAh delivered
- ÷ 0.8 usable (firmware cutoff at 3.5 V for 3.3 V regulator headroom, plus ageing) = 650 mAh
- × 1.3 margin on the MCU estimate = **~850 mAh → 1000 mAh cell**
- Expected runtime at the design load: 1000 × 0.8 / 43 ≈ **18 h**, or about 12 h even if the MCU draws 60 mA.

Charging: the XIAO's onboard charger is a low-current linear charger (check the exact rate against the Seeed schematic), so a 1000 mAh cell will take many hours. Plan on overnight charging, or add a dedicated 500 mA charger on the hinge board later.

## Mechanical integration (input to the Fusion mount design)

Measured from the Fusion model (2026-10-20):

- The hinge axis is lateral (X). Each stack is about 0.66 in wide; the Outer Hinge's outer face is at |X| ≈ 3.02 in, centred on the knee axis (Y = −6.0, Z = −0.5 in).
- The Inner Hinge carries a solid central boss on the axis; that is where the magnet goes. The Outer Hinge closes over it with a solid Ø2.00 in cap about **0.125 in (3.2 mm)** thick.
- The AS5600 needs a ~0.5–3 mm magnet-to-die gap. 3.2 mm of PETG plus clearance is too far, so the mount needs a **Ø0.40 in pocket in the outside of the cap leaving ≤ 0.03 in (0.8 mm) floor**, with the sensor IC centred over it. The rotation stop and snap fit stay as they are.
- The hinge enclosure (XIAO + AS5600 + shin IMU, about 30 × 25 × 12 mm inside) clips over the Outer Hinge cap on the **lateral** side only, so nothing faces the other leg. Keep the USB-C port reachable.
- Battery holder on the thigh frame: the band is 2.00 in tall and carries a 1.50 in strap recess. A 34 × 50 mm cell must not block the strap path, so check the end block or upper connector area before committing. On the band's outside (R ≈ 3.4 in) a 50 mm flat cell leaves ~3.6 mm sagitta, so the holder needs a curved base.

## Safety (not a medical device)

- Protected (PCM) cell only, fully enclosed. No exposed cell or bare contacts against skin.
- **Do not charge while worn.** Charge with the battery switch on and the brace off the leg.
- Strain-relieve the battery leads at both ends. Abrasion at the hinge service loop is the likeliest failure.
- E-stim stays out until it is a separate, isolated, independently reviewed module.
