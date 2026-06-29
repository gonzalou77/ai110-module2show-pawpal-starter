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


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    # --- Empty / boundary states ---

    def test_generate_schedule_no_tasks(self, sample_owner):
        """Scheduler with no tasks should produce empty lists without errors."""
        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert scheduler.todays_schedule == []
        assert scheduler.conflicts == []
        assert scheduler.deferred_tasks == []
        assert scheduler.vet_visits == []

    def test_detect_conflicts_no_tasks(self, sample_owner):
        """detect_conflicts() on an owner with no tasks returns an empty list."""
        scheduler = Scheduler(owner=sample_owner)
        assert scheduler.detect_conflicts() == []

    def test_filter_tasks_empty_schedule(self, sample_owner):
        """filter_tasks on an empty schedule should return an empty list."""
        scheduler = Scheduler(owner=sample_owner)
        assert scheduler.filter_tasks(status="pending") == []

    def test_generate_schedule_resets_previous_results(self, sample_owner, sample_pet):
        """Calling generate_schedule() twice should not accumulate stale results."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()
        scheduler.generate_schedule()  # second call

        assert len(scheduler.todays_schedule) == 1

    # --- Availability edge cases ---

    def test_empty_availability_lets_all_tasks_through(self, sample_pet):
        """When owner.availability is empty, no tasks are deferred for time mismatch."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=[],   # open schedule — no restrictions
            pets=[sample_pet],
        )
        t = make_task("Walk", "03:00", "high", "high", sample_pet)
        owner.add_task(t)

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert t in scheduler.todays_schedule
        assert scheduler.deferred_tasks == []

    # --- Recurrence edge cases ---

    def test_recurrence_preserves_all_task_fields(self, sample_owner, sample_pet):
        """next_occurrence() should carry over title, time, priority, urgency, duration."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet,
                      frequency="daily", due_date=date(2026, 6, 29))
        t.duration = 45
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_t = scheduler.complete_task(t)

        assert next_t.title == t.title
        assert next_t.time == t.time
        assert next_t.priority == t.priority
        assert next_t.urgency == t.urgency
        assert next_t.duration == t.duration
        assert next_t.pet is t.pet

    def test_monthly_recurrence_leap_year_feb(self, sample_owner, sample_pet):
        """Jan 31 monthly task in a leap year should clamp to Feb 29."""
        t = make_task("Leap check", "08:00", "low", "low", sample_pet,
                      frequency="monthly", due_date=date(2028, 1, 31))  # 2028 is a leap year
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_task = scheduler.complete_task(t)

        assert next_task.due_date == date(2028, 2, 29)

    def test_complete_task_on_already_done_task(self, sample_owner, sample_pet):
        """Completing an already-done task still generates a recurrence (idempotency)."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet,
                      frequency="daily", status="done", due_date=date(2026, 6, 29))
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        next_t = scheduler.complete_task(t)

        assert next_t is not None
        assert next_t.status == "pending"

    # --- Filtering edge cases ---

    def test_filter_nonexistent_pet_name_returns_empty(self, sample_owner, sample_pet):
        """Filtering by a pet name that matches no task returns an empty list."""
        t = make_task("Walk", "08:00", "high", "high", sample_pet)
        sample_owner.add_task(t)

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        assert scheduler.filter_tasks(pet_name="Ghost") == []

    def test_filter_task_with_no_pet_excluded_by_pet_name(self, sample_owner):
        """A task with pet=None should be excluded when filtering by pet_name."""
        t = Task(
            title="Generic task", frequency="daily", time="08:00",
            priority="low", status="pending", duration=10, urgency="low",
            pet=None, due_date=date(2026, 6, 29),
        )
        sample_owner.add_task(t)
        scheduler = Scheduler(owner=sample_owner)
        # manually place task since it has no pet (all_pet_tasks skips it)
        scheduler.todays_schedule.append(t)

        result = scheduler.filter_tasks(pet_name="Mochi")
        assert t not in result

    # --- Sorting edge cases ---

    def test_sort_empty_schedule_does_not_crash(self, sample_owner):
        """sort_by_time() and sort_schedule() on an empty list should not raise."""
        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()
        scheduler.sort_by_time()   # should not raise
        scheduler.sort_schedule()  # should not raise

    def test_sort_schedule_all_same_priority_urgency_sorted_by_time(self, sample_owner, sample_pet):
        """When priority and urgency are identical, tasks are ordered by time string."""
        times = ["18:00", "08:00", "12:00"]
        for i, t in enumerate(times):
            sample_owner.add_task(make_task(f"Task {i}", t, "medium", "medium", sample_pet))

        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_schedule()

        result_times = [t.time for t in scheduler.todays_schedule]
        assert result_times == sorted(result_times)

    # --- Conflict detection edge cases ---

    def test_conflict_warning_includes_task_titles(self, sample_pet, second_pet):
        """Conflict warning strings should mention both conflicting task titles."""
        owner = Owner(
            name="Jordan", number_of_pets=2, age=30,
            availability=["08:00"],
            pets=[sample_pet, second_pet],
        )
        t1 = make_task("Alpha task", "08:00", "high", "high", sample_pet)
        t2 = make_task("Beta task",  "08:00", "low",  "low",  second_pet)
        owner.add_task(t1)
        owner.add_task(t2)

        scheduler = Scheduler(owner=owner)
        warnings = scheduler.detect_conflicts()

        assert "Alpha task" in warnings[0]
        assert "Beta task" in warnings[0]

    def test_no_false_conflict_across_different_days(self, sample_owner, sample_pet):
        """Tasks on different due_dates but the same time string should still conflict
        because detect_conflicts() keys only on time, not date."""
        t1 = make_task("Walk", "08:00", "high", "high", sample_pet, due_date=date(2026, 6, 29))
        t2 = make_task("Feed", "08:00", "low",  "low",  sample_pet, due_date=date(2026, 6, 30))
        sample_owner.add_task(t1)
        sample_owner.add_task(t2)

        scheduler = Scheduler(owner=sample_owner)
        warnings = scheduler.detect_conflicts()

        # Current design keys on time string — both pending tasks at "08:00" do conflict
        assert len(warnings) == 1


# ---------------------------------------------------------------------------
# Next available slot
# ---------------------------------------------------------------------------

class TestNextAvailableSlot:

    def test_returns_first_free_slot(self, sample_pet):
        """When 08:00 is taken, next_available_slot() should return 12:00."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["08:00", "12:00", "18:00"],
            pets=[sample_pet],
        )
        owner.add_task(make_task("Walk", "08:00", "high", "high", sample_pet))

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot() == "12:00"

    def test_after_skips_earlier_slots(self, sample_pet):
        """next_available_slot(after='08:00') should skip 08:00 and return 12:00."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["08:00", "12:00", "18:00"],
            pets=[sample_pet],
        )
        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot(after="08:00") == "12:00"

    def test_after_skips_equal_slot(self, sample_pet):
        """after is strictly greater-than — the slot equal to after is excluded."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["08:00", "12:00"],
            pets=[sample_pet],
        )
        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot(after="12:00") is None

    def test_returns_none_when_all_slots_occupied(self, sample_pet):
        """None is returned when every availability slot is already in todays_schedule."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["08:00", "12:00"],
            pets=[sample_pet],
        )
        owner.add_task(make_task("Walk", "08:00", "high", "high", sample_pet))
        owner.add_task(make_task("Feed", "12:00", "low",  "low",  sample_pet))

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot() is None

    def test_returns_none_when_availability_empty(self, sample_pet):
        """With no availability defined, there are no slots to suggest."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=[],
            pets=[sample_pet],
        )
        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot() is None

    def test_slots_evaluated_in_sorted_order(self, sample_pet):
        """Slots are compared lexicographically so the earliest free slot is returned
        regardless of the order they were entered in owner.availability."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["18:00", "08:00", "12:00"],  # unsorted on purpose
            pets=[sample_pet],
        )
        owner.add_task(make_task("Walk", "08:00", "high", "high", sample_pet))

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot() == "12:00"

    def test_all_slots_free_returns_first(self, sample_pet):
        """When no tasks are scheduled, the first sorted availability slot is returned."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["12:00", "08:00", "18:00"],
            pets=[sample_pet],
        )
        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        assert scheduler.next_available_slot() == "08:00"

    def test_suggestion_differs_per_conflicted_task(self, sample_pet):
        """Passing different `after` values for two conflicted tasks can yield
        different suggestions, giving each task its own best slot."""
        owner = Owner(
            name="Jordan", number_of_pets=1, age=30,
            availability=["08:00", "12:00", "18:00"],
            pets=[sample_pet],
        )
        owner.add_task(make_task("Walk", "08:00", "high", "high", sample_pet))

        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        # task conflicted at 08:00 -> suggest 12:00
        assert scheduler.next_available_slot(after="08:00") == "12:00"
        # task conflicted at 12:00 -> suggest 18:00
        assert scheduler.next_available_slot(after="12:00") == "18:00"
