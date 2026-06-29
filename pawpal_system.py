from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


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

    def check_feeding_schedule(self) -> None:
        pass

    def water_refill_notification(self) -> None:
        pass

    def vaccination_schedule_check(self) -> None:
        pass

    def daily_schedule_check(self) -> None:
        pass


@dataclass
class Task:
    frequency: str
    time: str
    priority: str
    status: str
    duration: int
    urgency: str
    owner: Optional[Owner] = field(default=None, repr=False)
    pet: Optional[Pet] = field(default=None, repr=False)


@dataclass
class Owner:
    name: str
    number_of_pets: int
    age: int
    availability: list[str] = field(default_factory=list)

    def check_feeding_schedule(self) -> None:
        pass

    def check_pet_info(self) -> None:
        pass

    def vaccination_schedule_check(self) -> None:
        pass

    def daily_schedule_check(self) -> None:
        pass

    def vet_visit_schedule(self) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def edit_task(self, task: Task) -> None:
        pass


@dataclass
class Scheduler:
    owner: Owner
    todays_schedule: list = field(default_factory=list)
    deferred_tasks: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)
    vet_visits: list = field(default_factory=list)

    def generate_schedule(self) -> None:
        pass

    def sort_schedule(self) -> None:
        pass

    def edit_schedule(self) -> None:
        pass
