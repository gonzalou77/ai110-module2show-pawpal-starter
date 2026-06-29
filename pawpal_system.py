from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
URGENCY_ORDER  = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    species: str
    name: str
    date_of_birth: date
    breed: str
    gotcha_day: date
    next_vet_visit: Optional[date] = None
    flea_tick_due: Optional[date] = None
    heartworm_due: Optional[date] = None

    def check_feeding_schedule(self) -> str:
        """Return a feeding reminder string based on the pet's species."""
        if self.species.lower() == "dog":
            return f"{self.name} should be fed twice a day: morning and evening."
        return f"{self.name} should be fed twice a day or have food available."

    def water_refill_notification(self) -> str:
        """Return a reminder to refill the pet's water bowl."""
        return f"Refill {self.name}'s water bowl at least twice today."

    def vaccination_schedule_check(self) -> str:
        """Return any overdue flea, tick, or heartworm treatments for this pet."""
        today = date.today()
        lines = []
        if self.flea_tick_due and self.flea_tick_due <= today:
            lines.append(f"{self.name}: flea/tick treatment is due ({self.flea_tick_due}).")
        if self.heartworm_due and self.heartworm_due <= today:
            lines.append(f"{self.name}: heartworm treatment is due ({self.heartworm_due}).")
        return "\n".join(lines) if lines else f"{self.name} is up to date on treatments."

    def daily_schedule_check(self) -> str:
        """Return a combined daily summary of feeding, water, and vaccination checks."""
        checks = [
            self.check_feeding_schedule(),
            self.water_refill_notification(),
            self.vaccination_schedule_check(),
        ]
        return "\n".join(checks)


@dataclass
class Task:
    title: str
    frequency: str       # "daily", "weekly", "monthly"
    time: str            # "08:00" — 24-hour format
    priority: str        # "low", "medium", "high"
    status: str          # "pending", "done"
    duration: int        # minutes
    urgency: str         # "low", "medium", "high"
    owner: Optional[Owner] = field(default=None, repr=False)
    pet: Optional[Pet] = field(default=None, repr=False)

    def mark_done(self) -> None:
        """Set the task status to done."""
        self.status = "done"

    def is_pending(self) -> bool:
        """Return True if the task has not been completed yet."""
        return self.status == "pending"


@dataclass
class Owner:
    name: str
    number_of_pets: int
    age: int
    availability: list[str] = field(default_factory=list)  # e.g. ["08:00", "12:00", "18:00"]
    pets: list[Pet] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign this owner to the task and add it to the owner's task list."""
        task.owner = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the owner's task list if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def edit_task(self, task: Task, **updates) -> None:
        """Update any attributes on a task by passing keyword arguments."""
        for attr, value in updates.items():
            if hasattr(task, attr):
                setattr(task, attr, value)

    def check_feeding_schedule(self) -> str:
        """Return feeding reminders for all of this owner's pets."""
        return "\n".join(pet.check_feeding_schedule() for pet in self.pets)

    def check_pet_info(self) -> str:
        """Return a summary of basic info for each of the owner's pets."""
        lines = []
        for pet in self.pets:
            lines.append(
                f"{pet.name} | {pet.species} | {pet.breed} | "
                f"Born: {pet.date_of_birth} | Gotcha: {pet.gotcha_day}"
            )
        return "\n".join(lines)

    def vaccination_schedule_check(self) -> str:
        """Return vaccination and treatment status for all of the owner's pets."""
        return "\n".join(pet.vaccination_schedule_check() for pet in self.pets)

    def daily_schedule_check(self) -> str:
        """Return the full daily care summary for all of the owner's pets."""
        return "\n".join(pet.daily_schedule_check() for pet in self.pets)

    def vet_visit_schedule(self) -> str:
        """Return upcoming vet visit dates for all of the owner's pets."""
        lines = []
        for pet in self.pets:
            if pet.next_vet_visit:
                lines.append(f"{pet.name}: next vet visit on {pet.next_vet_visit}.")
        return "\n".join(lines) if lines else "No upcoming vet visits scheduled."

    def all_pet_tasks(self) -> list[Task]:
        """Collect every task linked to any of this owner's pets."""
        pet_tasks = []
        for task in self.tasks:
            if task.pet in self.pets:
                pet_tasks.append(task)
        return pet_tasks


@dataclass
class Scheduler:
    owner: Owner
    todays_schedule: list[Task] = field(default_factory=list)
    deferred_tasks: list[Task] = field(default_factory=list)
    conflicts: list[Task] = field(default_factory=list)
    vet_visits: list[Task] = field(default_factory=list)

    def generate_schedule(self) -> None:
        """
        Pull all pet-linked tasks from the owner, then bucket them:
        - vet visits go to vet_visits
        - tasks whose time falls outside owner availability go to deferred_tasks
        - overlapping tasks (same time slot) go to conflicts
        - everything else goes to todays_schedule
        """
        self.todays_schedule.clear()
        self.deferred_tasks.clear()
        self.conflicts.clear()
        self.vet_visits.clear()

        pending_tasks = [t for t in self.owner.all_pet_tasks() if t.is_pending()]

        seen_times: dict[str, Task] = {}

        for task in pending_tasks:
            if "vet" in task.title.lower():
                self.vet_visits.append(task)
                continue

            if self.owner.availability and task.time not in self.owner.availability:
                self.deferred_tasks.append(task)
                continue

            if task.time in seen_times:
                self.conflicts.append(task)
            else:
                seen_times[task.time] = task
                self.todays_schedule.append(task)

        self.sort_schedule()

    def sort_schedule(self) -> None:
        """Sort todays_schedule by priority then urgency, then time."""
        self.todays_schedule.sort(key=lambda t: (
            PRIORITY_ORDER.get(t.priority, 99),
            URGENCY_ORDER.get(t.urgency, 99),
            t.time,
        ))

    def edit_schedule(self, task: Task, **updates) -> None:
        """Edit a task's attributes and regenerate the schedule."""
        self.owner.edit_task(task, **updates)
        self.generate_schedule()

    def summary(self) -> str:
        """Return a formatted string of today's schedule, vet visits, conflicts, and deferred tasks."""
        lines = [f"Schedule for {self.owner.name}'s pets\n{'='*40}"]
        if self.todays_schedule:
            lines.append("\nToday's Tasks:")
            for t in self.todays_schedule:
                lines.append(f"  [{t.time}] {t.title} ({t.duration} min) — {t.priority} priority")
        if self.vet_visits:
            lines.append("\nVet Visits:")
            for t in self.vet_visits:
                lines.append(f"  [{t.time}] {t.title}")
        if self.conflicts:
            lines.append("\nConflicts (same time slot):")
            for t in self.conflicts:
                lines.append(f"  [{t.time}] {t.title} — needs rescheduling")
        if self.deferred_tasks:
            lines.append("\nDeferred (outside availability):")
            for t in self.deferred_tasks:
                lines.append(f"  [{t.time}] {t.title}")
        return "\n".join(lines)
