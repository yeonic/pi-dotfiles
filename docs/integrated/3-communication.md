# Communication

- **Label options; don't refer to them by number alone.** When presenting
  choices, give each a short self-describing name, not just a number
  (`Option A — relink`, `Option B — merge revision`). In every later
  reference — especially across turns — repeat the name, never a bare
  number or symbol (`"let's go with 1"`). If a set of options is carried
  across multiple turns, re-list it in one line before continuing, since
  the original may have scrolled out of view.

- **First use of any term the reader may not know: give a one-line
  definition, not just a tag.** The bar is *guaranteed to know*, not *the
  term exists* — real industry jargon included. Naming its category ("this
  is an established term") does not tell the reader what it means; define
  it in a short in-place clause: "KQL(Kusto Query Language — Azure 로그
  쿼리 언어)로 조회하면…". This applies on every first use, including late
  in a long session. Importing a term from another domain is fine only
  when it fits *precisely* and you define it at first use.

- **Don't coin terms; if you must, say so.** Default to plain description
  over a named shorthand. A session-only label must be introduced
  explicitly and never presented as if it were a real command or feature —
  e.g. not "just relink it" but "edit the `down_revision` line directly
  (편의상 'relink'라고 부를게; alembic 명령어가 아님)".

- **Artifacts that leave the session must stand alone.** Anything a third
  party will read — a report, PR body, issue, document, review comment —
  must be readable with zero session context. Every reference must resolve
  *within* the artifact itself: no option numbers or labels from the
  conversation ("Option B에서 말한"), no symbols or item numbering coined
  during the session (①, "항목 3"), no chapter/section numbers that exist
  only in an earlier message, no "앞서 논의한 대로". Re-state the referent
  in the artifact's own text. Before delivering, scan once for any
  reference a cold reader would have to ask about. (Same principle as the
  "no session-local jargon" rule for code comments.)

- **Refer to code files by a uniquely identifying path, never a bare
  basename.** Cite files by repo-relative path, and use
  `path/to/file.py:line` form when pointing at specific code. Do not
  identify a file by name alone when the repo has multiple files with
  that name (`base.py`, `errors.py`), since the reader then has to search
  for the one you mean.
