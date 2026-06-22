"""CLI demo for PawPal+ showing the enhanced scheduling, advanced algorithms,
formatted output, and JSON persistence added across Challenges 1–4."""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# Create owner
owner = Owner("Karla")

# Create pets
dog = Pet("Dog", "dog")
cat = Pet("Cat", "cat")

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Add tasks out of order, now with categories + priorities
dog.add_task(Task("Walk dog", "10:00", category="walk", priority=Priority.LOW))
dog.add_task(Task("Feed dog", "08:00", category="feeding", priority=Priority.MEDIUM))
cat.add_task(Task("Feed cat", "09:00", category="feeding", priority=Priority.MEDIUM))

# Add conflicting + high-priority tasks
dog.add_task(Task("Vet visit", "11:00", category="vet", priority=Priority.HIGH))
cat.add_task(Task("Medicine", "11:00", category="medication", priority=Priority.HIGH))

scheduler = Scheduler(owner)

# 1. Plain time-sorted schedule
print("=== Sorted by Time ===")
for task in scheduler.sort_by_time():
    print(task)

# 2. Challenge 3: priority-based scheduling (High → Low, then time)
print("\n=== Sorted by Priority (then time) ===")
for task in scheduler.sort_by_priority():
    print(task)

# 3. Challenge 4: structured table output (emojis + color-coded status)
scheduler.print_schedule_table()

# 4. Challenge 1: advanced algorithms
print("=== Weighted Priority Ranking (most important first) ===")
for task in scheduler.get_priority_ranking():
    print(f"  {scheduler.weighted_priority_score(task):>4}  {task.title}")

print("\nNext available 30-min slot after 08:00:",
      scheduler.find_next_available_slot("08:00"))

# 5. Conflict detection
print("\n=== Conflicts ===")
for warning in scheduler.detect_conflicts():
    print(warning)

# 6. Challenge 2: persistence round-trip
saved_path = scheduler.save_to_json("data.json")
print(f"\nSaved schedule to {saved_path}")

reloaded = Scheduler.load_from_json("data.json")
print(f"Reloaded {len(reloaded.get_all_tasks())} tasks for owner '{reloaded.owner.name}'.")
