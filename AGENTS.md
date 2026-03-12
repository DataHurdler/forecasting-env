# AGENTS.md

## Repository Intent
This repository is a shared coding-homework environment for a graduate forecasting class.  
Students run Codex locally against this repo.

## Agent Priorities
- Follow assignment instructions exactly before adding extras.
- Keep solutions reproducible and easy to grade.
- Explain technical outputs in business language.
- Make assumptions explicit and checkable.

## Audience Standard
- MBA: concise business interpretation and decision impact.
- Data Science: clear methods, metrics, and code quality.
- Economics: defensible assumptions and economic rationale.

## Folder Contract
- `assignments/`: official prompts, rubrics, and templates.
- `submissions/`: student or team deliverables by homework.
- `data/raw/`: course-provided data, never edited in place.
- `data/processed/`: student-generated cleaned data.
- `notebooks/`: exploratory and analysis notebooks.
- `src/`: reusable code utilities.

## Working Rules
- Do not modify assignment prompts unless asked by instructor.
- Do not overwrite raw data files.
- Prefer small, auditable changes over large rewrites.
- Keep dependency/setup assumptions inside each assignment deliverable.
- Do not commit secrets, tokens, or private datasets.

## Deliverable Minimum
Each homework submission should include:
- a reproducible analysis artifact (`.ipynb` and/or `.py`),
- a short `REPORT.md` covering objective, method, results, and recommendation,
- at least one baseline model and one comparison model,
- evaluation metrics with brief interpretation.

## Naming Conventions
- Submission folder: `submissions/hwNN_<student_or_team_name>/`
- Notebook: `hwNN_<topic>.ipynb`
- Report: `REPORT.md`
- Scripts/modules: lowercase snake_case
