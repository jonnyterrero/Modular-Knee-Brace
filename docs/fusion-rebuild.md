# Fusion 360 rebuild — engineering notes

How the SolidWorks MK-Brace became the parametric Fusion model in [`cad/fusion/`](../cad/fusion/README.md), what was measured, and what was corrected. Session log: [`progress/2026-10-04-fusion-rebuild.md`](progress/2026-10-04-fusion-rebuild.md).

## Source of truth

The rebuild follows the final SolidWorks set in [`cad/solidworks-final/`](../cad/solidworks-final/). Those `…final` parts were saved on 2025-05-02, the day the final report was saved, after every iteration in the course working folder (`pt2`, `pt3`, `Mirror…`). They differ from the parts in `modular-knee-brace-package/`.

The parts were uploaded to Fusion (project *Knee brace Design*, folder *SolidWorks originals*), converted, and measured face by face with `measure_part`.

## Measured geometry

### Frames (one design, two sizes)

| | Top Frame (thigh) | Bottom Frame (calf) |
| --- | --- | --- |
| Bore / outside diameter | 5.75 / 6.75 in | 4.50 / 5.50 in |
| Wrap (2 × half-angle) | 165° | 160° (see corrections) |
| Band height × wall | 2.00 × 0.50 in | 2.00 × 0.50 in |
| End blocks | 1.00 in tangent extension; drop 1.00 in toward the knee | same |
| Socket | 0.77 × 0.27 in, 1.01 in deep, R0.5 flared mouth over 0.319 in | same |
| Strap path | 1.50 × 0.125 in recess on the band, continuing through a slot in each end block under a 0.125 in bridge | same |
| Gusset | R1.00 between each end block and the band underside | same |

### Connectors

- Body 1.00 × 0.50 in; tabs 0.75 × 0.25 in. Each tab is 1.00 in from tip to body, including a 0.331 in R0.5 flared root.
- Upper connector 4.634 in long; lower connector 4.500 in.
- Each connector is lofted: the frame-end tab is rotated to match its frame socket (7.5° upper, 10° lower) while the hinge-end tab is square to the hinge. The twist runs in opposite directions on the two sides of the leg, which is why there are separate Left and Right parts.

### Hinge (snap-fit pivot)

- **Inner Hinge** (Left/Right): Ø2.00 × 0.50 in hub with a Ø1.625 × 0.375 in recess, a central mushroom snap boss, and a partial rim that acts as a rotation stop. Arm length 2.366 in from the hub centre.
- **Outer Hinge** (one part, used on both sides): Ø1.60 in spigot that seats in the Inner Hinge's recess, a Ø2.00 × 0.125 in cap, and a snap hole for the boss. Arm length 2.500 in.
- Every arm ends in the same 0.77 × 0.27 × 1.01 in socket with a flared mouth.

## Assembly layout

- Y is the leg axis (up), Z the front, X lateral. The Top Frame is the origin; the knee axis is at (0, −6.0, −0.5) in.
- The thigh frame's axis sits 0.5 in forward of the hinge axis and the calf frame's 0.5 in behind it, exactly where the original connector files place them.
- Load path on each side: Top Frame → Upper Connector → Inner Hinge ⟲ Outer Hinge → Lower Connector → Bottom Frame. Tabs seat fully (1.00 in), leaving 0.01 in at each socket floor.
- The Bottom Frame is the frame design flipped about X, so its band wraps the back of the calf and its sockets face the knee.

## Fit check

- Frame ↔ connector joints (all four): zero overlap by solid intersection.
- Hinge joints: tabs clear their sockets by at least 0.003 in along the straight section and stop 0.01 in short of the socket floor.
- The original connectors' tab spacing at the hinge is 0.014 in off the hinge stack. The hinges are placed to split it, leaving about 0.003 in press fit on one side of each flared seat, which is below FDM tolerance.

## Corrections to the originals

| Issue | In the originals | In the rebuild |
| --- | --- | --- |
| Frame diameters on the drawings | Ø6.75 / Ø5.50 read like bores | They are outside diameters; the bores are 5.75 / 4.50 in |
| Bottom Frame wrap | `Lower.SLDPRT` wraps 82.5° (7.5° sockets) while the lower connectors' tabs are angled 10° (Drawing 2's 80°); with 0.01 in clearance that 2.5° mismatch jams | Built at 80° so the connectors seat |
| Hinge tab spacing | 0.014 in mismatch between connectors and hinge stack | Split; see the fit check |

## Not yet reproduced

- R0.05–R0.10 edge rounds, the draft on each end block's lower outer face, and R0.25 corners at the strap openings.
- The connectors and hinges are exact copies (base features), so they do not follow the frame parameters. Rebuild them parametrically before a large refit.
- No materials, appearances or motion joints yet.
