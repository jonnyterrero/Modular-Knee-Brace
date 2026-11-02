# Electronics — Phase 2 (sensing)

Parts selection, architecture, power budget and schematic for the first sensing build. Firmware comes next and goes in this folder.

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
  [1S LiPo 1000 mAh, PCM]─J4─F1─SW1─VBAT_SW/GND┼──┐    │
  [Thigh IMU LSM6DSOX 0x6A] ──3V3/GND/SDA/SCL┼──┤    │  Hinge enclosure (on Outer Hinge cap)
  [FSR T1] [FSR T2] ──FSR_EN/T1/T2───────────┼──┤    │   ├─ XIAO ESP32-S3 (MCU, BLE, USB-C, charger)
                                             │  └────┼──►├─ AS5600 encoder (on hinge axis)
  Inner Hinge boss: Ø6×2.5 mm diametric      │       │   ├─ Shin IMU LSM6DSOX 0x6B (on board)
  magnet (rotates with the thigh)            │       │   └─ VBAT divider
                                             │       │  [FSR C1] [FSR C2] ── local wiring
```

- **Knee angle** comes straight from the encoder: the magnet turns with the thigh side (Inner Hinge), and the sensor rides on the shin side (Outer Hinge). This measures brace hinge rotation, which can differ from true knee flexion through brace migration, hinge misalignment and soft-tissue movement. Measure that difference during validation.
- **Pressure pads** indicate relative contact (is it worn, how loading shifts between pads, strap changes). FSR 402s are nonlinear with hysteresis, so don't report the readings as absolute pressure or joint load.
- **The shin IMU sits on the hinge board.** The Outer Hinge is rigid with the calf frame, so the board's orientation is the shin's orientation, and one cable run goes away.
- **8 conductors cross the joint:** VBAT_SW, GND, 3V3, SDA, SCL, FSR_EN, FSR_T1, FSR_T2. VBAT_SW is switched and fused at the cell, so it carries no battery voltage with SW1 off. (3V3 can still be live if USB is plugged in.) Route them as one silicone-jacketed bundle with a service loop close to the hinge axis, where flexion changes cable length least.

## Bill of materials (prototype)

| Ref | Part | Qty | Role / notes |
| --- | --- | --- | --- |
| U1 | Seeed XIAO ESP32-S3 (SKU 113991114, or tape-and-reel 100092361 for reflow) | 1 | MCU, BLE 5, native USB-C, onboard 1S LiPo charger (SGM40567). 21 × 17.8 mm. Battery pads are on the underside. |
| U2 | ams AS5600-ASOM, SOIC-8 | 1 | 12-bit magnetic angle sensor, I2C 0x36. Run at 3.3 V (VDD5V tied to VDD3V3). A breakout board is fine for the first bench test. |
| M1 | Diametric NdFeB magnet, Ø6 × 2.5 mm | 1 | Pressed into the Inner Hinge boss tip, centred on the axis. |
| U3, U4 | ST LSM6DSOXTR 6-axis IMU, LGA-14 | 2 | Shin (U3, SA0 = 1 → 0x6B, on the hinge board) and thigh (U4, SA0 = 0 → 0x6A, small thigh board). Breakouts are fine for the first bench test. |
| C1–C7 | 100 nF ×6, 1 µF ×1 | 7 | Decoupling: C1/C2 on U2, C3/C4 on U3, C6/C7 on U4; C5 filters VBAT_SENSE. |
| S1–S4 | Interlink FSR 402 (Ø12.7 mm active) | 4 | Fit/load pads: 2 on the thigh band inner face, 2 on the calf band. |
| R1–R4 | 10 kΩ | 4 | FSR divider legs to GND. |
| R5, R6 | 220 kΩ | 2 | VBAT divider (½ scale), ~10 µA drain. 100 nF from the midpoint to GND. |
| R7, R8 | 2.2 kΩ | 2 | I2C pull-ups (cable to the thigh IMU adds capacitance; 400 kHz). |
| BT1 | 1S LiPo 1000 mAh with protection circuit (PCM), ~50 × 34 × 5 mm (503450 size) | 1 | **Must** have a PCM. ~20 g. |
| J1, J3 | JST-PH 8-pin (B8B-PH-K-S) | 2 | Thigh harness, hinge end (J1) and thigh end (J3): VBAT_RAW, GND, 3V3, SDA, SCL, FSR_EN, FSR_T1, FSR_T2. |
| J2 | JST-PH 3-pin (B3B-PH-K-S) | 1 | Calf FSRs: FSR_EN, FSR_C1, FSR_C2. |
| SW1 | Slide switch in BAT+ | 1 | Hard power-off, at the cell on the thigh side (rev B), so the harness is dead when off. |
| F1 | PTC resettable fuse, 0.5 A hold, 1206 (exact part to be chosen) | 1 | At the cell, ahead of SW1: limits current if the harness is shorted (rev B). |
| J4 | JST-PH 2-pin (B2B-PH-K-S) | 1 | Battery plug on the thigh side, so the cell can be unplugged to charge. |
| — | Single-cell LiPo charger, 4.2 V CC/CV, 500 mA, JST-PH lead (off-brace, not on the schematic) | 1 | Charges the cell off the brace. Check polarity first. |
| R9–R12 | 1.5 kΩ | 4 | FSR series resistors (rev B): cap the ADC input at 2.87 V and limit harness fault current. |
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
| D7 | 44 | Spare. Rev B ties AS5600 DIR to GND (the datasheet says GND or VDD, and a GPIO floats during boot); invert direction in firmware. |
| D8 / A8 | 7 | FSR_C2 (ADC1) |
| D9 | 8 | Spare. The thigh IMU's INT1 is not routed, to keep the harness at 8 conductors; firmware polls it over I2C. |
| D10 | 9 | Shin IMU INT1 |

All analog inputs are on ADC1, which keeps working while BLE is active. ADC2 conflicts with the radio.

## Schematic

- KiCad 10 project: [`kicad/mk-brace-sensing.kicad_pro`](kicad/mk-brace-sensing.kicad_pro), one sheet, rev B. PDF: [`mk-brace-sensing-schematic.pdf`](mk-brace-sensing-schematic.pdf).
- The sheet is split into the hinge board, the thigh side of the harness and the calf FSRs. Parts connect by net label; J1 and J3 are the two ends of the same 8-way harness.
- Project symbols for the XIAO ESP32-S3, AS5600 and LSM6DSOX are in [`kicad/MKBrace.kicad_sym`](kicad/MKBrace.kicad_sym); KiCad's stock library has none of them. See the checklist below for what each one has been verified against.
- The XIAO footprint is Seeed's own `XIAO-ESP32-S3-SMD`, copied into `kicad/MKBrace.pretty/` from [Seeed-Studio/OPL_Kicad_Library](https://github.com/Seeed-Studio/OPL_Kicad_Library) under CC BY-SA 4.0. Its pads 23 and 24 are VBAT and GND, on the module's underside, so they need reflow or hand-soldered wires. The other underside pads stay unconnected.
- BT1, SW1 and the FSRs (S1–S4) have no footprint: they are wired off-board.
- ERC (2026-11-01, `kicad-cli`): 0 errors, 6 warnings, all intended: "bidirectional connected to power output" on the IMUs' SA0 and unused aux-I2C pins (SDx, SCx), tied to 3V3 or GND on purpose as ST specifies.
- The KiCad MCP server's library *search* finds nothing on KiCad 10. It only knows the 8.0/9.0 install paths and cuts URIs at spaces (`C:/Program Files/...`). Placing parts by `Library:Symbol` name still works.

## Pre-fabrication checklist

From the external design review (rev A), updated for rev B.

| Item | Status |
| --- | --- |
| AS5600 3.3 V supply and capacitors | **Verified** against the datasheet: VDD5V and VDD3V3 tied together with 100 nF. C2 (1 µF) is extra and harmless; the 10 µF is only for one-time programming, which this design doesn't use. |
| AS5600 DIR, PGO, OUT | **Verified**: DIR tied to GND (it must sit at GND or VDD); PGO has an internal pull-up and OUT is unused. |
| I2C addresses, CS | **Correct by design**: 0x36, 0x6A, 0x6B, CS high. Confirm with an I2C scan at bring-up. |
| LSM6DSOX symbol and footprint vs. purchased part | **Partly verified.** Pin numbers and unused-pin handling match ST's AN5192 for the sister LSM6DSO. **Open:** check against ST's LSM6DSOX datasheet (DS12814); st.com blocks scripted downloads. |
| XIAO pins 1–14 | **Verified** against Seeed's KiCad symbol and footprint. D0–D3 and D8 are ADC1-capable per Seeed's pin map. |
| XIAO battery pads | **Verified and corrected in rev B** to pads 23 (VBAT) and 24 (GND). |
| Switch and charging behaviour | **Decided:** the cell charges off the brace, unplugged at J4. **Open:** battery PCM ratings are unknown until a cell is chosen. |
| Connector pin 1, polarization, strain relief | **Partly done:** JST-PH is keyed. Pin-1 marking is a layout item, strain relief a mechanical one. |
| KiCad ERC | **Done:** 0 errors, 6 intended warnings. |
| FSR outputs at min and max resistance | **Calculated:** 0 V open, 2.82 V at 200 Ω (2.87 V at 0 Ω), inside the 0–2.9 V range at 12 dB. Bench-check with real sensors. |
| FSR_EN drive | **Verified:** 1.15 mA at most against a 20 mA default GPIO drive. |
| ADC range and settling | **Verified on paper:** VBAT_SENSE tops out at 2.1 V. The source impedance is 110 kΩ with 100 nF, about 11 ms time constant, so allow settling after power-up. Use ADC calibration. |
| I2C bus with the real harness | **Open (bench):** start at 100 kHz, check rise times with a scope, then raise the speed. Pull-ups draw 1.5 mA per line when low. |
| AS5600 magnet check | **Open (bench):** read STATUS (0x0B) MD/ML/MH and AGC to confirm field strength and gap. Axis must be within 0.25 mm of the package centre. |
| Measure idle, sampling, BLE and peak current | **Open (bench):** the 35 mA MCU figure is still an estimate. |

The 3.5 V firmware cutoff is a low-battery warning, not protection; the cell's PCM is the hardware protection. Voltage under load reads lower than resting voltage.

## Charging (decided 2026-11-01)

**Unplug the cell at J4 and charge it off the brace** with a separate charger. The XIAO's own charger would take roughly 10–20+ hours on a 1000 mAh cell, and this way the brace can't be charging while worn.

- **Charger:** single-cell LiPo, CC/CV to 4.2 V, 500 mA (0.5C for 1000 mAh, about 2–2.5 hours). Don't use a charger set above 1C (1 A).
- **Polarity:** JST-PH battery wiring isn't standardized between vendors. Check the cell's polarity with a meter against J4 and against the charger before the first connection. A reversed cell can destroy the electronics or the cell.
- **USB during firmware work:** the XIAO's charger will still top up the cell slowly if USB is plugged in with SW1 on. That's fine on the bench, but turn SW1 off or unplug J4 if you don't want that. Never do it while worn.

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

Charging: the XIAO's onboard charger is a small linear charger. Seeed's wiki table appears to list 50 mA for this board and 100 mA for the Plus, and resellers disagree. Either way it's too slow for daily use, so the cell charges off the brace; see *Charging* above.

## Mechanical integration (input to the Fusion mount design)

Measured from the Fusion model (2026-10-20):

- The hinge axis is lateral (X). Each stack is about 0.66 in wide; the Outer Hinge's outer face is at |X| ≈ 3.02 in, centred on the knee axis (Y = −6.0, Z = −0.5 in).
- Updated 2026-11-01 for the printable hinge: the Inner Hinge's hollow snap post (Ø0.36 in bore) comes up through an open bore in the Outer Hinge's cap, so no thin-floor pocket is needed. A plug holding the Ø6 mm magnet can press into the post, which would also lock the snap fingers. The sensor mounts over the bore on the cap's outer face.
- The AS5600 needs a ~0.5–3 mm magnet-to-die gap, with the magnet axis within 0.25 mm of the package centre. A printed mount may not hold 0.25 mm, so check it with the sensor's magnet-status bits.
- The hinge enclosure (XIAO + AS5600 + shin IMU, about 30 × 25 × 12 mm inside) clips over the Outer Hinge cap on the **lateral** side only, so nothing faces the other leg. Keep the USB-C port reachable.
- Battery holder on the thigh frame: the band is 2.00 in tall and carries a 1.50 in strap recess. A 34 × 50 mm cell must not block the strap path, so check the end block or upper connector area before committing. On the band's outside (R ≈ 3.4 in) a 50 mm flat cell leaves ~3.6 mm sagitta, so the holder needs a curved base.

## Safety (not a medical device)

- Protected (PCM) cell only, fully enclosed. No exposed cell or bare contacts against skin.
- **Do not charge while worn.** Charge with the battery switch on and the brace off the leg.
- Strain-relieve the battery leads at both ends. Abrasion at the hinge service loop is the likeliest failure.
- E-stim stays out until it is a separate, isolated, independently reviewed module.
