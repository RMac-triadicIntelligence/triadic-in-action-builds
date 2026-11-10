"""Double-well demonstration for v0.7 §7.4-7.7. The spec gives V(x,h)=h(x^2-1)^2 but NO update equation,
NO readiness rule and NO way for grace to act on dynamics. Everything below marked ASSUME is mine."""
from fixedpoint import rne, clip, Q
ETA_DIV = 8                       # ASSUME D1: step size 1/8 (v0.6 constant)
def grad(x, h):                   # V'(x) = 4 h x (x^2 - 1), all scaled by Q
    x2 = rne(x * x, Q)
    return rne(4 * h * rne(x * (x2 - Q), Q), Q)
def dw_step(x, h, b):             # ASSUME D2: overdamped x' = clip(x - V'(x)/8 + b)
    return clip(x - rne(grad(x, h), ETA_DIV) + b, -2 * Q, 2 * Q)
def run(h, b, steps, grace, ready_rule, theta=200, lower_barrier_control=False):
    """grace has NO dynamical path in the keel model (§1.2, §4.7, §5.1). In the negative-control model
    grace lowers h to h/4 (ASSUME D3)."""
    x, acc = -Q, 0; xs = [x]; ready = False
    for t in range(steps):
        acc += abs(b)
        hh = h // 4 if (lower_barrier_control and grace) else h
        x = dw_step(x, hh, b); xs.append(x)
    crossed = xs[-1] > 0 and xs[-2] > 0 and xs[-3] > 0
    if ready_rule == "evidence_accum": ready = acc >= theta          # ASSUME D4a: direction-free magnitude rule
    elif ready_rule == "would_cross": ready = crossed                 # ASSUME D4b: readiness := able to cross
    grace_enabled = crossed and grace and ready
    return dict(crossed=crossed, ready=ready, grace_enabled=grace_enabled, x_final=xs[-1])
