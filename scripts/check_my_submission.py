#!/usr/bin/env python3
"""Check your homework submission before you upload it to Canvas.

    python scripts/check_my_submission.py

No arguments needed. Run it from the top level of your repository. It looks at every folder
in submissions/, tells you what is missing, and counts your prompts.

Nothing here is a grade. It is a checklist so you do not lose marks to something mechanical.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBS = ROOT / "submissions"
POLICY = ROOT / "policy" / "homework_limits.json"

G, Y, R, B, X = "\033[32m", "\033[33m", "\033[31m", "\033[1m", "\033[0m"
def ok(m):   print(f"  {G}ok{X}    {m}")
def warn(m): print(f"  {Y}note{X}  {m}")
def bad(m):  print(f"  {R}FIX{X}   {m}")

def budgets() -> dict:
    try:
        p = json.loads(POLICY.read_text(encoding="utf-8"))
        return {k: v.get("max_prompts") for k, v in p.get("homeworks", {}).items()}
    except Exception:
        return {}

def count_prompts(log: pathlib.Path) -> int | None:
    try:
        return len(re.findall(r"^###\s+Prompt\s+\d+", log.read_text(encoding="utf-8"), re.M))
    except Exception:
        return None

def check(folder: pathlib.Path, buds: dict) -> int:
    print(f"\n{B}{folder.name}{X}")
    problems = 0
    stem = folder.name.rsplit("_", 1)[0] if "_" in folder.name else folder.name
    hw = next((k for k in sorted(buds, key=len, reverse=True) if folder.name.startswith(k + "_")), stem)

    qmd  = list(folder.glob("*.qmd"))
    html = list(folder.glob("*.html"))
    if qmd: ok(f"found {qmd[0].name}")
    else:   bad("no .qmd file — put your completed assignment here"); problems += 1
    if html: ok(f"found {html[0].name}")
    else:    bad("no .html — render your .qmd before submitting"); problems += 1

    if qmd and html and html[0].stat().st_mtime < qmd[0].stat().st_mtime:
        bad("your .html is OLDER than your .qmd — re-render, you have edits that are not in it")
        problems += 1
    elif qmd and html:
        ok("your .html is newer than your .qmd")

    log = folder / "PROMPT_LOG.md"
    if log.exists():
        n = count_prompts(log)
        if not n:
            bad("PROMPT_LOG.md has no '### Prompt <n>' entries — check the format"); problems += 1
        else:
            limit = buds.get(hw)
            if limit is None:                 ok(f"PROMPT_LOG.md lists {n} prompts")
            elif n <= limit:                  ok(f"PROMPT_LOG.md lists {n} prompts (budget {limit})")
            else:
                warn(f"PROMPT_LOG.md lists {n} prompts, budget is {limit} — that is allowed. "
                     "Add a line at the end saying where you got stuck.")
    else:
        bad("no PROMPT_LOG.md — see the assignment for the format"); problems += 1

    if (folder / "INITIAL_PROMPT.md").exists(): ok("found INITIAL_PROMPT.md")
    else: bad("no INITIAL_PROMPT.md — save the prompt you started your AI session with"); problems += 1

    if (folder / "REPORT.md").exists(): ok("found REPORT.md")
    else: warn("no REPORT.md — most assignments want one; check yours")
    return problems

def main() -> int:
    if not SUBS.exists():
        print(f"{R}No submissions/ folder found.{X} Run this from the top of your repository."); return 1
    folders = sorted(f for f in SUBS.iterdir() if f.is_dir() and not f.name.startswith("."))
    if not folders:
        print(f"{Y}submissions/ is empty.{X} Make a folder like submissions/hw01_part1_yourname/"); return 1

    print(f"{B}Checking {len(folders)} submission folder(s){X}")
    total = sum(check(f, budgets()) for f in folders)
    print()
    if total == 0:
        print(f"{G}Nothing to fix. Upload these files to the Canvas assignment.{X}")
    else:
        print(f"{R}{total} thing(s) to fix{X} before you submit. Notes are advisory; FIX lines are not.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
