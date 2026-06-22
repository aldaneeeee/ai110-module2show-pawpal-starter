import pytest

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, is_valid_time

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


# --- Challenge 3: priority-based scheduling --------------------------------

def test_sort_by_priority_orders_high_first():
    owner = Owner("Karla")
    pet = Pet("Dog")
    # Low priority is earlier in the day; High priority is later.
    pet.add_task(Task("Walk", "07:00", priority=Priority.LOW))
    pet.add_task(Task("Vet", "15:00", priority=Priority.HIGH))
    owner.add_pet(pet)

    ordered = Scheduler(owner).sort_by_priority()
    assert ordered[0].title == "Vet"      # High wins despite later time
    assert ordered[1].title == "Walk"


def test_sort_by_priority_falls_back_to_time():
    owner = Owner("Karla")
    pet = Pet("Dog")
    pet.add_task(Task("B", "10:00", priority=Priority.HIGH))
    pet.add_task(Task("A", "08:00", priority=Priority.HIGH))
    owner.add_pet(pet)

    ordered = Scheduler(owner).sort_by_priority()
    assert [t.title for t in ordered] == ["A", "B"]  # same priority -> by time


# --- Challenge 1: advanced algorithmic capability --------------------------

def test_find_next_available_slot_skips_taken_times():
    owner = Owner("Karla")
    pet = Pet("Dog")
    pet.add_task(Task("Feed", "08:00"))
    pet.add_task(Task("Walk", "08:30"))
    owner.add_pet(pet)

    slot = Scheduler(owner).find_next_available_slot("08:00", interval_minutes=30)
    assert slot == "09:00"


def test_weighted_ranking_prioritizes_high():
    owner = Owner("Karla")
    pet = Pet("Dog")
    pet.add_task(Task("Low task", "08:00", priority=Priority.LOW))
    pet.add_task(Task("High task", "09:00", priority=Priority.HIGH))
    owner.add_pet(pet)

    ranking = Scheduler(owner).get_priority_ranking()
    assert ranking[0].title == "High task"


# --- Challenge 2: JSON persistence -----------------------------------------

def test_save_and_load_round_trip(tmp_path):
    owner = Owner("Karla")
    dog = Pet("Dog", "dog")
    dog.add_task(Task("Vet visit", "11:00", priority=Priority.HIGH, category="vet"))
    owner.add_pet(dog)

    path = tmp_path / "data.json"
    Scheduler(owner).save_to_json(str(path))

    reloaded = Scheduler.load_from_json(str(path))
    tasks = reloaded.get_all_tasks()
    assert reloaded.owner.name == "Karla"
    assert len(tasks) == 1
    assert tasks[0].priority is Priority.HIGH
    assert tasks[0].category == "vet"


def test_load_missing_file_returns_empty_scheduler(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    scheduler = Scheduler.load_from_json(str(missing))
    assert scheduler.get_all_tasks() == []


# --- Time validation -------------------------------------------------------

def test_is_valid_time_accepts_good_times():
    assert is_valid_time("08:30")
    assert is_valid_time("00:00")
    assert is_valid_time("23:59")
    assert is_valid_time("8:00")        # single-digit hour is tolerated


def test_is_valid_time_rejects_bad_times():
    assert not is_valid_time("8am")
    assert not is_valid_time("25:00")   # hour out of range
    assert not is_valid_time("08:99")   # minute out of range
    assert not is_valid_time("0800")    # missing colon
    assert not is_valid_time("")


def test_task_rejects_invalid_time():
    with pytest.raises(ValueError):
        Task("Walk dog", "25:00")


def test_reschedule_rejects_invalid_time():
    task = Task("Walk dog", "10:00")
    with pytest.raises(ValueError):
        task.reschedule("nope")
    assert task.time == "10:00"         # unchanged after a failed reschedule
