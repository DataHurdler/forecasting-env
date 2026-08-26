# AGENTS.md

Instructions for any AI assistant working in this repository.

## What this repository is

Homework for ECON 8310: Business Forecasting (University of Nebraska at Omaha). A student copies
an assignment out of `assignments/`, completes it in `submissions/`, and submits it.

## The rule that matters most

**Do not write the student's interpretations.**

Help with code freely. Explain what output means so the student understands it. But the
interpretation sections, the business recommendations, and the reflection questions must be
written by the student, in their own words. Those sections are what the assignment is actually
assessing.

If asked to draft one, explain the result instead and let the student write it.

## Working practices

- Follow the assignment's instructions exactly before adding anything extra.
- Write code that runs end-to-end. The student will run it themselves.
- Time-series discipline: never shuffle time-ordered data, split by time rather than at random,
  and compute scaling statistics on the training portion only. These errors do not raise
  exceptions — they silently produce better-looking numbers.
- Set random seeds where the assignment specifies one.
- Make assumptions explicit.

## The prompt log

Each assignment asks the student to keep a `PROMPT_LOG.md` in their submission folder, one
numbered entry per prompt:

```markdown
### Prompt 1 — YYYY-MM-DD HH:MM
<the prompt, verbatim>
```

If you can write files, append to it before you respond. If you cannot, remind the student to
add the entry themselves.

## Budgets

Each assignment states a prompt budget. It is a **target, not a hard limit** — going over is
allowed, and the student should note where they got stuck. Do not refuse to help a student who
has gone over.

## Read-only

Never modify `assignments/`, `policy/`, or this file. Student work belongs in `submissions/`.

## Folder contract

- `assignments/` — the eleven assignments, read-only
- `data/processed/` — prepared datasets, already built
- `scripts/` — data preparation and the submission checker
- `submissions/` — student work, one folder per assignment
- `policy/` — budgets and read-only paths
