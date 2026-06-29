from datetime import date
import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler, save_to_json, load_from_json

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant that builds your pet's daily schedule.")

st.divider()

# --- Owner Setup ---
st.subheader("Owner Info")
col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    owner_age = st.number_input("Age", min_value=1, max_value=120, value=30)
with col3:
    num_pets = st.number_input("Number of pets", min_value=1, max_value=10, value=2)

availability = st.multiselect(
    "Available time slots",
    options=["07:00", "08:00", "09:00", "12:00", "15:00", "18:00", "20:00"],
    default=["08:00", "12:00", "18:00"],
)

st.divider()

# --- Pet Setup ---
st.subheader("Pets")

if "pets" not in st.session_state:
    _saved_pets, _saved_tasks = load_from_json()
    st.session_state.pets = _saved_pets
    st.session_state.tasks = _saved_tasks

with st.form("add_pet_form", clear_on_submit=True):
    st.markdown("**Add a pet**")
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with pcol2:
        pet_species = st.selectbox("Species", ["Dog", "Cat"])
    with pcol3:
        pet_breed = st.text_input("Breed", value="Shiba Inu")

    pcol4, pcol5 = st.columns(2)
    with pcol4:
        pet_dob = st.date_input("Date of birth", value=date(2020, 1, 1))
    with pcol5:
        pet_gotcha = st.date_input("Gotcha day", value=date(2020, 3, 1))

    next_vet = st.date_input("Next vet visit (optional)", value=None)

    if st.form_submit_button("Add pet"):
        if any(p["name"] == pet_name for p in st.session_state.pets):
            st.warning(f"A pet named '{pet_name}' already exists.")
        else:
            st.session_state.pets.append({
                "name": pet_name,
                "species": pet_species,
                "breed": pet_breed,
                "date_of_birth": pet_dob,
                "gotcha_day": pet_gotcha,
                "next_vet_visit": next_vet,
            })
            save_to_json(st.session_state.pets, st.session_state.tasks)
            st.success(f"{pet_name} added!")

if st.session_state.pets:
    st.write("**Your pets:**")
    st.table([{k: str(v) for k, v in p.items()} for p in st.session_state.pets])

    # Build Pet objects from session state and call pawpal_system methods
    live_pets = [
        Pet(
            species=p["species"],
            name=p["name"],
            date_of_birth=p["date_of_birth"],
            breed=p["breed"],
            gotcha_day=p["gotcha_day"],
            next_vet_visit=p.get("next_vet_visit"),
        )
        for p in st.session_state.pets
    ]
    live_owner = Owner(
        name=owner_name,
        number_of_pets=int(num_pets),
        age=int(owner_age),
        availability=availability,
        pets=live_pets,
    )

    with st.expander("Pet Info Summary", expanded=False):
        st.text(live_owner.check_pet_info())

    with st.expander("Daily Care Reminders", expanded=False):
        st.text(live_owner.daily_schedule_check())

    with st.expander("Upcoming Vet Visits", expanded=False):
        st.text(live_owner.vet_visit_schedule())
else:
    st.info("No pets added yet. Use the form above to add your first pet.")

st.divider()

# --- Task Setup ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []  # fallback if page loaded without pets block running

pet_names = [p["name"] for p in st.session_state.pets]

with st.form("add_task_form", clear_on_submit=True):
    st.markdown("**Add a task**")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        task_title = st.text_input("Task title", value="Morning walk")
    with tcol2:
        task_pet = st.selectbox("For which pet?", options=pet_names if pet_names else ["Add a pet first"])

    tcol3, tcol4, tcol5 = st.columns(3)
    with tcol3:
        task_time = st.selectbox("Time", ["07:00", "08:00", "09:00", "12:00", "15:00", "18:00", "20:00"])
    with tcol4:
        task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with tcol5:
        task_urgency = st.selectbox("Urgency", ["low", "medium", "high"], index=1)

    tcol6, tcol7 = st.columns(2)
    with tcol6:
        task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with tcol7:
        task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

    if st.form_submit_button("Add task") and pet_names:
        if any(t["title"] == task_title and t["pet"] == task_pet for t in st.session_state.tasks):
            st.warning(f"'{task_title}' already exists for {task_pet}.")
        else:
            st.session_state.tasks.append({
                "title": task_title,
                "pet": task_pet,
                "time": task_time,
                "priority": task_priority,
                "urgency": task_urgency,
                "duration": int(task_duration),
                "frequency": task_frequency,
                "status": "pending",
            })
            save_to_json(st.session_state.pets, st.session_state.tasks)
            st.success(f"Task '{task_title}' added for {task_pet}!")

if st.session_state.tasks:
    st.write("**Current tasks:**")
    st.table(st.session_state.tasks)

    with st.expander("Feeding Schedule (all pets)", expanded=False):
        if st.session_state.pets:
            live_pets = [
                Pet(
                    species=p["species"],
                    name=p["name"],
                    date_of_birth=p["date_of_birth"],
                    breed=p["breed"],
                    gotcha_day=p["gotcha_day"],
                    next_vet_visit=p.get("next_vet_visit"),
                )
                for p in st.session_state.pets
            ]
            live_owner = Owner(
                name=owner_name,
                number_of_pets=int(num_pets),
                age=int(owner_age),
                availability=availability,
                pets=live_pets,
            )
            st.text(live_owner.check_feeding_schedule())
        else:
            st.info("Add pets first to see the feeding schedule.")
else:
    st.info("No tasks yet. Add a task above to get started.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

sort_by_time = st.toggle("Sort by time instead of priority", value=False)

if st.button("Generate schedule", type="primary"):
    if not st.session_state.pets:
        st.error("Add at least one pet before generating a schedule.")
    elif not st.session_state.tasks:
        st.error("Add at least one task before generating a schedule.")
    else:
        # Build Pet objects
        pet_objects: dict[str, Pet] = {}
        for p in st.session_state.pets:
            pet_objects[p["name"]] = Pet(
                species=p["species"],
                name=p["name"],
                date_of_birth=p["date_of_birth"],
                breed=p["breed"],
                gotcha_day=p["gotcha_day"],
                next_vet_visit=p.get("next_vet_visit"),
            )

        # Build Owner
        owner = Owner(
            name=owner_name,
            number_of_pets=int(num_pets),
            age=int(owner_age),
            availability=availability,
            pets=list(pet_objects.values()),
        )

        # Build and add Tasks
        for t in st.session_state.tasks:
            task = Task(
                title=t["title"],
                frequency=t["frequency"],
                time=t["time"],
                priority=t["priority"],
                status=t["status"],
                duration=t["duration"],
                urgency=t["urgency"],
                pet=pet_objects.get(t["pet"]),
            )
            owner.add_task(task)

        # Run Scheduler
        scheduler = Scheduler(owner=owner)
        scheduler.generate_schedule()

        if sort_by_time:
            scheduler.sort_by_time()

        # --- Conflict warnings from detect_conflicts() ---
        conflict_warnings = scheduler.detect_conflicts()
        if conflict_warnings:
            st.markdown("### Scheduling Conflicts Detected")
            for warning in conflict_warnings:
                st.warning(warning)

        # --- Today's Tasks ---
        if scheduler.todays_schedule:
            st.success(
                f"Schedule generated! "
                f"{'Sorted by time.' if sort_by_time else 'Sorted by priority then urgency.'}"
            )
            st.markdown("### Today's Tasks")
            st.table([
                {
                    "Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Priority": t.priority.capitalize(),
                    "Urgency": t.urgency.capitalize(),
                    "Duration (min)": t.duration,
                    "Frequency": t.frequency.capitalize(),
                }
                for t in scheduler.todays_schedule
            ])

        # --- Vet Visits ---
        if scheduler.vet_visits:
            st.markdown("### Vet Visits")
            st.table([
                {
                    "Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Duration (min)": t.duration,
                }
                for t in scheduler.vet_visits
            ])

        # --- Bucketed conflicts (tasks bumped during generate_schedule) ---
        if scheduler.conflicts:
            st.markdown("### Tasks Bumped Due to Time Slot Collision")
            st.warning(
                f"{len(scheduler.conflicts)} task(s) share a time slot with an already-scheduled task "
                "and were removed from today's schedule. Move them to the suggested slot below."
            )
            st.table([
                {
                    "Conflicting Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Priority": t.priority.capitalize(),
                    "Suggested Slot": scheduler.next_available_slot(after=t.time) or "No free slot",
                }
                for t in scheduler.conflicts
            ])

        # --- Deferred Tasks ---
        if scheduler.deferred_tasks:
            st.markdown("### Deferred Tasks")
            st.warning(
                f"{len(scheduler.deferred_tasks)} task(s) fall outside your selected availability "
                "and were not scheduled today. Consider moving them to the suggested slot below."
            )
            st.table([
                {
                    "Original Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Priority": t.priority.capitalize(),
                    "Suggested Slot": scheduler.next_available_slot() or "No free slot",
                }
                for t in scheduler.deferred_tasks
            ])

        if not scheduler.todays_schedule and not scheduler.vet_visits:
            st.warning("No tasks could be scheduled. Check your availability and task times.")
