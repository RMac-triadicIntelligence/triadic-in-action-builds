# Grace toy v1: a double-well reference model for grace definition v10

Built by the conductor (Claude) at the keel's request, 2026-11-09. It is NOT normative. It is
one concrete reading of v10, written so the falsifiers have something executable to break.
Because the conductor built it, the conductor should not be the one to judge it.

Run: `python3 grace_toy.py` (Python 3, numpy). It takes about 30 s, writes results.json and
prints the prediction table. Same seed, same output: run 2's results.json sha256 is
49e579d9a2c636ea26ea79d68b7ecefd3f86d00a4a707a898299a31a0bd7bc1f.

## The model in one paragraph
The landscape is V(x,h) = h(x² − 1)², with two basins and a separatrix at x = 0, and grace never
changes it. The organism moves by its own drive along its own direction, plus noise. Its
readiness is its own maturity, earned by how far it ranges from its basin floor; grace never
writes it.
- **Filling** raises a water line L in the organism's basin. Below the line nothing holds the
  organism; above it the landscape acts exactly as before.
- **Nudge:** for a ready organism, a nudge makes the basin whole at once (R8). For an unready one
  it only adds fill.
- An unready organism's basin can't become whole (cap at 7/8 of the barrier).
- The negative control lowers the receiver's barrier at the same rate the keel arm fills.

## Two readings of filling, and the result that matters
Run 1 used the literal reading (A). It showed that filling carries UNREADY organisms over. So
run 2 adds a second reading (B) and runs everything under both.
- **A, positional:** the water line lifts the organism straight away, ready or not.
- **B, felt:** before readiness, fullness is felt, not positional. It speeds the organism's own
  maturation (up to 3×). The water line lifts the organism only once it is ready.

| Prediction | Reading A | Reading B |
|---|---|---|
| P1 R7: crosses alone at low barriers, not at high | PASS (32/32 at h ≤ 0.25; 0/32 at h ≥ 1) | PASS |
| P2 ready + filling crosses at every barrier, slower as it grows | PASS (median 5.7 → 229 time units, h 0.1 → 4) | PASS |
| P3 ready + nudge crosses at every barrier, same speed | PASS (3.1–3.6 units after the nudge, h ≥ 0.25) | PASS |
| P4 unready + nudge: no crossing, level rises | PASS | PASS |
| P5 filling makes the unready ready sooner, at every barrier | FAIL at low barriers | PASS (2.2–2.5× sooner at h ≥ 1) |
| **P9 two keys: grace never carries an unready organism over** | **FAIL: at h = 1, 32/32 cross unready vs 0/32 without grace** | PASS |
| P6 the receiver still feels the unchanged landscape above the water line | PASS | PASS |
| P7 a population audit catches a grantor who picks by destination | PASS (lottery z = 1.8; steering z = 13.4) | PASS |
| P8 grace arm never ends with less maturity (pre-declared) | FAIL (85/192 pairs) | FAIL (1/192) |

**Reading A breaks the two-key rule.** Lifted near the rim, the organism finishes the crossing by
its own drive and noise before it is ready. A lower cap only delays this: at half the barrier,
6/32 still cross unready at h = 1. This is ordinary noise physics: any remaining band is crossed
eventually.

**Reading B keeps every keel rule** in this toy. Its cost: until the organism is ready, grace
changes how fast it grows, not where it is.

## Two results that hold under both readings
- **Crossing times can't tell filling from a lowered barrier.** At h = 1 the median times are 41
  vs 42 units; at h = 4, 229 vs 223. What separates them is a drift probe above the water line.
  At h = 1 the receiver feels −1.29 (the unchanged landscape is −1.27); the control feels −0.67.
  So "the landscape never changes" is testable, but only with a probe declared in advance.
- **The selection-steering audit works on a simple case.** A grantor who grants only toward +1
  lands 100% of its crossings at +1 vs 57.5% for the lottery. The audit flags it at z = 13.4.

## What failed and why (nothing was tuned to pass)
- **P4 failed in run 1 because my test was wrong.** It counted organisms that had already crossed
  on their own before the nudge arrived. Fixed in run 2 by scoring only organisms still in their
  basin.
- **P5 (reading A).** At low barriers, both arms cross on their own almost at once, which ends the
  grant, so grace has no time to help. P5b re-scores it only where no-grace organisms never cross.
  It was added after the fact and is labeled POST-HOC.
- **P8 (both readings).** Maturity is the wrong yardstick for harm. After crossing, the organism
  presses against the steep outer wall and ranges less, so its maturity grows more slowly. P8b,
  also POST-HOC, measures "never ends less developed" instead and passes. Non-harm needs the
  keel's definition of "worse".
- **Run 1 classified crossings strictly** (grace only when the basin was already whole). Almost no
  crossing qualified, because organisms go over before the basin is whole. Run 2 counts a crossing
  as grace-enabled when the organism is ready and grace is acting.

## Assumptions to attack
- A1. The fill belongs to the basin. After crossing, the new basin starts empty; receipt of grace
  stays on the record.
- A2. An unready organism's basin can't become whole (cap 7/8). The sensitivity run is in
  results.json (E6).
- A3. Readiness = maturity from ranging, threshold 30.
- A4. Each organism's own drive has a fixed direction. Grace carries none.
- A5. Below the water line the landscape exerts no force on this organism. Whether that counts as
  "changing the landscape" is a definitional question for the keel. The probe shows the difference
  holds only above the line.
- A6. Each grant covers one crossing and ends there.
- All parameters were chosen by the conductor, not frozen by an independent party.
- The model is one-dimensional with one separatrix, so "the organism's position decides the
  direction" is trivial here. A multi-basin landscape is needed to test it.
- It uses float64 numpy, not the spec's fixed-point arithmetic, so it is not a golden-vector source.

## Questions for the keel
1. Reading A or B? A lifts even the unready, and they then cross without readiness. B makes
   fullness felt (faster growth) until readiness, then lifts.
2. Does the fill carry into the new basin after a crossing (A1)?
3. What counts as "worse" for the non-harm rule?

## Files
- grace_toy.py: current model (run 2)
- raw_output.txt, results.json: run 2 output
- run1/: the first version, its output and results, kept unchanged for the record
