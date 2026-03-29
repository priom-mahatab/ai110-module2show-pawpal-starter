import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

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

    st.write("Manage existing pet")
    pet_manage_options = {
        f"{pet.name} ({pet.species}) [{pet.pet_id}]": pet.pet_id
        for pet in st.session_state.owner.pets
    }
    selected_manage_pet_label = st.selectbox(
        "Choose pet to edit",
        list(pet_manage_options.keys()),
        key="manage_pet_select",
    )
    selected_manage_pet_id = pet_manage_options[selected_manage_pet_label]
    selected_manage_pet = st.session_state.owner.get_pet(selected_manage_pet_id)

    if selected_manage_pet:
        edit_col1, edit_col2 = st.columns(2)
        with edit_col1:
            edit_pet_name = st.text_input("Edit pet name", value=selected_manage_pet.name)
            edit_species = st.selectbox(
                "Edit species",
                ["dog", "cat", "other"],
                index=["dog", "cat", "other"].index(selected_manage_pet.species)
                if selected_manage_pet.species in {"dog", "cat", "other"}
                else 2,
            )
            edit_age = st.number_input(
                "Edit age (years)",
                min_value=0,
                max_value=40,
                value=int(selected_manage_pet.age_years),
                step=1,
            )
        with edit_col2:
            edit_special_needs = st.text_area(
                "Edit special needs (comma-separated)",
                value=", ".join(selected_manage_pet.special_needs),
            )
            edit_medical_notes = st.text_area(
                "Edit medical notes",
                value=selected_manage_pet.medical_notes,
            )

        pet_action_col1, pet_action_col2 = st.columns(2)
        with pet_action_col1:
            if st.button("Save pet changes", key="save_pet_changes"):
                parsed_needs = [item.strip() for item in edit_special_needs.split(",") if item.strip()]
                updated = st.session_state.owner.update_pet(
                    selected_manage_pet_id,
                    name=edit_pet_name,
                    species=edit_species,
                    age_years=int(edit_age),
                    special_needs=parsed_needs,
                    medical_notes=edit_medical_notes,
                )
                if updated:
                    st.success("Pet profile updated.")
                else:
                    st.error("Unable to update pet profile.")

        with pet_action_col2:
            if st.button("Remove pet", key="remove_pet_btn"):
                removed = st.session_state.owner.remove_pet(selected_manage_pet_id)
                if removed:
                    st.success("Pet removed.")
                    st.rerun()
                else:
                    st.error("Unable to remove pet.")
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


def _create_scheduler(owner: Owner) -> Scheduler:
    combined_tasks = [task for pet in owner.pets for task in pet.tasks]
    scheduler_pet = owner.pets[0] if owner.pets else Pet(pet_id="none", name="", species="")
    return Scheduler(owner=owner, pet=scheduler_pet, tasks=combined_tasks)


def _format_minute(minute_of_day: int | None) -> str:
    if minute_of_day is None:
        return "--:--"
    hour = minute_of_day // 60
    minute = minute_of_day % 60
    return f"{hour:02d}:{minute:02d}"


def _extract_unscheduled_reasons(explanation_notes: list[str]) -> dict[str, str]:
    reasons: dict[str, str] = {}
    for note in explanation_notes:
        if not note.startswith("Skipped '"):
            continue
        title_end = note.find("'", len("Skipped '"))
        if title_end == -1:
            continue
        title = note[len("Skipped '"):title_end]
        reason_start = note.find("because ")
        if reason_start != -1:
            reason = note[reason_start:].replace("because ", "", 1).rstrip(".")
        else:
            reason = "Could not fit into the schedule"
        reasons[title] = reason
    return reasons

if all_tasks:
    st.write("Current tasks in session memory:")
    st.table(all_tasks)

    st.write("Manage existing task")
    task_pet_options = {
        f"{pet.name} ({pet.species}) [{pet.pet_id}]": pet.pet_id
        for pet in st.session_state.owner.pets
        if pet.tasks
    }

    if task_pet_options:
        selected_task_pet_label = st.selectbox(
            "Choose pet for task editing",
            list(task_pet_options.keys()),
            key="task_manage_pet_select",
        )
        selected_task_pet_id = task_pet_options[selected_task_pet_label]
        selected_task_pet = st.session_state.owner.get_pet(selected_task_pet_id)

        if selected_task_pet and selected_task_pet.tasks:
            task_options = {
                f"{task.title} [{task.task_id}]": task.task_id
                for task in selected_task_pet.tasks
            }
            selected_task_label = st.selectbox(
                "Choose task to edit",
                list(task_options.keys()),
                key="task_edit_select",
            )
            selected_task_id = task_options[selected_task_label]
            selected_task = selected_task_pet.get_task(selected_task_id)

            if selected_task:
                task_edit_col1, task_edit_col2, task_edit_col3 = st.columns(3)
                with task_edit_col1:
                    edit_task_title = st.text_input("Edit task title", value=selected_task.title)
                    edit_task_category = st.text_input(
                        "Edit category", value=selected_task.category or "general"
                    )
                    edit_duration = st.number_input(
                        "Edit duration (minutes)",
                        min_value=1,
                        max_value=240,
                        value=int(selected_task.duration_minutes),
                    )
                with task_edit_col2:
                    edit_priority = st.selectbox(
                        "Edit priority",
                        ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(selected_task.priority)
                        if selected_task.priority in {"low", "medium", "high"}
                        else 1,
                    )
                    edit_status = st.selectbox(
                        "Edit status",
                        ["pending", "completed", "complete", "done"],
                        index=["pending", "completed", "complete", "done"].index(
                            selected_task.status
                        )
                        if selected_task.status in {"pending", "completed", "complete", "done"}
                        else 0,
                    )
                    edit_time_block = st.selectbox(
                        "Edit time block",
                        ["", "morning", "afternoon", "evening"],
                        index=["", "morning", "afternoon", "evening"].index(
                            selected_task.preferred_time_block
                        )
                        if selected_task.preferred_time_block in {"", "morning", "afternoon", "evening"}
                        else 0,
                    )
                with task_edit_col3:
                    edit_recurrence = st.selectbox(
                        "Edit recurrence",
                        ["none", "daily", "weekly"],
                        index=["none", "daily", "weekly"].index(selected_task.recurrence)
                        if selected_task.recurrence in {"none", "daily", "weekly"}
                        else 0,
                    )
                    edit_occurrences = st.number_input(
                        "Edit occurrences",
                        min_value=1,
                        max_value=30,
                        value=int(selected_task.occurrences),
                        step=1,
                    )
                    edit_hhmm = st.text_input(
                        "Edit start (HH:MM, optional)", value=selected_task.scheduled_start_hhmm
                    )

                edit_task_notes = st.text_area("Edit task notes", value=selected_task.notes)

                task_action_col1, task_action_col2 = st.columns(2)
                with task_action_col1:
                    if st.button("Save task changes", key="save_task_changes"):
                        updated_task = selected_task_pet.update_task(
                            selected_task_id,
                            title=edit_task_title.strip(),
                            category=edit_task_category.strip(),
                            duration_minutes=int(edit_duration),
                            priority=edit_priority,
                            status=edit_status,
                            preferred_time_block=edit_time_block,
                            notes=edit_task_notes.strip(),
                            recurrence=edit_recurrence,
                            occurrences=int(edit_occurrences),
                            scheduled_start_hhmm=edit_hhmm.strip(),
                        )
                        if updated_task:
                            st.success("Task updated.")
                        else:
                            st.error(
                                "Task update failed. Check title, duration, priority, recurrence, and HH:MM format."
                            )

                with task_action_col2:
                    if st.button("Remove task", key="remove_task_btn"):
                        removed_task = selected_task_pet.remove_task(selected_task_id)
                        if removed_task:
                            st.success("Task removed.")
                            st.rerun()
                        else:
                            st.error("Unable to remove task.")
    else:
        st.info("No tasks available to edit yet.")

    scheduler = _create_scheduler(st.session_state.owner)
    sorted_tasks = scheduler.sort_tasks_by_time()

    st.write("Sorted tasks (using Scheduler.sort_tasks_by_time)")
    st.table(
        [
            {
                "task_id": task.task_id,
                "title": task.title,
                "pet": task.pet_name,
                "priority": task.priority,
                "status": task.status,
                "time_block": task.preferred_time_block or "anytime",
                "start": task.scheduled_start_hhmm or _format_minute(task.scheduled_start_minute),
            }
            for task in sorted_tasks
        ]
    )

    st.write("Filter tasks (using Scheduler.filter_tasks)")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All"] + [pet.name for pet in st.session_state.owner.pets],
            key="filter_pet",
        )
    with filter_col2:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "pending", "completed"],
            key="filter_status",
        )

    filtered_tasks = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All" else pet_filter,
        status=None if status_filter == "All" else status_filter,
        tasks=sorted_tasks,
    )

    if filtered_tasks:
        st.success(f"Showing {len(filtered_tasks)} task(s) after filter.")
        st.table([task.to_display_row() for task in filtered_tasks])
    else:
        st.warning("No tasks match the selected filter.")
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

    if not all_tasks:
        st.info("No tasks to schedule yet.")
    else:
        scheduler = _create_scheduler(st.session_state.owner)
        plan = scheduler.generate_schedule()
        explanation_notes = scheduler.explain_plan()
        unscheduled = scheduler.get_unscheduled_tasks()

        if plan:
            st.success(f"Scheduled {len(plan)} task(s) for today.")
            st.table(
                [
                    {
                        "time": f"{_format_minute(item['start_minute'])} - {_format_minute(item['end_minute'])}",
                        "task": item["title"],
                        "pet": item.get("pet_name") or item.get("pet_id") or "Unknown",
                        "priority": item["priority"],
                        "time_block": item["time_block"],
                    }
                    for item in plan
                ]
            )
        else:
            st.warning("No tasks could be scheduled with the current constraints.")

        conflict_notes = [
            note for note in explanation_notes if "conflict" in note.lower()
        ]
        if conflict_notes:
            st.warning(
                f"Scheduling conflicts detected in {len(conflict_notes)} task decision(s). Review details below."
            )
            for note in conflict_notes:
                st.write(f"- {note}")
            st.info(
                "Tip: reduce task duration, adjust preferred time blocks, or increase available minutes to avoid conflicts."
            )

        if unscheduled:
            reason_map = _extract_unscheduled_reasons(explanation_notes)
            st.warning(f"{len(unscheduled)} task(s) were not scheduled.")
            st.table(
                [
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "pet": task.pet_name,
                        "duration_minutes": task.duration_minutes,
                        "priority": task.priority,
                        "reason": reason_map.get(task.title, "Conflict or time limit"),
                    }
                    for task in unscheduled
                ]
            )
