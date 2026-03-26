from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # ---------------------------
    # Create Owner
    # ---------------------------
    owner = Owner("Aishat")

    # ---------------------------
    # Create Pets
    # ---------------------------
    dog = Pet("Buddy", "Dog", 4)
    cat = Pet("Nyla", "Cat", 2)

    # ---------------------------
    # Create Tasks
    # ---------------------------
    task1 = Task("Morning walk", 30, "Daily")
    task2 = Task("Feed breakfast", 10, "Daily")
    task3 = Task("Play time", 20, "Daily")

    task4 = Task("Clean litter box", 15, "Daily")
    task5 = Task("Evening feeding", 10, "Daily")

    # ---------------------------
    # Assign Tasks to Pets
    # ---------------------------
    dog.add_task(task1)
    dog.add_task(task2)
    dog.add_task(task3)

    cat.add_task(task4)
    cat.add_task(task5)

    # ---------------------------
    # Add Pets to Owner
    # ---------------------------
    owner.add_pet(dog)
    owner.add_pet(cat)

    # ---------------------------
    # Create Scheduler
    # ---------------------------
    scheduler = Scheduler(owner)

    # ---------------------------
    # Print Today's Schedule
    # ---------------------------
    print("\n===== Today's Schedule =====\n")

    schedule = scheduler.get_schedule_summary()

    for item in schedule:
        print(item)

    print("\n===========================\n")


if __name__ == "__main__":
    main()