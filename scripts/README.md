# Scripts

## validate_submission.py
Instructor-side validator for final submissions.

Example:
```bash
python scripts/validate_submission.py \
  --student-root /path/to/student/repo \
  --reference-root /path/to/instructor/canonical/repo \
  --homework hw01
```

Checks:
- locked files/directories unchanged (compared to canonical reference repo),
- required submission files present,
- `INITIAL_PROMPT.md` matches required initial prompt text,
- prompt log format and sequential prompt ids,
- budgeted prompt count does not exceed policy limit (default excludes initial contract prompt),
- one commit per prompt when commit policy is enabled,
- commit messages match format: `hwNN prompt <id>: <short summary>`.

Note: commit-per-prompt checks require student `.git` history to be available.
