# Python-assignment — Quiz App

This is our summer class project: a terminal multiple-choice quiz app, split
into 4 independent files so four people can work at the same time without
stepping on each other.

```
quiz_app/
├── questions.py           Person 1 — the question bank
├── quiz_logic.py          Person 2 — the quiz engine (scoring, shuffling, timer)
├── scoreboard.py          Person 3 — saving scores, leaderboard, reports
├── main.py                Person 4 — menus, keyboard input, wiring   <-- run this
├── build_single_file.py   merges the 4 files into one
├── quiz_app_single.py     generated single-file version (do not edit by hand)
└── scores.json            created automatically after the first game
```

Run it:

```bash
python main.py
```

Requires Python 3.8+ only — no pip installs.

---

## Who does what

| # | File | Owner | Responsibility | Can test alone? |
|---|------|-------|----------------|-----------------|
| 1 | `questions.py` | Person 1 | All quiz content: `Question` class, the `QUESTIONS` list, filtering by category/difficulty, and `validate_questions()` self-check. Imports nothing from the project. | `python questions.py` |
| 2 | `quiz_logic.py` | Person 2 | One quiz run: shuffles questions and options, serves them one at a time, grades answers, tracks score/time/grade. No `print()`, no `input()`. | `python quiz_logic.py` |
| 3 | `scoreboard.py` | Person 3 | Everything that outlives a game: writes/reads `scores.json`, ranks results, per-player stats, and formats the result card, review and leaderboard text. | `python scoreboard.py` |
| 4 | `main.py` | Person 4 | The only file that talks to the human: banner, menus, input validation, and calling parts 1–3 in the right order. | `python main.py` |

**Why this split works:** only Person 4 imports other people's files.
Person 2's engine works with *any* object that has `.text`, `.options` and
`.answer_index`, so it needs no import from Part 1 at all — Person 2 tests with
fake questions. Nobody is blocked waiting for anybody.

---

## The contract (agree on this before you start coding)

Nobody renames these. If you must change one, tell the group first.

**Part 1 provides**

```python
Question(text, options, answer_index, category, difficulty, explanation)
Question.answer                 # correct option as text
QUESTIONS                       # list of Question
get_categories()                # ["Geography", "History", "Python", "Science"]
get_questions(category=None, difficulty=None, limit=None)
count_questions(category=None)
validate_questions()            # [] means healthy
```

**Part 2 provides**

```python
SKIPPED                         # -1, the "skipped" answer value
Quiz(questions, shuffle_questions=True, shuffle_options=True, seed=None)
quiz.current_question           # the Question being asked
quiz.current_options            # its options, already shuffled
quiz.submit(index) -> AnswerRecord
quiz.skip()  /  quiz.finish()
quiz.is_finished, quiz.number, quiz.total
quiz.score, quiz.percentage, quiz.elapsed, quiz.grade
quiz.wrong_records()            # for the review screen
quiz.summary()                  # dict Part 3 saves
AnswerRecord.is_correct, .skipped, .chosen_option, .correct_option, .seconds
```

**Part 3 provides**

```python
save_result(player, score, total, category, seconds)
load_scores()  /  top_scores(limit, category)  /  clear_scores()
player_stats(name)
format_result_card(player, summary, category)
format_review(wrong_records)
format_leaderboard(limit, category)
```

**Part 4 provides** `main()` — and nothing else imports it.

---

## Working order (suggested)

1. All four agree on the contract above (15 minutes, do it together).
2. Everyone writes and tests their own file with `python <yourfile>.py`.
3. Person 4 integrates: run `python main.py` and fix any mismatches as a group.
4. Merge into one file (below) if your submission requires a single `.py`.

Tip: put the 4 files in one folder from day one, and only ever edit *your* file.
That way `git` (or Google Drive, or a zip) never gives you a merge conflict.

---

## How to merge the 4 files into one

### Option A — automatic (recommended)

```bash
python build_single_file.py
```

That writes `quiz_app_single.py`, then run it:

```bash
python quiz_app_single.py
```

Re-run the build any time somebody edits their part. Never edit
`quiz_app_single.py` directly — your changes get overwritten on the next build.

### Option B — by hand (this is exactly what the script automates)

1. Create a new empty file, `quiz_app_single.py`.
2. Copy the **whole body** of the files in this order — order matters, because
   Python must see a name defined before the code that uses it:
   `questions.py` → `quiz_logic.py` → `scoreboard.py` → `main.py`
3. **Delete every cross-file import**, i.e. any line like
   `from questions import ...`, `from quiz_logic import ...`,
   `from scoreboard import ...`. Everything now lives in one file, so those
   names are already in scope.
4. **Move all standard-library imports to the top** and delete duplicates.
   The full set for this project is:
   ```python
   import json
   import random
   import sys
   import time
   from dataclasses import dataclass
   from datetime import datetime
   from pathlib import Path
   from typing import Any, List, Optional
   ```
5. **Delete every `if __name__ == "__main__":` block except the last one**
   (the one from `main.py` that calls `main()`). Those blocks are each person's
   private self-test; if you leave them in, they all run on startup.
6. Optionally paste a comment banner between the parts so it stays readable.
7. Run `python quiz_app_single.py` and confirm it behaves the same as
   `python main.py`.

### Merge gotchas to check

- **Two people used the same name.** If Part 1 and Part 3 both define a helper
  called `format(...)`, the second one silently wins. Search the merged file
  for duplicate `def` names before you submit.
- **Order.** `Quiz` must appear above the code that calls `Quiz(...)`.
  Function bodies are fine either way; module-level code is not.
- **`__file__`.** `scoreboard.py` uses `Path(__file__)` to locate
  `scores.json`, so the merged file writes `scores.json` next to itself. That
  still works, it just may be a different folder than before.

---

## Git workflow — one branch per person

`main` holds the shared scaffold only: this README, `.gitignore` and
`build_single_file.py`. **Each member adds their own file on their own branch**,
and the app runs once all four branches are merged back into `main`.

| Branch | Adds | Owner |
|--------|------|-------|
| `main` | README, .gitignore, build tool | shared |
| `bibhuti` | `questions.py` | Person 1 — done |
| `person2` | `quiz_logic.py` | Person 2 |
| `person3` | `scoreboard.py` | Person 3 |
| `person4` | `main.py` | Person 4 |

```bash
# each person, once: make your own branch off main
git switch main
git switch -c person2        # use your own name
```

Day to day, on your own branch, only touching your own file:

```bash
git add questions.py
git commit -m "Add 10 more Python questions"
```

When your part is done, merge it back into main:

```bash
git switch main
git merge bibhuti
```

Once all four are merged, `main` has every file and the app runs:

```bash
python main.py
```

If somebody else merged before you, refresh your branch first so any conflict
happens on *your* branch instead of on `main`:

```bash
git switch bibhuti
git merge main
```

Two rules that keep this conflict-free:

1. **Only edit your own file.** Four people, four files, zero overlap.
2. **Don't commit `quiz_app_single.py` from your branch.** It is a generated
   file — if all four of you rebuild it, every merge conflicts on it. Whoever
   integrates runs `python build_single_file.py` once on `main` at the end and
   commits the result.

`scores.json` and `__pycache__/` are already in `.gitignore` — they are local
run data, not source.

---

## Extension ideas (if you need more to divide up)

- Person 1: load questions from `questions.json` instead of hard-coded Python
- Person 2: per-question countdown timer; difficulty-weighted points
- Person 3: export results to CSV; per-category accuracy charts
- Person 4: colours via ANSI codes, or a Tkinter GUI on top of the same engine
