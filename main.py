from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner("Karla")

# Create pets
dog = Pet("Dog")
cat = Pet("Cat")

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Add tasks out of order to test sorting
task1 = Task("Walk dog", "10:00")
task2 = Task("Feed dog", "08:00")
task3 = Task("Feed cat", "09:00")

dog.add_task(task1)
dog.add_task(task2)
cat.add_task(task3)

# Add conflicting tasks for conflict detection
dog.add_task(Task("Vet visit", "11:00"))
cat.add_task(Task("Medicine", "11:00"))

# Create scheduler
scheduler = Scheduler(owner)

# 1. Sorted schedule
print("Sorted Schedule:")
for task in scheduler.sort_by_time():
    print(task)

# 2. Filter by pet name
print("\nDog Tasks Only:")
for task in scheduler.filter_tasks(pet_name="Dog"):
    print(task)

# 3. Filter completed tasks
task2.mark_complete()

print("\nCompleted Tasks:")
for task in scheduler.filter_tasks(completed=True):
    print(task)

print("\nPending Tasks:")
for task in scheduler.filter_tasks(completed=False):
    print(task)

# 4. Conflict detection
print("\nConflicts:")
for warning in scheduler.detect_conflicts():
    print(warning)
