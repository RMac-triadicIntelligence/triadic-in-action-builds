"""v0.7 §7.13 fixed-point rules applied to the v0.6 §5.3-5.4 linear toy (v0.7 does not restate the toy
equations; G01 refers to 'v0.6 default z0', so the v0.6 equations are assumed carried forward: ASSUMPTION A1)."""
Q = 1024
def rne(n, d):
    """n/d, round to nearest, ties to even (d > 0)."""
    qt, r = divmod(n, d)
    if 2 * r > d or (2 * r == d and qt % 2 == 1): qt += 1
    return qt
def clip(v, lo=-Q, hi=Q): return max(lo, min(hi, v))

def matvec(M, v, mode):
    """mode 'each': round each scaled product then add (v0.6 wording).
       mode 'once': full-width dot product, round once (one reading of v0.7 'rounding point fixed after
       each scaled multiplication'). AMBIGUITY B1."""
    if mode == "each":
        return [sum(rne(M[i][j] * v[j], Q) for j in range(2)) for i in range(2)]
    return [rne(sum(M[i][j] * v[j] for j in range(2)), Q) for i in range(2)]

def step(st, enc, mv="each"):
    z, E, T, D, P = st["z"], st["E"], st["T"], st["D"], st["P"]
    f = enc if enc is not None else [0, 0]
    E1 = [clip(E[k] + rne(f[k], 8)) for k in range(2)]                     # saturate at destination E
    PE = [P[k] + E1[k] for k in range(2)]                                   # no intermediate saturation (7.13)
    DPE = matvec(D, PE, mv); Tz = matvec(T, z, mv)                          # old T (7.13)
    M = [clip(DPE[k] + Tz[k]) for k in range(2)]                            # saturate at destination M
    DE = matvec(D, E1, mv)
    T1 = [[clip(T[i][j] + rne(DE[i] * z[j], Q * 8)) for j in range(2)] for i in range(2)]  # single rounding
    z1 = [clip(z[k] + rne(M[k] - z[k], 8)) for k in range(2)]               # unsaturated M - z
    I1 = [(m > 0) - (m < 0) for m in M]
    return dict(st, z=z1, E=E1, T=T1, I=I1, t=st["t"] + 1), dict(z_before=z, z_after=z1, E_before=E, E_after=E1,
                T_before=T, T_after=T1, M=M, I=I1)

def init(z0=(-256, 128), D=None, P=(512, -256)):
    return dict(t=0, z=list(z0), E=[0, 0], T=[[0, 0], [0, 0]], D=D or [[Q, 0], [0, Q]], P=list(P), I=[0, 0], W=0)

def classify(xs):
    """v0.7 §7.11 crossing classifier over x by learning step. Returns list of (t_candidate, label)."""
    out, t, n = [], 0, len(xs)
    while t < n - 1:
        a, b = xs[t], xs[t + 1]
        if a != 0 and b == 0:
            out.append((t, "ZERO_TOUCH")); t += 1; continue
        if a != 0 and b != 0 and (a > 0) != (b > 0):
            win = xs[t + 2:t + 4]
            if len(win) < 2: out.append((t, "CANDIDATE_OPEN_END_OF_TRACE")); break
            if any(w == 0 for w in win): lab = "ZERO_WINDOW_UNRESOLVED"
            elif any((w > 0) != (b > 0) for w in win): lab = "OSCILLATION_NO_CONFIRMED_CROSSING"
            else: lab = "CONFIRMED_CANDIDATE"
            out.append((t, lab)); t += 3; continue   # return leg belongs to the same candidate (7.11)
        t += 1
    return out
