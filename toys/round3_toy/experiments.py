#!/usr/bin/env python3
import itertools, json
from toy_v06 import *
gold = open("golden_A.txt").read().rstrip("\n")

print("=== EXP1: Appendix A golden trace, default reading ===")
st, rows, xs = run((256, 128), [None]*10, None, DEFAULT)
out = fmt(rows); print(out)
print("BYTE-IDENTICAL TO APPENDIX A:", out == gold)
print("T after 10 steps:", st["T"], " I:", st["I"], " crossings:", classify(xs))

print("\n=== EXP2: which alternative readings does the golden trace catch? ===")
alts = {"round": ["even", "half_away", "floor", "trunc"], "sat_each_add": [True, False],
        "outer_single_round": [False, True], "M_uses_T_next": [False, True], "sat_diff": [False, True]}
for k, vals in alts.items():
    for v in vals:
        if v == DEFAULT[k]: continue
        o = dict(DEFAULT, **{k: v}); _, r, _ = run((256, 128), [None]*10, None, o)
        f = fmt(r); first = next((i for i,(a,b) in enumerate(zip(f.split("\n"), gold.split("\n"))) if a != b), None)
        print(f"{k}={v}: matches={f==gold} first_diff_row={first}")

print("\n=== EXP3: spec default z0=(-256,128) from 5.3, NONE encounters, no support ===")
st, rows, xs = run((-256, 128), [None]*10, None, DEFAULT)
print(fmt(rows)); print("x by step:", xs); print("classification:", classify(xs))

print("\n=== EXP4: pure-hold invariance (0/1/15 holds), with encounters ===")
encs = [[1024, -1024], None, [-800, 600], [300, 300], None, [-1024, -1024], [512, 0], None, [0, 1024], [-640, 128]]
ref = None
for h in (0, 1, 15):
    st, rows, xs = run((-256, 128), encs, [h]*10, DEFAULT)
    key = json.dumps([[r[c] for c in COLS[1:]] + [r["T_next"]] for r in rows])
    if ref is None: ref = key
    print(f"holds={h}: final z={st['z']} T={st['T']} W={st['W']} identical_to_0_holds={key==ref}")

print("\n=== EXP5: same encounter stream, alternative readings diverge? (exercise T, clip, rounding) ===")
base_st, base_rows, _ = run((-256, 128), encs, None, DEFAULT)
for k, vals in alts.items():
    for v in vals:
        if v == DEFAULT[k]: continue
        o = dict(DEFAULT, **{k: v}); st, rows, _ = run((-256, 128), encs, None, o)
        diff = [i for i,(a,b) in enumerate(zip(rows, base_rows)) if (a["x_after"],a["y_after"],a["T_next"]) != (b["x_after"],b["y_after"],b["T_next"])]
        print(f"{k}={v}: final z={st['z']} T={st['T']} differs_at_steps={diff}")
print("default final:", base_st["z"], base_st["T"])

print("\n=== EXP6: saturation-order divergence, minimal case ===")
# z far negative, M at +q: M - z exceeds q. Does subtraction saturate before /8?
for sd in (False, True):
    o = dict(DEFAULT, sat_diff=sd)
    st = init((-1000, 0)); st["P"] = [1024, 0]
    st2, r = step(st, None, o); print(f"sat_diff={sd}: M={r['M_x']} x_after={r['x_after']}")
# intermediate saturation in M = D(P+E) + Tz
for se in (True, False):
    o = dict(DEFAULT, sat_each_add=se)
    st = init((1024, 1024)); st["P"] = [1024, 0]; st["E"] = [1024, 0]; st["T"] = [[-1024, 0], [0, 0]]
    st2, r = step(st, None, o); print(f"sat_each_add={se}: P+E -> M_x={r['M_x']}")

print("\n=== EXP7: crossing classifier edge cases (spec 5.6) ===")
for name, xs in {"through_zero": [-5, 0, 5, 9, 12], "oscillate": [-5, 5, -3, -4, -6],
                 "zero_in_confirm_window": [-5, 5, 0, 7, 8], "recross_immediately_after_confirm": [-5, 5, 6, 7, -1, -2, -3]}.items():
    print(name, xs, classify(xs))

print("\n=== EXP8: ties actually hit in the golden trace (where rounding mode matters) ===")
st = init((256, 128)); ties = []
for t in range(10):
    for k, c in enumerate("xy"):
        d = [512, -256][k] - st["z"][k]
        if d % 8 == 4: ties.append((t, c, d, d/8))
    st, _ = step(st, None, DEFAULT)
print("exact .5 ties on (M-z)/8:", ties)

print("\n=== EXP9: outer-product double rounding vs single rounding, minimal case ===")
for osr in (False, True):
    o = dict(DEFAULT, outer_single_round=osr)
    st = init((45, 0)); st["E"] = [100 - 0, 0]   # E_next stays 100 with NONE encounter
    st2, r = step(st, None, o); print(f"outer_single_round={osr}: T_next={r['T_next']}")

print("\n=== EXP10: gate refusal at the default-z0 crossing (spec 5.6/2.8 do not say) ===")
print("A0=REFUSE and grace/gate PENDING. At t=3 the candidate x: -2 -> 62 must be 'staged, not committed'.")
print("Reading R1 (gate blocks the ordinary state): z stays at (-2,1) and every later step re-proposes the same crossing -> frozen organism.")
print("Reading R2 (gate blocks only the J_F deposit): z crosses, J_F empty. Spec 1.5 'disjoint write sets' suggests R2; 5.6 'checks admissibility before committing candidate state' suggests R1.")
st = init((-256, 128))
for t in range(3): st, _ = step(st, None, DEFAULT)
frozen = dict(st); seq = []
for t in range(3, 10):
    cand, r = step(frozen, None, DEFAULT); seq.append((t, frozen["z"][0], cand["z"][0]))  # R1: never commit
print("R1 trace (t, committed x, refused candidate x):", seq)
