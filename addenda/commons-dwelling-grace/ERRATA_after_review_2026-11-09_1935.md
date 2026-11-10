# Errata after outside review (2026-11-09 19:35 CT)

Reviews: Grok bot (CD-F1..F9), ChatGPT (independent review zip), Grok Expert (summary only).
Both scripts reproduce byte for byte on two other machines. The conductor accepts every finding below.

## commons
1. "It never rained: 0" is wrong. Seed 13 has ONE crossing with zero rain and zero fill (ChatGPT).
   Rounding hid it. Correct statement: 1 turning in about 8,600 lives. Rare, not impossible.
2. PA (conservation) and PC (orphans) tested nothing. PA is a bookkeeping identity. In PC, with no
   fill, grip never enters the equations, so "best ground" and "no ground" are the same test (bot,
   ChatGPT). Both are withdrawn as passed predictions.
3. PB is mixed. With an open hand, turning falls from 81% to 74% as fill goes from 1x to 3x.
4. The 75-80% turning result is a rule added after run 1 plus a value of B picked after a sweep.
   The pre-registered model is run 1: about 1%.
5. Recognition changes grip without any act by the organism, against the docstring's own rule.
6. "Ground barely matters" is partly built in (the inherited shift is capped at 0.3).
7. The silence result (turning slightly higher after the rain stops) is not clean while the water
   line has no ceiling.
8. The predictions file cannot be shown to predate the first run (all timestamps equal). Next time:
   publish its hash before running anything.
9. Both of grace's paths to the crossing here (the lift, and recognition) change the organism's
   effective landscape or its grip. The keel's rule, confirmed again at 19:14, is that grace never
   changes the field. So this model gives grace an effect by a route the keel forbids.

## dwelling_grace
10. The constants were mine, not the library's. Rerun with the constants Grok bot reports from the
    library code (gamma 10, n 6, rise 0.35, fade 0.45, depth 0.8, boost 0.8, decay 0.22, relief 0.6;
    Euler, not odeint; I have not read that code file myself):
    - a 0.3 jump crosses at t=0 with dwelling 0, and at every later time. Timing does not matter.
    - a locked organism (closure 0.9) crosses on a 0.9 jump without any forgiveness.
    - with noise 0.02 and no nudge, 25% cross on their own.
    So "a gentle nudge needs dwelling" and "a locked organism ignores every nudge until forgiven"
    were products of my constants. Both are WITHDRAWN.
11. The hard shove that works with no dwelling is a push, which the keel forbids.
12. The witness gate and the memory decay of the forgiveness operator were not implemented.

## What this does to the evening's readings
- The keel's 19:14 ruling (forgiveness changes the field; grace does not) is the keel's. Of the two
  things I cited for it, the joined-model result is withdrawn. The other stands: the unchanged
  grace-state-vs-parametric run, where the closed regime gave 0 of 160 crossings.
- "Readiness is dwelling" has no model support now. It remains a reading.
