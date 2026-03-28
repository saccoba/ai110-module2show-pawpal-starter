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


