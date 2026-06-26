# PawPal+ Session Notes

## Class Design (finalized)

### Pet
**Attributes:** species (Dog/Cat only), name, date_of_birth, breed, gotcha_day, next_vet_visit, flea_tick_due, heartworm_due (dogs only — None for cats)
**Methods:** check_feeding_schedule(), water_refill_notification(), vaccination_schedule_check(), daily_schedule_check()

### Task
**Attributes:** frequency, time, priority, status, duration, urgency, owner (ref), pet (ref)
**Methods:** none — pure data object
> Note: add/remove/edit moved to Owner. When owner.add_task(task) is called, also set task.owner = self.

### Owner
**Attributes:** name, number_of_pets, availability (List), age
**Methods:** check_feeding_schedule() *(shows all pets' schedules)*, check_pet_info(), vaccination_schedule_check(), daily_schedule_check(), vet_visit_schedule(), add_task(task), remove_task(task), edit_task(task)

### Scheduler
**Attributes:** todays_schedule (List), deferred_tasks (List), conflicts (List), vet_visits (List)
**Methods:** generate_schedule(), sort_schedule(), edit_schedule()

---

## Relationships
- Owner 1 → 1..* Pet (owns)
- Owner 1 → 0..* Task (manages)
- Scheduler 1 → 1 Owner (schedules for)
- Scheduler 1 → 0..* Task (organizes)
- Pet 1 → 0..* Task (has care tasks)

---

## Key Design Decisions
- `check_feeding_schedule()` lives on **both** Pet and Owner — Owner's version aggregates across all pets
- `add_task / remove_task / edit_task` live on **Owner**, not Task — Task is a pure data object
- `heartworm_due` is only relevant for dogs — set to `None` for cats
- `Task.owner` and `Task.pet` are back-references; keep them in sync when calling `owner.add_task(task)`

---

## Files
- UML draft: [diagrams/uml_draft.mmd](diagrams/uml_draft.mmd)
- App skeleton: [app.py](app.py)

---

## WHERE TO RESUME

**Phase 1, Step 4** — implement class stubs in Python (no logic yet, just `__init__` and method skeletons with `pass`).

Suggested next step: create `pawpal_system.py` with all four classes stubbed out, then connect to `app.py`.
