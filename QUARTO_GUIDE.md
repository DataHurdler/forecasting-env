# Working with `.qmd` Files

Every assignment in this course is a **Quarto** document — a `.qmd` file. This page gets you set
up and shows you what you actually need to do with one.

You will never create a `.qmd` from scratch. You copy the assignment and fill in the blanks.

---

# Part 1 — Setting up

You need three things. Budget twenty minutes the first time.

## 1. Python

You need Python 3.10 or newer. Check what you have:

```bash
python --version
```

If that fails, try `python3 --version`. If neither works, install from
<https://www.python.org/downloads/> — and on Windows, **tick "Add Python to PATH"** on the first
screen of the installer. Missing that is the single most common Windows setup problem.

Then install the packages:

```bash
pip install jupyter pandas numpy matplotlib statsmodels scikit-learn
pip install prophet pygam xgboost torch pymc arviz
```

`jupyter` is not optional. Quarto runs your Python through a Jupyter kernel, so rendering fails
without it — even though none of your code imports it.

**macOS, before Week 5:** `brew install libomp`, once. Without it `import xgboost` fails.

## 2. Quarto

Download from <https://quarto.org/docs/get-started/> and run the installer. Then confirm:

```bash
quarto --version
```

Any 1.4 or newer is fine.

## 3. An editor — pick one

**Either of these works well. Choose one and stick with it.**

### Option A — VS Code

The most widely used editor in the industry, and the one you are most likely to meet again after
this course.

1. Install from <https://code.visualstudio.com/>
2. Click the Extensions icon in the left sidebar — four squares, one detached — or press
   `Ctrl+Shift+X` (`Cmd+Shift+X` on Mac)
3. Search for and install **two** extensions:

| Extension | Publisher | Why |
|---|---|---|
| **Quarto** | Posit | `.qmd` editing, the Render button, preview |
| **Python** | Microsoft | runs your code, picks the interpreter |

Both are free.

### Option B — Positron

Posit's editor, purpose-built for data science. **Quarto support is built in** — no extensions to
install — and it shows your variables and plots in dedicated panes, which many people find easier
when working with data.

1. Install from <https://positron.posit.co/>
2. That is the whole setup

If you have used RStudio, Positron will feel familiar immediately.

### Which should you choose?

Neither is wrong, and every instruction in this course works in both.

- **VS Code** if you want the more transferable skill, or you already use it for something else.
  More people use it, so more of the answers you find online will match what you see.
- **Positron** if you want less setup and a layout designed around data work. Fewer steps to get
  running, and the variable and plot panes are genuinely nice.

## Open the repository as a *folder*

Whichever you chose: **File → Open Folder** → select the repository folder. Not a single file —
the whole folder. Both editors need to see the project to resolve data paths correctly.

## Check it works

Open any assignment in `assignments/` and click **Render**. A preview should appear beside your
code. If it does, you are set up.

---

# Part 2 — What a `.qmd` actually is

A `.qmd` is one file holding three things.

## The YAML header

At the very top, between `---` lines:

```
---
title: "Homework 1, Part 1: Exponential Smoothing"
format:
  html:
    toc: true
---
```

This controls the output. **Leave it alone** unless an assignment says otherwise.

## Prose

Ordinary markdown. `**bold**`, `*italic*`, `# headings`, `- bullets`. This is where you write
your answers.

## Code chunks

Python between triple backticks with `{python}`:

````
```{python}
import pandas as pd
weekly = pd.read_csv("data/processed/m5_weekly.csv")
print(weekly.shape)
```
````

Output appears below the chunk when you run or render it.

## What the assignments look like

Every question has two parts you fill in:

````
```{python}
# TODO: fit SES and report test RMSE
```
````

> **Your response:** *(you write here, in your own words)*

The code chunk is for code. The **Your response** block is for your writing — and that part must
be yours, not your AI assistant's. See [AI_POLICY.md](AI_POLICY.md).

---

# Part 3 — Running and rendering

Two different things, and the distinction matters.

**Running a chunk** executes that one block so you can see its output while you work. Click the
little **▶ Run Cell** that appears above a chunk, or press `Ctrl+Shift+Enter`
(`Cmd+Shift+Enter` on Mac) with your cursor inside it.

**Rendering** runs the whole document top to bottom in a fresh session and produces the `.html`
you submit. Click **Render**, or:

```bash
quarto render submissions/hw01_part1_yourname/HW01_Part1_ETS.qmd
```

> **Why the difference matters.** While you work, you run chunks one at a time and variables pile
> up in memory. Rendering starts from nothing. **A document that works chunk-by-chunk can fail
> completely on render** — usually because something was defined in a chunk you later edited or
> deleted.
>
> Always render before you submit. It is the same discipline as restarting a notebook kernel.

---

# Part 4 — The four errors you will actually hit

## `quarto: command not found`

Quarto is not installed, or your terminal opened before you installed it. Install it, then
**close and reopen VS Code entirely**.

## `No module named 'yaml'` or "Unable to start the Jupyter kernel"

`jupyter` is not installed in the Python that Quarto is using.

```bash
pip install jupyter
```

If it persists, VS Code is probably using a different Python than your terminal. Press
`Ctrl+Shift+P` (`Cmd+Shift+P`), type **Python: Select Interpreter**, and pick the one where you
installed the packages.

## `FileNotFoundError: data/processed/m5_weekly.csv`

Your working directory is wrong. Assignments read that path relative to the **repository root**,
so you must open the repository as a folder in VS Code — not the `.qmd` on its own.

If you opened a single file, close it and use File → Open Folder instead.

## Your `.html` does not show your latest work

You edited the `.qmd` and did not re-render. This is the most common way to lose marks in this
course, and `python scripts/check_my_submission.py` checks for it specifically — it compares the
timestamps and tells you if your `.html` is older than your `.qmd`.

Render, then check, then push.

---

# Other editors

**RStudio** also renders `.qmd`, though Python environment setup takes more configuring than in
either VS Code or Positron. Workable if it is what you already have.

**Google Colab does not support `.qmd` files.** It is a notebook environment with no Quarto
installed and no way to add it. You cannot complete these assignments in Colab — please set up
VS Code or Positron instead.

---

# Going further

- **<https://quarto.org/docs/get-started/>** — official tutorial; pick your editor at the top and
  it adapts
- **<https://quarto.org/docs/computations/python.html>** — code chunks and chunk options
- **<https://quarto.org/docs/output-formats/html-basics.html>** — HTML output options
