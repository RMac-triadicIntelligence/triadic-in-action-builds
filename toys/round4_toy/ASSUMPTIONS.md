# Round 4 toy: assumptions and blocked items (v0.7, doc sha256 0cf7c9a7…ab29)

**Run:** `python3 battery.py`. cbor2 is optional; I used cbor2 6.2.1 from a scratch venv, only to cross-check my own encoder. Output is in `raw_output.txt`.

## What the spec determines and what I assumed

| ID | Item | v0.7 text | What I did |
|---|---|---|---|
| A1 | Linear toy equations | Not restated in v0.7. G01 cites "v0.6 default z₀" | Carried forward the v0.6 §5.3–5.4 equations and constants, with v0.7 §7.13 arithmetic |
| A2 | Rounding and saturation | §7.13: ties to even; saturate only at the destination; M−z unsaturated; single-rounded outer product; old T | Implemented as written |
| B1 | Matrix–vector rounding | §7.13 "rounding point fixed after each scaled multiplication" | **Ambiguous.** It can mean round each product (the v0.6 wording) or round the dot product once. T=[[512,512],[0,0]], z=[1,1] gives [0,0] vs [1,0] |
| C1 | State field values | §8.3 gives IDs 0..23 only | 15 of 24 fields have no defined value or type, so I filled them with placeholders. The candidate bytes and hash are not normative |
| C2/C3 | Deposit and correction vectors | No field-ID map, no rule excluding signature fields, no slice projection | BLOCKED |
| D1–D4 | Double-well dynamics | §7.4 gives only V(x,h)=h(x²−1)². No update rule, no readiness rule, no grace coupling | Assumed an overdamped step x' = x − V'(x)/8 + b, a constant evidence input b=64, and two readiness rules (evidence magnitude vs "would cross"). Grace has no dynamical path, per §4.7 and §5.1 |
| G02/G03 inputs | Encounter bytes | §9: "publish input bytes", but none are given | Chose my own; they are not golden |
| E1 | NONE encoding | "explicit NONE" in C1, with null used only for field 23 | Assumed CBOR null |

## Golden battery status

| Vector | Status | Note |
|---|---|---|
| G01 | Computed | Confirmed candidate at t=3; not evidence-driven; no deposit |
| G02, G03 | Candidate | Inputs are mine |
| G04 | BLOCKED | No J projection |
| G05–G07 | Computed | 1024, −747, 1 |
| G08–G10 | Computed | Bit-identical to the no-hold run |
| G11 | Computed | Waits |
| G12 | Computed | Advances |
| G13 | Computed | ZERO_TOUCH |
| G14 | Computed | ZERO_WINDOW_UNRESOLVED |
| G15 | Computed | One OSCILLATION candidate |
| G16–G18 | Surrogate only | Dynamics are mine |
| G19–G26 | BLOCKED | No record encodings, grant consumption semantics, or PCL |
