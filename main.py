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

# --- Tasks ---
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

# --- Add tasks to owner ---
for task in [morning_walk, luna_feeding, flea_treatment, evening_walk, vet_checkup]:
    jordan.add_task(task)

# --- Run scheduler ---
scheduler = Scheduler(owner=jordan)
scheduler.generate_schedule()

print(scheduler.summary())
