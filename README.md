# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
#Schedule for Jordan's pets
#========================================

#Today's Tasks:
#  [08:00] Morning walk (30 min) � high priority
#  [12:00] Flea/tick treatment for Mochi (10 min) � medium priority
#  [18:00] Evening walk (45 min) � medium priority
#
#Vet Visits:
#  [12:00] Vet checkup for Luna
#
#Conflicts (same time slot):
#  [08:00] Feed Luna � needs rescheduling
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
(.venv) PS C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter> .venv\Scripts\python.exe -m pytest tests/test_pawpal.py -v
==================================================================================================================== test session starts ====================================================================================================================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\gonza\OneDrive\Desktop\CodePath\Unit-3\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 2 items                                                                                                                                                                                                                                            

tests/test_pawpal.py::test_mark_done_changes_status PASSED                                                                                                                                                                                             [ 50%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                                                                                                                                                                                    [100%]

===================================================================================================================== 2 passed in 0.03s =====================================================================================================================
```

## 📐 Smarter Scheduling

PawPal+ implements four scheduling algorithms in `pawpal_system.py` that turn a flat list of pet care tasks into an organized, conflict-aware daily plan.

---

### Sorting Behavior

**Method:** `Scheduler.sort_schedule()` · `Scheduler.sort_by_time()`

Tasks can be sorted two ways depending on what the owner needs:

- **Priority-first** (`sort_schedule`) — the default sort applied automatically after every `generate_schedule()` call. Ranks tasks by priority (`high → medium → low`), then urgency, then time. Uses lookup dicts `PRIORITY_ORDER` and `URGENCY_ORDER` so the sort key is a simple tuple comparison.
- **Chronological** (`sort_by_time`) — re-orders `todays_schedule` by the `HH:MM` time string. Works without parsing because zero-padded time strings sort correctly as plain strings (lexicographic order equals time order).

```python
scheduler.generate_schedule()   # priority-first by default
scheduler.sort_by_time()        # switch to chronological view
```

---

### Filtering Behavior

**Method:** `Scheduler.filter_tasks(status, pet_name)`

Returns a filtered subset of `todays_schedule` without mutating it. Both parameters are optional and combine as AND conditions:

| Parameter  | Type  | Effect                                                       |
|------------|-------|--------------------------------------------------------------|
| `status`   | `str` | Keep only tasks matching `"pending"` or `"done"`             |
| `pet_name` | `str` | Keep only tasks assigned to a pet with this name             |

Passing neither argument returns all tasks unchanged. Tasks with no assigned pet are excluded when `pet_name` is provided.

```python
scheduler.filter_tasks(status="pending", pet_name="Mochi")  # Mochi's incomplete tasks only
scheduler.filter_tasks(pet_name="Luna")                     # all of Luna's tasks
scheduler.filter_tasks(status="done")                       # completed tasks across all pets
```

---

### Conflict Detection Logic

**Method:** `Scheduler.detect_conflicts()`

Scans all pending pet tasks and returns a list of human-readable warning strings — never raises an exception. An empty list means the schedule is clean.

**Algorithm:**

1. Collect all pending tasks across every pet the owner owns.
2. Group them into buckets by time slot using a `defaultdict`.
3. For each bucket with two or more tasks, generate every unique pair with `itertools.combinations` (prevents duplicate `(a, b)` / `(b, a)` comparisons).
4. Classify each pair by pet name:
   - **Same pet** → `"Same-pet conflict"` — the pet is double-booked at that time.
   - **Different pets** → `"Owner conflict"` — the owner can't physically attend both simultaneously.

```python
warnings = scheduler.detect_conflicts()
for warning in warnings:
    print(warning)
# WARNING Same-pet conflict at 18:00: 'Evening walk' and 'Bath time' are both scheduled for Mochi.
# WARNING Owner conflict at 08:00: 'Morning walk' (Mochi) and 'Luna breakfast' (Luna) overlap - you can't attend both.
```

---

### Recurring Task Logic

**Methods:** `Task.next_occurrence()` · `Scheduler.complete_task(task)`

When a recurring task is marked complete, the system automatically generates the next instance and registers it with the owner — no manual re-entry needed.

**`Task.next_occurrence()`** calculates the next `due_date` based on `frequency`:

| Frequency   | Interval             | Notes                                                                                   |
|-------------|----------------------|-----------------------------------------------------------------------------------------|
| `"daily"`   | `timedelta(days=1)`  | Always exactly one day forward                                                          |
| `"weekly"`  | `timedelta(weeks=1)` | Always exactly seven days forward                                                       |
| `"monthly"` | Calendar-aware       | Clamps day to the true last day of the target month — handles leap years and rollovers  |

**`Scheduler.complete_task(task)`** orchestrates the full completion flow:

1. Marks the task as `"done"`.
2. If `frequency` is `daily`, `weekly`, or `monthly`, calls `next_occurrence()`.
3. Registers the new task with the owner automatically.
4. Returns the new task (or `None` for non-recurring tasks).

```python
next_task = scheduler.complete_task(evening_walk)
# evening_walk.status -> "done"
# next_task.due_date  -> tomorrow's date
# next_task.status    -> "pending"
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
