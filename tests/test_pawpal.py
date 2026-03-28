from pawpal_system import Task, Pet


# ---------------------------
# Test 1: Task Completion
# ---------------------------
def test_task_mark_complete():
    task = Task("Walk dog", 30, "Daily")

    # Initially should be False
    assert task.completed is False

    # Mark complete
    task.mark_complete()

    # Now should be True
    assert task.completed is True


# ---------------------------
# Test 2: Task Addition to Pet
# ---------------------------
def test_add_task_to_pet():
    pet = Pet("Buddy", "Dog", 4)

    # Initially no tasks
    assert len(pet.tasks) == 0

    # Add a task
    task = Task("Feed dog", 10, "Daily")
    pet.add_task(task)

    # Now should have 1 task
    assert len(pet.tasks) == 1


# ---------------------------
# Test 3: Scheduler Task Filtering
# ---------------------------
from pawpal_system import Owner, Scheduler

def test_scheduler_filter_tasks_by_status_and_pet():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    cat = Pet("Mittens", "Cat", 2)

    dog.add_task(Task("Feed dog", 10, "Daily"))
    dog.add_task(Task("Walk dog", 30, "Daily"))
    cat.add_task(Task("Feed cat", 8, "Daily"))

    # Mark one as complete
    dog.tasks[0].mark_complete()

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)

    assert len(scheduler.get_tasks(completed=True)) == 1
    assert len(scheduler.get_tasks(completed=False)) == 2
    assert len(scheduler.get_tasks(pet_name="Buddy")) == 2
    assert len(scheduler.get_tasks(pet_name="Buddy", completed=False)) == 1


def test_scheduler_recurring_task_creates_next_occurrence():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    daily_task = Task("Feed dog", 10, "Daily")

    dog.add_task(daily_task)
    owner.add_pet(dog)

    scheduler = Scheduler(owner)

    assert scheduler.mark_task_complete("Buddy", "Feed dog") is True
    # Original should be completed
    assert dog.tasks[0].completed is True
    # A new recurrence task should be added and incomplete
    assert len(dog.tasks) == 2
    assert dog.tasks[1].description == "Feed dog"
    assert dog.tasks[1].completed is False


def test_scheduler_recurring_task_weekly():
    owner = Owner("Alice")
    cat = Pet("Mittens", "Cat", 2)
    weekly_task = Task("Groom cat", 20, "Weekly")

    cat.add_task(weekly_task)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)

    assert scheduler.mark_task_complete("Mittens", "Groom cat") is True
    assert len(cat.tasks) == 2
    assert cat.tasks[1].description == "Groom cat"
    assert cat.tasks[1].completed is False


def test_scheduler_conflict_warning_for_overlapping_tasks():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    owner.add_pet(dog)

    task1 = Task("Morning walk", 30, "Daily", start_time="09:00")
    task2 = Task("Vet check", 30, "Daily", start_time="09:00")

    dog.add_task(task1)

    scheduler = Scheduler(owner)
    warning = scheduler.get_conflict_warning("Buddy", task2)

    assert warning is not None
    assert "conflicts" in warning


# ---------------------------
# Test: No conflict when tasks don't overlap
# ---------------------------
def test_scheduler_no_conflict_warning_when_tasks_do_not_overlap():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    owner.add_pet(dog)

    # 09:00–09:30, then 10:00–10:30 — gap between them
    task1 = Task("Morning walk", 30, "Daily", start_time="09:00")
    task2 = Task("Training", 30, "Daily", start_time="10:00")

    dog.add_task(task1)

    scheduler = Scheduler(owner)
    warning = scheduler.get_conflict_warning("Buddy", task2)

    assert warning is None


# ---------------------------
# Test: Non-recurring tasks do not auto-queue
# ---------------------------
def test_scheduler_non_recurring_task_does_not_create_next_occurrence():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    one_time_task = Task("Vet appointment", 60, "once")

    dog.add_task(one_time_task)
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    assert scheduler.mark_task_complete("Buddy", "Vet appointment") is True
    assert dog.tasks[0].completed is True
    # No new task should be added
    assert len(dog.tasks) == 1


# ===========================================================
# Edge Case Tests
# ===========================================================

# --- Sorting ---

def test_sort_tasks_by_time_equal_durations_stable():
    """Tasks with equal durations should all appear in the sorted result."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Walk", 30, "daily"))
    dog.add_task(Task("Feed", 30, "daily"))
    dog.add_task(Task("Play", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    result = scheduler.sort_tasks_by_time()
    assert len(result) == 3
    assert all(t.time == 30 for t in result)


def test_sort_time_strings_midnight_boundary():
    """Times near midnight should sort correctly in chronological order."""
    scheduler = Scheduler(Owner("Alice"))
    result = scheduler.sort_time_strings(["23:55", "00:05", "12:00"])
    assert result == ["00:05", "12:00", "23:55"]


def test_sort_time_strings_single_element():
    """A single-element list should not crash and return that element."""
    scheduler = Scheduler(Owner("Alice"))
    result = scheduler.sort_time_strings(["08:00"])
    assert result == ["08:00"]


def test_sort_time_strings_empty_list():
    """An empty list should return an empty list without error."""
    scheduler = Scheduler(Owner("Alice"))
    result = scheduler.sort_time_strings([])
    assert result == []


def test_sort_tasks_by_description_case_insensitive():
    """Alphabetical sort should treat uppercase and lowercase the same."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("walk", 30, "daily"))
    dog.add_task(Task("Feed", 10, "daily"))
    dog.add_task(Task("Groom", 20, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    result = scheduler.sort_tasks_by_description()
    descriptions = [t.description for t in result]
    assert descriptions == sorted(descriptions, key=str.lower)


# --- Recurring tasks ---

def test_recurring_task_case_insensitive_frequency():
    """'Daily' (capitalized) should trigger auto-queue just like 'daily'."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Feed dog", 10, "Daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Buddy", "Feed dog")
    assert len(dog.tasks) == 2


def test_mark_task_complete_unknown_pet_returns_false():
    """Completing a task for a non-existent pet should return False."""
    scheduler = Scheduler(Owner("Alice"))
    assert scheduler.mark_task_complete("Ghost", "Feed") is False


def test_mark_task_complete_unknown_task_returns_false():
    """Completing a task description that doesn't exist should return False."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Feed dog", 10, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    assert scheduler.mark_task_complete("Buddy", "Nonexistent task") is False


def test_recurring_task_completed_twice_queues_two_new_instances():
    """Completing a recurring task twice should result in 3 total tasks."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Feed dog", 10, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Buddy", "Feed dog")   # 1 done + 1 new
    scheduler.mark_task_complete("Buddy", "Feed dog")   # second instance done + 1 new
    assert len(dog.tasks) == 3


# --- Conflict detection ---

def test_conflict_warning_new_task_without_start_time():
    """A new task with no start_time should never trigger a conflict warning."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Morning walk", 30, "daily", start_time="09:00"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    new_task = Task("Training", 30, "daily")  # no start_time
    assert scheduler.get_conflict_warning("Buddy", new_task) is None


def test_conflict_warning_adjacent_tasks_not_overlapping():
    """Tasks that share a boundary (end == next start) should not conflict."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Morning walk", 30, "daily", start_time="09:00"))  # ends 09:30
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    next_task = Task("Training", 30, "daily", start_time="09:30")  # starts 09:30
    assert scheduler.get_conflict_warning("Buddy", next_task) is None


def test_conflict_warning_unknown_pet_returns_none():
    """Checking conflicts for a pet that doesn't exist should return None."""
    scheduler = Scheduler(Owner("Alice"))
    new_task = Task("Walk", 30, "daily", start_time="09:00")
    assert scheduler.get_conflict_warning("Ghost", new_task) is None


# --- Filtering ---

def test_get_tasks_no_filters_returns_all():
    """Calling get_tasks() with no arguments returns every task."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    cat = Pet("Mittens", "Cat", 2)
    dog.add_task(Task("Walk", 30, "daily"))
    cat.add_task(Task("Feed", 10, "daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    assert len(scheduler.get_tasks()) == 2


def test_get_tasks_unknown_pet_returns_empty():
    """Filtering by a pet name that doesn't exist should return an empty list."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Walk", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    assert scheduler.get_tasks(pet_name="Ghost") == []


# ===========================================================
# Task method coverage
# ===========================================================

def test_task_mark_incomplete():
    task = Task("Walk dog", 30, "daily")
    task.mark_complete()
    assert task.completed is True
    task.mark_incomplete()
    assert task.completed is False


def test_task_update_task_fields():
    task = Task("Walk dog", 30, "daily")
    task.update_task(description="Run with dog", time=45, frequency="weekly")
    assert task.description == "Run with dog"
    assert task.time == 45
    assert task.frequency == "weekly"


def test_task_update_task_negative_time_raises():
    import pytest
    task = Task("Walk dog", 30, "daily")
    with pytest.raises(ValueError):
        task.update_task(time=-5)


def test_task_update_task_partial_update():
    """Updating only one field should leave others unchanged."""
    task = Task("Walk dog", 30, "daily")
    task.update_task(time=60)
    assert task.description == "Walk dog"
    assert task.time == 60
    assert task.frequency == "daily"


def test_task_get_summary_incomplete():
    task = Task("Walk dog", 30, "daily")
    summary = task.get_summary()
    assert "Walk dog" in summary
    assert "30" in summary
    assert "Not Completed" in summary


def test_task_get_summary_complete():
    task = Task("Walk dog", 30, "daily")
    task.mark_complete()
    summary = task.get_summary()
    assert "Completed" in summary
    assert "Not Completed" not in summary


# ===========================================================
# Pet method coverage
# ===========================================================

def test_pet_remove_task_existing():
    pet = Pet("Buddy", "Dog", 4)
    pet.add_task(Task("Walk", 30, "daily"))
    assert pet.remove_task("Walk") is True
    assert len(pet.tasks) == 0


def test_pet_remove_task_nonexistent():
    pet = Pet("Buddy", "Dog", 4)
    assert pet.remove_task("Nonexistent") is False


def test_pet_remove_task_case_insensitive():
    pet = Pet("Buddy", "Dog", 4)
    pet.add_task(Task("Walk", 30, "daily"))
    assert pet.remove_task("walk") is True


def test_pet_get_completed_and_incomplete_tasks():
    pet = Pet("Buddy", "Dog", 4)
    t1 = Task("Walk", 30, "daily")
    t2 = Task("Feed", 10, "daily")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)

    assert len(pet.get_completed_tasks()) == 1
    assert len(pet.get_incomplete_tasks()) == 1


def test_pet_get_pet_summary():
    pet = Pet("Buddy", "Dog", 4)
    pet.add_task(Task("Walk", 30, "daily"))
    summary = pet.get_pet_summary()
    assert "Buddy" in summary
    assert "4" in summary
    assert "Dog" in summary


# ===========================================================
# Owner method coverage
# ===========================================================

def test_owner_remove_pet_existing():
    owner = Owner("Alice")
    owner.add_pet(Pet("Buddy", "Dog", 4))
    assert owner.remove_pet("Buddy") is True
    assert len(owner.pets) == 0


def test_owner_remove_pet_nonexistent():
    owner = Owner("Alice")
    assert owner.remove_pet("Ghost") is False


def test_owner_get_pet_found_and_not_found():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    owner.add_pet(dog)

    assert owner.get_pet("Buddy") is dog
    assert owner.get_pet("Ghost") is None


def test_owner_get_all_tasks_across_pets():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    cat = Pet("Mittens", "Cat", 2)
    dog.add_task(Task("Walk", 30, "daily"))
    cat.add_task(Task("Feed", 10, "daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    assert len(owner.get_all_tasks()) == 2


def test_owner_get_owner_summary():
    owner = Owner("Alice")
    owner.add_pet(Pet("Buddy", "Dog", 4))
    summary = owner.get_owner_summary()
    assert "Alice" in summary
    assert "1" in summary


# ===========================================================
# Scheduler.get_schedule_summary
# ===========================================================

def test_scheduler_get_schedule_summary():
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Walk", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    summary = scheduler.get_schedule_summary()
    assert len(summary) == 1
    assert "Buddy" in summary[0]
    assert "Walk" in summary[0]


def test_scheduler_get_schedule_summary_empty():
    scheduler = Scheduler(Owner("Alice"))
    assert scheduler.get_schedule_summary() == []


# ===========================================================
# Required: Sorting Correctness
# Verify tasks are returned in chronological order.
# ===========================================================

def test_sorting_correctness_chronological_order():
    """sort_time_strings returns start times in strict chronological order."""
    scheduler = Scheduler(Owner("Alice"))
    times = ["14:00", "07:30", "09:15", "23:00", "00:45"]
    result = scheduler.sort_time_strings(times)
    assert result == ["00:45", "07:30", "09:15", "14:00", "23:00"]


def test_sorting_correctness_tasks_by_duration_ascending():
    """sort_tasks_by_time(ascending=True) returns shortest tasks first."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Long walk", 60, "daily"))
    dog.add_task(Task("Quick feed", 10, "daily"))
    dog.add_task(Task("Play", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    result = scheduler.sort_tasks_by_time(ascending=True)
    durations = [t.time for t in result]
    assert durations == sorted(durations)


def test_sorting_correctness_tasks_by_duration_descending():
    """sort_tasks_by_time(ascending=False) returns longest tasks first."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Long walk", 60, "daily"))
    dog.add_task(Task("Quick feed", 10, "daily"))
    dog.add_task(Task("Play", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    result = scheduler.sort_tasks_by_time(ascending=False)
    durations = [t.time for t in result]
    assert durations == sorted(durations, reverse=True)


# ===========================================================
# Required: Recurrence Logic
# Marking a daily task complete creates a new incomplete task.
# ===========================================================

def test_recurrence_logic_daily_creates_new_incomplete_task():
    """Completing a daily task produces exactly one new incomplete copy."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Morning walk", 30, "daily"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Buddy", "Morning walk")

    assert dog.tasks[0].completed is True          # original is done
    assert len(dog.tasks) == 2                     # one new task queued
    assert dog.tasks[1].description == "Morning walk"
    assert dog.tasks[1].completed is False         # new task is not yet done
    assert dog.tasks[1].frequency == "daily"       # frequency is preserved


# ===========================================================
# Required: Conflict Detection
# Scheduler flags tasks scheduled at the same time.
# ===========================================================

def test_conflict_detection_flags_exact_duplicate_start_time():
    """Two tasks starting at the same time should produce a conflict warning."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Walk", 30, "daily", start_time="08:00"))
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    duplicate = Task("Feed", 15, "daily", start_time="08:00")
    warning = scheduler.get_conflict_warning("Buddy", duplicate)

    assert warning is not None
    assert "conflicts" in warning.lower()


def test_conflict_detection_flags_partial_overlap():
    """A task starting mid-way through an existing task should be flagged."""
    owner = Owner("Alice")
    dog = Pet("Buddy", "Dog", 4)
    dog.add_task(Task("Walk", 60, "daily", start_time="08:00"))  # 08:00–09:00
    owner.add_pet(dog)

    scheduler = Scheduler(owner)
    overlap = Task("Training", 30, "daily", start_time="08:30")  # 08:30–09:00
    warning = scheduler.get_conflict_warning("Buddy", overlap)

    assert warning is not None
    assert "conflicts" in warning.lower()


