import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session-state bootstrap
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Karla")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------

st.header("Add a Pet")

pet_name = st.text_input("Pet name")
pet_type = st.text_input("Pet type")

if st.button("Add Pet"):
    if pet_name.strip():
        new_pet = Pet(pet_name, pet_type)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"{pet_name} was added successfully.")
    else:
        st.warning("Please enter a pet name.")

# ---------------------------------------------------------------------------
# My Pets
# ---------------------------------------------------------------------------

st.header("My Pets")

if st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.name}")
else:
    st.write("No pets added yet.")

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------

st.divider()
st.header("Add a Task")

if not st.session_state.owner.pets:
    st.info("Add a pet first, then add tasks.")
else:
    pet_options = {p.name: p for p in st.session_state.owner.pets}
    selected_pet_name = st.selectbox("Select a pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_name]

    task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
    task_time = st.text_input("Time (HH:MM)", placeholder="e.g. 08:00")

    if st.button("Add Task"):
        if task_title.strip() and task_time.strip():
            new_task = Task(task_title, task_time)
            selected_pet.add_task(new_task)
            st.success(f"Task '{task_title}' added for {selected_pet.name}.")
        else:
            st.warning("Please enter both a task title and a time.")

# ---------------------------------------------------------------------------
# Today's Schedule
# ---------------------------------------------------------------------------

st.divider()
st.header("Today's Schedule")

scheduler = Scheduler(st.session_state.owner)

tasks = scheduler.sort_by_time()
conflicts = scheduler.detect_conflicts()

if tasks:
    for task in tasks:
        status = "Done" if task.completed else "Not Done"
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            st.write(f"**{task.time}**")
        with col2:
            st.write(task.title)
        with col3:
            if task.completed:
                st.success("Done")
            else:
                if st.button("Mark complete", key=id(task)):
                    task.mark_complete()
                    st.rerun()
else:
    st.write("No tasks scheduled yet.")

if conflicts:
    for warning in conflicts:
        st.warning(warning)
