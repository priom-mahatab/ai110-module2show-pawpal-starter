import streamlit as st
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=120)

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
with col2:
    available_minutes = st.number_input(
        "Available minutes today",
        min_value=0,
        max_value=600,
        value=int(st.session_state.owner.available_minutes_per_day),
        step=5,
    )

if st.button("Save owner"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_minutes_per_day = int(available_minutes)
    st.success("Owner saved in session memory.")

st.write(
    f"Current owner: {st.session_state.owner.name} | "
    f"Available time: {st.session_state.owner.available_minutes_per_day} min"
)

st.divider()

st.subheader("Pets")
pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    duplicate_pet = any(
        pet.name.strip().lower() == pet_name.strip().lower()
        for pet in st.session_state.owner.pets
    )
    if not pet_name.strip():
        st.error("Pet name cannot be empty.")
    elif duplicate_pet:
        st.warning("A pet with that name already exists.")
    else:
        new_pet = Pet(
            pet_id=f"pet-{st.session_state.next_pet_id}",
            name=pet_name.strip(),
            species=species,
        )
        st.session_state.next_pet_id += 1
        st.session_state.owner.pets.append(new_pet)
        st.success(f"Added pet: {new_pet.name}")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "task_count": len(pet.tasks),
            }
            for pet in st.session_state.owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
st.caption("Adding a task creates a Task object and stores it in the selected Pet.")

if st.session_state.owner.pets:
    pet_options = {f"{pet.name} ({pet.species})": pet for pet in st.session_state.owner.pets}
    selected_pet_label = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_label]

    task_col1, task_col2, task_col3 = st.columns(3)
    with task_col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with task_col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with task_col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    time_block = st.selectbox("Preferred time block", ["", "morning", "afternoon", "evening"])

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Task title cannot be empty.")
        else:
            new_task = Task(
                task_id=f"task-{st.session_state.next_task_id}",
                title=task_title.strip(),
                category="general",
                duration_minutes=int(duration),
                priority=priority,
                preferred_time_block=time_block,
            )
            st.session_state.next_task_id += 1
            selected_pet.add_task(new_task)
            st.success(f"Added task to {selected_pet.name}: {new_task.title}")
else:
    st.info("Add at least one pet before adding tasks.")

all_tasks = [
    {
        "pet": pet.name,
        "task_id": task.task_id,
        "title": task.title,
        "duration_minutes": task.duration_minutes,
        "priority": task.priority,
        "status": task.status,
        "time_block": task.preferred_time_block or "anytime",
    }
    for pet in st.session_state.owner.pets
    for task in pet.tasks
]

if all_tasks:
    st.write("Current tasks in session memory:")
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This preview confirms your object graph is stored in session memory.")

if st.button("Generate schedule"):
    total_tasks = sum(len(pet.tasks) for pet in st.session_state.owner.pets)
    st.write("Today's schedule")
    st.write(f"Owner: {st.session_state.owner.name}")
    st.write(f"Pets: {len(st.session_state.owner.pets)}")
    st.write(f"Tasks captured: {total_tasks}")
    if all_tasks:
        st.table(all_tasks)
    else:
        st.info("No tasks to schedule yet.")
