#!/usr/bin/env python3
"""Extract harness-friction signals from a day's pi sessions.

Reads JSONL session files under ~/.pi/agent/sessions and surfaces the moments
that matter for evolving the agent: user corrections, interrupts (aborts),
repeated instructions, frustration markers, gated-git the agent ran on its own,
tool-error loops, and long unattended stretches.

It prints a COMPACT markdown report (quotes truncated, lists capped) so the
caller can reason over signals instead of loading raw sessions into context.

Usage:
    python3 signals.py [--date YYYY-MM-DD] [--grep SUBSTR] [--max N]
"""

import argparse
import datetime as dt
import glob
import json
import os
import re

SESS_ROOT = os.path.expanduser("~/.pi/agent/sessions")
CLAUDE_SESS_ROOT = os.path.expanduser("~/.claude/projects")

# Claude Code marks an aborted turn as a user message carrying this sentinel,
# instead of pi's assistant stopReason="aborted".
CLAUDE_INTERRUPT = "[Request interrupted by user"

# User text that redirects / negates the agent's current course.
CORRECTION = re.compile(
    r"(아니[야요]?\b|그게\s*아니|아닌데|다시\b|왜\s|하지\s*마|멈춰|그만|되돌려|취소|"
    r"\bno[,. ]|\bnot\b|don'?t\b|stop\b|wrong\b|revert\b|undo\b|that'?s not|"
    r"instead\b|rollback)",
    re.IGNORECASE,
)
# Stronger annoyance / repeated-friction markers.
FRUSTRATION = re.compile(
    r"(왜\s*자꾸|몇\s*번|진짜|아\s|짜증|또\b|\?\?+|!!+|제발|자꾸|again\?|seriously|"
    r"come on|ffs|wtf)",
    re.IGNORECASE,
)
# State-mutating git the agent should ask before running (mirrors guardrails).
GATED_GIT = re.compile(
    r"\bgit\s+(commit|push|reset\s+--(hard|merge|keep)|rebase|merge|cherry-pick|"
    r"revert|clean\s+-|branch\s+-[dD]|tag\s+-d|stash\s+(drop|clear))\b"
    r"|\bgh\s+(pr\s+(merge|close)|release\s+(create|delete))\b",
    re.IGNORECASE,
)


def text_of(content):
    """Flatten a message content (str | list of blocks) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                out.append(b.get("text", ""))
        return " ".join(out)
    return ""


# System-injected user-role messages that are NOT human turns: pi skill
# templates, Claude Code slash-command tags, skill bodies, Stop-hook feedback,
# `!`-run local-command echoes, and post-compaction continuation summaries.
INJECTION_PREFIXES = (
    "<skill", "<command-name>", "<command-message>", "<local-command-",
    "<task-notification", "<system-reminder>",
    "base directory for this skill:", "stop hook feedback:",
    "caveat: the messages below were generated",
    "this session is being continued from a previous conversation",
)


def is_injection(text):
    s = text.lstrip()
    if 'location="' in s[:120]:
        return True
    low = s[:200].lower()
    return any(low.startswith(p) for p in INJECTION_PREFIXES)


def clip(s, n=140):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def hhmm(ts):
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
    except Exception:
        return "??:??"


def in_range(ts, start, end):
    try:
        d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().date()
        return start <= d <= end
    except Exception:
        return False


def assistant_action(msg):
    """One-line summary of what the assistant did in a message."""
    tools = []
    txt = ""
    for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
        if b.get("type") == "toolCall":
            name = b.get("name", "?")
            args = b.get("arguments", {}) or {}
            hint = args.get("path") or args.get("file_path") or args.get("command") or ""
            tools.append(f"{name}({clip(str(hint), 40)})" if hint else name)
        elif b.get("type") == "text":
            txt = b.get("text", "") or txt
    if tools:
        return "→ " + ", ".join(tools[:3])
    if txt:
        return clip(txt, 90)
    return "(no visible action)"


def _raw_lines(path):
    """Yield parsed JSON objects from a JSONL session file, skipping junk."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def is_claude_format(path):
    """Claude Code sessions have no pi 'session' header; their turns are
    top-level type=user/assistant with an Anthropic-style message block."""
    for o in _raw_lines(path):
        t = o.get("type")
        if t == "session":
            return False
        if t in ("user", "assistant") and isinstance(o.get("message"), dict):
            return True
        if t in ("model_change", "compaction"):
            return False
    return False


def _norm_claude_blocks(content):
    """Anthropic content list -> pi-shaped block list (toolCall/text) + the
    tool_result blocks split out (Claude nests tool results inside user turns)."""
    pi_blocks, tool_results, texts = [], [], []
    if isinstance(content, str):
        texts.append(content)
        pi_blocks.append({"type": "text", "text": content})
        return pi_blocks, tool_results, texts
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            bt = b.get("type")
            if bt == "text":
                texts.append(b.get("text", ""))
                pi_blocks.append({"type": "text", "text": b.get("text", "")})
            elif bt == "tool_use":
                pi_blocks.append({"type": "toolCall", "name": b.get("name", "?"),
                                  "arguments": b.get("input", {}) or {}})
            elif bt == "tool_result":
                tool_results.append(b)
    return pi_blocks, tool_results, texts


def read_claude(path, start, end):
    """Read a Claude Code session, normalizing to pi-shaped entries that the
    common analysis loop understands. Returns (header, entries, touched_date)."""
    header = None
    entries = []
    touched_date = False
    tool_name_by_id = {}  # tool_use_id -> tool name, for labeling tool_result errors
    last_assistant = None  # to retro-mark an interrupt onto the turn it aborted

    for o in _raw_lines(path):
        t = o.get("type")
        ts = o.get("timestamp", "")
        if header is None and o.get("cwd"):
            header = {"type": "session", "cwd": o.get("cwd")}
        if ts and in_range(ts, start, end):
            touched_date = True

        if o.get("isCompactSummary") or (t == "system" and o.get("subtype") == "compact"):
            entries.append({"type": "compaction", "timestamp": ts})
            continue
        if t not in ("user", "assistant"):
            continue

        msg = o.get("message", {})
        if t == "assistant":
            for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id"):
                    tool_name_by_id[b["id"]] = b.get("name", "?")
            pi_blocks, _, _ = _norm_claude_blocks(msg.get("content"))
            entry = {"type": "message", "timestamp": ts,
                     "message": {"role": "assistant", "model": msg.get("model"),
                                 "stopReason": msg.get("stop_reason"), "content": pi_blocks}}
            entries.append(entry)
            last_assistant = entry
            continue

        # user turn: may be real text, an interrupt sentinel, or nested tool results
        _, tool_results, texts = _norm_claude_blocks(msg.get("content"))
        joined = " ".join(texts).strip()
        if joined and CLAUDE_INTERRUPT in joined:
            if last_assistant is not None:
                last_assistant["message"]["stopReason"] = "aborted"
            remainder = joined.split("]", 1)[-1].strip()
            if len(remainder) > 8:  # user redirected right after aborting
                entries.append({"type": "message", "timestamp": ts,
                                "message": {"role": "user", "content": remainder}})
            continue
        if joined:
            entries.append({"type": "message", "timestamp": ts,
                            "message": {"role": "user", "content": joined}})
            continue
        for b in tool_results:  # tool-result-only user turn -> toolResult entries
            entries.append({"type": "message", "timestamp": ts,
                            "message": {"role": "toolResult",
                                        "isError": bool(b.get("is_error")),
                                        "toolName": tool_name_by_id.get(b.get("tool_use_id"), "?"),
                                        "content": b.get("content", "")}})
    return header, entries, touched_date


def read_pi(path, start, end):
    """Read a pi session. Returns (header, entries, touched_date)."""
    header = None
    entries = []
    touched_date = False
    for o in _raw_lines(path):
        if o.get("type") == "session":
            header = o
            continue
        ts = o.get("timestamp", "")
        if in_range(ts, start, end):
            touched_date = True
        entries.append(o)
    return header, entries, touched_date


def analyze(path, start, end):
    """Return a dict of signals for one session, or None if not in [start, end]."""
    if is_claude_format(path):
        header, entries, touched_date = read_claude(path, start, end)
    else:
        header, entries, touched_date = read_pi(path, start, end)
    if not touched_date:
        return None

    model = None
    n_user = n_asst = n_tool = n_err = n_compact = 0
    aborts, corrections, frustration, gated, error_loops, long_runs = [], [], [], [], [], []
    repeats = []

    seen_user = {}  # normalized -> (count, first_quote)
    last_asst = "(start)"  # last assistant action summary
    streak = 0  # consecutive non-user entries
    user_seen = 0  # how many real user turns so far
    err_run = {"name": None, "n": 0, "snippet": ""}

    for o in entries:
        typ = o.get("type")
        ts = o.get("timestamp", "")
        if typ == "model_change":
            model = o.get("modelId", model)
            continue
        if typ == "compaction":
            n_compact += 1
            continue
        if typ != "message":
            continue
        msg = o.get("message", {})
        role = msg.get("role")

        if role == "assistant":
            model = model or msg.get("model")
            n_asst += 1
            streak += 1
            if msg.get("stopReason") == "aborted":
                aborts.append((hhmm(ts), assistant_action(msg)))
            last_asst = assistant_action(msg)
            # detect gated git inside tool calls
            for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if b.get("type") == "toolCall":
                    cmd = str((b.get("arguments") or {}).get("command", ""))
                    if cmd and GATED_GIT.search(cmd):
                        gated.append((hhmm(ts), clip(cmd, 80)))

        elif role == "toolResult":
            n_tool += 1
            streak += 1
            if msg.get("isError"):
                n_err += 1
                name = msg.get("toolName", "?")
                snip = clip(text_of(msg.get("content", [])), 80)
                if err_run["name"] == name:
                    err_run["n"] += 1
                    err_run["snippet"] = snip
                else:
                    if err_run["n"] >= 3:
                        error_loops.append((err_run["name"], err_run["n"], err_run["snippet"]))
                    err_run = {"name": name, "n": 1, "snippet": snip}
            else:
                if err_run["n"] >= 3:
                    error_loops.append((err_run["name"], err_run["n"], err_run["snippet"]))
                err_run = {"name": None, "n": 0, "snippet": ""}

        elif role == "bashExecution":
            streak += 1
            cmd = msg.get("command", "")
            if cmd and GATED_GIT.search(cmd):
                gated.append((hhmm(ts), clip(cmd, 80)))

        elif role == "user":
            n_user += 1
            t = text_of(msg.get("content", ""))
            if not t.strip():
                streak += 1
                continue
            # System-injected turns (skill bodies, command tags, hook feedback,
            # local-command echoes) are not human input: they must not reset the
            # autonomous-streak counter, nor count as corrections/repeats.
            if is_injection(t):
                continue
            if streak >= 12:
                long_runs.append((hhmm(ts), streak, last_asst))
            streak = 0
            user_seen += 1
            q = clip(t, 140)
            # The first user turn is the task spec, not a correction.
            if user_seen > 1:
                if CORRECTION.search(t):
                    corrections.append((hhmm(ts), q, last_asst))
                if FRUSTRATION.search(t):
                    frustration.append((hhmm(ts), q))
            norm = re.sub(r"\W+", " ", t.lower()).strip()[:60]
            if norm and len(norm) > 8:
                if norm in seen_user:
                    seen_user[norm][0] += 1
                else:
                    seen_user[norm] = [1, q]

    if err_run["n"] >= 3:
        error_loops.append((err_run["name"], err_run["n"], err_run["snippet"]))
    for norm, (cnt, q) in seen_user.items():
        if cnt >= 2:
            repeats.append((cnt, q))

    if not any([aborts, corrections, frustration, gated, error_loops, long_runs, repeats]):
        return {"empty": True, "header": header, "model": model, "cwd": header.get("cwd") if header else "?",
                "counts": (n_user, n_asst, n_tool, n_err, n_compact)}

    return {
        "empty": False,
        "path": path,
        "cwd": header.get("cwd") if header else "?",
        "model": model,
        "counts": (n_user, n_asst, n_tool, n_err, n_compact),
        "aborts": aborts,
        "corrections": corrections,
        "frustration": frustration,
        "gated": gated,
        "error_loops": error_loops,
        "long_runs": long_runs,
        "repeats": repeats,
    }


def render(results, start, end, maxn, totals_only=False):
    tot = {k: 0 for k in ["aborts", "corrections", "frustration", "gated", "error_loops", "long_runs", "repeats"]}
    active = [r for r in results if r and not r.get("empty")]
    quiet = [r for r in results if r and r.get("empty")]
    for r in active:
        for k in tot:
            tot[k] += len(r.get(k, []))

    span = start.isoformat() if start == end else f"{start.isoformat()} … {end.isoformat()}"
    days = (end - start).days + 1
    print(f"# Harness-friction report — {span}  ({days}d, all projects)")
    print(f"\nSessions with friction: {len(active)} | quiet sessions: {len(quiet)}")
    print("\n**Signal totals:** " + (", ".join(f"{k}={v}" for k, v in tot.items() if v) or "(none)"))
    if totals_only:
        return

    def emit(title, rows, fmt):
        if not rows:
            return
        print(f"\n**{title}** ({len(rows)})")
        for row in rows[:maxn]:
            print("  - " + fmt(row))
        if len(rows) > maxn:
            print(f"  - … +{len(rows) - maxn} more")

    for r in active:
        proj = os.path.basename(r["cwd"].rstrip("/")) or r["cwd"]
        u, a, t, e, c = r["counts"]
        print(f"\n## {proj}  ·  {r['model'] or '?'}  ·  {u}u/{a}a/{t}tool/{e}err/{c}compact")
        print(f"`{r['path']}`")
        emit("⎋ Interrupts (user hit Esc)", r["aborts"], lambda x: f"{x[0]}  was: {x[1]}")
        emit("↩ Corrections / redirects", r["corrections"],
             lambda x: f"{x[0]}  user: \"{x[1]}\"  (after: {x[2]})")
        emit("⟳ Repeated instructions", r["repeats"], lambda x: f"×{x[0]}  \"{x[1]}\"")
        emit("✻ Frustration markers", r["frustration"], lambda x: f"{x[0]}  \"{x[1]}\"")
        emit("⚠ Gated git the agent ran", r["gated"], lambda x: f"{x[0]}  `{x[1]}`")
        emit("✖ Tool-error loops", r["error_loops"], lambda x: f"{x[0]} ×{x[1]}  {x[2]}")
        emit("∞ Long unattended stretches", r["long_runs"],
             lambda x: f"{x[0]}  {x[1]} steps w/o user input, last: {x[2]}")

    if quiet:
        print("\n## Quiet sessions (no friction signals)")
        for r in quiet:
            proj = os.path.basename(r["cwd"].rstrip("/")) or r["cwd"]
            print(f"  - {proj}  ({r['counts'][0]}u/{r['counts'][1]}a)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="single day YYYY-MM-DD (local); default today if no range")
    ap.add_argument("--since", default="", help="range start YYYY-MM-DD (local)")
    ap.add_argument("--until", default="", help="range end YYYY-MM-DD (local); default today")
    ap.add_argument("--grep", default="", help="only sessions whose cwd path contains this substring")
    ap.add_argument("--root", default="", help="scan only this session root; default scans both pi and Claude Code")
    ap.add_argument("--max", type=int, default=6, help="max rows printed per signal list")
    ap.add_argument("--totals", action="store_true", help="print only the summary totals (for before/after comparison)")
    args = ap.parse_args()
    if args.since:
        start = dt.date.fromisoformat(args.since)
        end = dt.date.fromisoformat(args.until) if args.until else dt.date.today()
    else:
        day = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
        start = end = day

    roots = [args.root] if args.root else [SESS_ROOT, CLAUDE_SESS_ROOT]
    files = []
    for root in roots:
        files += glob.glob(os.path.join(root, "*", "*.jsonl"))
    # cheap pre-filter by mtime within a generous window around the range
    lo = dt.datetime.combine(start, dt.time.min).timestamp() - 6 * 3600
    hi = dt.datetime.combine(end, dt.time.max).timestamp() + 6 * 3600
    files = [f for f in files if lo <= os.path.getmtime(f) <= hi]
    if args.grep:
        files = [f for f in files if args.grep in f]

    results = [analyze(f, start, end) for f in sorted(files)]
    results = [r for r in results if r]
    if not results:
        span = start.isoformat() if start == end else f"{start}..{end}"
        print(f"No sessions found for {span}"
              + (f" matching '{args.grep}'" if args.grep else "") + ".")
        return
    render(results, start, end, args.max, totals_only=args.totals)


if __name__ == "__main__":
    main()
