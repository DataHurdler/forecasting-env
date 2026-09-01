# Start Here

## Which repository am I looking at?

There are **two** ECON 8310 repositories, and you only ever clone one of them.

| Repository | What it holds | What you do with it |
|---|---|---|
| **`forecasting-env`** — *this one* | The assignments, the datasets, and the folder your work goes into | **Clone it.** Every homework you write and submit lives here |
| `forecasting-course` | Slides, labs, assignments, the book and the workbook — the teaching materials | Nothing. You read these on the web, not in a clone |

**Course website** (slides, labs, assignments, book, workbook): <https://www.luozijun.com/forecasting-course/>

Your **syllabus, the term calendar and lecture recordings are on Canvas**, not on the website.

If you are looking for a lecture or a lab, it is on the website. If you are looking for
homework, it is here. Everything you need for ECON 8310 **homework** is in this repository.

---

## 1. One-time setup

**Get this repository onto your machine.**

```bash
git clone https://github.com/DataHurdler/forecasting-env.git
```

Or open <https://github.com/DataHurdler/forecasting-env>, click the green **Code** button, and
download the ZIP — then unzip it somewhere you will find again.

**Set up Python.** You need Python 3.10 or newer and these packages:

```
jupyter pandas numpy matplotlib statsmodels scikit-learn
prophet pygam xgboost torch pymc arviz
```

`jupyter` is not optional — Quarto runs your Python through a Jupyter kernel, and rendering fails
without it even though nothing in your code imports it.

**macOS only, before Week 5:** `brew install libomp`, once. Without it `import xgboost` fails.

**Install Quarto** from <https://quarto.org/docs/get-started/>, and an editor — either **VS Code**
(with the Quarto extension) or **Positron** (Quarto built in). Either works.

Full step-by-step setup, what a `.qmd` file actually is, and the four errors you will hit:
**[QUARTO_GUIDE.md](QUARTO_GUIDE.md)**. Read that first if you have not used Quarto before.

**Google Colab will not work** — it cannot open `.qmd` files.

**When something breaks**, read [Troubleshooting](https://www.luozijun.com/forecasting-course/files/troubleshooting.html) — it covers the failures this course actually produces, and it is faster than waiting on a reply.

---

## 2. Get the data

Every assignment reads from `data/processed/`. **Try building it yourself first** — it is worth
seeing where the data comes from:

```bash
python scripts/prep_m5.py            # the main dataset
python scripts/prep_fred.py          # macro series, Lecture 2
python scripts/prep_electricity.py   # hourly demand, Lecture 3
```

`prep_m5.py` downloads about 48 MB and takes a few minutes.

**If that fails for any reason, you are not stuck.** The finished files are already committed in
`data/processed/`. Nothing in this course is blocked by a download.

---

## 3. Do an assignment

1. Copy the assignment out of `assignments/` into a new folder:

   ```
   submissions/hw01_part1_<yourname>/HW01_Part1_ETS.qmd
   ```

   Use the exact assignment name for the folder prefix — `hw01_part1`, `hw05_part2`, and so on.
   It is written at the top of each assignment.

2. Open the assignment and find **Initial Prompt for Your AI Assistant**. Send that block as the first
   message to whichever AI assistant you are using. Save it as `INITIAL_PROMPT.md` in your folder.

3. Work through the questions. Fill in the code chunks and write the answers.

4. Keep a `PROMPT_LOG.md` in your folder as you go (see below).

5. Render it:

   ```bash
   quarto render submissions/hw01_part1_<yourname>/HW01_Part1_ETS.qmd
   ```

---

## 4. Check before you submit

```bash
python scripts/check_my_submission.py
```

No arguments. It tells you what is missing. **The most common way to lose marks is submitting an
`.html` that is older than your `.qmd`** — you edited, then forgot to re-render. This catches that.

---

## 5. Submit

Three ways. Any of them is fine.

**Command line**

```bash
git add submissions/hw01_part1_<yourname>
git commit -m "hw01_part1: submission"
git push
```

**GitHub Desktop** — <https://desktop.github.com>. Point it at this folder, write a summary,
click Commit, then Push. No commands to remember.

**Your browser** — go to your repository on github.com, open the `submissions/` folder,
**Add file → Upload files**, and drag your folder in. This needs no git knowledge at all.

Push before the deadline. Push time is submission time.
