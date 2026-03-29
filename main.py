from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pawpal_system import Owner, Pet, Scheduler, Task


def main():
	owner = Owner(owner_id="o1", name="Jordan", available_minutes_per_day=120)

	dog = Pet(pet_id="p1", name="Mochi", species="dog", age_years=3)
	cat = Pet(pet_id="p2", name="Luna", species="cat", age_years=2)

	owner.pets.append(dog)
	owner.pets.append(cat)

	# Intentionally add tasks out of order to verify Scheduler sorting/filtering.
	dog.add_task(
		Task(
			task_id="t2",
			title="Evening feeding",
			category="feeding",
			duration_minutes=15,
			priority="high",
			status="pending",
			preferred_time_block="evening",
			scheduled_start_hhmm="18:15",
		)
	)
	dog.add_task(
		Task(
			task_id="t1",
			title="Morning walk",
			category="walk",
			duration_minutes=30,
			priority="high",
			status="completed",
			preferred_time_block="morning",
			scheduled_start_hhmm="08:30",
		)
	)
	cat.add_task(
		Task(
			task_id="t4",
			title="Night medication",
			category="meds",
			duration_minutes=10,
			priority="high",
			status="pending",
			preferred_time_block="evening",
			scheduled_start_hhmm="19:00",
		)
	)
	cat.add_task(
		Task(
			task_id="t3",
			title="Afternoon play",
			category="enrichment",
			duration_minutes=20,
			priority="medium",
			status="completed",
			preferred_time_block="afternoon",
			scheduled_start_hhmm="14:00",
		)
	)

	all_tasks = [task for pet in owner.pets for task in pet.tasks]
	scheduler = Scheduler(owner=owner, pet=dog, tasks=all_tasks)

	print("Raw tasks (in insertion order)")
	print("-" * 60)
	for idx, task in enumerate(all_tasks, start=1):
		print(f"{idx}. {task.title} | pet={task.pet_name} | status={task.status} | start={task.scheduled_start_hhmm}")

	sorted_tasks = scheduler.sort_tasks_by_time()
	print("\nSorted tasks (by block + HH:MM)")
	print("-" * 60)
	for idx, task in enumerate(sorted_tasks, start=1):
		block = task.preferred_time_block or "anytime"
		print(
			f"{idx}. [{block}] {task.scheduled_start_hhmm} {task.title} "
			f"for {task.pet_name} (status={task.status})"
		)

	completed_or_luna = scheduler.filter_tasks_by_completion_or_pet_name(
		completion_status="completed",
		pet_name="Luna",
	)
	print("\nFiltered tasks (completed OR pet name == Luna)")
	print("-" * 60)
	for idx, task in enumerate(completed_or_luna, start=1):
		print(f"{idx}. {task.title} | pet={task.pet_name} | status={task.status}")

	pending_for_mochi = scheduler.filter_tasks(pet_name="Mochi", status="pending")
	print("\nFiltered tasks (Mochi AND pending)")
	print("-" * 60)
	for idx, task in enumerate(pending_for_mochi, start=1):
		print(f"{idx}. {task.title} | pet={task.pet_name} | status={task.status}")


if __name__ == "__main__":
	main()



