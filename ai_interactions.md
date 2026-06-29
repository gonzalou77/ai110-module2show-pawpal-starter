# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- I asked it to fillout the README.ME -->

**What did the agent do?**

<!-- Let me check the existing test file first.

Globpattern: "tests/**/*.py"
Found 1 file
Read c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\tests\test_pawpal.py
Now I have a clear picture. I'll write comprehensive tests covering sorting, recurrence logic, and conflict detection.

Write c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\tests\test_pawpal.py
452 lines
from datetime import date
import pytest
from pawpal_system import Pet, Task, Owner, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
def second_pet():
    return Pet(
        species="Cat",
        name="Luna",
        date_of_birth=date(2021, 2, 14),
        breed="Tabby",
        gotcha_day=date(2021, 3, 1),
    )


@pytest.fixture
def sample_owner(sample_pet):
    return Owner(
        name="Jordan",
        number_of_pets=1,
        age=30,
        availability=["08:00", "12:00", "18:00"],
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
        due_date=date(2026, 6, 29),
    )


def make_task(title, time, priority, urgency, pet, frequency="daily", status="pending", due_date=date(2026, 6, 29)):
    return Task(
        title=title,
        frequency=frequency,
        time=time,
        priority=priority,
        status=status,
        duration=15,
        urgency=urgency,
        pet=pet,
        due_date=due_date,
    )


# ---------------------------------------------------------------------------
# Existing tests (preserved)
# ---------------------------------------------------------------------------

def test_mark_done_changes_status(sample_task):
    assert sample_task.status == "pending"
    sample_task.mark_done()
    assert sample_task.status == "done"


def test_add_task_increases_pet_task_count(sample_owner, sample_pet, sample_task):
    tasks_for_pet_before = sum(1 for t in sample_owner.tasks if t.pet == sample_pet)
    sample_owner.add_task(sample_task)
    tasks_for_pet_after = sum(1 for t in sample_owner.tasks if t.pet == sample_pet)
    assert tasks_for_pet_after == tasks_for_pet_before + 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

class TestSortingCorrectness:

    def test_sort_schedule_priority_order(self, sample_owner, sample_pet):
        """High-priority tasks should appear before medium and low in todays_schedule."""
        low = make_task("Low task",    "12:00", "low",    "low",    sample_pet)
        med = make_task("Medium task", "08:00", "medium", "medium", sample_pet)
        high = make_task("High task",  "18:00", "high",   "high",   sample_pet)

        for t in [low, med, high]:
            sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        priorities = [t.priority for t in scheduler.todays_schedule]
        assert priorities == sorted(priorities, key=lambda p: {"high": 0, "medium": 1, "low": 2}[p])

    def test_sort_schedule_urgency_tiebreaker(self, sample_owner, sample_pet):
        """When priority is equal, higher-urgency tasks should come first."""
        high_u = make_task("High urgency", "08:00", "high", "high",   sample_pet)
        low_u  = make_task("Low urgency",  "12:00", "high", "low",    sample_pet)

        for t in [low_u, high_u]:
            sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert scheduler.todays_schedule[0].urgency == "high"

    def test_sort_by_time_overrides_priority_sort(self, sample_owner, sample_pet):
        """sort_by_time() should reorder tasks chronologically regardless of priority."""
        t1 = make_task("Late high",   "18:00", "high", "high", sample_pet)
        t2 = make_task("Early low",   "08:00", "low",  "low",  sample_pet)

        for t in [t1, t2]:
            sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()
        scheduler.sort_by_time()

        times = [t.time for t in scheduler.todays_schedule]
        assert times == sorted(times)

    def test_sort_by_time_stable_for_single_task(self, sample_owner, sample_pet):
        """sort_by_time() on a single-task schedule should not crash or reorder."""
        t = make_task("Solo task", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()
        scheduler.sort_by_time()

        assert len(scheduler.todays_schedule) == 1


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

class TestFiltering:

    def test_filter_by_status_pending(self, sample_owner, sample_pet):
        """filter_tasks(status='pending') returns only pending tasks."""
        t1 = make_task("Walk",  "08:00", "high", "high", sample_pet)
        t2 = make_task("Bath",  "12:00", "low",  "low",  sample_pet, status="done")

        for t in [t1, t2]:
            sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        # manually put done task into todays_schedule for filter testing
        scheduler.todays_schedule.append(t2)
        result = scheduler.filter_tasks(status="pending")
        assert all(t.status == "pending" for t in result)

    def test_filter_by_pet_name(self, second_pet, sample_pet):
        """filter_tasks(pet_name=...) returns only tasks for that pet."""
        owner = Owner(
            name="Jordan", number_of_pets=2, age=30,
            availability=["08:00", "12:00"],
            pets=[sample_pet, second_pet],
        )
        t_mochi = make_task("Walk Mochi", "08:00", "high", "high", sample_pet)
        t_luna  = make_task("Feed Luna",  "12:00", "low",  "low",  second_pet)

        owner.add_task(t_mochi)
        owner.add_task(t_luna)

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        result = scheduler.filter_tasks(pet_name="Luna")
        assert all(t.pet.name == "Luna" for t in result)

    def test_filter_combined_status_and_pet(self, second_pet, sample_pet):
        """filter_tasks with both args returns only matching tasks."""
        owner = Owner(
            name="Jordan", number_of_pets=2, age=30,
            availability=["08:00", "12:00"],
            pets=[sample_pet, second_pet],
        )
        t1 = make_task("Walk Mochi", "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed Luna",  "12:00", "low",  "low",  second_pet)

        owner.add_task(t1)
        owner.add_task(t2)

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        result = scheduler.filter_tasks(status="pending", pet_name="Mochi")
        assert all(t.status == "pending" and t.pet.name == "Mochi" for t in result)

    def test_filter_no_args_returns_all(self, sample_owner, sample_pet):
        """filter_tasks() with no args returns every task in todays_schedule."""
        for i, time in enumerate(["08:00", "12:00", "18:00"]):
            sample_owner.add_task(make_task(f"Task {i}", time, "high", "high", sample_pet))

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert scheduler.filter_tasks() == scheduler.todays_schedule

    def test_filter_does_not_mutate_schedule(self, sample_owner, sample_pet):
        """filter_tasks() must not modify todays_schedule in place."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()
        original_len = len(scheduler.todays_schedule)

        scheduler.filter_tasks(status="done")  # should return empty, not remove tasks
        assert len(scheduler.todays_schedule) == original_len


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

class TestRecurrenceLogic:

    def test_daily_recurrence_advances_one_day(self, sample_owner, sample_pet):
        """Completing a daily task creates a new task due the next day."""
        t = make_task("Daily walk", "08:00", "high", "high", sample_pet,
                      frequency="daily", due_date=date(2026, 6, 29))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task is not None
        assert next_task.due_date == date(2026, 6, 30)
        assert next_task.status == "pending"

    def test_weekly_recurrence_advances_seven_days(self, sample_owner, sample_pet):
        """Completing a weekly task creates a new task due seven days later."""
        t = make_task("Weekly bath", "08:00", "medium", "medium", sample_pet,
                      frequency="weekly", due_date=date(2026, 6, 29))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task is not None
        assert next_task.due_date == date(2026, 7, 6)

    def test_monthly_recurrence_advances_one_month(self, sample_owner, sample_pet):
        """Completing a monthly task creates a new task in the following month."""
        t = make_task("Monthly vet", "08:00", "high", "high", sample_pet,
                      frequency="monthly", due_date=date(2026, 6, 15))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task is not None
        assert next_task.due_date == date(2026, 7, 15)

    def test_monthly_recurrence_clamps_feb(self, sample_owner, sample_pet):
        """Jan 31 monthly task should clamp to Feb 28 (non-leap year)."""
        t = make_task("Monthly check", "08:00", "low", "low", sample_pet,
                      frequency="monthly", due_date=date(2026, 1, 31))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task.due_date == date(2026, 2, 28)

    def test_monthly_recurrence_december_rolls_to_january(self, sample_owner, sample_pet):
        """Dec monthly task should roll over to January of the next year."""
        t = make_task("Dec task", "08:00", "low", "low", sample_pet,
                      frequency="monthly", due_date=date(2026, 12, 10))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task.due_date == date(2027, 1, 10)

    def test_recurrence_registers_next_task_with_owner(self, sample_owner, sample_pet):
        """complete_task() should add the next occurrence to owner.tasks."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet, frequency="daily")
        sample_owner.add_task(t)
        initial_count = len(sample_owner.tasks)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.complete_task(t)

        assert len(sample_owner.tasks) == initial_count + 1

    def test_one_time_task_returns_none(self, sample_owner, sample_pet):
        """Tasks with an unknown/one-time frequency should not generate a recurrence."""
        t = make_task("One-off grooming", "08:00", "low", "low", sample_pet, frequency="once")
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        result = scheduler.complete_task(t)

        assert result is None

    def test_completed_task_is_marked_done(self, sample_owner, sample_pet):
        """complete_task() must mark the original task as done."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.complete_task(t)

        assert t.status == "done"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:

    def test_same_time_different_pets_is_owner_conflict(self, sample_pet, second_pet):
        """Two tasks at the same time for different pets = owner conflict."""
        owner = Owner(
            name="Jordan", number_of_pets=2, age=30,
            availability=["08:00"],
            pets=[sample_pet, second_pet],
        )
        t1 = make_task("Walk Mochi", "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed Luna",  "08:00", "low",  "low",  second_pet)
        owner.add_task(t1)
        owner.add_task(t2)

        scheduler = Scheduler(owner=owner)
        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "Owner conflict" in warnings[0]
        assert "08:00" in warnings[0]

    def test_same_time_same_pet_is_same_pet_conflict(self, sample_owner, sample_pet):
        """Two tasks at the same time for the same pet = same-pet conflict."""
        t1 = make_task("Walk",  "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed",  "08:00", "low",  "low",  sample_pet)
        sample_owner.add_task(t1)
        sample_owner.add_task(t2)

        scheduler = Scheduler(owner=sample_owner)
        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "Same-pet conflict" in warnings[0]

    def test_no_conflict_different_times(self, sample_owner, sample_pet):
        """Tasks at different time slots should produce no warnings."""
        t1 = make_task("Walk", "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed", "12:00", "low",  "low",  sample_pet)
        sample_owner.add_task(t1)
        sample_owner.add_task(t2)

        scheduler = Scheduler(owner=sample_owner)
        warnings = scheduler.detect_conflicts()

        assert warnings == []

    def test_three_tasks_same_time_produces_three_pairs(self, sample_pet, second_pet):
        """Three tasks at the same time slot should produce C(3,2)=3 conflict pairs."""
        third_pet = Pet(
            species="Dog", name="Rex",
            date_of_birth=date(2018, 1, 1),
            breed="Lab",
            gotcha_day=date(2018, 2, 1),
        )
        owner = Owner(
            name="Jordan", number_of_pets=3, age=30,
            availability=["08:00"],
            pets=[sample_pet, second_pet, third_pet],
        )
        for pet in [sample_pet, second_pet, third_pet]:
            owner.add_task(make_task(f"Task {pet.name}", "08:00", "high", "high", pet))

        scheduler = Scheduler(owner=owner)
        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 3

    def test_done_tasks_excluded_from_conflict_detection(self, sample_owner, sample_pet):
        """Completed tasks should not appear in conflict detection results."""
        t1 = make_task("Walk", "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed", "08:00", "low",  "low",  sample_pet, status="done")
        sample_owner.add_task(t1)
        sample_owner.add_task(t2)

        scheduler = Scheduler(owner=sample_owner)
        warnings = scheduler.detect_conflicts()

        assert warnings == []

    def test_generate_schedule_buckets_conflicts(self, sample_pet, second_pet):
        """generate_schedule() should move second task at same slot to conflicts list."""
        owner = Owner(
            name="Jordan", number_of_pets=2, age=30,
            availability=["08:00"],
            pets=[sample_pet, second_pet],
        )
        t1 = make_task("Walk Mochi", "08:00", "high", "high", sample_pet)
        t2 = make_task("Feed Luna",  "08:00", "low",  "low",  second_pet)
        owner.add_task(t1)
        owner.add_task(t2)

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert len(scheduler.todays_schedule) == 1
        assert len(scheduler.conflicts) == 1

    def test_deferred_tasks_outside_availability(self, sample_owner, sample_pet):
        """Tasks at times not in owner availability are deferred, not scheduled."""
        t = make_task("Midnight walk", "00:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert t in scheduler.deferred_tasks
        assert t not in scheduler.todays_schedule

    def test_vet_tasks_routed_to_vet_visits(self, sample_owner, sample_pet):
        """Tasks with 'vet' in the title go to vet_visits, not todays_schedule."""
        t = make_task("Vet checkup", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert t in scheduler.vet_visits
        assert t not in scheduler.todays_schedule
i forgot, include edge cases as well.
Now let me run the tests to confirm they all pass before addressing edge cases.

Bash
IN
cd "c:/Users/gonza/OneDrive/Desktop/CodePath/Unit-3/ai110-module2show-pawpal-starter" && python -m pytest tests/test_pawpal.py -v 2>&1

OUT
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 27 items

tests/test_pawpal.py::test_mark_done_changes_status PASSED               [  3%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  7%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_priority_order PASSED [ 11%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_urgency_tiebreaker PASSED [ 14%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_overrides_priority_sort PASSED [ 18%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_stable_for_single_task PASSED [ 22%]
tests/test_pawpal.py::TestFiltering::test_filter_by_status_pending PASSED [ 25%]
tests/test_pawpal.py::TestFiltering::test_filter_by_pet_name PASSED      [ 29%]
tests/test_pawpal.py::TestFiltering::test_filter_combined_status_and_pet PASSED [ 33%]
tests/test_pawpal.py::TestFiltering::test_filter_no_args_returns_all PASSED [ 37%]
tests/test_pawpal.py::TestFiltering::test_filter_does_not_mutate_schedule PASSED [ 40%]
tests/test_pawpal.py::TestRecurrenceLogic::test_daily_recurrence_advances_one_day PASSED [ 44%]
tests/test_pawpal.py::TestRecurrenceLogic::test_weekly_recurrence_advances_seven_days PASSED [ 48%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_advances_one_month PASSED [ 51%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_clamps_feb PASSED [ 55%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_december_rolls_to_january PASSED [ 59%]
tests/test_pawpal.py::TestRecurrenceLogic::test_recurrence_registers_next_task_with_owner PASSED [ 62%]
tests/test_pawpal.py::TestRecurrenceLogic::test_one_time_task_returns_none PASSED [ 66%]
tests/test_pawpal.py::TestRecurrenceLogic::test_completed_task_is_marked_done PASSED [ 70%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_different_pets_is_owner_conflict PASSED [ 74%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_same_pet_is_same_pet_conflict PASSED [ 77%]
tests/test_pawpal.py::TestConflictDetection::test_no_conflict_different_times PASSED [ 81%]
tests/test_pawpal.py::TestConflictDetection::test_three_tasks_same_time_produces_three_pairs PASSED [ 85%]
tests/test_pawpal.py::TestConflictDetection::test_done_tasks_excluded_from_conflict_detection PASSED [ 88%]
tests/test_pawpal.py::TestConflictDetection::test_generate_schedule_buckets_conflicts PASSED [ 92%]
tests/test_pawpal.py::TestConflictDetection::test_deferred_tasks_outside_availability PASSED [ 96%]
tests/test_pawpal.py::TestConflictDetection::test_vet_tasks_routed_to_vet_visits PASSED [100%]

============================= 27 passed in 0.07s ==============================
All 27 pass. Now adding the edge cases you requested.

Read c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\tests\test_pawpal.py (from line 331)
Edit c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\tests\test_pawpal.py
Added 182 lines
Bash
IN
cd "c:/Users/gonza/OneDrive/Desktop/CodePath/Unit-3/ai110-module2show-pawpal-starter" && python -m pytest tests/test_pawpal.py -v 2>&1

OUT
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 41 items

tests/test_pawpal.py::test_mark_done_changes_status PASSED               [  2%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  4%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_priority_order PASSED [  7%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_urgency_tiebreaker PASSED [  9%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_overrides_priority_sort PASSED [ 12%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_stable_for_single_task PASSED [ 14%]
tests/test_pawpal.py::TestFiltering::test_filter_by_status_pending PASSED [ 17%]
tests/test_pawpal.py::TestFiltering::test_filter_by_pet_name PASSED      [ 19%]
tests/test_pawpal.py::TestFiltering::test_filter_combined_status_and_pet PASSED [ 21%]
tests/test_pawpal.py::TestFiltering::test_filter_no_args_returns_all PASSED [ 24%]
tests/test_pawpal.py::TestFiltering::test_filter_does_not_mutate_schedule PASSED [ 26%]
tests/test_pawpal.py::TestRecurrenceLogic::test_daily_recurrence_advances_one_day PASSED [ 29%]
tests/test_pawpal.py::TestRecurrenceLogic::test_weekly_recurrence_advances_seven_days PASSED [ 31%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_advances_one_month PASSED [ 34%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_clamps_feb PASSED [ 36%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_december_rolls_to_january PASSED [ 39%]
tests/test_pawpal.py::TestRecurrenceLogic::test_recurrence_registers_next_task_with_owner PASSED [ 41%]
tests/test_pawpal.py::TestRecurrenceLogic::test_one_time_task_returns_none PASSED [ 43%]
tests/test_pawpal.py::TestRecurrenceLogic::test_completed_task_is_marked_done PASSED [ 46%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_different_pets_is_owner_conflict PASSED [ 48%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_same_pet_is_same_pet_conflict PASSED [ 51%]
tests/test_pawpal.py::TestConflictDetection::test_no_conflict_different_times PASSED [ 53%]
tests/test_pawpal.py::TestConflictDetection::test_three_tasks_same_time_produces_three_pairs PASSED [ 56%]
tests/test_pawpal.py::TestConflictDetection::test_done_tasks_excluded_from_conflict_detection PASSED [ 58%]
tests/test_pawpal.py::TestConflictDetection::test_generate_schedule_buckets_conflicts PASSED [ 60%]
tests/test_pawpal.py::TestConflictDetection::test_deferred_tasks_outside_availability PASSED [ 63%]
tests/test_pawpal.py::TestConflictDetection::test_vet_tasks_routed_to_vet_visits PASSED [ 65%]
tests/test_pawpal.py::TestEdgeCases::test_generate_schedule_no_tasks PASSED [ 68%]
tests/test_pawpal.py::TestEdgeCases::test_detect_conflicts_no_tasks PASSED [ 70%]
tests/test_pawpal.py::TestEdgeCases::test_filter_tasks_empty_schedule PASSED [ 73%]
tests/test_pawpal.py::TestEdgeCases::test_generate_schedule_resets_previous_results PASSED [ 75%]
tests/test_pawpal.py::TestEdgeCases::test_empty_availability_lets_all_tasks_through PASSED [ 78%]
tests/test_pawpal.py::TestEdgeCases::test_recurrence_preserves_all_task_fields PASSED [ 80%]
tests/test_pawpal.py::TestEdgeCases::test_monthly_recurrence_leap_year_feb PASSED [ 82%]
tests/test_pawpal.py::TestEdgeCases::test_complete_task_on_already_done_task PASSED [ 85%]
tests/test_pawpal.py::TestEdgeCases::test_filter_nonexistent_pet_name_returns_empty PASSED [ 87%]
tests/test_pawpal.py::TestEdgeCases::test_filter_task_with_no_pet_excluded_by_pet_name PASSED [ 90%]
tests/test_pawpal.py::TestEdgeCases::test_sort_empty_schedule_does_not_crash PASSED [ 92%]
tests/test_pawpal.py::TestEdgeCases::test_sort_schedule_all_same_priority_urgency_sorted_by_time PASSED [ 95%]
tests/test_pawpal.py::TestEdgeCases::test_conflict_warning_includes_task_titles PASSED [ 97%]
tests/test_pawpal.py::TestEdgeCases::test_no_false_conflict_across_different_days PASSED [100%]

============================= 41 passed in 0.09s ==============================
41/41 passing. Here's a summary of what was built:

4 test classes, 41 total tests:

Class	# Tests	What it covers
TestSortingCorrectness	4	Priority order, urgency tiebreaker, sort_by_time() override, single-task stability
TestFiltering	5	Filter by status, by pet name, combined AND filter, no-args passthrough, immutability
TestRecurrenceLogic	8	Daily/weekly/monthly advancement, Feb clamping (non-leap + leap year), Dec→Jan rollover, owner registration, one-time tasks, mark-done side effect
TestConflictDetection	8	Owner vs same-pet conflicts, 3-way combinatorics, done tasks excluded, generate_schedule bucketing, deferral, vet routing
TestEdgeCases	14	Empty schedule/no tasks, double generate_schedule() idempotency, empty availability, recurrence field preservation, leap-year Feb 29, filtering ghost pets/null-pet tasks, sorting an empty list, conflict warning content, same-time across different due dates
\temp\readonly\Bash tool output (9ivcy2)
add a section titled "Testing PawPal+" in the README.md. include the command to run tests (python -m pytest) and a brief description of what the tests cover and provide a confidence level (1-5 starts) in the systems reliability based on the test results
Globpattern: "README.md"
Found 6 files
Read c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md
The README already has a Testing PawPal+ section but it's outdated — only 2 tests and no description. I'll replace it with the full updated version.

Edit c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md
Removed 1 line
Read c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md (lines 66-95)
Edit c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md
Modified
Fixed two linting warnings: added spaces around the | separators in the table divider row (MD060), and changed the bold-star rating to plain text so it's no longer flagged as emphasis-used-as-heading (MD036).

c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md
please include the bash output of the pytest results as well
Bash Run pytest and capture full output
IN
cd "c:/Users/gonza/OneDrive/Desktop/CodePath/Unit-3/ai110-module2show-pawpal-starter" && python -m pytest tests/test_pawpal.py -v 2>&1

OUT
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 41 items

tests/test_pawpal.py::test_mark_done_changes_status PASSED               [  2%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  4%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_priority_order PASSED [  7%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_schedule_urgency_tiebreaker PASSED [  9%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_overrides_priority_sort PASSED [ 12%]
tests/test_pawpal.py::TestSortingCorrectness::test_sort_by_time_stable_for_single_task PASSED [ 14%]
tests/test_pawpal.py::TestFiltering::test_filter_by_status_pending PASSED [ 17%]
tests/test_pawpal.py::TestFiltering::test_filter_by_pet_name PASSED      [ 19%]
tests/test_pawpal.py::TestFiltering::test_filter_combined_status_and_pet PASSED [ 21%]
tests/test_pawpal.py::TestFiltering::test_filter_no_args_returns_all PASSED [ 24%]
tests/test_pawpal.py::TestFiltering::test_filter_does_not_mutate_schedule PASSED [ 26%]
tests/test_pawpal.py::TestRecurrenceLogic::test_daily_recurrence_advances_one_day PASSED [ 29%]
tests/test_pawpal.py::TestRecurrenceLogic::test_weekly_recurrence_advances_seven_days PASSED [ 31%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_advances_one_month PASSED [ 34%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_clamps_feb PASSED [ 36%]
tests/test_pawpal.py::TestRecurrenceLogic::test_monthly_recurrence_december_rolls_to_january PASSED [ 39%]
tests/test_pawpal.py::TestRecurrenceLogic::test_recurrence_registers_next_task_with_owner PASSED [ 41%]
tests/test_pawpal.py::TestRecurrenceLogic::test_one_time_task_returns_none PASSED [ 43%]
tests/test_pawpal.py::TestRecurrenceLogic::test_completed_task_is_marked_done PASSED [ 46%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_different_pets_is_owner_conflict PASSED [ 48%]
tests/test_pawpal.py::TestConflictDetection::test_same_time_same_pet_is_same_pet_conflict PASSED [ 51%]
tests/test_pawpal.py::TestConflictDetection::test_no_conflict_different_times PASSED [ 53%]
tests/test_pawpal.py::TestConflictDetection::test_three_tasks_same_time_produces_three_pairs PASSED [ 56%]
tests/test_pawpal.py::TestConflictDetection::test_done_tasks_excluded_from_conflict_detection PASSED [ 58%]
tests/test_pawpal.py::TestConflictDetection::test_generate_schedule_buckets_conflicts PASSED [ 60%]
tests/test_pawpal.py::TestConflictDetection::test_deferred_tasks_outside_availability PASSED [ 63%]
tests/test_pawpal.py::TestConflictDetection::test_vet_tasks_routed_to_vet_visits PASSED [ 65%]
tests/test_pawpal.py::TestEdgeCases::test_generate_schedule_no_tasks PASSED [ 68%]
tests/test_pawpal.py::TestEdgeCases::test_detect_conflicts_no_tasks PASSED [ 70%]
tests/test_pawpal.py::TestEdgeCases::test_filter_tasks_empty_schedule PASSED [ 73%]
tests/test_pawpal.py::TestEdgeCases::test_generate_schedule_resets_previous_results PASSED [ 75%]
tests/test_pawpal.py::TestEdgeCases::test_empty_availability_lets_all_tasks_through PASSED [ 78%]
tests/test_pawpal.py::TestEdgeCases::test_recurrence_preserves_all_task_fields PASSED [ 80%]
tests/test_pawpal.py::TestEdgeCases::test_monthly_recurrence_leap_year_feb PASSED [ 82%]
tests/test_pawpal.py::TestEdgeCases::test_complete_task_on_already_done_task PASSED [ 85%]
tests/test_pawpal.py::TestEdgeCases::test_filter_nonexistent_pet_name_returns_empty PASSED [ 87%]
tests/test_pawpal.py::TestEdgeCases::test_filter_task_with_no_pet_excluded_by_pet_name PASSED [ 90%]
tests/test_pawpal.py::TestEdgeCases::test_sort_empty_schedule_does_not_crash PASSED [ 92%]
tests/test_pawpal.py::TestEdgeCases::test_sort_schedule_all_same_priority_urgency_sorted_by_time PASSED [ 95%]
tests/test_pawpal.py::TestEdgeCases::test_conflict_warning_includes_task_titles PASSED [ 97%]
tests/test_pawpal.py::TestEdgeCases::test_no_false_conflict_across_different_days PASSED [100%]

============================= 41 passed in 0.05s ==============================
Edit c:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\README.md
Added 55 lines
Click to expand
The pytest output is now embedded in the README under a "Sample output" subsection, sitting between the coverage table and the reliability confidence rating. -->

**What did you have to verify or fix manually?**

<!-- i had to verify that the sample output was in fact in the README.md file. when i checked, it was not and had to prompt again for it to be included in the  README.me file. Though it sounds like a waste to use AI for this, but in reality an accurate and good README.md file takes time to properly craft. Using AI for this make the README.md file setup more efficient and accurate -->

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
