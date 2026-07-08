---
id: 0006
title: stop-hook: gate on independent subagent review (not self-attest)
date: 2026-06-24
status: reverted
decided: 2026-07-08
knob: hook
target: hooks/verify-standards.sh
evidence: 2026-06-23 session 512bedf7: Stop hook fired x23, agent rubber-stamped standards self-review ('다 됐다'). Self-attestation can't verify judgment standards; gate now requires transcript evidence of a standards-review subagent since last edit.
review_by: 2026-07-01
tags: [stop-hook,standards,verification,subagent]
---

# stop-hook: gate on independent subagent review (not self-attest)

## Why
2026-06-23 session 512bedf7: Stop hook fired x23, agent rubber-stamped standards self-review ('다 됐다'). Self-attestation can't verify judgment standards; gate now requires transcript evidence of a standards-review subagent since last edit.

## What
Reverted 2026-07-08. Even at `PI_REVIEW_MIN_LINES=10` the Stop gate fired on
nearly every substantive edit — the forced independent review became noise. It
also gated on `docs/standards`, not this repo's `docs/conventions`. Removed the
gate (`verify-standards.sh` + its feeder `mark-code-edit.sh`) in favor of
invoking review skills explicitly (`/code-review`, `code-review-convention`)
when wanted.

## Links
