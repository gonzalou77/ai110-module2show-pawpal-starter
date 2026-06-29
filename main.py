from datetime import date
from pawpal_system import Pet, Task, Owner, Scheduler

# --- Pets ---
mochi = Pet(
    species="Dog",
    name="Mochi",
    date_of_birth=date(2019, 4, 12),
    breed="Shiba Inu",
    gotcha_day=date(2019, 6, 1),
    next_vet_visit=date(2026, 7, 15),
    flea_tick_due=date(2026, 6, 20),
)

luna = Pet(
    species="Cat",
    name="Luna",
    date_of_birth=date(2021, 9, 3),
    breed="Domestic Shorthair",
    gotcha_day=date(2021, 11, 10),
    next_vet_visit=date(2026, 8, 5),
)

# --- Owner ---
jordan = Owner(
    name="Jordan",
    number_of_pets=2,
    age=30,
    availability=["08:00", "12:00", "18:00"],
    pets=[mochi, luna],
)

# --- Tasks added out of order ---
evening_walk = Task(
    title="Evening walk",
    frequency="daily",
    time="18:00",
    priority="medium",
    status="pending",
    duration=45,
    urgency="low",
    pet=mochi,
)

flea_treatment = Task(
    title="Flea/tick treatment for Mochi",
    frequency="monthly",
    time="12:00",
    priority="medium",
    status="pending",
    duration=10,
    urgency="high",
    pet=mochi,
)

luna_feeding = Task(
    title="Feed Luna",
    frequency="daily",
    time="08:00",
    priority="high",
    status="pending",
    duration=5,
    urgency="medium",
    pet=luna,
)

vet_checkup = Task(
    title="Vet checkup for Luna",
    frequency="yearly",
    time="12:00",
    priority="high",
    status="pending",
    duration=60,
    urgency="medium",
    pet=luna,
)

morning_walk = Task(
    title="Morning walk",
    frequency="daily",
    time="08:00",
    priority="high",
    status="pending",
    duration=30,
    urgency="high",
    pet=mochi,
)

# --- Add tasks to owner ---
for task in [evening_walk, flea_treatment, luna_feeding, vet_checkup, morning_walk]:
    jordan.add_task(task)

# --- Capture raw insertion order before scheduler sorts anything ---
raw_order = [t for t in jordan.tasks if t.pet in jordan.pets]

# --- Run scheduler ---
scheduler = Scheduler(owner=jordan)
scheduler.generate_schedule()

print(scheduler.summary())

# --- Before: disorganized order (as added) ---
print("\n--- Today's Tasks BEFORE Sorting ---")
for task in raw_order:
    print(f"  [{task.time}] {task.title} ({task.duration} min | {task.priority} priority | for {task.pet.name if task.pet else 'N/A'})")

# --- Priority-first then time sort (default after generate_schedule) ---
print("\n--- Today's Tasks AFTER sort_schedule() — priority first, then time ---")
scheduler.sort_schedule()
for task in scheduler.todays_schedule:
    print(f"  [{task.time}] {task.title} ({task.duration} min | {task.priority} priority | for {task.pet.name if task.pet else 'N/A'})")

# --- Sort by time only ---
scheduler.sort_by_time()
print("\n--- Today's Tasks AFTER sort_by_time() — chronological only ---")
for task in scheduler.todays_schedule:
    print(f"  [{task.time}] {task.title} ({task.duration} min | {task.priority} priority | for {task.pet.name if task.pet else 'N/A'})")

# --- Before: all tasks unfiltered ---
print("\n--- All Tasks BEFORE Filtering ---")
for task in scheduler.todays_schedule:
    print(f"  [{task.time}] {task.title} | pet: {task.pet.name if task.pet else 'N/A'} | status: {task.status}")

# --- Filter: pending tasks for Mochi only ---
pending_mochi = scheduler.filter_tasks(status="pending", pet_name="Mochi")
print("\n--- Tasks AFTER Filtering (Mochi | pending only) ---")
for task in pending_mochi:
    print(f"  [{task.time}] {task.title} | pet: {task.pet.name} | status: {task.status}")

# --- Complete a recurring task and show the auto-generated next occurrence ---
print("\n--- Completing 'Evening walk' (daily recurring) ---")
next_walk = scheduler.complete_task(evening_walk)
print(f"  '{evening_walk.title}' marked: {evening_walk.status} | was due: {evening_walk.due_date}")
if next_walk:
    print(f"  Next occurrence auto-created: '{next_walk.title}' | due: {next_walk.due_date} | status: {next_walk.status}")

print("\n--- Completing 'Flea/tick treatment' (monthly recurring) ---")
next_flea = scheduler.complete_task(flea_treatment)
print(f"  '{flea_treatment.title}' marked: {flea_treatment.status} | was due: {flea_treatment.due_date}")
if next_flea:
    print(f"  Next occurrence auto-created: '{next_flea.title}' | due: {next_flea.due_date} | status: {next_flea.status}")

# --- Conflict detection demo ---
# Same-pet conflict: Mochi has two tasks at 18:00
bath_time = Task(
    title="Bath time",
    frequency="weekly",
    time="18:00",
    priority="low",
    status="pending",
    duration=20,
    urgency="low",
    pet=mochi,
)

# Different-pet conflict: Luna and Mochi both have tasks at 08:00
luna_breakfast = Task(
    title="Luna breakfast",
    frequency="daily",
    time="08:00",
    priority="high",
    status="pending",
    duration=10,
    urgency="high",
    pet=luna,
)

jordan.add_task(bath_time)
jordan.add_task(luna_breakfast)

print("\n" + "="*50)
print("CONFLICT DETECTION DEMO")
print("="*50)
print("Tasks intentionally scheduled at the same time:")
print(f"  [18:00] Evening walk  (Mochi)  <-- same time")
print(f"  [18:00] Bath time     (Mochi)  <-- same time, same pet")
print(f"  [08:00] Morning walk  (Mochi)  <-- same time")
print(f"  [08:00] Luna breakfast (Luna)  <-- same time, different pet")
print()

conflict_warnings = scheduler.detect_conflicts()
if conflict_warnings:
    for warning in conflict_warnings:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")
