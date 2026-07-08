# Communication

- **Label options; don't refer to them by number alone.** When presenting
  choices, give each a short self-describing name, not just a number
  (`Option A — relink`, `Option B — merge revision`). In every later
  reference — especially across turns — repeat the name, never a bare
  number or symbol (`"let's go with 1"`). If a set of options is carried
  across multiple turns, re-list it in one line before continuing, since
  the original may have scrolled out of view.

- **Don't coin terms, and tag ANY non-plain label on first use — real
  jargon included.** Default to plain description over a named shorthand.
  When a short label is genuinely useful, the first time it appears state
  which it is: (a) an actual command / feature / API name, (b) an
  established industry term, or (c) a label you are coining only for this
  conversation. The tag is required even for (b) — "it's a real term" is
  not a license to drop it untagged; the test is whether the reader is
  *guaranteed to know it*, not whether it exists. Using a label repeatedly
  across a long or multi-turn session without ever tagging it is the same
  violation, just spread out. Importing a term from another domain is fine
  only when it fits *precisely* and you define it on first use; importing
  it because it loosely fits, or using it without that explanation, is the
  violation (e.g. a DB-query term dropped unexplained into an email-tool
  spec). Never present a coined word as if it were a real command or
  feature — e.g. not "just relink it" but "edit the `down_revision` line
  directly (I'm calling this 'relink' for short; it is not an alembic
  command)".

- **Refer to code files by a uniquely identifying path, never a bare
  basename.** Cite files by repo-relative path, and use
  `path/to/file.py:line` form when pointing at specific code. Do not
  identify a file by name alone when the repo has multiple files with
  that name (`base.py`, `errors.py`), since the reader then has to search
  for the one you mean.
