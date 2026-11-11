# Open items (as of 2026-11-11)

## Waiting on the user

- [ ] **Printer details:** model and layer cap. The frames are 381 layers at 0.2 mm (254 at 0.3), by far the tallest parts. If they're over the cap, shorten `block_drop` / `frame_height`. The Top Frame's footprint is 178 × 111 mm.
- [ ] **Hinge test print:** one `right-inner-hinge.stl` (base face down) and one `outer-hinge.stl` (cap face down). Report the snap and the motion; tune `hinge_clearance` / `snap_interference` from that.
- [ ] **LSM6DSOX datasheet (DS12814)** from st.com, saved into the repo, so the symbol's pinout can be checked against the real part rather than the sister LSM6DSO.
- [ ] **Frame fit on the wearer** with the 180° wrap.

## Next for Claude, once the above is in

- [ ] Fusion mounts: magnet plug in the Inner Hinge snap post, sensor mount over the Outer Hinge cap bore, hinge enclosure, and a curved battery holder clear of the strap recess (62 × 34 × 5 mm cell, about 5.6 mm curve).
- [ ] PCB layout for both boards. The hinge board needs the AS5600 centred on the axis within 0.25 mm. Mark + at J4.
- [ ] Choose the FSR 402 order number and a Ø6 × 2.5 mm diametric magnet supplier.

## Bench work (needs hardware)

- [ ] Check cell polarity against J4 with a meter before first connection.
- [ ] Solder the Adafruit 4410's jumper closed for 500 mA.
- [ ] Measure idle, sampling, BLE and peak current. The 35 mA MCU figure and the peak figures are calculated.
- [ ] I2C bus with the real harness at 100 kHz: check rise times with a scope.
- [ ] AS5600 magnet: read STATUS (0x0B) MD/ML/MH and AGC.
- [ ] Firmware: BLE TX at 9 dBm or less, polled thigh IMU, gated FSR sampling, 3.5 V low-battery warning.

## Housekeeping

- [ ] `modular-knee-brace-package/files/Left_Hinge_Innerfinal-Static 1.LOG` shows as deleted locally but was never committed. Commit or restore it.
- [ ] `dev/` is an untracked folder that this session didn't create; review it.
- [ ] Claude's saved memory for this project lives with the `integrations&automations` folder. Copy it to this folder's project memory if sessions will start here from now on.
