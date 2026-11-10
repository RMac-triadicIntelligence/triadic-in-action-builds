"""open_hand3.py: the same open-hand rule in a big community (grid, wraps at the edges). NOT normative."""
import json, hashlib, sys
import numpy as np

def run(S=300, steps=12000, plenty=1.3, shape='half', leak=0.0, fists=0.0, seed=1, window=500):
    rng = np.random.default_rng(seed)
    need = rng.uniform(0.5, 1.5, (S, S)).astype(np.float32); hand = rng.uniform(1.0, 4.0, (S, S)).astype(np.float32)
    fist = rng.uniform(size=(S, S)) < fists
    col = np.arange(S)[None, :] * np.ones((S, 1))
    if shape == 'half': m = np.where(col < S // 2, 1.0, 0.1)
    elif shape == 'patchy': m = np.where(rng.uniform(size=(S, S)) < 0.25, 1.0, 0.02)
    elif shape == 'point': m = np.zeros((S, S)); m[S // 2, S // 2] = 1.0
    m = (m * plenty * need.sum() / m.sum()).astype(np.float32)
    L = np.zeros((S, S), np.float32); want_w = []; cnt = 0; acc = 0.0
    unmet_last = np.zeros((S, S)); n_last = 0
    for t in range(steps):
        L += rng.exponential(1.0, (S, S)).astype(np.float32) * m
        eat = np.minimum(L, need); L -= eat
        w = eat < need - 1e-6; acc += float(w.mean()); cnt += 1
        if t >= steps - window: unmet_last += (need - eat) / need; n_last += 1
        over = np.where(fist, 0.0, np.maximum(L - hand, 0.0)).astype(np.float32); L -= over
        o = over * (0.25 * (1.0 - leak))
        L += np.roll(o, 1, 0) + np.roll(o, -1, 0) + np.roll(o, 1, 1) + np.roll(o, -1, 1)
        if cnt == window: want_w.append(round(acc / cnt, 4)); acc = 0.0; cnt = 0
    u = unmet_last / n_last
    res = dict(members=S * S, want_by_window=want_w[:4] + ['...'] + want_w[-3:] if len(want_w) > 8 else want_w,
               want_last_window=want_w[-1], worst_member_unmet_last_window=round(float(u.max()), 3),
               share_missing_over_half_last_window=round(float((u > 0.5).mean()), 4))
    if shape == 'half':   # unmet need by distance (columns) into the dry half from the nearer wet edge
        d = np.minimum(np.arange(S // 2), S // 2 - 1 - np.arange(S // 2)); prof = u[:, S // 2:].mean(0)
        res['unmet_by_hops_from_rain'] = {int(k): round(float(prof[d == k].mean()), 3) for k in (0, 5, 10, 20, 40, 74) if (d == k).any()}
        res['unmet_wet_half'] = round(float(u[:, :S // 2].mean()), 4)
    if fists: res['unmet_among_open_hands'] = round(float(u[~fist].mean()), 4)
    return res

def main():
    out = {}
    out['B1 plenty, rain on half'] = run()
    out['B2 plenty, patches'] = run(shape='patchy', steps=4000)
    out['B3 fists 10%, rain on half'] = run(fists=0.1)
    out['B3b fists 10%, patches'] = run(fists=0.1, shape='patchy', steps=4000)
    out['B3c fists 30%, patches'] = run(fists=0.3, shape='patchy', steps=4000)
    out['B4 leak 5%, rain on half'] = run(leak=0.05)
    out['B5 leak 5%, patches'] = run(leak=0.05, shape='patchy', steps=4000)
    out['B6 scarcity 0.8x, rain on half'] = run(plenty=0.8)
    out['B6b scarcity 0.8x, patches'] = run(plenty=0.8, shape='patchy', steps=4000)
    out['all rain on one member'] = run(shape='point')
    out['B7 one million members, plenty, patches'] = run(S=1000, steps=2000, shape='patchy')
    blob = json.dumps(out, indent=1); open('results_round3.json', 'w').write(blob)
    print('results_round3.json sha256', hashlib.sha256(blob.encode()).hexdigest())
    for k, v in out.items(): print(k, '\n   ', v)

if __name__ == '__main__':
    main()
