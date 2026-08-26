# ECON 8310 — Homework Repository

Business Forecasting · University of Nebraska at Omaha · Fall 2026

**New here? Read [STUDENT_QUICKSTART.md](STUDENT_QUICKSTART.md).**

Course website: <https://datahurdler.github.io/Forecasting-Course/>

---

## What is in here

| Folder | What it holds |
|---|---|
| `assignments/` | The eleven homework assignments, as `.qmd` files. Copy one out; do not edit it in place. |
| `data/processed/` | The prepared datasets every assignment reads. Already built for you. |
| `scripts/` | Data preparation, and `check_my_submission.py` to run before you push. |
| `submissions/` | Your work. One folder per assignment. |
| `policy/` | Prompt budgets and read-only paths. |
| `QUARTO_GUIDE.md` | Setting up VS Code and Quarto, and how to work in a `.qmd`. **Start here.** |
| `AI_POLICY.md` | How to use an AI assistant on this course. Read it once. |

---

## The short version

1. Copy the assignment from `assignments/` into `submissions/<assignment>_<yourname>/`
2. Send its **Initial Prompt** to your AI assistant; save it as `INITIAL_PROMPT.md`
3. Do the work, keeping a `PROMPT_LOG.md` as you go
4. `quarto render` your `.qmd`
5. `python scripts/check_my_submission.py`
6. Commit and push — or upload through github.com if you prefer

---

## Folder naming

Name your folder for the assignment exactly as the assignment names itself, then your name:

```
submissions/hw01_part1_jsmith/
submissions/hw05_part2_jsmith/
submissions/hw07_jsmith/
```

Each submission folder should end up containing:

- your completed `.qmd`
- the rendered `.html`
- `PROMPT_LOG.md`
- `INITIAL_PROMPT.md`
- `REPORT.md`, where the assignment asks for one

`check_my_submission.py` verifies all of this.

---

## Do not edit

`assignments/`, `policy/`, and `AGENTS.md` are read-only. If you think something in them is wrong,
tell me — you may well be right, but do not fix it locally, because your grade is checked against
the originals.

---

## For instructors

Validate a student repository against this canonical copy:

```bash
python scripts/validate_submission.py \
  --student-root /path/to/student/repo \
  --reference-root . \
  --homework hw01_part1
```
