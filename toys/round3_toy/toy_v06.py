#!/usr/bin/env python3
"""Reference toy for 'From Reykjavik to Relational Grace' v0.6, sections 5.3-5.6 and Appendix A.
Written from the spec text only (doc sha256 e03df96b...1dc1f). Every guess is a named OPTION below
and is logged in ASSUMPTIONS.md. Defaults = the reading the author of this file thinks most literal.
Gate/grace logic is NOT implemented (spec: PENDING); crossings are only classified, never authorized.
Canonical CBOR hashing is NOT implemented (field IDs / domain tags / version not given in spec)."""
import json, sys
Q = 1024
LO, HI = -Q, Q

def div_round(n, d, mode):
    """n/d rounded to integer. d > 0."""
    if mode == "even":            # spec: nearest, ties to even
        qt, r = divmod(n, d)      # floor division, 0 <= r < d
        if 2 * r > d or (2 * r == d and qt % 2 == 1):
            qt += 1
        return qt
    if mode == "half_away":
        s = -1 if n < 0 else 1
        qt, r = divmod(abs(n), d)
        if 2 * r >= d: qt += 1
        return s * qt
    if mode == "floor":           # what '>> 3' or Python '//' gives
        return n // d
    if mode == "trunc":           # what C '/' gives
        return int(n / d) if abs(n) < 2**52 else (abs(n) // d) * (1 if n >= 0 else -1)
    raise ValueError(mode)

def clip(v): return max(LO, min(HI, v))
def sat_add(a, b, opt): return clip(a + b) if opt["sat_each_add"] else a + b
def fmul(a, b, opt): return div_round(a * b, Q, opt["round"])   # product of two scaled ints

def matvec(Mx, v, opt):
    out = []
    for i in range(2):            # row-major, round each product, then add in order
        acc = fmul(Mx[i][0], v[0], opt)
        acc = sat_add(acc, fmul(Mx[i][1], v[1], opt), opt)
        out.append(acc)
    return out

def step(st, enc, opt):
    """One learning step, spec 5.4. enc is None (NONE) or a 2-int feature vector."""
    z, E, T, D, P = st["z"], st["E"], st["T"], st["D"], st["P"]
    f = enc if enc is not None else [0, 0]
    E_next = [clip(E[k] + div_round(f[k], 8, opt["round"])) for k in range(2)]
    PE = [sat_add(P[k], E_next[k], opt) for k in range(2)]
    DPE = matvec(D, PE, opt)
    Tz = None if opt["M_uses_T_next"] else matvec(T, z, opt)
    DE = matvec(D, E_next, opt)
    if opt["outer_single_round"]:
        T_next = [[clip(T[i][j] + div_round(DE[i] * z[j], 8 * Q, opt["round"])) for j in range(2)] for i in range(2)]
    else:
        T_next = [[clip(T[i][j] + div_round(fmul(DE[i], z[j], opt), 8, opt["round"])) for j in range(2)] for i in range(2)]
    if opt["M_uses_T_next"]:
        Tz = matvec(T_next, z, opt)
    M = [clip(sat_add(DPE[k], Tz[k], opt)) for k in range(2)]
    diff = [M[k] - z[k] for k in range(2)]
    if opt["sat_diff"]:
        diff = [clip(d) for d in diff]
    z_next = [clip(z[k] + div_round(diff[k], 8, opt["round"])) for k in range(2)]
    I_next = [(m > 0) - (m < 0) for m in M]
    row = dict(x_before=z[0], y_before=z[1], M_x=M[0], M_y=M[1], x_after=z_next[0], y_after=z_next[1],
               E_x=E_next[0], E_y=E_next[1], W=0, T_next=T_next, I=I_next)
    st2 = dict(st, z=z_next, E=E_next, T=T_next, I=I_next, W=0, t=st["t"] + 1)
    return st2, row

def hold(st):
    """Pure hold slot (5.5): only W changes; t does not advance."""
    return dict(st, W=st["W"] + 1)

def classify(xs):
    """5.6 crossing classification over a list of x values indexed by learning step.
    Returns list of (t, label). OPTION zero_in_window: how x==0 during confirmation counts (spec silent)."""
    out = []
    for t in range(len(xs) - 1):
        a, b = xs[t], xs[t + 1]
        if a == 0 or b == 0:
            if (a == 0) != (b == 0) or a == b == 0:
                out.append((t, "UNKNOWN_CROSSING")); continue
        if a * b < 0:
            win = xs[t + 2:t + 4]
            if len(win) < 2: out.append((t, "CANDIDATE_UNCONFIRMED_END_OF_TRACE"))
            elif all((w > 0) == (b > 0) and w != 0 for w in win): out.append((t, "CONFIRMED_CROSSING"))
            elif any(w == 0 for w in win): out.append((t, "AMBIGUOUS_ZERO_IN_WINDOW(spec silent)"))
            else: out.append((t, "OSCILLATION_NO_CONFIRMED_CROSSING"))
    return out

def init(z0=(-256, 128)):
    return dict(t=0, z=list(z0), E=[0, 0], T=[[0, 0], [0, 0]], D=[[Q, 0], [0, Q]], P=[512, -256],
                Q=0, W=0, I=[0, 0], B=[], A="REFUSE", J=[])

DEFAULT = dict(round="even", sat_each_add=True, outer_single_round=False, M_uses_T_next=False, sat_diff=False)

def run(z0, encs, holds, opt):
    st = init(z0); rows = []; xs = [st["z"][0]]
    for k, enc in enumerate(encs):
        for _ in range(holds[k] if holds else 0): st = hold(st)
        st, r = step(st, enc, opt); r["t"] = k; rows.append(r); xs.append(st["z"][0])
    return st, rows, xs

COLS = ["t", "x_before", "y_before", "M_x", "M_y", "x_after", "y_after", "E_x", "E_y", "W"]
def fmt(rows): return "\n".join(" | ".join(str(r[c]) for c in COLS) for r in rows)
