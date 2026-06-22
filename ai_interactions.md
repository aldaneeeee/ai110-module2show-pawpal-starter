# AI Interactions — PawPal+ Extensions

This document records how an AI coding assistant was used to build the five
extension challenges on top of the PawPal+ starter, plus a multi-model prompt
comparison for a complex algorithmic task.

---

## Agent Workflow (Challenge 1)

### Files modified
| File | Change |
| --- | --- |
| `pawpal_system.py` | Added `Priority` enum, `priority` + `category` fields on `Task`, `sort_by_priority`, `find_next_available_slot`, `weighted_priority_score`, `get_priority_ranking`, emoji/color helpers, `print_schedule_table`, and `save_to_json` / `load_from_json`. |
| `main.py` | Rewrote the CLI demo to exercise priority sorting, the weighted ranking, the next-slot finder, table output, and a persistence round-trip. |
| `app.py` | Wired priority + category selectors into the Streamlit UI, added a "next free slot" suggestion, sort-by-priority/time toggle, emoji/priority badges, and auto-save on every change. |
| `tests/test_pawpal.py` | Added 6 tests covering priority sorting, slot finding, weighted ranking, and JSON save/load round-trips. |
| `requirements.txt` | Added `tabulate` for structured CLI tables. |
| `.gitignore` | Ignored the generated `data.json`. |
| `README.md` | Documented persistence workflow, CLI output examples, and formatting features. |

### What I asked the agent to do
> "Add a third algorithmic capability beyond basic sorting/filtering/conflict
> detection — a 'next available slot' finder and a weighted prioritization
> ranking — to the Scheduler in `pawpal_system.py`."

### What it completed
- `find_next_available_slot(preferred_time, interval_minutes, day_end)` — scans
  forward in fixed steps from a preferred time and returns the first slot not
  already occupied by a task, or `None` if the day fills up.
- `weighted_priority_score(task)` — combines the priority level with how early
  in the day the task falls (and penalizes completed tasks) to produce a single
  urgency score.
- `get_priority_ranking()` — returns pending tasks ordered by that score.
- Helper time math (`_to_minutes` / `_to_hhmm`) so "HH:MM" strings can be
  compared and incremented safely.

### Manual corrections I made
- The agent's first draft of `find_next_available_slot` returned the preferred
  time even when it was already taken; I corrected the loop so it checks the
  candidate against the set of taken times **before** returning.
- The weighted score initially ignored completed tasks, so finished work still
  ranked highly. I added a `completion_penalty` so completed tasks sink to the
  bottom.
- The agent placed the time-helper methods as free functions; I moved them onto
  `Scheduler` as `@staticmethod`s to keep the time logic colocated with the
  scheduling code.

---

## Prompt Comparison (Challenge 5)

### Complex algorithmic task
Designing the **persistence layer** — serializing nested `Owner → Pet → Task`
objects (including the `Priority` enum) to JSON and rebuilding them on load,
without breaking the existing positional `Task(...)` constructor calls used
throughout the codebase and tests.

> **Prompt given to both models:**
> "I have dataclasses `Task` and `Pet` and a plain class `Owner` in Python.
> `Task` has a `Priority` enum field. I need to save an `Owner` (with nested
> pets and tasks) to a JSON file and load it back. Should I use `marshmallow`,
> or hand-written `to_dict`/`from_dict`? Show me the implementation."

| Aspect | **Model A (Claude)** | **Model B (Gemini)** |
| --- | --- | --- |
| Recommendation | Custom `to_dict` / `from_dict` per class | `marshmallow` schemas |
| What was useful | Zero new dependencies; serialized the enum by `.name` and rebuilt it with a tolerant `Priority.from_str`; handled the missing-file case by returning an empty scheduler so first runs don't crash. | Clean declarative schemas; automatic validation of field types; good for a larger API where input can't be trusted. |
| What was flawed | Slightly more boilerplate (one method pair per class); no automatic type validation on load. | Added a heavy dependency for a 3-class project; the generated `EnumField` config was fiddly and its first version dropped the `category` default; overkill for a local single-user file. |
| Final decision | **Chose Claude's custom dictionary conversion.** | Rejected `marshmallow` as too heavy for this project's scope. |

### Why this decision
For a small, single-user app persisting to one local `data.json`, hand-written
`to_dict`/`from_dict` keeps the project dependency-light and easy to read, and
the enum round-trips cleanly via its `.name`. Storing the priority by name
(`"HIGH"`) rather than its integer value also makes the JSON human-readable. If
PawPal+ later grew into a multi-user web service accepting untrusted input,
revisiting `marshmallow` (or `pydantic`) for validation would be worthwhile.
