---
name: writing-documents
description: Use when asked to write or draft a document others will read — a PRD, design spec, RFC, issue or PR comment, ADR, review note, or similar prose artifact.
---

# Writing Documents

## Overview

A document is read by people who weren't in the conversation that produced it.
Write so a cold reader understands it: plainly, with the reasoning kept — not
compressed into dense jargon.

## 1. Pick the document type

The type is the document's **shape** (what the content is), not where it's
posted. A request often names both — "write this up as an ADR and post it as a
GitHub issue." The shape word (ADR / PRD / design doc / spec) picks the type; the
destination (a GitHub issue, a PR, a file) is only where it goes and does not
change the type. So "post it as an ADR to a GitHub issue" → ADR shape, posted to
an issue — not the proposal-comment shape.

Infer the type from context. If a shape is named or clear, proceed — don't ask.
Ask only when no shape is named and context leaves it genuinely ambiguous.

| Type | Use for | Template |
|---|---|---|
| PRD | product/feature requirements: problem, goals, scope | `templates/prd.md` |
| Design spec | technical design before building: alternatives, trade-offs | `templates/design-spec.md` |
| ADR | one architecture decision, recorded immutably | `templates/adr.md` |
| Proposal / decision comment | a decision or proposal posted to a thread, when **no formal shape above is named** | `templates/proposal-comment.md` |

For anything not in the table, write plain prose using the tone rules below —
don't force-fit a template.

## 2. Draft from the template

Fill the template's sections. Drop sections that don't apply; don't pad to fill
them. The template scaffold (headers) stays in English; write the **content** in
the working language — Korean by default, per the Language standards.

## Tone & manner — what a good document IS

A recipe for the finished shape, not a list of don'ts.

- **Self-explaining, but only for real terms.** Define genuine jargon,
  acronyms, and API names (KQL, ADR) in a short clause at the point they first
  appear, so a reader who wasn't there still follows (same bar as the
  term-tagging rule in the Communication standards). Don't dress a plain phrase
  up as a term: if a phrase already reads plainly, it needs no "this means…"
  preamble. A definition is a few inline words, not a standalone sentence
  opening the section.
- **Decision and reason, balanced.** State what was decided *and* why — both.
  Not a bare conclusion, not rambling rationale.
- **Plain words over jargon.** Don't reach for a technical term to compress;
  the ordinary word reads faster. Density is not brevity — a noun-stack is
  short to write and slow to read.
- **Concise by default, but explain the earned parts.** Keep it tight — except
  any point that was clarified, questioned, or argued during the conversation
  with the requester. Those earned their attention; carry that explanation into
  the document instead of compressing it back out.

## 3. Finalize — review before publishing

When the requester moves to confirm/finalize the draft (e.g. "확정하자",
"let's ship it", "post it"), then BEFORE publishing, dispatch a subagent to
review the document on two lenses — **facts** (hallucinations, unsupported
claims, overstated certainty) and **shape** (thin sections, examples not in code
blocks, places a table or diagram would read faster, manufactured "term:"
definitions). Use `document-review-prompt.md`, passing it the draft and the
context/sources the draft was built from. Fix what it surfaces, then publish.

A fresh subagent catches both, because the author is blind to their own
fabrications and their own bloat. This is a gate at finalize time — not a pass on
every draft.

## Common mistakes

- Compressing reasoning into noun-stacks ("server-side filtering", "byte
  invariant") and calling it done — opaque to a cold reader.
- Stating a conclusion with no why, or why with no conclusion.
- Thin sections that don't earn their place; examples buried in prose instead of
  a code block.
- Publishing a factual or external-facing document without the adversarial pass.
