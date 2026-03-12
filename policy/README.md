# Policy

This folder defines grading policy used by instructor-side validation.

## Files
- `homework_limits.json`: prompt budget and required files.
- `locked_paths.txt`: files/directories that should remain unchanged in student submissions.
- `homework_limits.json` also defines commit-per-prompt policy.

## Important Enforcement Note
Students can still edit local files on their own machines.  
Enforcement happens when the instructor validates the final submission against the canonical reference repository.
Strict commit-per-prompt verification requires the student repository to include `.git` history.
