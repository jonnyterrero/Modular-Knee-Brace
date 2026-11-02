# 2026-11-02 — Battery, fuse, switch and charger chosen

Claude Code (Opus 5.5).

## Picks

| Part | Choice | Why |
| --- | --- | --- |
| Cell | Adafruit 258: 1200 mAh, PCM, 62 × 34 × 5 mm, 23 g | Has a datasheet and UN38.3 and MSDS documents, and its polarity matches the charger. About 22 h at the design load. Longer than the 50 mm cell first planned. |
| Fuse | Littelfuse 1206L050YR: 0.5 A hold, 1 A trip, 6 VDC | Trips well below the cell's 1.2 A continuous limit and clears the radio's peaks. |
| Switch | C&K PCM12SMTR: 300 mA at 6 VDC | Matches the footprint already on the thigh board. Needs the firmware limit below. |
| Charger | Adafruit 4410: USB-C, 100 mA default, 500 mA with jumper | Same vendor as the cell, so polarity matches. |

Prices when read: cell $9.95 and charger $5.95, both listed in stock (charger: 15 left).

## Finding: radio peaks set a firmware rule

The ESP32-S3 datasheet (table 5-8) lists Bluetooth LE TX peaks of 335 mA at 21 dBm and 193 mA at 9 dBm. Full power would exceed the switch's 300 mA rating, at about 380 mA at the battery. So firmware must limit BLE TX to 9 dBm or less (about 225 mA at the battery). This is on both schematics and in `electronics/README.md`.

## Limits of this check

- Figures come from vendor pages, the PKCELL cell specification, the 1206L family datasheet and ESP32-S3 datasheet v2.2. Peak current at the battery is a calculation assuming 85% regulator efficiency. Nothing has been measured.
- The cell's datasheet gives no PCM overcurrent figure. Adafruit states only the 3.0 V cutoff and short protection.
- The 1206L050's own resistance row was cut off in the extracted datasheet text, so the 0.75 Ω used is the 1206L050/15's value. The switch rating comes from distributor listings; C&K's own PDF wasn't reachable.
- J4's polarity against the cell has to be checked with a meter.
- Interlink's exact FSR 402 order number and the magnet supplier are still not chosen.
