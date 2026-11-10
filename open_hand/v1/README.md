# open_hand: one question
Built by the conductor (Claude), 2026-11-10. NOT normative. Run: `python3 open_hand.py` (numpy, 5 s).
PREDICTIONS.md (sha256 5e6aa5924f727ee33c7a4792045cf27a927e5eea5c2cf0edfa670221bb895379) and open_hand.py
(sha256 fb1c28f9efd5cb819487601865dd6bbdedcbef015788a05b9615745f4bb5decf) were hashed and shown to
the keel at 13:09 UTC, before the first run. results.json sha256 e6deb22b...4871.

Share of member-days in want (5 seeds, steps 500-3000):
| Rain vs total need | OPEN all / dry half | ASKED all / dry half | BARNS all / dry half |
|---|---|---|---|
| 1.3x | 0% / 0% | 42% / 84% | 48% / 97% |
| 1.0x | 5% / 10% | 45% / 89% | 49% / 99% |
| 0.8x | 25% / 51% | 47% / 93% | 50% / 100% |

Committed predictions: OH1, OH2, OH3 all held. They were safe bets: OH3 is true by construction, and
OH1/OH2 follow from "all excess moves on" once total rain exceeds total need.
The information is in what was not predicted (see the open ledger, entries 15-17).
Assumptions to attack: a ring with two neighbours; rain on one contiguous half; the ASKED rule (one
neighbour, half of holdings, only when in want); excess passed on in full, every step; no cost to
passing on; needs and hand sizes fixed.
