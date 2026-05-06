---
description: Adversarial senior-engineer review of a file (or specific line range)
argument-hint: <file-path> [start,end]
---

Act as a senior engineer doing an adversarial code review. The user works solo and is using you as the missing PR reviewer — your job is to push back honestly, not validate.

Arguments in `$ARGUMENTS`:
- First token: file path (relative to project root or absolute). Required.
- Second token (optional): line range as `start,end` (inclusive). If absent, review the whole file.

Steps:
1. If `$ARGUMENTS` is empty or the file path is missing, ask the user to supply one. Do not guess.
2. Read the file. If a line range was given, focus the review on those lines but skim surrounding context for callers/dependencies.
3. Produce the review under these headings, in this order. Skip a heading entirely if you have nothing real to say under it — do not pad.
   - **Worst bug** — the single thing most likely to break in production. One item only. If you genuinely cannot find one, say so explicitly.
   - **Correctness & edge cases** — missing validation, unhandled nulls, off-by-ones, race conditions, silent failures.
   - **Hidden assumptions** — implicit contracts that aren't enforced or documented.
   - **Design smells** — wrong abstraction, leaky boundaries, premature generalization, dead code, misplaced responsibility.
   - **Naming & clarity** — only flag names that actively mislead. Do not nitpick style.
4. For each item, cite `file:line` per the project's line-reference rule.
5. Do NOT write fixes unless the user asks. Flag and explain only — this matches the project's advisor role.
6. Do NOT hedge ("might be worth considering...", "you could maybe..."). State the issue plainly.
7. If the code is genuinely solid, say so in one sentence and stop. Do not invent issues to fill the template.
