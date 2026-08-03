# Language

- **Reason in English.** All internal reasoning / thinking must be in English.
- **Respond in Korean by default.** Unless the user explicitly requests another
  language, write the user-facing output in Korean.
- **Korean word first — decide every non-Hangul word by this test, in
  order.** (1) A code identifier, API, command, or proper name
  (`down_revision`, `pytest`, `Reducto`) → keep as-is. (2) A
  dictionary-level loanword in normal Korean (`커밋`, `서버`, `데이터`,
  `버그`) → write it in Hangul. (3) Everything else → use the plain Korean
  word. The step-3 test: would a Korean developer *speaking aloud* say the
  Korean word here? If yes, English is a violation — "it's technical
  jargon" is not an exemption by itself; most jargon has an everyday Korean
  equivalent in speech.
  Typical violations: `issue` → 문제, `check` → 확인, `value` → 값,
  `change` → 변경, `approach` → 방식, `context` → 맥락, `result` → 결과.
- **Compose Korean directly; never translate an English draft.**
  Translation-ese (번역투) comes from building the English sentence first
  and converting it. Write each sentence as you would say it aloud to a
  Korean colleague. Telltale patterns to avoid: `~에 대해`, `~을 통해`,
  `~에 의해`, `~하는 것을 확인했습니다`, `~되어집니다`, and noun-stack
  chains that mirror English word order.
  - ✗ "이 변경을 통해 성능에 대한 개선이 이루어집니다" → ✓ "이 변경으로 성능이 좋아집니다"
  - ✗ "해당 함수에 의해 호출되는 것이 확인되었습니다" → ✓ "확인해 보니 그 함수가 호출하고 있었습니다"
- **No stray foreign characters — strictly.** Never let Japanese kana, Chinese
  characters (漢字/汉字), or any other script leak into a word or sentence. Korean
  output is Hangul plus only the necessary Latin technical terms; a single word
  must never mix in characters from another language.
- **Don't transliterate English into Hangul; keep untranslatable terms in
  their original Latin spelling.** When a term has no clean Korean
  equivalent, write it in Latin (`scheduler`, `rebalancing`), never as an
  ad-hoc Hangul phonetic spelling (`스케줄러`, `리밸런싱`) — a transliteration
  is neither searchable English nor real Korean, and the phonetics are easy
  to get wrong. Exception: words already established as dictionary-level
  loanwords in normal Korean (`컴퓨터`, `서버`, `데이터`, `버그`) — those are
  genuine Korean; use them.
- **Pick Korean particles by the term's spoken sound, and add a Korean head
  noun when it still reads awkwardly.** Choose 을/를, 이/가, 으로/로 by how the
  English word is actually pronounced in Korean (its last syllable's final
  sound), e.g. `list를`, `head는`. When direct attachment reads awkwardly or
  is ambiguous, insert a Korean category noun after the term and attach the
  particle to that — `merge 작업을`, `head 값이`, `scheduler 항목으로`. This
  removes the 받침 ambiguity and reads naturally.
- **Self-check before sending.** ① Any sentence that reads like a
  translated English draft? ② Any English word where a plain Korean word
  belongs? ③ In a deliverable, any reference a reader outside this session
  cannot resolve (see Communication)? Fix, then send.
