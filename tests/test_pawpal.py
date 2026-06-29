from datetime import date
import pytest
from pawpal_system import Pet, Task, Owner


@pytest.fixture
def sample_pet():
    return Pet(
        species="Dog",
        name="Mochi",
        date_of_birth=date(2019, 4, 12),
        breed="Shiba Inu",
        gotcha_day=date(2019, 6, 1),
    )


@pytest.fixture
def sample_owner(sample_pet):
    return Owner(
        name="Jordan",
        number_of_pets=1,
        age=30,
        pets=[sample_pet],
    )


@pytest.fixture
def sample_task(sample_pet):
    return Task(
        title="Morning walk",
        frequency="daily",
        time="08:00",
        priority="high",
        status="pending",
        duration=30,
        urgency="high",
        pet=sample_pet,
    )


def test_mark_done_changes_status(sample_task):
    assert sample_task.status == "pending"
    sample_task.mark_done()
    assert sample_task.status == "done"


def test_add_task_increases_pet_task_count(sample_owner, sample_pet, sample_task):
    tasks_for_pet_before = sum(1 for t in sample_owner.tasks if t.pet == sample_pet)
    sample_owner.add_task(sample_task)
    tasks_for_pet_after = sum(1 for t in sample_owner.tasks if t.pet == sample_pet)
    assert tasks_for_pet_after == tasks_for_pet_before + 1
