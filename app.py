import streamlit as st
from pawpal_system import (
    Owner, Pet, Task, Scheduler, Priority, CATEGORY_EMOJI, is_valid_time,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

DATA_PATH = "data.json"

# ---------------------------------------------------------------------------
# Session-state bootstrap (Challenge 2: load persisted data on first run)
# ---------------------------------------------------------------------------

if "scheduler" not in st.session_state:
    # load_from_json returns a Scheduler; falls back to an empty owner if no file.
    loaded = Scheduler.load_from_json(DATA_PATH)
    if loaded.owner.name == "New Owner":
        loaded.owner.name = "Karla"
    st.session_state.scheduler = loaded
    st.session_state.owner = loaded.owner

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler


def persist() -> None:
    """Save the current state to data.json."""
    scheduler.save_to_json(DATA_PATH)


# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------

st.header("Add a Pet")

pet_name = st.text_input("Pet name")
pet_type = st.text_input("Pet type")

if st.button("Add Pet"):
    if pet_name.strip():
        owner.add_pet(Pet(pet_name, pet_type))
        persist()
        st.success(f"{pet_name} was added successfully.")
    else:
        st.warning("Please enter a pet name.")

# ---------------------------------------------------------------------------
# My Pets
# ---------------------------------------------------------------------------

st.header("My Pets")

if owner.pets:
    for pet in owner.pets:
        st.write(f"- {pet.name}")
else:
    st.write("No pets added yet.")

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------

st.divider()
st.header("Add a Task")

if not owner.pets:
    st.info("Add a pet first, then add tasks.")
else:
    pet_options = {p.name: p for p in owner.pets}
    selected_pet_name = st.selectbox("Select a pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_name]

    task_title = st.text_input("Task title", placeholder="e.g. Morning walk")

    # Challenge 1: suggest the next free slot so the owner avoids conflicts.
    suggested = scheduler.find_next_available_slot()
    task_time = st.text_input(
        "Time (HH:MM)",
        value=suggested or "",
        help=f"Next free slot suggested: {suggested}",
    )

    category = st.selectbox("Category", list(CATEGORY_EMOJI.keys()))
    priority_name = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)

    if st.button("Add Task"):
        if not (task_title.strip() and task_time.strip()):
            st.warning("Please enter both a task title and a time.")
        elif not is_valid_time(task_time.strip()):
            st.warning("Please enter a valid 24-hour time, e.g. 08:30.")
        else:
            selected_pet.add_task(
                Task(
                    task_title,
                    task_time.strip(),
                    priority=Priority.from_str(priority_name),
                    category=category,
                )
            )
            persist()
            st.success(f"Task '{task_title}' added for {selected_pet.name}.")

# ---------------------------------------------------------------------------
# Today's Schedule (Challenge 3 + 4: priority order, emojis, status colors)
# ---------------------------------------------------------------------------

st.divider()
st.header("Today's Schedule")

sort_mode = st.radio("Sort by", ["Priority", "Time"], horizontal=True)
tasks = scheduler.sort_by_priority() if sort_mode == "Priority" else scheduler.sort_by_time()
conflicts = scheduler.detect_conflicts()

# Color per priority for the status badge.
priority_badge = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}

if tasks:
    for task in tasks:
        col1, col2, col3, col4 = st.columns([1.5, 3, 1.5, 2])
        with col1:
            st.write(f"**{task.time}**")
        with col2:
            st.write(f"{task.emoji} {task.title}")
        with col3:
            st.write(f"{priority_badge[task.priority]} {task.priority.name.title()}")
        with col4:
            if task.completed:
                st.success("Done")
            else:
                if st.button("Mark complete", key=id(task)):
                    task.mark_complete()
                    persist()
                    st.rerun()
else:
    st.write("No tasks scheduled yet.")

if conflicts:
    for warning in conflicts:
        st.warning(warning)
