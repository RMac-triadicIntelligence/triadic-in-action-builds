# First run of the full stochastic protocol in grace-state-vs-parametric

Run by the conductor (Claude), 2026-11-09 ~19:15 CT, from the uploaded zip.
- tools/verify_source.py: "Source matches the original upload."
- unit tests: 6 of 6 pass.
- Executed unchanged: model.stochastic_tests() and model.verdict() (original seed 20260808, 40 runs
  per arm and noise level, horizon 300). NOT run: the 9x9 basin scan and the figure (time).

Result: P1 PASS, P2 PASS, P4 PASS, P3 FAIL.
- P1 closed -> open in the barrier regime (k=0.5): 0/40, 6/40, 40/40, 40/40 at noise 0.01-0.10.
- P2 closed -> open in the closed regime (k=2.0): 0/160.
- P3 open -> closed with the field unchanged (k=0.5): 0/160. The prediction was "some returns".
- P4 open -> closed after the parametric change (k=0.2): 0/160.

Reading, with the repo's own cautions (docs/INTERPRETATION.md): zero hits in a finite sample do not
prove impossibility. What the run does show is an asymmetry at these settings: a closed system in
the barrier regime opens under noise, and an opened one was never seen to close, whether or not the
field was rewritten.
