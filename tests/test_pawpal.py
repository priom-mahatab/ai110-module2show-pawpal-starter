import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_updates_task_status():
    task = Task(title="Evening Walk", category="walk", duration_minutes=20, priority="high")
    initial_status = getattr(task, "status", None)

    task.mark_complete()

    assert getattr(task, "status", None) != initial_status
    assert str(getattr(task, "status", "")).lower() in {"complete", "completed", "done"}


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