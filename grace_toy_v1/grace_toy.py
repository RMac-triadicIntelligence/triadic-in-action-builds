"""
grace_toy.py — double-well reference toy for grace definition v10 (keel-approved)

Conductor-built (Claude), 2026-11-09, at the keel's request. NOT normative. It is one
concrete reading of v10, written so the falsifiers have something executable to break.

Landscape (never changed by grace):  V(x,h) = h (x² − 1)²,  basins at x = ±1, separatrix x = 0,
barrier height h.

Organism i (all organism-owned except the grace receipt log):
  x        position
  basin    the basin it is in (−1 or +1)
  s        its own developmental direction (fixed; the way its own drive points)
  m        maturity, accumulated from its own experience; ready  ⇔  m ≥ THETA
  L        fill level of its current basin (energy units above the basin floor)
  c        capacity to receive (R6): scales how fast grace fills it

Ordinary dynamics (overdamped, Euler–Maruyama):
  dx = [F(x) + MU·s] dt + SIGMA dW
  F(x) = −∂V/∂x(x,h)   except inside the filled region of the organism's own basin
                        (same side as its basin and V(x,h) < L), where F = 0.
  This is the reading of "grace fills the basin; the whole basin lifts the organism up and
  over": below the water line nothing holds the organism; above it the landscape acts exactly
  as before. V and h are never modified.

Readiness (organism-owned, never written by grace): m grows by KAPPA·u·dt, where u is how far
the organism ranges from its basin floor (|x − basin|, capped at 1, either direction). A fuller
organism ranges further, so it matures faster: "fullness helps it become ready over time"
(item 4) arrives through its own rule.

Grace (item 2):
  filling  standing grant: L += G·c·dt while the grant lasts.
  nudge    single event: if ready, L := max(L, h) (the basin made whole at once, R8);
           if not ready, L += NUDGE_FILL (it fills; it is not pushed over, R4).
  cap      an unready organism's basin never becomes whole: L ≤ h·(1 − MARGIN) (assumption A2).
  A grace-enabled crossing therefore needs both keys: grace (L ≥ h) and readiness.

TWO READINGS OF FILLING (run 1 showed they behave differently; the keel chooses):
  A 'position'     the water line acts on position at once, ready or not (the literal reading).
  B 'development'  before readiness the fill is felt, not positional: it speeds the organism's own
                   maturation (dm gains a factor 1 + BETA·min(L/h, 1)); the water line acts on
                   position only once the organism is ready.

Crossing is confirmed when x passes ±X_CONFIRM on the far side of the separatrix. Kinds:
  GRACE        ready, with grace acting (fill present or a nudge): both keys
  OWN_FILLED   crossed while UNREADY with the water line acting on position (reading A only):
               a crossing grace made possible without the readiness key
  OWN          crossed by its own dynamics, grace not acting on position (R7)
  LOWERED      negative-control arm only
After the first crossing the per-crossing grant ends and the new basin starts unfilled
(assumption A1); receipt of grace stays on the record.

Negative control ("grace lowers the barrier", rejected by the keel): the receiver's barrier is
lowered at the same rate the keel arm fills, h_eff = max(h − G·c·t, 0), readiness-gated like the
keel arm, so only the mechanism differs.

Run:  python3 grace_toy.py  → writes results.json and prints the prediction table.
"""
import json, math, hashlib, sys
import numpy as np

# ---- parameters (frozen for this run) -------------------------------------------------------
DT = 0.01
SIGMA = 0.35          # organism's own noise
MU = 0.30             # organism's own drive magnitude, along its own direction s
X_CONFIRM = 0.5       # crossing confirmed past ±0.5 in the new basin
KAPPA = 1.0           # maturation rate per unit of ranging
THETA = 30.0          # readiness threshold on m
G = 0.02              # fill rate (energy per unit time) at capacity 1
NUDGE_FILL = 0.10     # fill added by a nudge to an unready organism
MARGIN = 1.0 / 8.0    # unready cap: L ≤ h(1 − MARGIN)
BETA = 2.0            # reading B: fullness speeds maturation by up to (1 + BETA)
H_SET = [0.10, 0.25, 0.50, 1.00, 2.00, 4.00]
N_PER_H = 32
SEED = 20261109


def V(x, h):
    return h * (x * x - 1.0) ** 2


def dV(x, h):
    return 4.0 * h * x * (x * x - 1.0)


def simulate(arm, h_vals, n, t_max, seed, start_ready, nudge_t=None, margin=MARGIN,
             s_start=None, grant_mask=None, record_L=False, mode='position'):
    """Vectorized over (len(h_vals), n). Same seed ⇒ same noise in every arm (matched pairs).
    arm ∈ {'none','fill','nudge','lower'}."""
    rng = np.random.default_rng(seed)
    H = np.asarray(h_vals, dtype=float)[:, None] * np.ones((1, n))
    shape = H.shape
    cap_rng = np.random.default_rng(seed + 1)
    c = cap_rng.uniform(0.5, 1.5, size=shape)              # R6 capacity to receive
    basin = -np.ones(shape) if s_start is None else -np.asarray(s_start, float) * np.ones(shape)
    s = -basin.copy()                                       # own direction: toward the far basin
    x = basin.copy()
    m = np.full(shape, THETA if start_ready else 0.0)
    L = np.zeros(shape)
    h_eff = H.copy()
    granted = np.ones(shape, bool) if grant_mask is None else np.asarray(grant_mask, bool) * np.ones(shape, bool)
    active = granted.copy()                                 # grant in force (ends at first crossing)
    t_ready = np.where(m >= THETA, 0.0, np.nan)
    t_cross = np.full(shape, np.nan)
    kind = np.full(shape, '', dtype=object)
    dest = np.zeros(shape)
    L_at_nudge_before = L_at_nudge_after = None
    steps = int(round(t_max / DT))
    nudge_k = None if nudge_t is None else int(round(nudge_t / DT))
    sq = SIGMA * math.sqrt(DT)
    trace = []
    for k in range(steps):
        t = k * DT
        ready = m >= THETA
        # grace input (direction-free scalars only)
        if arm == 'fill':
            L = np.where(active, L + G * c * DT, L)
        elif arm == 'lower':
            h_eff = np.where(active & ready, np.maximum(h_eff - G * c * DT, 0.0), h_eff)
        if arm == 'nudge' and k == nudge_k:
            L_at_nudge_before = L.copy()
            L = np.where(active & ready, np.maximum(L, H), np.where(active, L + NUDGE_FILL, L))
        cap = np.where(ready, np.inf, H * (1.0 - margin))
        L = np.minimum(L, cap)
        if arm == 'nudge' and k == nudge_k:
            L_at_nudge_after = L.copy()
        # ordinary dynamics: the landscape acts everywhere above the water line
        same_side = np.sign(x) == basin
        positional = ready if mode == 'development' else np.ones(shape, bool)
        in_fill = same_side & (V(x, H) < L) & positional
        F = np.where(in_fill, 0.0, -dV(x, h_eff))
        x = x + (F + MU * s) * DT + sq * rng.standard_normal(shape)
        # maturity from the organism's own ranging, either direction
        u = np.minimum(np.abs(x - basin), 1.0)
        boost = (1.0 + BETA * np.minimum(L / H, 1.0)) if mode == 'development' else 1.0
        m = m + KAPPA * u * boost * DT
        newly_ready = (m >= THETA) & np.isnan(t_ready)
        t_ready = np.where(newly_ready, t + DT, t_ready)
        # crossing confirmation (first crossing only is scored)
        crossed = (np.sign(x) == -basin) & (np.abs(x) >= X_CONFIRM) & np.isnan(t_cross)
        if crossed.any():
            ready_now = m >= THETA
            k_grace = crossed & ready_now & (L > 0) & (arm != 'lower')
            k_lower = crossed & (arm == 'lower') & (h_eff < H)
            k_filled = crossed & ~ready_now & (L > 0) & (mode == 'position') & (arm != 'lower')
            k_own = crossed & ~k_grace & ~k_lower & ~k_filled
            kind = np.where(k_grace, 'GRACE', kind)
            kind = np.where(k_lower, 'LOWERED', kind)
            kind = np.where(k_filled, 'OWN_FILLED', kind)
            kind = np.where(k_own, 'OWN', kind)
            t_cross = np.where(crossed, t + DT, t_cross)
            dest = np.where(crossed, -basin, dest)
            basin = np.where(crossed, -basin, basin)       # now in the new basin
            L = np.where(crossed, 0.0, L)                  # A1: new basin starts unfilled
            h_eff = np.where(crossed, H, h_eff)            # control: landscape restored
            active = active & ~crossed                     # per-crossing grant ends
        if record_L and k % 100 == 0:
            trace.append(float(L[0, 0]))
    return dict(H=H, c=c, nudge_k=nudge_k, t_cross=t_cross, kind=kind, t_ready=t_ready, m=m, dest=dest,
                L_before=L_at_nudge_before, L_after=L_at_nudge_after, trace=trace, granted=granted)


def drift_probe(h, level, lowered_h, n=20000, seed=7):
    """Declared observable that separates the keel model from the control: the receiver's
    measured drift at a point ABOVE the water line (V = 0.75h, inner side of the left basin).
    Keel: equals the unchanged landscape force −V'(x0,h). Control: equals −V'(x0,h_eff)."""
    rng = np.random.default_rng(seed)
    x0 = -math.sqrt(1.0 - math.sqrt(0.75))                  # V(x0,h) = 0.75 h, between floor and Σ
    out = {}
    for name, (Lv, he) in {'keel': (level, h), 'control': (0.0, lowered_h)}.items():
        x = np.full(n, x0)
        in_fill = V(x, h) < Lv
        F = np.where(in_fill, 0.0, -dV(x, he))
        x1 = x + (F + MU) * DT + SIGMA * math.sqrt(DT) * rng.standard_normal(n)
        est = float(np.mean((x1 - x) / DT) - MU)
        se = float(np.std((x1 - x) / DT) / math.sqrt(n))
        out[name] = dict(measured=est, se=se)
    out['landscape_force'] = float(-dV(x0, h))
    out['x0'] = x0
    return out


def summarize(res, label):
    rows = []
    for i, h in enumerate(H_SET):
        tc = res['t_cross'][i]
        kd = res['kind'][i]
        n = len(tc)
        crossed = ~np.isnan(tc)
        kinds = {k: int(np.sum(kd == k)) for k in ['GRACE', 'OWN', 'OWN_FILLED', 'LOWERED']}
        rows.append(dict(arm=label, h=h, n=n, crossed=int(crossed.sum()),
                         median_t=(float(np.median(tc[crossed])) if crossed.any() else None),
                         kinds=kinds,
                         median_t_ready=(float(np.nanmedian(res['t_ready'][i])) if np.any(~np.isnan(res['t_ready'][i])) else None)))
    return rows


def battery(mode):
    """The full prediction battery under one reading of filling. Predictions P1–P9 were written
    before run 1; items marked POST-HOC were added after run 1 and are labeled as such."""
    out, P = {}, {}
    T1 = 500.0
    e1 = {arm: simulate(arm, H_SET, N_PER_H, T1, SEED, start_ready=True, nudge_t=10.0, mode=mode)
          for arm in ['none', 'fill', 'nudge', 'lower']}
    out['E1'] = {arm: summarize(r, arm) for arm, r in e1.items()}
    s = out['E1']
    P['P1_R7_own_crossing'] = dict(
        claim='No grace: the organism crosses on its own at the lowest barrier and fails at the highest',
        crossed_by_h=[r['crossed'] for r in s['none']], PASS=s['none'][0]['crossed'] == N_PER_H and s['none'][-1]['crossed'] == 0)
    med = [r['median_t'] for r in s['fill']]
    P['P2_filling'] = dict(
        claim='Ready + filling: crosses at every barrier weight, as grace-enabled crossings; median time grows with weight',
        crossed=[r['crossed'] for r in s['fill']], grace_kind=[r['kinds']['GRACE'] for r in s['fill']], median_t=med,
        PASS=all(r['kinds']['GRACE'] == N_PER_H for r in s['fill']) and all(a < b for a, b in zip(med, med[1:])))
    medn = [r['median_t'] for r in s['nudge']]
    # organisms that crossed on their own before the nudge are excluded from the nudge timing
    tn = e1['nudge']['t_cross']
    after = [float(np.median(tn[i][tn[i] > 10.0] - 10.0)) if np.any(tn[i] > 10.0) else None for i in range(len(H_SET))]
    hi = [a for a, h in zip(after, H_SET) if h >= 0.5 and a is not None]
    P['P3_nudge'] = dict(
        claim='Ready + one nudge: every organism still in its basin crosses; time after the nudge roughly independent of weight (max/min < 2 over h >= 0.5, where no one crossed before the nudge)',
        crossed=[r['crossed'] for r in s['nudge']], median_t_after_nudge=after,
        PASS=all(r['crossed'] == N_PER_H for r in s['nudge']) and len(hi) > 0 and max(hi) / min(hi) < 2.0)
    P['INFO_control_clock'] = dict(
        claim='Context: the lowered-barrier control crosses on nearly the same clock as filling, so crossing times cannot separate them',
        median_t_fill=med, median_t_lower=[r['median_t'] for r in s['lower']])
    probes = {h: drift_probe(h, level=0.5 * h, lowered_h=0.5 * h) for h in [1.0, 4.0]}
    out['E2_drift_probe'] = probes
    ok = [abs(p['keel']['measured'] - p['landscape_force']) < 4 * p['keel']['se'] and
          abs(p['control']['measured'] - p['landscape_force']) > 10 * p['control']['se'] for p in probes.values()]
    P['P6_landscape_unchanged'] = dict(
        claim='Above the water line the receiver feels the unchanged landscape force; the control does not',
        detail={str(h): dict(keel=round(p['keel']['measured'], 3), control=round(p['control']['measured'], 3), landscape=round(p['landscape_force'], 3)) for h, p in probes.items()},
        PASS=all(ok))
    # unready + one nudge (fixed in run 2: only organisms still in their basin at the nudge are scored)
    e3n = simulate('nudge', H_SET, N_PER_H, 40.0, SEED + 3, start_ready=False, nudge_t=10.0, mode=mode)
    still = ~(e3n['t_cross'] <= 10.0)
    grace_at_nudge = int(np.sum((e3n['kind'] == 'GRACE') & still))
    rose = bool(np.all((e3n['L_after'] > e3n['L_before'])[still]))
    P['P4_unready_nudge'] = dict(
        claim='Unready + nudge: no grace-enabled crossing, and the level rises (scored over organisms still in their basin; run 1 wrongly included ones that had already crossed on their own)',
        still_in_basin=int(still.sum()), grace_crossings=grace_at_nudge, level_rose=rose, PASS=(grace_at_nudge == 0 and rose))
    T3 = 800.0
    e3 = {arm: simulate(arm, H_SET, N_PER_H, T3, SEED + 5, start_ready=False, mode=mode) for arm in ['none', 'fill']}
    out['E3'] = {arm: summarize(r, arm) for arm, r in e3.items()}
    tr_none = [r['median_t_ready'] for r in out['E3']['none']]
    tr_fill = [r['median_t_ready'] for r in out['E3']['fill']]
    P['P5_fullness_helps_readiness'] = dict(
        claim='Unready + filling becomes ready sooner than matched no-grace, at every barrier weight, and then crosses',
        median_t_ready_none=tr_none, median_t_ready_fill=tr_fill, crossed_fill=[r['crossed'] for r in out['E3']['fill']],
        PASS=all((b is not None) and (a is None or b < a) for a, b in zip(tr_none, tr_fill)) and all(r['crossed'] == N_PER_H for r in out['E3']['fill']))
    keep = [i for i, r in enumerate(out['E3']['none']) if r['crossed'] == 0]
    P['P5b_POST_HOC'] = dict(
        claim='POST-HOC (added after run 1): same as P5, scored only at barriers where no-grace organisms never cross on their own, since there the grant ends at an early own crossing in both arms',
        h=[H_SET[i] for i in keep], speedup=[round(tr_none[i] / tr_fill[i], 2) for i in keep if tr_fill[i]],
        PASS=all(tr_fill[i] is not None and tr_fill[i] < tr_none[i] for i in keep))
    unready_cross = [int(np.sum((~np.isnan(e3['fill']['t_cross'][i])) & ((e3['fill']['t_cross'][i] < e3['fill']['t_ready'][i]) | np.isnan(e3['fill']['t_ready'][i])))) for i in range(len(H_SET))]
    own_none = [r['crossed'] for r in out['E3']['none']]
    P['P9_two_keys_hold'] = dict(
        claim='Two keys: grace never carries an unready organism over. Crossings-before-readiness in the grace arm never exceed own crossings in the no-grace arm',
        unready_crossings_grace_arm=unready_cross, own_crossings_no_grace=own_none,
        PASS=all(a <= b for a, b in zip(unready_cross, own_none)))
    worse = (e3['fill']['m'] < e3['none']['m'] - 1e-9)
    P['P8_non_harm'] = dict(
        claim='Grace arm never ends with less maturity than its matched no-grace twin',
        pairs=int(worse.size), worse=int(worse.sum()), min_diff=round(float(np.min(e3['fill']['m'] - e3['none']['m'])), 2), PASS=int(worse.sum()) == 0)
    prog_f = np.where(np.isnan(e3['fill']['t_cross']), -1.0, 1.0)
    prog_n = np.where(np.isnan(e3['none']['t_cross']), -1.0, 1.0)
    P['P8b_POST_HOC'] = dict(
        claim='POST-HOC: grace arm never ends less developed (still short of a crossing its twin made). Maturity proved a poor welfare measure: after crossing, the organism presses against the steep outer wall and ranges less',
        worse=int(np.sum(prog_f < prog_n)), PASS=int(np.sum(prog_f < prog_n)) == 0)
    N5 = 400
    half = np.array([1.0] * (N5 // 2) + [-1.0] * (N5 // 2))
    lottery = np.random.default_rng(SEED + 9).uniform(size=N5) < 0.30
    steer = (half > 0) & (np.random.default_rng(SEED + 10).uniform(size=N5) < 0.60)
    audit = {}
    for name, mask in {'lottery': lottery, 'steering_grantor': steer}.items():
        r = simulate('fill', [1.0], N5, 200.0, SEED + 11, start_ready=True, s_start=half, grant_mask=mask, mode=mode)
        p_plus, p_minus, pp = mask[half > 0].mean(), mask[half < 0].mean(), mask.mean()
        z = (p_plus - p_minus) / (math.sqrt(pp * (1 - pp) * (4 / N5)) or 1e-9)
        g = r['kind'][0] == 'GRACE'
        audit[name] = dict(grant_rate_dest_plus=float(p_plus), grant_rate_dest_minus=float(p_minus), z=round(float(z), 2),
                           flagged=bool(abs(z) > 3.0), grace_crossings=int(g.sum()),
                           share_landing_plus=(round(float(np.mean(r['dest'][0][g] > 0)), 3) if g.any() else None))
    out['E5_selection_audit'] = audit
    P['P7_selection_audit'] = dict(
        claim='The population audit passes the lottery grantor and flags the grantor who grants by destination',
        detail=audit, PASS=(not audit['lottery']['flagged']) and audit['steering_grantor']['flagged'])
    if mode == 'position':
        sens = {}
        for mg in [1 / 32, 1 / 8, 1 / 4, 1 / 2]:
            r = simulate('fill', H_SET, N_PER_H, T3, SEED + 5, start_ready=False, margin=mg, mode=mode)
            sens[f'{mg:.4f}'] = [int(np.sum((~np.isnan(r['t_cross'][i])) & ((r['t_cross'][i] < r['t_ready'][i]) | np.isnan(r['t_ready'][i])))) for i in range(len(H_SET))]
        out['E6_cap_sensitivity_unready_crossings_by_h'] = sens
    out['PREDICTIONS'] = P
    return out


def main():
    out = {'params': dict(DT=DT, SIGMA=SIGMA, MU=MU, X_CONFIRM=X_CONFIRM, KAPPA=KAPPA, THETA=THETA, G=G,
                          NUDGE_FILL=NUDGE_FILL, MARGIN=MARGIN, BETA=BETA, H_SET=H_SET, N_PER_H=N_PER_H, SEED=SEED)}
    for mode, label in [('position', 'A_position'), ('development', 'B_development')]:
        out[label] = battery(mode)
    blob = json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o), sort_keys=True)
    with open('results.json', 'w') as f:
        f.write(blob)
    lines = ['results.json sha256 ' + hashlib.sha256(blob.encode()).hexdigest()]
    for label in ['A_position', 'B_development']:
        lines.append(f'== Reading {label}')
        for k, v in out[label]['PREDICTIONS'].items():
            tag = 'INFO' if 'PASS' not in v else ('PASS' if v['PASS'] else 'FAIL')
            lines.append(f"{tag:4}  {k}: {v['claim']}")
    print('\n'.join(lines))
    return out


if __name__ == '__main__':
    main()
