"""PawPal+ core data model: Task, Pet, Owner, and Scheduler."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single care task for a pet."""

    title: str
    time: str                       # e.g. "08:00"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def reschedule(self, new_time: str) -> None:
        """Change the task time."""
        self.time = new_time

    def __str__(self) -> str:
        """Return a formatted string showing task status, title, and time."""
        status = "✓" if self.completed else "○"
        return f"  [{status}] {self.title} at {self.time}"


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

    def print_schedule(self) -> None:
        """Print a readable summary grouped by pet."""
        print(f"\n=== {self.owner.name}'s Schedule ===")
        for p in self.owner.pets:
            print(f"\n  {p.name}:")
            pet_tasks = p.get_tasks()
            if not pet_tasks:
                print("    No tasks.")
            for t in pet_tasks:
                print(t)
        print()


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    demo_owner.add_pet(mochi)
    demo_owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:00"))
    mochi.add_task(Task("Vet checkup", "10:00"))
    luna.add_task(Task("Flea treatment", "09:00"))
    luna.add_task(Task("Grooming", "14:00"))

    demo_scheduler = Scheduler(demo_owner)
    demo_scheduler.print_schedule()

    demo_scheduler.mark_complete(mochi, "Morning walk")

    print("=== Pending tasks ===")
    for t in demo_scheduler.get_all_pending_tasks():
        print(t)
