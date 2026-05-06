---
description: Print the current contents of SHARPEN.md
---

Read `SHARPEN.md` at the project root and display its contents to the user.

Rules:
- Read-only. Do not modify the file.
- If `SHARPEN.md` does not exist, say so plainly and suggest using `/sharpen <item>` to start the list.
- If the file exists but contains no bullet items (only the heading or whitespace), say "SHARPEN.md exists but is empty" and stop.
- Otherwise, print the file contents verbatim and prefix with the count of bullet items, e.g. "**3 items on the list:**".
- Do not summarize, reword, or comment on the items. The user is reading their own list.
