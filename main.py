from asyncio import all_tasks
from sched import scheduler
from turtle import done

import streamlit as st
from streamlit.config import cat 
from pawpal_system import Owner, Pet, Task, Scheduler
import pandas as pd


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
    # Add overlapping tasks and detect conflict
    # ---------------------------
    same_time_task1 = Task("Walk dog", 30, "Daily", start_time="09:00")
    same_time_task2 = Task("Vet check", 30, "Daily", start_time="09:00")

    dog.add_task(same_time_task1)

    scheduler = Scheduler(owner)
    conflict_warning = scheduler.get_conflict_warning("Buddy", same_time_task2)
    if conflict_warning:
        print("\n" + conflict_warning + "\n")

    dog.add_task(same_time_task2)

    # ---------------------------
    # Create Scheduler
    # ---------------------------
    # scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t.completed)
    remaining = total - done

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tasks", total)
    m2.metric("Completed", done)
    m3.metric("Remaining", remaining)

    st.divider()
    # ---------------------------
    # Add a couple of extra tasks out of immediate priority order
    # ---------------------------
    dog.add_task(Task("Evening walk", 45, "Daily"))
    cat.add_task(Task("Midday nap check", 5, "Daily"))

    # mark some tasks complete for filtering checks
    dog.tasks[1].mark_complete()  # Feed breakfast done
    cat.tasks[0].mark_complete()  # Clean litter box done

    # ---------------------------
    # Print Today's Schedule
    # ---------------------------
    print("\n===== Today's Schedule =====\n")
    for item in scheduler.get_schedule_summary():
        print(item)

    # ---------------------------
    # Print Sort by Duration
    # ---------------------------
    print("\n===== Tasks Sorted by Time (Ascending) =====\n")
    for task in scheduler.sort_tasks_by_time(ascending=True):
        print(task.get_summary())

    # ---------------------------
    # Print Filtered Tasks
    # ---------------------------
    print("\n===== Completed Tasks =====\n")
    for task in scheduler.get_tasks(completed=True):
        print(task.get_summary())

    print("\n===== Incomplete Buddy Tasks =====\n")
    for task in scheduler.get_tasks(pet_name="Buddy", completed=False):
        print(task.get_summary())

    print("\n===========================\n")


    if __name__ == "__main__":
     main()