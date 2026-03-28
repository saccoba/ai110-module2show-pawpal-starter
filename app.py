import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
import pandas as pd

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ------------------------------------------------------------------
# Session state bootstrap
# ------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner("My Owner")

owner: Owner = st.session_state.owner

# ------------------------------------------------------------------
# Sidebar — owner + pet setup
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Setup")
    owner_name = st.text_input("Owner name", value=owner.name)
    if owner_name != owner.name:
        owner.name = owner_name

    st.subheader("Add a pet")
    new_pet_name = st.text_input("Pet name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
    new_pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    if st.button("Add pet") and new_pet_name.strip():
        if owner.get_pet(new_pet_name.strip()) is None:
            owner.add_pet(Pet(new_pet_name.strip(), new_pet_species, int(new_pet_age)))
            st.success(f"Added {new_pet_name.strip()}!")
        else:
            st.warning(f"{new_pet_name.strip()} already exists.")

    if owner.pets:
        st.subheader("Pets")
        for p in owner.pets:
            st.caption(p.get_pet_summary())

# ------------------------------------------------------------------
# Guard — need at least one pet
# ------------------------------------------------------------------
if not owner.pets:
    st.info("Add a pet in the sidebar to get started.")
    st.stop()

scheduler = Scheduler(owner)

# ------------------------------------------------------------------
# Summary metrics
# ------------------------------------------------------------------
all_tasks = scheduler.get_all_tasks()
total = len(all_tasks)
done = sum(1 for t in all_tasks if t.completed)
remaining = total - done

m1, m2, m3 = st.columns(3)
m1.metric("Total Tasks", total)
m2.metric("Completed", done)
m3.metric("Remaining", remaining)

st.divider()

# ------------------------------------------------------------------
# Add a task
# ------------------------------------------------------------------
st.subheader("Add a Task")

pet_names = [p.name for p in owner.pets]
col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
with col1:
    selected_pet = st.selectbox("Pet", pet_names, key="task_pet")
with col2:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with col3:
    duration = st.number_input("Duration (min)", min_value=1, max_value=480, value=30, key="task_dur")
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], key="task_freq")
with col5:
    start_time = st.text_input("Start (HH:MM)", value="", key="task_time")

if st.button("Add task"):
    start = start_time.strip() if start_time.strip() else None
    new_task = Task(task_title.strip(), int(duration), frequency, start_time=start)

    # Check for conflicts before adding
    warning = scheduler.get_conflict_warning(selected_pet, new_task)
    if warning:
        st.warning(f"⚠️ {warning}")
    else:
        pet = owner.get_pet(selected_pet)
        pet.add_task(new_task)
        st.success(f"Added '{task_title.strip()}' to {selected_pet}.")

st.divider()

# ------------------------------------------------------------------
# Schedule display
# ------------------------------------------------------------------
st.subheader("Today's Schedule")

sort_order = st.radio(
    "Sort tasks by duration",
    ["Shortest first", "Longest first"],
    horizontal=True,
)
ascending = sort_order == "Shortest first"

if not scheduler.get_all_tasks():
    st.info("No tasks yet. Add some above.")
else:
    fc1, fc2 = st.columns(2)
    with fc1:
        filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
    with fc2:
        filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Completed"], key="filter_status")

    # Build filtered + sorted rows
    display_tasks = []
    for pet in owner.pets:
        if filter_pet != "All" and pet.name != filter_pet:
            continue
        for task in pet.tasks:
            if filter_status == "Completed" and not task.completed:
                continue
            if filter_status == "Incomplete" and task.completed:
                continue
            display_tasks.append((pet.name, task))

    display_tasks.sort(key=lambda x: x[1].time, reverse=not ascending)

    if not display_tasks:
        st.warning("No tasks match the current filters.")
    else:
        rows = []
        for pet_label, task in display_tasks:
            rows.append({
                "Status": "✅ Done" if task.completed else "🔲 Pending",
                "Pet": pet_label,
                "Task": task.description,
                "Duration (min)": task.time,
                "Frequency": task.frequency.capitalize(),
                "Start Time": task.start_time if task.start_time else "—",
            })
        st.table(pd.DataFrame(rows))

st.divider()

# ------------------------------------------------------------------
# Mark a task complete
# ------------------------------------------------------------------
st.subheader("Mark Task Complete")

incomplete = scheduler.get_tasks(completed=False)
if not incomplete:
    st.success("All tasks are complete!")
else:
    task_options = []
    for pet in owner.pets:
        for task in pet.get_incomplete_tasks():
            task_options.append((pet.name, task.description))

    labels = [f"{p} — {d}" for p, d in task_options]
    chosen = st.selectbox("Select task to complete", labels, key="complete_select")
    if st.button("Mark complete"):
        idx = labels.index(chosen)
        pet_n, desc = task_options[idx]
        scheduler.mark_task_complete(pet_n, desc)
        st.success(f"Marked '{desc}' complete. If recurring, next instance queued.")
        st.rerun()

st.divider()

# ------------------------------------------------------------------
# Conflict checker (manual)
# ------------------------------------------------------------------
st.subheader("Check for Conflicts")
st.caption("Preview whether a new task would conflict before adding it.")

cc1, cc2, cc3, cc4 = st.columns([2, 2, 1, 1])
with cc1:
    check_pet = st.selectbox("Pet", pet_names, key="check_pet")
with cc2:
    check_title = st.text_input("Task title", value="Vet visit", key="check_title")
with cc3:
    check_dur = st.number_input("Duration (min)", min_value=1, max_value=480, value=30, key="check_dur")
with cc4:
    check_time = st.text_input("Start (HH:MM)", value="09:00", key="check_time")

if st.button("Check conflict"):
    probe = Task(check_title.strip(), int(check_dur), "once", start_time=check_time.strip() or None)
    result = scheduler.get_conflict_warning(check_pet, probe)
    if result:
        st.error(f"⚠️ {result}")
    else:
        st.success("No conflict detected — safe to schedule.")
