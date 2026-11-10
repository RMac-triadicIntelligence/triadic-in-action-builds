"""open_hand2.py: round 2 attacks on the open-hand rule. The OPEN rule itself is unchanged from open_hand.py:
holding above the hand's size runs on to the neighbours. Conductor-built (Claude), NOT normative."""
import json, hashlib
import numpy as np
STEPS = 3000; BURN = 500

def graph(kind, n, rng):
    A = np.zeros((n, n))
    if kind in ('ring', 'smallworld'):
        for i in range(n): A[i, (i + 1) % n] = A[i, (i - 1) % n] = 1
        if kind == 'smallworld':
            for _ in range(8):
                a, b = rng.choice(n, 2, replace=False); A[a, b] = A[b, a] = 1
    elif kind == 'grid':
        s = int(round(n ** 0.5))
        for i in range(n):
            r, c = divmod(i, s)
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)): A[i, ((r + dr) % s) * s + (c + dc) % s] = 1
    return A / A.sum(1, keepdims=True)              # row i: where i's overflow goes, equal shares

def rain_means(shape, kind, n, t=0):
    m = np.full(n, 0.0)
    if shape == 'half':
        if kind == 'grid':
            s = int(round(n ** 0.5)); m = np.where((np.arange(n) % s) < s // 2, 1.0, 0.1)
        else: m = np.where(np.arange(n) < n // 2, 1.0, 0.1)
    elif shape == 'point': m[0] = 1.0
    elif shape == 'moving': m = np.where(((np.arange(n) - t // 50) % n) < n // 4, 1.0, 0.02)
    return m

def run(seed, n=64, kind='ring', shape='half', plenty=1.3, arm='OPEN', leak=0.0, fists=0.0, order='eat_first', tiny=False, steps=STEPS):
    rng = np.random.default_rng(seed)
    need = rng.uniform(0.5, 1.5, n); hand = rng.uniform(0.2, 0.8, n) if tiny else rng.uniform(1.0, 4.0, n)
    W = graph(kind, n, rng); fist = rng.uniform(size=n) < fists
    patch = (rng.uniform(size=n) < 0.25) if shape == 'patchy' else None
    L = np.zeros(n); inflow = np.zeros(n); unmet = np.zeros((steps, n)); pool = 0.0
    for t in range(steps):
        m = np.where(patch, 1.0, 0.02) if shape == 'patchy' else rain_means(shape, kind, n, t)
        m = m * plenty * need.sum() / m.sum()
        r = rng.exponential(1.0, n) * m
        if arm == 'CENTRAL':
            pool += r.sum(); eat = need * min(1.0, pool / need.sum()); pool -= eat.sum(); unmet[t] = need - eat; continue
        L = L + r + inflow; inflow = np.zeros(n)
        def spill():
            nonlocal L, inflow
            over = np.where(fist, 0.0, np.maximum(L - hand, 0.0)); L = L - over; inflow = (over * (1 - leak)) @ W
        if arm == 'OPEN' and order == 'cap_first': spill()
        eat = np.minimum(L, need); L = L - eat; unmet[t] = need - eat
        if arm == 'OPEN' and order == 'eat_first': spill()
        if arm == 'ASKED+':
            for i in rng.permutation(np.flatnonzero(unmet[t] > 1e-12)):
                g = int(np.argmax(L)); amt = min(L[g], unmet[t, i]); L[g] -= amt; unmet[t, i] -= amt
    u = unmet[BURN:] / need
    return u

def score(u, sel=None):
    if sel is not None: u = u[:, sel]
    per = u.mean(0)
    return dict(want=round(float((u > 1e-9).mean()), 3), unmet=round(float(u.mean()), 3), worst_member_unmet=round(float(per.max()), 3))

def avg(runs): return {k: round(float(np.mean([r[k] for r in runs])), 3) for k in runs[0]}

def main():
    S = (1, 2, 3); out = {}
    out['A0 baseline ring half plenty OPEN'] = avg([score(run(s)) for s in S])
    for lk in (0.05, 0.2): out[f'A1 leak {lk} ring'] = avg([score(run(s, leak=lk)) for s in S])
    out['A1 leak 0.2 grid'] = avg([score(run(s, leak=0.2, kind='grid')) for s in S])
    for kind in ('ring', 'grid', 'smallworld'):
        for f in (0.1, 0.3): out[f'A2 fists {f} {kind}'] = avg([score(run(s, kind=kind, fists=f)) for s in S])
    for kind in ('grid', 'smallworld'): out[f'A3 {kind} half plenty'] = avg([score(run(s, kind=kind)) for s in S])
    for shape in ('point', 'patchy', 'moving'):
        for kind in ('ring', 'grid'): out[f'A4 rain {shape} {kind}'] = avg([score(run(s, kind=kind, shape=shape)) for s in S])
    out['A5 spill-before-eating, tiny hands'] = avg([score(run(s, order='cap_first', tiny=True)) for s in S])
    out['A5 eat-then-spill, tiny hands'] = avg([score(run(s, order='eat_first', tiny=True)) for s in S])
    out['A5 spill-before-eating, normal hands'] = avg([score(run(s, order='cap_first')) for s in S])
    for plenty in (1.3, 1.0, 0.8):
        for arm in ('OPEN', 'ASKED+', 'CENTRAL'): out[f'A7 {arm} ring rain={plenty}x'] = avg([score(run(s, arm=arm, plenty=plenty)) for s in S])
        out[f'A7 OPEN grid rain={plenty}x'] = avg([score(run(s, kind='grid', plenty=plenty)) for s in S])
    # A6 scale: ring of 600, when is the middle of the dry half first fed, and steady state
    n = 600; u = run(1, n=n, steps=30000); mid = 3 * n // 4
    fed = np.flatnonzero(u[:, mid] < 1e-9)
    out['A6 ring of 600'] = dict(first_day_middle_of_dry_half_is_fed=(int(fed[0]) + BURN if fed.size else None),
                                 want_last_5000_days=round(float((u[-5000:] > 1e-9).mean()), 3), want_first_5000_days=round(float((u[:5000] > 1e-9).mean()), 3))
    blob = json.dumps(out, indent=1); open('results_round2.json', 'w').write(blob)
    print('results_round2.json sha256', hashlib.sha256(blob.encode()).hexdigest())
    for k, v in out.items(): print(f'{k:42s} {v}')

if __name__ == '__main__':
    main()
