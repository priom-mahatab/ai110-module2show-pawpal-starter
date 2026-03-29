import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task


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