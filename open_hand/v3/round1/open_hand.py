"""open_hand.py: one question. See PREDICTIONS.md. Conductor-built (Claude), NOT normative."""
import json, hashlib
import numpy as np
N = 60; STEPS = 4000; DROUGHT_AT = 3000

def world(seed, plenty):
    rng = np.random.default_rng(seed)
    need = rng.uniform(0.5, 1.5, N)                 # daily need; differs by member
    hand = rng.uniform(1.0, 4.0, N)                 # how much a hand can hold; differs by member
    mean = np.where(np.arange(N) < N // 2, 1.0, 0.1)  # wet half, dry half
    mean = mean * plenty * need.sum() / mean.sum()  # total rain = plenty x total need
    rain = rng.exponential(mean, size=(STEPS, N))
    return need, hand, rain, rng

def run(arm, seed, plenty, drought=False):
    need, hand, rain, rng = world(seed, plenty)
    L = np.zeros(N); want = np.zeros((STEPS, N), bool); fell = eaten = 0.0
    for t in range(STEPS):
        r = rain[t] if not (drought and t >= DROUGHT_AT) else 0.0
        L = L + r; fell += float(np.sum(r))
        eat = np.minimum(L, need); want[t] = eat < need - 1e-12; L = L - eat; eaten += float(eat.sum())
        if arm == 'OPEN':
            over = np.maximum(L - hand, 0.0); L = L - over + 0.5 * np.roll(over, 1) + 0.5 * np.roll(over, -1)
        elif arm == 'ASKED':
            asker = np.flatnonzero(want[t]); side = rng.integers(0, 2, asker.size) * 2 - 1
            giver = (asker + side) % N; gift = np.zeros(N); take = np.zeros(N)
            for a, g in zip(asker, giver):          # each giver gives half of what it still holds
                amt = 0.5 * (L[g] - take[g]); take[g] += amt; gift[a] += amt
            L = L - take + gift
    assert abs(fell - eaten - L.sum()) < 1e-6 * max(1.0, fell)
    return want

def summarise(want, lo=500, hi=DROUGHT_AT):
    w = want[lo:hi]; wet, dry = w[:, :N // 2].mean(), w[:, N // 2:].mean()
    per = w.mean(0)
    return dict(want_all=round(float(w.mean()), 4), want_wet_half=round(float(wet), 4), want_dry_half=round(float(dry), 4),
                worst_member=round(float(per.max()), 4), members_never_in_want=int((per == 0).sum()))

def main():
    out = {}
    for plenty in (1.3, 1.0, 0.8):
        for arm in ('OPEN', 'ASKED', 'BARNS'):
            runs = [summarise(run(arm, s, plenty)) for s in (1, 2, 3, 4, 5)]
            out[f'{arm} rain={plenty}x'] = {k: round(float(np.mean([r[k] for r in runs])), 4) for k in runs[0]}
    # scarcity under OPEN: want by distance from the wet half
    w = np.mean([run('OPEN', s, 0.8)[500:DROUGHT_AT].mean(0) for s in (1, 2, 3, 4, 5)], 0)
    dist = np.minimum(np.arange(N // 2), N // 2 - 1 - np.arange(N // 2))      # hops into the dry half from its nearer edge
    out['OPEN scarcity: want in dry half by hops from the rain'] = {int(d): round(float(w[N // 2:][dist == d].mean()), 3) for d in sorted(set(dist.tolist()))[::3]}
    out['OPEN scarcity: want in wet half'] = round(float(w[:N // 2].mean()), 3)
    # drought: rain stops at DROUGHT_AT after plenty; how long until half are in want, and all
    for arm in ('OPEN', 'ASKED', 'BARNS'):
        half = []; allw = []; d100 = []
        for s in (1, 2, 3, 4, 5):
            share = run(arm, s, 1.3, drought=True)[DROUGHT_AT:].mean(1)
            half.append(int(np.argmax(share >= 0.5)) if (share >= 0.5).any() else None)
            allw.append(int(np.argmax(share >= 0.999)) if (share >= 0.999).any() else None)
            d100.append(round(float(share[100]), 3))
        out[f'drought {arm}'] = dict(steps_until_half_in_want=half, steps_until_all_in_want=allw, share_in_want_100_steps_in=d100)
    blob = json.dumps(out, indent=1); open('results.json', 'w').write(blob)
    print('results.json sha256', hashlib.sha256(blob.encode()).hexdigest()); print(blob)

if __name__ == '__main__':
    main()
