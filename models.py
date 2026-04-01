from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskCategory(Enum):
    FEEDING = "Feeding"
    VET = "Vet"
    GROOMING = "Grooming"
    WALK = "Walk"
    MEDICATION = "Medication"
    OTHER = "Other"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    description: str
    due_date: date
    category: TaskCategory
    pet: Pet                        # back-reference so Scheduler knows which pet
    is_complete: bool = False

    def complete(self) -> None:
        """Mark this task as complete."""
        self.is_complete = True

    def reschedule(self, new_date: date) -> None:
        """Move the task to a new due date."""
        self.due_date = new_date

    def __repr__(self) -> str:
        status = "done" if self.is_complete else "pending"
        return (
            f"Task({self.category.value!r}, pet={self.pet.name!r}, "
            f"due={self.due_date}, {status})"
        )


# ---------------------------------------------------------------------------
# Pet  (pure data — no scheduling responsibility)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def get_info(self) -> str:
        """Return a human-readable summary of the pet."""
        return (
            f"{self.name} is a {self.age}-year-old {self.breed} ({self.species})."
        )


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, email: str, phone: str) -> None:
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's roster."""
        if pet in self.pets:
            self.pets.remove(pet)

    def __repr__(self) -> str:
        return f"Owner({self.name!r}, pets={[p.name for p in self.pets]})"


# ---------------------------------------------------------------------------
# Scheduler  (single source of truth for all tasks)
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    # --- task management ---------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Register a task with the scheduler."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler."""
        if task in self.tasks:
            self.tasks.remove(task)

    def mark_task_complete(self, task: Task) -> None:
        """Mark a specific task as complete."""
        task.complete()

    # --- queries -----------------------------------------------------------

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        return [t for t in self.tasks if t.pet is pet]

    def get_tasks_for_owner(self, owner: Owner) -> list[Task]:
        """Return all tasks across every pet owned by this owner."""
        return [t for t in self.tasks if t.pet in owner.pets]

    def get_upcoming_tasks(self, as_of: Optional[date] = None) -> list[Task]:
        """Return incomplete tasks due on or after `as_of` (defaults to today), sorted by date."""
        cutoff = as_of or date.today()
        return sorted(
            [t for t in self.tasks if not t.is_complete and t.due_date >= cutoff],
            key=lambda t: t.due_date,
        )

    def get_tasks_by_category(self, category: TaskCategory) -> list[Task]:
        """Return all tasks of a given category."""
        return [t for t in self.tasks if t.category is category]

    # --- reminders ---------------------------------------------------------

    def send_reminder(self, task: Task) -> str:
        """Return a reminder string for the given task (hook in real notifications here)."""
        return (
            f"Reminder: '{task.title}' for {task.pet.name} "
            f"is due on {task.due_date}."
        )

    def __repr__(self) -> str:
        return f"Scheduler(tasks={len(self.tasks)})"
