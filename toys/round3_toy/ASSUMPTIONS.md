# Round 3 toy reproduction: assumptions and ambiguity log

Source: v0.6 §5.3–5.6 and Appendix A (doc sha256 e03df96b…1dc1f, inside file_0952.txt sha256 dd9f09aa…096f).
Code was written from the spec text alone. Every guess is a named option in `toy_v06.py`. Nothing outside the spec was added silently.

## Result
- Appendix A reproduces **byte-for-byte** with the default reading (EXP1). `golden_A.txt` was extracted from the document and cmp-checked against it.
- The trace distinguishes only the **rounding mode**: half-away and trunc fail at row 2, floor at row 3 (EXP2).
- The trace **cannot** distinguish A2, A3, A5 or A6 below. All four alternative readings also reproduce it exactly (EXP2). Each one does change results on other inputs (EXP5, EXP6, EXP9).

## Ambiguities (places where two implementers can diverge)

| # | Spec text | Readings | Divergence shown | Caught by trace? |
|---|---|---|---|---|
| A1 | "rounds to nearest… ties to even" | (default) even; half-away; floor (`>>3`); trunc (C `/`) | EXP2 and EXP5 | Yes |
| A2 | "addition saturates to [-q,q] for bounded coordinates" | saturate after every add (default) vs only at the final `clip` | EXP6: P=1024, E=1024, T₀₀=−1024, z=1024 gives M_x = 0 vs 1024 | No |
| A3 | `z + (M−z)/8` | M−z unsaturated (default) vs saturated (M−z is a sum of bounded coordinates) | EXP6: z=−1000, M=1024 gives x_after = −747 vs −872 | No |
| A4 | Which coordinates are "bounded" | Is T bounded? P₀+E? the M−z difference? Not listed. Default: all of z, E, T, M and intermediate sums except M−z | (same family as A2/A3) | No |
| A5 | `outer(D×E_next, z)/8` | round the product, then round /8 (default: "round each product") vs one rounding of DE·z/(8q) | EXP9: DE=100, z=45 gives T₀₀ = 0 vs 1 | No (T is never nonzero in the trace) |
| A6 | M uses T or T_next? | §5.4 lists M before T_next. Default: M uses old T | EXP5: differs at step 9 | No |
| A7 | E column in Appendix A | E before or after the step? Both are 0 there | Not testable | No |
| A8 | W column | W is reset at every learning step (§5.5), so W at a learning-step row is always 0. Nothing is defined for hold ticks | W can never differ in any learning-step trace | No |
| A9 | Crossing when x passes through exactly 0 (−5, 0, +5) | Both steps are UNKNOWN_CROSSING under §5.6. A real crossing through zero is never a candidate | EXP7 | No |
| A10 | x = 0 inside the 2-step confirmation window | Spec silent: reversal, persistence, or UNKNOWN? Logged as AMBIGUOUS | EXP7 | No |
| A11 | Return leg of an oscillation (+5 → −3 → −4 → −6) | Is the return a new candidate? With the literal rule it is a CONFIRMED crossing back | EXP7 | No |
| A12 | Gate refusal (A₀=REFUSE, gate PENDING) at a candidate | R1: the staged state is not committed, so z freezes forever (EXP10). R2: z crosses with no J_F deposit. §5.6 "before committing candidate state" vs §1.5 "disjoint write sets" | EXP10 | No (the trace was overridden to avoid crossings) |
| A13 | H/L "append authenticated encounter receipts" | Receipt bytes, NONE-step receipt yes/no, and whether support/hold events are receipted in L. Not implemented | n/a | No (not listed) |
| A14 | Canonical CBOR state hash | Field IDs, domain-tag strings, version number, inclusion rules and test vectors are all absent. "Canonical key order" has two RFC meanings: RFC 8949 bytewise vs RFC 7049 length-first. Not implemented (BLOCKED per §5.2) | n/a | No |
| A15 | Seed/perturbation field (E2) | Not in Ω (§5.1) and not in the §5.3 initial values. Not implemented | n/a | No |
| A16 | J_F in Φ | §5.1 Φ takes J_F, but the §5.4 toy M has no J term. Implemented with no J term (literal §5.4) | n/a | No |
| A17 | Encounter features /8 | Assumed the same ties-to-even divide | none observed | No |

## What the golden trace exercises
- **Exercised:** z relaxation toward the constant M = P₀; ties-to-even at 3 exact .5 ties (rows 2 and 3 positive, row 6 negative).
- **Not exercised:**
  - E (always 0), so U/T is never nonzero and outer() is never tested;
  - T×z, which is always 0;
  - D other than identity;
  - any clip/saturation edge (all values stay within ±512);
  - dwell holds and W;
  - any encounter, including NONE vs zero-feature;
  - a crossing, a candidate, oscillation, or UNKNOWN;
  - gate refusal or deposit, J_F, and corrections;
  - I, H, L, A and the state hash.
- In effect it tests one line: `z += round_even((P₀ − z)/8)`.

## Files
- `toy_v06.py`: reference toy with option flags (defaults = most literal reading).
- `experiments.py`: EXP1–EXP10.
- `raw_output.txt`: raw stdout of `python3 experiments.py`.
- `golden_A.txt`: Appendix A rows as extracted from the document.

Run: `cd round3_toy && python3 experiments.py`
