# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

- Add pets and manage multiple animals
- Create and assign tasks to each pet
- View a daily schedule of all tasks
- Sort tasks by time
- Filter tasks by completion status or pet
- Detect scheduling conflicts between tasks

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

# Extensions

The sections below document the five extension challenges built on top of the
starter. See [`ai_interactions.md`](ai_interactions.md) for the AI agent
workflow and multi-model prompt comparison.

## Challenge 1 — Advanced algorithmic capability

Beyond the basic sort/filter/conflict logic, the `Scheduler` now offers:

- **`find_next_available_slot(preferred_time, interval_minutes, day_end)`** —
  scans forward from a preferred time and returns the first slot not already
  taken by a task (used in the UI to suggest a conflict-free time).
- **`weighted_priority_score(task)` / `get_priority_ranking()`** — ranks
  pending tasks by a weighted urgency score that blends priority level with how
  early the task is in the day.

## Challenge 2 — Data persistence

### Persistence workflow
1. On startup, `app.py` calls `Scheduler.load_from_json("data.json")`. If the
   file doesn't exist yet (first run), it returns a scheduler with an empty
   owner instead of crashing.
2. Every time the user adds a pet, adds a task, or marks one complete, the app
   calls `scheduler.save_to_json("data.json")`.
3. The next time the app (or `main.py`) runs, the saved pets and tasks are
   restored automatically.

### How serialization works
Complex nested objects (`Owner → Pet → Task`) and the `Priority` enum are
handled with **custom dictionary conversion** rather than a library like
`marshmallow`:

- `Task.to_dict()` / `Task.from_dict()` — the `Priority` enum is stored by name
  (e.g. `"HIGH"`) and rebuilt with the tolerant `Priority.from_str()`.
- `Pet.to_dict()` / `Pet.from_dict()` — recursively (de)serializes its tasks.
- `Scheduler.save_to_json()` / `Scheduler.load_from_json()` — write/read the
  whole owner tree as one JSON document.

(The reasoning behind choosing custom dicts over `marshmallow` is documented in
the prompt comparison in `ai_interactions.md`.)

### Files modified for persistence
- `pawpal_system.py` — added `to_dict`/`from_dict` on `Task` and `Pet`, and
  `save_to_json`/`load_from_json` on `Scheduler`.
- `app.py` — load on boot, save after every mutation.
- `main.py` — demonstrates a save → load round-trip.
- `.gitignore` — ignores the generated `data.json`.

## Challenge 3 — Advanced priority scheduling

`Task` now has a `priority` field (`Priority.LOW` / `MEDIUM` / `HIGH`). The new
`Scheduler.sort_by_priority()` sorts by **priority first (High → Low), then by
time**. The CLI output below shows the difference — `Vet visit` (High, 11:00)
and `Medicine` (High, 11:00) jump ahead of the earlier-but-lower-priority
`Feed dog` (08:00):

```
=== Sorted by Time ===
  [○] 🍖 Feed dog at 08:00
  [○] 🍖 Feed cat at 09:00
  [○] 🚶 Walk dog at 10:00
  [○] 🏥 Vet visit at 11:00
  [○] 💊 Medicine at 11:00

=== Sorted by Priority (then time) ===
  [○] 🏥 Vet visit at 11:00
  [○] 💊 Medicine at 11:00
  [○] 🍖 Feed dog at 08:00
  [○] 🍖 Feed cat at 09:00
  [○] 🚶 Walk dog at 10:00

=== Weighted Priority Ranking (most important first) ===
   378  Vet visit
   378  Medicine
   296  Feed dog
   290  Feed cat
   184  Walk dog

Next available 30-min slot after 08:00: 08:30
```

## Challenge 4 — Professional UI & output formatting

Formatting features added:

- **Emojis per task category** via the `CATEGORY_EMOJI` map (🍖 feeding,
  🚶 walk, 🏥 vet, ✂️ grooming, 💊 medication, 🎾 play, 🐾 other), exposed as
  `Task.emoji`.
- **Color-coded status indicators** using ANSI escape codes — pending tasks are
  colored by priority (red/yellow/green) and completed tasks show a green ✓ via
  `Task.status_icon`.
- **Structured CLI tables** with the [`tabulate`](https://pypi.org/project/tabulate/)
  library (`rounded_grid` format) in `Scheduler.print_schedule_table()`, with a
  graceful plain-text fallback if `tabulate` isn't installed.

Example table output (`scheduler.print_schedule_table()`):

```
📋 Karla's Daily Plan
╭────┬────────┬────────────┬─────────────┬───────╮
│    │ Time   │ Priority   │ Task        │ Pet   │
├────┼────────┼────────────┼─────────────┼───────┤
│ ○  │ 11:00  │ HIGH       │ 🏥 Vet visit │ Dog   │
│ ○  │ 11:00  │ HIGH       │ 💊 Medicine  │ Cat   │
│ ○  │ 08:00  │ MEDIUM     │ 🍖 Feed dog  │ Dog   │
│ ○  │ 09:00  │ MEDIUM     │ 🍖 Feed cat  │ Cat   │
│ ○  │ 10:00  │ LOW        │ 🚶 Walk dog  │ Dog   │
╰────┴────────┴────────────┴─────────────┴───────╯
```

In the Streamlit UI, the same data renders with emoji + colored priority badges
(🔴 High, 🟡 Medium, 🟢 Low) and a Priority/Time sort toggle.

## Running the demo & tests

```bash
pip install -r requirements.txt   # now includes tabulate
python main.py                    # CLI demo of all features above
pytest -q                         # 12 tests, including priority + persistence
```
