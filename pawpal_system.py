"""PawPal+ core data model: Task, Pet, Owner, and Scheduler.

This module is the single source of truth for the PawPal+ domain logic. It now
supports:
  * Priority-based scheduling (Challenge 3)
  * An advanced "next available slot" / weighted-priority algorithm (Challenge 1)
  * JSON persistence via save_to_json / load_from_json (Challenge 2)
  * Professional, color-coded, emoji-rich output formatting (Challenge 4)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:  # graceful fallback if tabulate isn't installed
    _HAS_TABULATE = False


# ---------------------------------------------------------------------------
# Priority (Challenge 3)
# ---------------------------------------------------------------------------

class Priority(Enum):
    """Task priority. Higher value == more urgent (sorts first)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_str(cls, value: str) -> "Priority":
        """Parse a priority from a (case-insensitive) string like 'high'."""
        try:
            return cls[value.strip().upper()]
        except KeyError:
            return cls.MEDIUM


# ---------------------------------------------------------------------------
# Presentation helpers (Challenge 4) — emojis & ANSI color codes
# ---------------------------------------------------------------------------

# ANSI escape codes for color-coded CLI output.
_RESET = "\033[0m"
_COLORS = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "grey": "\033[90m",
    "bold": "\033[1m",
}

# Emoji per task category, used in the formatted schedule output.
CATEGORY_EMOJI = {
    "feeding": "🍖",
    "walk": "🚶",
    "vet": "🏥",
    "grooming": "✂️",
    "medication": "💊",
    "play": "🎾",
    "other": "🐾",
}

# Color per priority level for the color-coded status indicators.
PRIORITY_COLOR = {
    Priority.HIGH: "red",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "green",
}


def _colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color code (no-op if the color is unknown)."""
    code = _COLORS.get(color)
    return f"{code}{text}{_RESET}" if code else text


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_time(time_str: str) -> bool:
    """Return True if `time_str` is a valid 24-hour 'HH:MM' time.

    Accepts "00:00" through "23:59" (and tolerates a single-digit hour like
    "8:00"). Rejects anything that isn't two colon-separated numbers in range,
    e.g. "8am", "25:00", "08:99", or "".
    """
    if not isinstance(time_str, str):
        return False
    parts = time_str.split(":")
    if len(parts) != 2:
        return False
    hours, minutes = parts
    if not (hours.isdigit() and minutes.isdigit()):
        return False
    return 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single care task for a pet."""

    title: str
    time: str                              # e.g. "08:00"
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    category: str = "other"

    def __post_init__(self) -> None:
        """Validate fields right after construction (runs for every Task)."""
        if not is_valid_time(self.time):
            raise ValueError(
                f"Invalid time {self.time!r}. Expected 24-hour 'HH:MM', e.g. '08:30'."
            )

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def reschedule(self, new_time: str) -> None:
        """Change the task time."""
        if not is_valid_time(new_time):
            raise ValueError(
                f"Invalid time {new_time!r}. Expected 24-hour 'HH:MM', e.g. '08:30'."
            )
        self.time = new_time

    # --- presentation ------------------------------------------------------

    @property
    def emoji(self) -> str:
        """Return the emoji for this task's category."""
        return CATEGORY_EMOJI.get(self.category.lower(), CATEGORY_EMOJI["other"])

    @property
    def status_icon(self) -> str:
        """Color-coded status indicator (green check when done)."""
        if self.completed:
            return _colorize("✓", "green")
        return _colorize("○", PRIORITY_COLOR.get(self.priority, "yellow"))

    def __str__(self) -> str:
        """Return a formatted string showing status, emoji, title, and time."""
        title = self.title if self.completed else _colorize(
            self.title, PRIORITY_COLOR.get(self.priority, "yellow")
        )
        return f"  [{self.status_icon}] {self.emoji} {title} at {self.time}"

    # --- persistence (Challenge 2) -----------------------------------------

    def to_dict(self) -> dict:
        """Convert this task into a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "time": self.time,
            "completed": self.completed,
            "priority": self.priority.name,   # store enum by name, not object
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dictionary produced by to_dict()."""
        return cls(
            title=data["title"],
            time=data["time"],
            completed=data.get("completed", False),
            priority=Priority.from_str(data.get("priority", "MEDIUM")),
            category=data.get("category", "other"),
        )


@dataclass
class Pet:
    """Represents a pet with a name, type, and list of care tasks."""

    name: str
    pet_type: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self) -> str:
        """Return the pet's name as its string representation."""
        return self.name

    # --- persistence (Challenge 2) -----------------------------------------

    def to_dict(self) -> dict:
        """Convert this pet (and its nested tasks) into a dictionary."""
        return {
            "name": self.name,
            "pet_type": self.pet_type,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its nested tasks) from a dictionary."""
        pet = cls(name=data["name"], pet_type=data.get("pet_type", ""))
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


class Owner:
    """Represents a pet owner who can have multiple pets."""

    def __init__(self, name: str) -> None:
        """Initialize an owner with a name and an empty pet list."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        if pet in self.pets:
            self.pets.remove(pet)

    def __str__(self) -> str:
        """Return a string with the owner's name and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) or "none"
        return f"{self.name} (pets: {pet_names})"


class Scheduler:
    """Manages and retrieves tasks across all pets belonging to an owner."""

    # Default data file used by save_to_json / load_from_json.
    DEFAULT_PATH = "data.json"

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner to manage tasks for."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across every pet, sorted by time."""
        all_tasks = [
            t
            for p in self.owner.pets
            for t in p.get_tasks()
        ]
        return sorted(all_tasks, key=lambda t: t.time)

    def get_all_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def mark_complete(self, pet: Pet, task_title: str) -> None:
        """Mark a task complete by title for a given pet."""
        for task in pet.get_tasks():
            if task.title.lower() == task_title.lower():
                task.mark_complete()
                return

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by time."""
        return sorted(self.get_all_tasks(), key=lambda task: task.time)

    # --- Challenge 3: priority-based scheduling ----------------------------

    def sort_by_priority(self) -> list[Task]:
        """Return all tasks sorted by priority (High→Low), then by time.

        This is the enhanced scheduling logic: a High-priority 14:00 task
        outranks a Low-priority 07:00 task. Within the same priority level,
        tasks fall back to chronological order.
        """
        return sorted(
            self.get_all_tasks(),
            key=lambda t: (-t.priority.value, t.time),
        )

    # --- Challenge 1: advanced algorithmic capability ----------------------

    def find_next_available_slot(
        self,
        preferred_time: str = "08:00",
        interval_minutes: int = 30,
        day_end: str = "21:00",
    ) -> str | None:
        """Find the next free time slot at or after `preferred_time`.

        Scans forward from the preferred time in `interval_minutes` steps and
        returns the first slot that no existing task already occupies. Returns
        None if the day fills up before `day_end`. This lets the app suggest a
        conflict-free time when the owner adds a new task.
        """
        taken = {t.time for t in self.get_all_tasks()}
        current = self._to_minutes(preferred_time)
        end = self._to_minutes(day_end)
        while current <= end:
            candidate = self._to_hhmm(current)
            if candidate not in taken:
                return candidate
            current += interval_minutes
        return None

    def weighted_priority_score(self, task: Task) -> int:
        """Compute a weighted urgency score for a task.

        Combines priority weight with how early the task is in the day so that
        a High-priority morning task scores highest. Used to rank the day's
        "most important" tasks beyond a plain sort.
        """
        priority_weight = task.priority.value * 100
        # Earlier in the day == slightly more urgent; subtract elapsed minutes.
        earliness = (24 * 60 - self._to_minutes(task.time)) // 10
        completion_penalty = 0 if not task.completed else -1000
        return priority_weight + earliness + completion_penalty

    def get_priority_ranking(self) -> list[Task]:
        """Return pending tasks ranked by weighted priority score (desc)."""
        pending = self.get_all_pending_tasks()
        return sorted(pending, key=self.weighted_priority_score, reverse=True)

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert 'HH:MM' to minutes since midnight."""
        hours, minutes = (int(part) for part in hhmm.split(":"))
        return hours * 60 + minutes

    @staticmethod
    def _to_hhmm(minutes: int) -> str:
        """Convert minutes since midnight back to 'HH:MM'."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    # --- filtering & conflicts ---------------------------------------------

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Filter tasks by completion status or pet name."""
        filtered = []
        for p in self.owner.pets:
            for task in p.tasks:
                if completed is not None and task.completed != completed:
                    continue
                if pet_name is not None and p.name != pet_name:
                    continue
                filtered.append(task)
        return filtered

    def detect_conflicts(self) -> list[str]:
        """Return warnings for tasks scheduled at the same time."""
        tasks = self.get_all_tasks()
        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time:
                    conflicts.append(
                        f"Conflict: '{tasks[i].title}' and '{tasks[j].title}' are both at {tasks[i].time}"
                    )
        return conflicts

    # --- Challenge 4: professional output formatting -----------------------

    def print_schedule(self) -> None:
        """Print a readable summary grouped by pet (with emojis + colors)."""
        header = _colorize(f"\n=== {self.owner.name}'s Schedule ===", "bold")
        print(header)
        for p in self.owner.pets:
            print(_colorize(f"\n  {p.name} ({p.pet_type or 'pet'}):", "cyan"))
            pet_tasks = p.get_tasks()
            if not pet_tasks:
                print("    No tasks.")
            for t in pet_tasks:
                print(t)
        print()

    def print_schedule_table(self, by_priority: bool = True) -> None:
        """Print the full schedule as a structured CLI table.

        Uses the `tabulate` library when available for clean column alignment,
        and falls back to a simple aligned layout otherwise.
        """
        tasks = self.sort_by_priority() if by_priority else self.sort_by_time()
        # Map each task back to its pet for the table's "Pet" column.
        pet_of = {id(t): p.name for p in self.owner.pets for t in p.get_tasks()}

        rows = []
        for t in tasks:
            rows.append([
                t.status_icon,
                t.time,
                _colorize(t.priority.name, PRIORITY_COLOR.get(t.priority, "yellow")),
                f"{t.emoji} {t.title}",
                pet_of.get(id(t), "?"),
            ])

        headers = ["", "Time", "Priority", "Task", "Pet"]
        print(_colorize(f"\n📋 {self.owner.name}'s Daily Plan", "bold"))
        if _HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))
        else:
            print("  ".join(headers))
            for row in rows:
                print("  ".join(str(cell) for cell in row))
        print()

    # --- Challenge 2: JSON persistence -------------------------------------

    def save_to_json(self, path: str | None = None) -> str:
        """Save the owner, pets, and tasks to a JSON file.

        Uses custom dict conversion (Pet.to_dict / Task.to_dict) so that nested
        objects and the Priority enum serialize cleanly. Returns the file path.
        """
        path = path or self.DEFAULT_PATH
        data = {
            "owner": self.owner.name,
            "pets": [p.to_dict() for p in self.owner.pets],
        }
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return path

    @classmethod
    def load_from_json(cls, path: str | None = None) -> "Scheduler":
        """Load owner, pets, and tasks from a JSON file into a new Scheduler.

        Returns a fresh Scheduler. If the file does not exist, returns a
        scheduler for a default empty owner so first runs don't crash.
        """
        path = path or cls.DEFAULT_PATH
        file = Path(path)
        if not file.exists():
            return cls(Owner("New Owner"))

        data = json.loads(file.read_text())
        owner = Owner(data.get("owner", "New Owner"))
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return cls(owner)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    demo_owner.add_pet(mochi)
    demo_owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:00", category="walk", priority=Priority.MEDIUM))
    mochi.add_task(Task("Vet checkup", "10:00", category="vet", priority=Priority.HIGH))
    luna.add_task(Task("Flea treatment", "09:00", category="medication", priority=Priority.HIGH))
    luna.add_task(Task("Grooming", "14:00", category="grooming", priority=Priority.LOW))

    demo_scheduler = Scheduler(demo_owner)
    demo_scheduler.print_schedule_table()

    print("Next available 30-min slot after 09:00:",
          demo_scheduler.find_next_available_slot("09:00"))
