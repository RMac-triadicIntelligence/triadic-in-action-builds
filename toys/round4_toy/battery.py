#!/usr/bin/env python3
"""Round 4 history-seat computations for v0.7. Run: python3 battery.py (cbor2 optional, for cross-check)."""
import json, hashlib, copy
from fixedpoint import *
from canon import enc, digest, xcheck
import doublewell as dw
H = lambda s: print("\n=== " + s + " ===")

H("TAGS: §8.2 domain-tag bytes")
TAGS = ["RNR07:STATE:", "RNR07:PERMIT:", "RNR07:GRACE:", "RNR07:RELAY:", "RNR07:DEPOSIT:", "RNR07:CORRECTION:", "RNR07:INTENT:", "RNR07:SCHEDULER:"]
for t in TAGS: print(f"{t:20s} {t.encode('ascii').hex()}")
print("prefix-free:", not any(a != b and b.startswith(a) for a in TAGS for b in TAGS))

H("C1: canonical STATE vector, initial state, empty J, explicit NONE")
Z32 = bytes(32)
# Values the spec determines (or that follow from v0.6 §5.3 if carried forward) vs PLACEHOLDERS (spec silent).
C1 = {0: 7,            # PLACEHOLDER schema_version value not given
      1: Z32,          # PLACEHOLDER subject_id type/value not given
      2: 0,            # founder generation assumed 0
      3: 0,            # learning_step 0
      4: Z32,          # PLACEHOLDER history_tip: birth-record encoding/tag not given
      5: Z32,          # PLACEHOLDER constitution_hash: K encoding not given
      6: Z32,          # PLACEHOLDER basis_hash: D encoding not given
      7: [[0, 0], [0, 0]],   # T0 zero (v0.6); nested-array layout ASSUMED
      8: None,         # empty J -> explicit null ASSUMED for 'explicit NONE'
      9: [-256, 128],  # v0.6 z0
      10: [0, 0], 11: 0,
      12: None,        # PLACEHOLDER readiness_commitment scheme not given
      13: None,        # PLACEHOLDER fullness_commitment scheme not given
      14: 0,           # PLACEHOLDER standing_status enum not given
      15: None,        # no grace received -> null ASSUMED
      16: [0, 0],      # I0 (v0.6)
      17: None,        # B empty -> null ASSUMED
      18: "REFUSE",    # PLACEHOLDER enum encoding (text vs int) not given
      19: Z32,         # PLACEHOLDER provenance_tip
      20: 0,           # PLACEHOLDER policy_version value
      21: 0,           # PLACEHOLDER registry_anchor
      22: [0, 0],      # empty J projection assumed zero vector
      23: None}        # reserved_null: explicit null (spec)
b, h = digest(b"RNR07:STATE:", C1)
print("CANDIDATE C1 CBOR hex:", b.hex()); print("len", len(b), "SHA-256(tag||cbor):", h, " cbor2 cross-check:", xcheck(C1))
alts = {"schema_version=1": (0, 1), "schema_version='RNR07'": (0, "RNR07"), "subject_id=uint 1": (1, 1),
        "T flat [0,0,0,0]": (7, [0, 0, 0, 0]), "J tip = 32 zero bytes": (8, Z32), "authorization_status=int 1": (18, 1),
        "readiness_commitment=sha256(0)": (12, hashlib.sha256(b"\x00").digest()), "standing_status=null": (14, None),
        "policy_version=1": (20, 1), "burden_tip = []": (17, [])}
for name, (k, v) in alts.items():
    c = dict(C1); c[k] = v; print(f"  alt {name:32s} -> {digest(b'RNR07:STATE:', c)[1][:16]}…")
print("Spec-determined fields: 3,9,10,11,16,23 (+2,7,22 by mild assumption); spec-silent: 0,1,4,5,6,8,12,13,14,15,17,18,19,20,21")
print("C2/C3: BLOCKED — no field-ID map for LineageDeposit/CORRECTION, no signature-exclusion rule, no slice projection.")
print("Commitment brute-force: if readiness_commitment = SHA256(tag||enc(bool)), the two possible digests are:")
for r in (False, True): print("   ready=", r, hashlib.sha256(b"RNR07:STATE:" + enc(r)).hexdigest()[:16], "…")

H("G01: v0.6 default z0, NONE encounters, v0.7 arithmetic (10 steps)")
st = init(); xs = [st["z"][0]]; rows = []
for t in range(10):
    st, r = step(st, None); xs.append(st["z"][0]); rows.append((t, r["z_before"], r["M"], r["z_after"]))
for r in rows: print(r)
cl = classify(xs); print("x:", xs, "\nclassification:", cl)
# evidence-driven test (§7.10): counterfactual with no new encounter from same pre-candidate state is identical
print("evidence-driven? counterfactual (no new encounter) identical by construction -> NOT evidence-driven -> no deposit")
print("G01 trace equals v0.6 Appendix-A-style default run under v0.6 rules:", xs == [-256, -160, -76, -2, 62, 118, 167, 210, 248, 281, 310])

H("G02/G03 candidates: nonzero Encounter, nonzero T (inputs chosen by me; spec gives none)")
st = init(); encs = [[1024, -1024], [800, 600], [-512, 256]]
for e in encs:
    st, r = step(st, e); print(json.dumps({k: r[k] for k in ("E_before","E_after","T_before","T_after","z_before","z_after","M","I")}))
T_now = st["T"]; s2 = copy.deepcopy(st); s2["T"] = [[0, 0], [0, 0]]
a, ra = step(st, None); b2, rb = step(s2, None)
print("G03: M with T =", ra["M"], " M with T-empty control =", rb["M"])

H("B1: matvec rounding ambiguity that survives v0.7 §7.13")
T = [[512, 512], [0, 0]]; z = [1, 1]
print("T×z round-each:", matvec(T, z, "each"), " round-once:", matvec(T, z, "once"))
st = init(); st["T"] = [[3, 1], [-1, 2]]; st["z"] = [512, 512]
for mv in ("each", "once"):
    s, r = step(st, None, mv); print(f"  full step mv={mv}: M={r['M']} z_after={r['z_after']}")

H("G05-G07: v0.7 rules resolve the v0.6 ambiguities (values under v0.7 rules)")
st = init((1024, 1024), P=(1024, 0)); st["E"] = [1024, 0]; st["T"] = [[-1024, 0], [0, 0]]
_, r = step(st, None); print("G05 M_x (no intermediate saturation):", r["M"][0])
st = init((-1000, 0), P=(1024, 0)); _, r = step(st, None); print("G06 x_after (M-z unsaturated):", r["z_after"][0])
st = init((45, 0)); st["E"] = [100, 0]; _, r = step(st, None); print("G07 T00 (single rounding):", r["T_after"][0][0])

H("G08-G12: holds and queue (pure holds change only W; NONE vs wait)")
def run_sched(events):
    s = init(); W = 0; log = []
    for ev in events:
        if ev == "HOLD": W += 1; log.append(("hold", s["t"], W))
        elif ev == "EMPTY": log.append(("wait", s["t"]))           # G11: no learning step
        else:
            s, _ = step(s, None if ev == "NONE" else ev); W = 0; log.append(("step", s["t"], s["z"]))
    return s, log
base, _ = run_sched([[256, 0], [256, 0]])
for n in (0, 1, 15):
    s, _ = run_sched([[256, 0]] + ["HOLD"] * n + [[256, 0]]); print(f"G{8 if n==0 else 9 if n==1 else 10}: holds={n} state==base:", s["z"] == base["z"] and s["T"] == base["T"])
s, log = run_sched([[256, 0], "EMPTY", "EMPTY"]); print("G11 empty queue: t =", s["t"], log[-1])
s, log = run_sched([[256, 0], "NONE"]); print("G12 NONE step: t =", s["t"], "z =", s["z"])

H("G13-G15: classifier under v0.7 §7.11")
for name, xs in {"G13 through-zero": [-5, 0, 5, 9, 12], "G14 zero-in-window": [-5, 5, 0, 7, 8],
                 "G15 oscillation+return": [-5, 5, -3, -4, -6, -7], "extra: candidate at last step": [-5, -3, 4]}.items():
    print(name, xs, classify(xs))

H("G16-G18 surrogate: double-well, grace has no dynamical path (spec gives no update rule; mine is ASSUMED)")
B = 64   # constant evidence input per step, scaled (ASSUME)
print("h | crossed(no grace) | crossed(grace) | [evidence_accum] ready / grace-enabled | [would_cross] ready / grace-enabled | neg-control(grace lowers h) crossed")
for h in (64, 128, 256, 512, 1024, 2048):
    ng = dw.run(h, B, 60, False, "evidence_accum"); g = dw.run(h, B, 60, True, "evidence_accum")
    g2 = dw.run(h, B, 60, True, "would_cross"); nc = dw.run(h, B, 60, True, "evidence_accum", lower_barrier_control=True)
    print(f"{h:5d} | {ng['crossed']!s:5} | {g['crossed']!s:5} | {g['ready']!s:5} / {g['grace_enabled']!s:5} | {g2['ready']!s:5} / {g2['grace_enabled']!s:5} | {nc['crossed']!s:5}")
print("Reading D4a: ready at every h, success falls to 0 at h>=512 -> prediction FAILS, and fails identically with no grace.")
print("Reading D4b: success among ready = 100% at every h by definition -> prediction PASSES tautologically.")
print("Unready+grace (G17): fullness phi is not an argument of Phi or U (§7.2, §7.3) -> every behavioral probe identical to no-grace arm.")

H("Relay fan-out (§2.3): per-branch non-increase does not bound total")
def fan(budget, depth, k):
    return 0 if depth == 0 or budget == 0 else k + k * fan(budget - 1, depth - 1, k)
print("grant relay_budget=3 depth=3, each holder relays to k=10:", fan(3, 3, 10), "relayed grants from one origin")

H("§4.8 ordering by per-organism learning step")
print("Deposit X (sibling A, t=100) commits at anchor r=10. Deposit Y (sibling B, t=50) confirms at r=11.")
print("Rule order says Y before X; X is already at the tip. Either the order rule is violated or X must wait for every sibling forever.")

H("T quantization: does T ever contribute to M in the linear toy? (H1/G03 relevance)")
import random
random.seed(7)   # ASSUME: uniform random encounter features in [-1024,1024], 500 steps, frozen seed 7
st = init(); nz = 0; mx = 0; tmax = 0
for t in range(500):
    e = [random.randint(-1024, 1024), random.randint(-1024, 1024)]
    tz = matvec(st["T"], st["z"], "each"); nz += any(tz); mx = max(mx, max(abs(v) for v in tz))
    tmax = max(tmax, max(abs(v) for row in st["T"] for v in row))
    st, _ = step(st, e)
print(f"steps with T×z != 0: {nz}/500; max |T×z| = {mx} units ({mx/1024:.4f}); max |T entry| = {tmax} units")
