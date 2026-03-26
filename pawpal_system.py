from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """
    Represents a single pet-care activity.
    """
    description: str
    time: int  # duration in minutes
    frequency: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as not completed."""
        self.completed = False

    def update_task(
        self,
        description: Optional[str] = None,
        time: Optional[int] = None,
        frequency: Optional[str] = None,
    ) -> None:
        """Update task details."""
        if description is not None:
            self.description = description
        if time is not None:
            if time < 0:
                raise ValueError("Task time cannot be negative.")
            self.time = time
        if frequency is not None:
            self.frequency = frequency

    def get_summary(self) -> str:
        """Return a readable summary of the task."""
        status = "Completed" if self.completed else "Not Completed"
        return f"{self.description} ({self.time} min, {self.frequency}) - {status}"


@dataclass
class Pet:
    """
    Stores pet details and a list of tasks.
    """
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task matching the description."""
        for task in self.tasks:
            if task.description.lower() == description.lower():
                self.tasks.remove(task)
                return True
        return False

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_completed_tasks(self) -> List[Task]:
        """Return completed tasks only."""
        return [task for task in self.tasks if task.completed]

    def get_incomplete_tasks(self) -> List[Task]:
        """Return incomplete tasks only."""
        return [task for task in self.tasks if not task.completed]

    def get_pet_summary(self) -> str:
        """Return a readable summary of the pet."""
        return f"{self.name} is a {self.age}-year-old {self.species} with {len(self.tasks)} task(s)."


@dataclass
class Owner:
    """
    Manages multiple pets and provides access to all their tasks.
    """
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find and return a pet by name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_owner_summary(self) -> str:
        """Return a readable summary of the owner and pet count."""
        return f"{self.name} has {len(self.pets)} pet(s)."


class Scheduler:
    """
    The brain of the system.
    Retrieves, organizes, and manages tasks across pets.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Get all tasks for one specific pet."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return []
        return pet.get_tasks()

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks across all pets."""
        return [task for task in self.get_all_tasks() if task.completed]

    def get_incomplete_tasks(self) -> List[Task]:
        """Get all incomplete tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def sort_tasks_by_time(self, ascending: bool = True) -> List[Task]:
        """Return tasks sorted by duration."""
        return sorted(self.get_all_tasks(), key=lambda task: task.time, reverse=not ascending)

    def sort_tasks_by_description(self) -> List[Task]:
        """Return tasks sorted alphabetically by description."""
        return sorted(self.get_all_tasks(), key=lambda task: task.description.lower())

    def mark_task_complete(self, pet_name: str, description: str) -> bool:
        """Mark a task complete for a given pet."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description.lower() == description.lower():
                task.mark_complete()
                return True
        return False

    def get_schedule_summary(self) -> List[str]:
        """Return a simple text summary of all tasks."""
        summary = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                summary.append(f"{pet.name}: {task.get_summary()}")
        return summary