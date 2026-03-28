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
    start_time: Optional[str] = None  # format HH:MM
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

    def get_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name."""
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = self.get_tasks_by_pet(pet_name)

        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return tasks

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks across all pets."""
        return [task for task in self.get_all_tasks() if task.completed]

    def get_incomplete_tasks(self) -> List[Task]:
        """Get all incomplete tasks across all pets."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def sort_tasks_by_time(self, ascending: bool = True) -> List[Task]:
        """Return tasks sorted by duration using task.time as key."""
        return sorted(self.get_all_tasks(), key=lambda task: task.time, reverse=not ascending)

    def sort_tasks_by_description(self) -> List[Task]:
        """Return tasks sorted alphabetically by description."""
        return sorted(self.get_all_tasks(), key=lambda task: task.description.lower())

    def sort_time_strings(self, times: List[str]) -> List[str]:
        """Sort a list of 'HH:MM' formatted time strings.

        Args:
            times: List of time strings in 24-hour format (e.g. '09:30', '17:15').

        Returns:
            List[str]: New list sorted in chronological order.
        """
        return sorted(times, key=lambda s: tuple(map(int, s.split(':'))))

    def _time_str_to_minutes(self, time_str: str) -> int:
        """Convert an 'HH:MM' string into minutes since midnight.

        Args:
            time_str: Time string in 24-hour format.

        Returns:
            int: Number of minutes from 00:00.
        """
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def get_conflict_warning(self, pet_name: str, new_task: Task) -> Optional[str]:
        """Check if the new task overlaps with existing tasks for the same pet.

        This method performs lightweight conflict detection that returns a warning
        message when tasks overlap, without raising an exception.

        Args:
            pet_name: Name of the pet whose schedule is checked.
            new_task: New Task to validate (must include start_time).

        Returns:
            Optional[str]: Warning message if conflict exists, otherwise None.
        """
        if new_task.start_time is None:
            return None

        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return None

        new_start = self._time_str_to_minutes(new_task.start_time)
        new_end = new_start + new_task.time

        for existing_task in pet.tasks:
            if existing_task.start_time is None:
                continue
            existing_start = self._time_str_to_minutes(existing_task.start_time)
            existing_end = existing_start + existing_task.time

            if new_start < existing_end and existing_start < new_end:
                return (
                    f"Warning: task '{new_task.description}' ({new_task.start_time}) "
                    f"conflicts with '{existing_task.description}' "
                    f"({existing_task.start_time})."
                )

        return None

    def mark_task_complete(self, pet_name: str, description: str) -> bool:
        """Mark a task complete for a given pet.

        If the task is recurring (daily/weekly), automatically create the next instance.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description.lower() == description.lower():
                task.mark_complete()

                if task.frequency.lower() in ["daily", "weekly"]:
                    next_task = Task(task.description, task.time, task.frequency)
                    pet.add_task(next_task)

                return True
        return False

    def _time_str_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM time string to minutes since midnight."""
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def get_conflict_warning(self, pet_name: str, new_task: Task) -> Optional[str]:
        """Return warning message if new_task conflicts with existing tasks; otherwise None."""
        if new_task.start_time is None:
            return None

        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return None

        new_start = self._time_str_to_minutes(new_task.start_time)
        new_end = new_start + new_task.time

        for existing_task in pet.tasks:
            if existing_task.start_time is None:
                continue
            existing_start = self._time_str_to_minutes(existing_task.start_time)
            existing_end = existing_start + existing_task.time

            if new_start < existing_end and existing_start < new_end:
                return (
                    f"Warning: task '{new_task.description}' ({new_task.start_time}) "
                    f"conflicts with '{existing_task.description}' "
                    f"({existing_task.start_time})."
                )

        return None

    def get_schedule_summary(self) -> List[str]:
        """Return a simple text summary of all tasks."""
        summary = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                summary.append(f"{pet.name}: {task.get_summary()}")
        return summary