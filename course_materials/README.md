# Course materials

Reference material for ITSS/OPRE 3312. It's kept here so the squad (and Claude) can see what each week asked for.

```
course_materials/
├─ slides/          # lecture decks, named NN-ITSS-OPRE3312-<Title>.pptx
└─ claude_notes/    # Markdown notes Claude reads before working on the project
```

## Slides on file

| Week | Deck | Notes |
|---|---|---|
| 3 | `03-ITSS-OPRE3312-The_First_Filter_Conditionals_Loops.pptx` | [week03_first_filter.md](claude_notes/week03_first_filter.md) |
| 4 | `04-ITSS-OPRE3312-Evidence_Lockers_Lists_Sets_Dicts.pptx` | [week04_evidence_lockers.md](claude_notes/week04_evidence_lockers.md) |
| Midterm | *(deck not on file yet)* | [midterm_cold_case_file.md](claude_notes/midterm_cold_case_file.md) |
| 8 | `08-ITSS-OPRE3312-Pro_Workflow_Branching_Packages.pptx` | [week08_pro_workflow.md](claude_notes/week08_pro_workflow.md) |

Missing decks: weeks 1, 2, 5, 6, 7 and the midterm. Drop them into `slides/` using the same naming pattern.

## Adding a new week

1. Put the deck in `slides/` as `NN-ITSS-OPRE3312-<Title>.pptx`.
2. Ask Claude to read it and write `claude_notes/weekNN_<topic>.md` in the same format as the existing notes.
3. Add a row to the table above and to the index in [claude_notes/00_project_context.md](claude_notes/00_project_context.md).
