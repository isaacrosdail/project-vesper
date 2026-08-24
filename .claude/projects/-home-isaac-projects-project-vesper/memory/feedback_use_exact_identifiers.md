---
name: feedback_use_exact_identifiers
description: Never invent/rename identifiers mid-explanation — use the exact names present in the code
metadata:
  type: feedback
---

When referencing variables, properties, functions, or any identifier, use the EXACT name as it currently exists in the file. Never coin a "cleaner" name on the fly while explaining, and never silently substitute a renamed version.

**Why:** Renaming mid-explanation breaks the reader's ability to map advice back to real code — they go looking for `showCompletedToggle`, it doesn't exist, and the whole point gets lost. It reads as careless and erodes trust in the review.

**How to apply:** Quote identifiers verbatim from the current source (re-read if unsure). If proposing a rename, say so explicitly ("rename X to Y") — never just start using Y as if it were already there. Naming is the user's call; surface the existing name, don't impose a new one. Related: [[feedback_no_assumptions]].
