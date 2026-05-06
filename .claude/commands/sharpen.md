---
description: Add an item to SHARPEN.md (the sharpen-the-saw backlog)
argument-hint: <item description>
---

Append a single new bullet to `SHARPEN.md` at the project root.

The bullet text is: $ARGUMENTS

Rules:
- Append only. Do not reformat, reorder, or edit any existing content.
- Format: `- $ARGUMENTS` on a new line at the end of the file.
- If `SHARPEN.md` does not exist, create it with `# Sharpen the Saw` as the first line, a blank line, then the bullet.
- If `$ARGUMENTS` is empty, do NOT modify the file. Tell the user the command needs an argument and show them the current contents of SHARPEN.md so they can see what's already on the list.
- After appending, confirm in one short sentence what was added. Do not summarize the whole file.
