from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------
# Owner
# ---------------------------
@dataclass
class Owner:
    name: str
    available_time_per_day: int
    preferences: Optional[str] = None

    def update_info(self, name: str, available_time: int):
        pass

    def set_preferences(self, preferences: str):
        pass


# ---------------------------
# Pet
# ---------------------------
@dataclass
class Pet:
    name: str
    type: str
    age: int
    breed: Optional[str] = None
    care_notes: Optional[str] = None

    def update_pet_info(self, name: str, age: int):
        pass

    def get_pet_summary(self):
        pass


# ---------------------------
# Task
# ---------------------------
@dataclass
class Task:
    task_name: str
    duration: int
    priority: int
    category: Optional[str] = None
    preferred_time: Optional[str] = None
    is_completed: bool = False

    def edit_task(self, name: str, duration: int, priority: int):
        pass

    def mark_completed(self):
        pass

    def get_task_details(self):
        pass


# ---------------------------
# Schedule
# ---------------------------
@dataclass
class Schedule:
    date: str
    tasks: List[Task] = field(default_factory=list)
    total_time: int = 0

    def add_task(self, task: Task):
        pass

    def remove_task(self, task: Task):
        pass

    def display_schedule(self):
        pass


# ---------------------------
# Scheduler (logic class)
# ---------------------------
class Scheduler:

    def generate_schedule(self, owner: Owner, pet: Pet, tasks: List[Task]) -> Schedule:
        pass

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass

    def check_time_limit(self, tasks: List[Task], available_time: int) -> List[Task]:
        pass

    def explain_plan(self):
        pass