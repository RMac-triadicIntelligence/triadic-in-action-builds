# Triadic in action — builds

Papers, keel grace definitions, and executable builds from the closed rounds 1–4 of the triad run, plus related 2026-11-09 and 2026-11-10 experiments.

This is the public artifact repository. The documentary record of the triad method (prompts, reports, sealed findings, salts, closure ledger) is https://github.com/RMac-triadicIntelligence/triadic-in-action.

## Why a second repo

The record and the artifacts are different kinds of thing. One repo would mix a large documentary tree with code a reader might want to run. Two upload batches also match how the work arrived: the triad archive on one side, and the toys, grace line, and 2026-11-10 `open_hand` builds on the other. Already-public packages are linked, not duplicated.

## Layout

```
papers/v0.4 .. v0.7     Authoritative (and, where it matters, superseded) paper texts
grace_definitions/      Keel grace definitions v1–v11, plus the 2026-11-09 Matthew 18 answer
grace_toy_v1/           Conductor-built double-well toy of grace v10. NOT normative.
toys/round3_toy/        Falsifier B's v0.6 reference toy (reproduced bit-for-bit)
toys/round4_toy/        Falsifier B's v0.7 battery (reproduced bit-for-bit with cbor2)
open_hand/v1..v3        Conductor-built 2026-11-10 experiments. NOT normative.
reviews/relational-transitions-v0.1/   Conductor review of an already-public package
addenda/commons-dwelling-grace/        ERRATA and a later run not yet in the public repo
received/               Original zips for the new builds
```

## Papers (authoritative hashes)

| Version | File | SHA-256 |
|---|---|---|
| v0.4 (frozen) | `papers/v0.4/Reykjavik_Relational_Grace_v0.4.txt` | `a247652dd5f98365be74245ce6195e06a94673eb4dce48ceb329ca3553903eba` |
| v0.5 (authoritative) | `papers/v0.5/Reykjavik_Relational_Grace_v0.5.txt` | `8ced5fd1833909c218880619daaeea2109fb484d1ea1e5ddb80f245d79f6fd05` |
| v0.6 (assembled) | `papers/v0.6/Reykjavik_Relational_Grace_v0.6.txt` | `e03df96bc0175491c79645c94f0d4fc275d47c1b264d65ced059ccf41766dc1f` |
| v0.7 (assembled) | `papers/v0.7/Reykjavik_Relational_Grace_v0.7.txt` | `0cf7c9a7bac7205c830d492e2f398fe04018d1e22da4c3dddc4388f2ebaaab29` |

Superseded pastes, retracted first blocks, and part files are kept next to those, labeled as such. No v0.8 is included.

## Grace definitions

v1 through v11 are here, as filed in the 2026-11-09 handover's `grace/` folder. v10 (`ec9032c7…f5d9`) was current at the close of Round 4. v11 (`c44be20e…6847`) was written the same afternoon, after Round 4 closed, from the keel's Matthew 18 answer and a further Gospel reading; it is a keel definition, not a Round 5 prompt, but it was intended to be sent onward before v0.8 was finalized. `grace_toy_v1` predates v11 and models v10.

## Reproductions, 2026-11-10, America/Chicago

- `toys/round3_toy`: `python3 experiments.py` matched `raw_output.txt` bit-for-bit.
- `toys/round4_toy`: `python3 battery.py` matched `raw_output.txt` bit-for-bit when `cbor2` 6.2.1 was installed. Without it, the CBOR sha256 is the same and the cross-check field prints `None`.
- `grace_toy_v1`: `python3 grace_toy.py` (~30 s, numpy) wrote `results.json` with sha256 `49e579d9a2c636ea26ea79d68b7ecefd3f86d00a4a707a898299a31a0bd7bc1f`, matching the package README.
- `open_hand` v3's million-member run was not re-run here (the README says about two minutes). Earlier rounds were not required for this staging.

## Already public — do not treat as new projects

- Commons v1 and dwelling_grace (2026-11-09 evening), plus the history-seat review: https://github.com/RMac-triadicIntelligence/commons-dwelling-grace (commit `60f799c`). Two later pieces from the same evening archive are **not** in that repo yet and are staged here as `addenda/commons-dwelling-grace/` (the errata after review, and `grace_state_vs_parametric_full_run/`). They can be added to that repo later rather than starting a third project.
- Relational Transitions v0.1: https://github.com/RMac-triadicIntelligence/relational-transitions-v0.1 (commit `c575fb9`). The conductor review of 2026-11-10 is new and is staged under `reviews/`.
- Lab notebook: https://github.com/RMac-triadicIntelligence/lab-notebook (HEAD `936d813`).

## Dates

Paper and toy work dates are 2026-11-09. `open_hand` and the Relational Transitions review are 2026-11-10 (morning, America/Chicago; the open_hand predictions were hashed for the keel at 7:09, 7:12 and 7:14 AM CT / 13:09–13:14 UTC). Commit dates, if this is later published, will be the publish date.

## Related repositories

- This repo: https://github.com/RMac-triadicIntelligence/triadic-in-action-builds
- Triad record (method, reports, opened seals): https://github.com/RMac-triadicIntelligence/triadic-in-action
- Commons and dwelling grace (already public): https://github.com/RMac-triadicIntelligence/commons-dwelling-grace
- Relational Transitions v0.1 (already public): https://github.com/RMac-triadicIntelligence/relational-transitions-v0.1
- Lab notebook (already public): https://github.com/RMac-triadicIntelligence/lab-notebook

## License

Apache License 2.0. See `LICENSE` and `NOTICE`. Several packages arrived without a license file and are staged here under Apache-2.0 at Rusty's request, with authorship recorded in `NOTICE`.
