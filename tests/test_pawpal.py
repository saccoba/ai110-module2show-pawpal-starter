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