---
id: 0007
title: evolve-harness extractor reads Claude Code sessions
date: 2026-07-01
status: permanent
knob: skills
target: skills/evolve-harness/signals.py
evidence: signals.py only read ~/.pi/agent/sessions; 2026-06-30 had 0 pi sessions (all work in Claude Code) so retro found nothing. Now scans pi + ~/.claude/projects, sniffs format, normalizes Claude schema (tool_use->toolCall, nested tool_result->toolResult, interrupt sentinel->aborted, isCompactSummary->compaction) + is_injection filter for skill bodies/command tags/hook feedback/task-notification. pi 06-08 totals unchanged; standards-review PASS.
tags: [tooling,evolve-harness,observability]
---

# evolve-harness extractor reads Claude Code sessions

## Why
signals.py only read ~/.pi/agent/sessions; 2026-06-30 had 0 pi sessions (all work in Claude Code) so retro found nothing. Now scans pi + ~/.claude/projects, sniffs format, normalizes Claude schema (tool_use->toolCall, nested tool_result->toolResult, interrupt sentinel->aborted, isCompactSummary->compaction) + is_injection filter for skill bodies/command tags/hook feedback/task-notification. pi 06-08 totals unchanged; standards-review PASS.

## What

## Links
