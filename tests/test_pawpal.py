import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_updates_task_status():
    task = Task(title="Evening Walk", category="walk", duration_minutes=20, priority="high")
    initial_status = getattr(task, "status", None)

    next_instance = task.mark_complete()

    assert getattr(task, "status", None) != initial_status
    assert str(getattr(task, "status", "")).lower() in {"complete", "completed", "done"}
    assert next_instance is None


def test_mark_complete_creates_next_instance_for_daily_task():
    task = Task(
        task_id="t1",
        title="Daily meds",
        category="meds",
        duration_minutes=10,
        priority="high",
        recurrence="daily",
    )

    next_instance = task.mark_complete()

    assert next_instance is not None
    assert next_instance.task_id == "t1-next-1"
    assert next_instance.parent_task_id == "t1"
    assert next_instance.status == "pending"


def test_scheduler_complete_task_appends_next_weekly_occurrence():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    recurring = Task(
        task_id="w1",
        title="Weekly grooming",
        category="grooming",
        duration_minutes=30,
        priority="medium",
        recurrence="weekly",
        status="pending",
    )
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[recurring])

    next_instance = scheduler.complete_task("w1")

    assert next_instance is not None
    assert recurring.status == "completed"
    assert next_instance.task_id == "w1-next-1"
    assert next_instance.recurrence == "weekly"
    assert any(task.task_id == "w1-next-1" for task in scheduler.tasks)


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Breakfast", category="feeding", duration_minutes=10, priority="medium")
    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


def test_sort_tasks_by_time_orders_blocks_then_start_time():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t3", title="Evening meds", category="meds", duration_minutes=10, priority="high", preferred_time_block="evening"),
        Task(task_id="t2", title="Morning walk", category="walk", duration_minutes=20, priority="high", preferred_time_block="morning", scheduled_start_minute=9 * 60),
        Task(task_id="t1", title="Breakfast", category="feeding", duration_minutes=10, priority="medium", preferred_time_block="morning", scheduled_start_minute=8 * 60),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    ordered = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in ordered] == ["t1", "t2", "t3"]


def test_sort_tasks_by_time_accepts_hhmm_start_strings():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(
            task_id="t2",
            title="Morning walk",
            category="walk",
            duration_minutes=20,
            priority="high",
            preferred_time_block="morning",
            scheduled_start_hhmm="09:00",
        ),
        Task(
            task_id="t1",
            title="Breakfast",
            category="feeding",
            duration_minutes=10,
            priority="medium",
            preferred_time_block="morning",
            scheduled_start_hhmm="08:00",
        ),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    ordered = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in ordered] == ["t1", "t2"]


def test_filter_tasks_by_pet_and_status_returns_expected_tasks():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t1", title="Walk", category="walk", duration_minutes=20, priority="high", pet_id="p1", pet_name="Mochi", status="pending"),
        Task(task_id="t2", title="Feed", category="feeding", duration_minutes=10, priority="medium", pet_id="p1", pet_name="Mochi", status="completed"),
        Task(task_id="t3", title="Play", category="enrichment", duration_minutes=15, priority="low", pet_id="p2", pet_name="Luna", status="pending"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    filtered = scheduler.filter_tasks(pet_id="p1", status="pending")

    assert len(filtered) == 1
    assert filtered[0].task_id == "t1"


def test_expand_recurring_tasks_adds_daily_occurrences_within_window():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(
            task_id="t1",
            title="Medication",
            category="meds",
            duration_minutes=5,
            priority="high",
            recurrence="daily",
            occurrences=3,
        ),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    expanded = scheduler.expand_recurring_tasks(days=3)

    assert len(expanded) == 3
    assert expanded[0].task_id == "t1"
    assert expanded[1].parent_task_id == "t1"
    assert expanded[2].parent_task_id == "t1"


def test_detect_conflicts_finds_overlapping_time_windows():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[])
    plan = [
        {"task_id": "t1", "start_minute": 8 * 60, "end_minute": 8 * 60 + 30},
        {"task_id": "t2", "start_minute": 8 * 60 + 20, "end_minute": 9 * 60},
        {"task_id": "t3", "start_minute": 9 * 60, "end_minute": 9 * 60 + 15},
    ]

    conflicts = scheduler.detect_conflicts(plan)

    assert conflicts == [("t1", "t2")]


def test_build_time_order_uses_hhmm_start_time_for_plan_window():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(
            task_id="t1",
            title="Medication",
            category="meds",
            duration_minutes=15,
            priority="high",
            preferred_time_block="morning",
            scheduled_start_hhmm="08:30",
        )
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    plan = scheduler.build_time_order(tasks)

    assert plan[0]["start_minute"] == (8 * 60) + 30
    assert plan[0]["end_minute"] == (8 * 60) + 45


def test_filter_tasks_by_completion_or_pet_name_uses_or_matching():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t1", title="Walk", category="walk", duration_minutes=20, priority="high", pet_name="Mochi", status="pending"),
        Task(task_id="t2", title="Feed", category="feeding", duration_minutes=10, priority="medium", pet_name="Mochi", status="completed"),
        Task(task_id="t3", title="Play", category="enrichment", duration_minutes=15, priority="low", pet_name="Luna", status="pending"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    filtered = scheduler.filter_tasks_by_completion_or_pet_name(
        completion_status="completed",
        pet_name="Luna",
    )

    assert [task.task_id for task in filtered] == ["t2", "t3"]

def test_tasks_returned_in_chronological_order_by_preferred_time_block():
    """Verify tasks are ordered by time block priority: morning < afternoon < evening"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t3", title="Evening meds", category="meds", duration_minutes=10, priority="high", preferred_time_block="evening"),
        Task(task_id="t1", title="Morning walk", category="walk", duration_minutes=20, priority="high", preferred_time_block="morning"),
        Task(task_id="t2", title="Afternoon play", category="enrichment", duration_minutes=15, priority="medium", preferred_time_block="afternoon"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    ordered = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in ordered] == ["t1", "t2", "t3"]


def test_tasks_chronological_order_within_same_time_block():
    """Verify tasks within same time block are ordered by scheduled_start_minute"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t2", title="Mid-morning walk", category="walk", duration_minutes=20, priority="high", preferred_time_block="morning", scheduled_start_minute=9 * 60),
        Task(task_id="t1", title="Early morning feed", category="feeding", duration_minutes=10, priority="medium", preferred_time_block="morning", scheduled_start_minute=8 * 60),
        Task(task_id="t3", title="Late morning groom", category="grooming", duration_minutes=30, priority="low", preferred_time_block="morning", scheduled_start_minute=10 * 60),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    ordered = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in ordered] == ["t1", "t2", "t3"]


def test_tasks_chronological_order_mixed_hhmm_and_minute_formats():
    """Verify chronological ordering works with mixed scheduled_start_hhmm and scheduled_start_minute"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    tasks = [
        Task(task_id="t3", title="Noon play", category="enrichment", duration_minutes=15, priority="medium", preferred_time_block="afternoon", scheduled_start_minute=12 * 60),
        Task(task_id="t1", title="Morning med", category="meds", duration_minutes=5, priority="high", preferred_time_block="morning", scheduled_start_hhmm="08:00"),
        Task(task_id="t2", title="Late morning walk", category="walk", duration_minutes=20, priority="high", preferred_time_block="morning", scheduled_start_hhmm="10:30"),
    ]
    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    ordered = scheduler.sort_tasks_by_time()

    assert [task.task_id for task in ordered] == ["t1", "t2", "t3"]


def test_daily_task_mark_complete_creates_next_day_occurrence_with_pending_status():
    """Confirm marking a daily task complete generates next occurrence with pending status"""
    task = Task(
        task_id="daily_1",
        title="Daily vitamins",
        category="meds",
        duration_minutes=5,
        priority="high",
        recurrence="daily",
        status="pending"
    )

    next_task = task.mark_complete()

    assert task.status in {"complete", "completed", "done"}
    assert next_task is not None
    assert next_task.task_id == "daily_1-next-1"
    assert next_task.status == "pending"
    assert next_task.recurrence == "daily"


def test_daily_task_chain_creates_sequential_next_occurrences():
    """Verify completing daily task chain creates subsequent occurrences with correct IDs"""
    task = Task(
        task_id="daily_med",
        title="Daily medication",
        category="meds",
        duration_minutes=10,
        priority="high",
        recurrence="daily",
        status="pending"
    )

    first_next = task.mark_complete()
    assert first_next.task_id == "daily_med-next-1"

    second_next = first_next.mark_complete()
    assert second_next is not None
    assert second_next.task_id == "daily_med-next-2"
    assert second_next.parent_task_id == "daily_med"


def test_scheduler_complete_daily_task_updates_task_list():
    """Verify scheduler.complete_task() adds daily task next occurrence to task list"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    daily_task = Task(
        task_id="d1",
        title="Morning feed",
        category="feeding",
        duration_minutes=15,
        priority="high",
        recurrence="daily",
        status="pending"
    )
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[daily_task])
    initial_task_count = len(scheduler.tasks)

    next_task = scheduler.complete_task("d1")

    assert len(scheduler.tasks) == initial_task_count + 1
    assert any(t.task_id == "d1-next-1" for t in scheduler.tasks)
    assert next_task.status == "pending"


def test_detect_conflicts_flags_overlapping_time_windows():
    """Verify scheduler flags duplicate/overlapping times in plan"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[])
    plan = [
        {"task_id": "t1", "start_minute": 8 * 60, "end_minute": 8 * 60 + 30},
        {"task_id": "t2", "start_minute": 8 * 60 + 15, "end_minute": 8 * 60 + 45},  # Overlaps with t1
    ]

    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) > 0
    assert ("t1", "t2") in conflicts or ("t2", "t1") in conflicts


def test_detect_conflicts_no_duplicates_for_adjacent_tasks():
    """Verify adjacent (non-overlapping) tasks are NOT flagged as conflicts"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[])
    plan = [
        {"task_id": "t1", "start_minute": 8 * 60, "end_minute": 8 * 60 + 30},
        {"task_id": "t2", "start_minute": 8 * 60 + 30, "end_minute": 9 * 60},  # Starts exactly when t1 ends
    ]

    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) == 0


def test_detect_conflicts_multiple_overlaps():
    """Verify scheduler detects all pairwise conflicts in complex overlapping scenarios"""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    scheduler = Scheduler(owner=owner, pet=pet, tasks=[])
    plan = [
        {"task_id": "t1", "start_minute": 8 * 60, "end_minute": 9 * 60},
        {"task_id": "t2", "start_minute": 8 * 60 + 30, "end_minute": 9 * 60 + 30},  # Overlaps t1
        {"task_id": "t3", "start_minute": 8 * 60 + 45, "end_minute": 10 * 60},      # Overlaps t1, t2
    ]

    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) >= 2
    conflict_pairs = {tuple(sorted([c[0], c[1]])) for c in conflicts}
    assert ("t1", "t2") in conflict_pairs
    assert ("t1", "t3") in conflict_pairs or ("t2", "t3") in conflict_pairs