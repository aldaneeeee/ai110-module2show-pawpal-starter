from pawpal_system import Owner, Pet, Task, Scheduler

def test_mark_task_complete():
    task = Task("Feed dog", "08:00")
    task.mark_complete()
    assert task.completed is True

def test_add_task_to_pet():
    pet = Pet("Dog")
    task = Task("Walk dog", "10:00")
    pet.add_task(task)
    assert len(pet.tasks) == 1

def test_owner_add_pet():
    owner = Owner("Karla")
    pet = Pet("Cat")
    owner.add_pet(pet)
    assert len(owner.pets) == 1

def test_scheduler_get_all_tasks():
    owner = Owner("Karla")
    dog = Pet("Dog")
    cat = Pet("Cat")

    dog.add_task(Task("Feed dog", "08:00"))
    cat.add_task(Task("Feed cat", "09:00"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    tasks = scheduler.get_all_tasks()

    assert len(tasks) == 2

def test_sort_by_time():
    owner = Owner("Karla")
    pet = Pet("Dog")

    pet.add_task(Task("Walk", "10:00"))
    pet.add_task(Task("Feed", "08:00"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    tasks = scheduler.sort_by_time()
    assert tasks[0].time == "08:00"
    assert tasks[1].time == "10:00"

def test_detect_conflicts():
    owner = Owner("Karla")
    dog = Pet("Dog")
    cat = Pet("Cat")

    dog.add_task(Task("Walk", "09:00"))
    cat.add_task(Task("Feed", "09:00"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
