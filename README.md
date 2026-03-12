# Forecasting-Env

GitHub classroom repository for graduate business forecasting homework.  
Students clone this repo to their own machines and use Codex as their coding assistant.

## Purpose
- Central place for coding homework and project submissions.
- Shared structure across MBA, Data Science, and Economics students.
- Consistent standards for reproducibility and business interpretation.

## Student Start (Codex-first)
1. Clone your course repo copy locally.
   If you downloaded a zip instead, run `git init` in the repo before using Codex.
2. Open the folder in Codex.
3. Read `AGENTS.md` before starting work.
4. Send the exact required initial prompt in `prompts/REQUIRED_INITIAL_PROMPT.md`.
5. Open the current assignment in `assignments/`.
6. Complete code and writeup in your assignment folder.
7. Commit and push your work.

## Repository Structure
- `AGENTS.md`: repository rules for students and coding agents.
- `assignments/`: assignment prompts, templates, and rubrics.
- `submissions/`: student work folders by assignment.
- `prompts/`: required prompt text students must use to initialize Codex.
- `policy/`: instructor policy (prompt limits, locked paths).
- `scripts/validate_submission.py`: instructor-side validation script.
- `data/raw/`: provided datasets (read-only source copies).
- `data/processed/`: cleaned datasets created by students.
- `notebooks/`: exploratory and analysis notebooks.
- `src/`: reusable code modules.

## Suggested Homework Flow
1. Start from `assignments/HW_TEMPLATE.md`.
2. Create a folder like `submissions/hw01_<student_or_team_name>/`.
3. Add code in notebooks and/or `src/`.
4. Keep `INITIAL_PROMPT.md` and `PROMPT_LOG.jsonl` in the submission folder.
5. Create one git commit after each prompt with message: `hwNN prompt <id>: <short summary>`.
6. Keep prompt usage within the assignment limit (excluding the initial contract prompt).
7. Include a short `REPORT.md` with business conclusions.
8. Push changes with clear commit messages.

## Notes for Instructors
- Keep assignment prompts and grading rubrics inside `assignments/`.
- Use a common naming convention for easy grading and automation.
- Keep datasets versioned and documented.
- For strict commit-per-prompt enforcement, validate against a student git repo (not a zip copy without `.git`).
- Validate submissions against your canonical repo copy:
  ```bash
  python scripts/validate_submission.py \
    --student-root /path/to/student/repo \
    --reference-root /path/to/this/canonical/repo \
    --homework hw01
  ```
