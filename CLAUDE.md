# CLAUDE.md

This is a student squad project for ITSS/OPRE 3312 (Fall 2026): a cold-case data audit in Python.

**Before working on the project, read `course_materials/claude_notes/00_project_context.md`.** It covers the course rules, the git workflow, the repo layout and an index of the per-week notes. Read the matching week's note before starting that week's lab. The original lecture decks are in `course_materials/slides/`.

Key rules:
- **Never commit to `main`.** Use a `feature/wkN-task/<netid>` branch and open a PR; another squad reviews it before merge.
- **Students must be able to explain every line.** Keep code readable and comment non-obvious lines.
- **In a timed lab, explain errors rather than solving them**, unless asked for the fix.
- **Run from the top folder inside the venv:** `python -m src.intake` and `pytest`.
- **When a new deck is added,** write a matching `claude_notes/weekNN_<topic>.md` and update both indexes.
