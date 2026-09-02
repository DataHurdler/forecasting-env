# Using AI on ECON 8310 Homework

This course expects you to use an AI assistant. This page says how.

---

## Any tool is fine

ChatGPT, Claude, Gemini, GitHub Copilot, Codex — in an editor or in a browser tab. Use what you
have. UNO's ChatGPT Edu workspace does **not** include Codex, so nothing in these assignments
requires it; every initial prompt is written for whatever assistant you have.

If your tool cannot run code or write files, you will copy code across, run it yourself, and paste
results back. **That is a perfectly good way to do this course**, and arguably a better one: you
will see every error message with your own eyes, which is where a lot of the learning is.

**If you want an assistant inside your editor**, GitHub Copilot is free for verified students
through [GitHub Education](https://education.github.com/) and works natively in VS Code. Apply
early rather than the night before Homework 1 — eligibility is verified, and it is re-checked
periodically.

---

## Working in a browser chat

Everything below applies if your assistant lives in a browser tab and cannot touch your files.

**You do not need to share the data.** Every assignment's initial prompt already describes the
dataset column by column — that is why it is written the way it is. An assistant can write correct
code for `m5_weekly.csv` without ever seeing the file. If something looks wrong and you want the
assistant to see the data, paste the output of `df.head()` and `df.dtypes`. That is almost always
enough.

**If you do upload the file, upload it so the assistant can *see* it, not so it can *run* it.**
The prepared files are small enough to attach — `m5_weekly.csv` is 657 KB — and a chat assistant
will happily run an analysis on an uploaded copy and hand you finished numbers and plots. Those
numbers came out of its environment, not yours.

> **What is graded is the interpretation of your own output.** Your `.qmd` has to render on your
> machine, and your written answers have to follow from the numbers *that render* produced. A
> result you got from a chat sandbox and cannot reproduce locally is worse than a modest result
> you can.

**The file and git rules are yours.** Each assignment's initial prompt tells the assistant where to
put files and how to commit. A browser chat cannot do either — so it should tell you what to write
and what to commit, and you do it. That costs nothing in marks. Submitting through the browser
needs no git at all: on github.com open `submissions/`, choose **Add file → Upload files**, and
drag your folder in ([STUDENT_QUICKSTART.md](STUDENT_QUICKSTART.md) has all three routes).

---

## Your prompt log

Keep a `PROMPT_LOG.md` in your submission folder listing every prompt you sent, in order:

```markdown
### Prompt 1 — 2026-09-01 14:32
Fit simple exponential smoothing to the CA_1 FOODS series and report the test RMSE.

### Prompt 2 — 2026-09-01 14:51
Now add Holt's linear trend with damping, and compare against the previous fit.
```

If your assistant can write the file, let it. If you are in a browser chat, paste them in as you
go — it takes seconds and is far easier than reconstructing them afterwards.

---

## The prompt budget is a target, not a limit

Each assignment states a budget. It exists to make you decide what is worth asking, which is a
real skill and the reason it is there at all.

**You may go over it.** If you do, log the extra prompts and add one line at the end of your log
saying where you got stuck. That costs you nothing.

It also helps me: if half the class needs fourteen prompts on a question I budgeted nine for, the
question is harder than I intended and I want to know.

**What does cost you** is a log that does not match the work you submit. Under-reporting to hit a
number is the one thing here that is genuinely dishonest.

---

## What you must write yourself

**The code can be AI-assisted. The thinking cannot.**

Write these yourself, in your own words:

- every **interpretation** of a result
- every **business recommendation**
- every **reflection** question
- anything explaining *why* a model behaved as it did

The assignments' initial prompts now tell your assistant explicitly to explain output to you but
**not** to draft the answers you submit. Keep it that way.

This is not an arbitrary rule. Those sections are what the marks are actually for. A model can
produce fluent prose about a forecast in seconds; what it cannot do is know which of your results
surprised you, or which number you do not believe. That is the part worth your time, and the part
worth mine to read.

---

## Being stuck is allowed

If you cannot get something working, say so in your submission and describe what you tried. A
clear account of a failure earns marks. A quietly copied number that you cannot explain does not.
