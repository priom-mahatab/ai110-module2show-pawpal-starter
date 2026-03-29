from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pawpal_system import Owner, Pet, Task


def main():
	owner = Owner(owner_id="o1", name="Jordan", available_minutes_per_day=120)

	dog = Pet(pet_id="p1", name="Mochi", species="dog", age_years=3)
	cat = Pet(pet_id="p2", name="Luna", species="cat", age_years=2)

	owner.pets.append(dog)
	owner.pets.append(cat)

	dog.tasks.extend(
		[
			Task(
				task_id="t1",
				title="Morning walk",
				category="walk",
				duration_minutes=30,
				priority="high",
				preferred_time_block="morning",
			),
			Task(
				task_id="t2",
				title="Evening feeding",
				category="feeding",
				duration_minutes=15,
				priority="high",
				preferred_time_block="evening",
			),
		]
	)

	cat.tasks.extend(
		[
			Task(
				task_id="t3",
				title="Afternoon play",
				category="enrichment",
				duration_minutes=20,
				priority="medium",
				preferred_time_block="afternoon",
			),
			Task(
				task_id="t4",
				title="Night medication",
				category="meds",
				duration_minutes=10,
				priority="high",
				preferred_time_block="evening",
			),
		]
	)

	all_tasks: list[tuple[str, Task]] = []
	for pet in owner.pets:
		for task in pet.tasks:
			all_tasks.append((pet.name, task))

	time_order = {"morning": 0, "afternoon": 1, "evening": 2, "": 3}
	all_tasks.sort(
		key=lambda item: (
			time_order.get(item[1].preferred_time_block, 3),
			-priority_to_score(item[1].priority),
		)
	)

	print("Today's schedule")
	print(f"Owner: {owner.name}")
	print("-" * 40)
	for idx, (pet_name, task) in enumerate(all_tasks, start=1):
		block = task.preferred_time_block or "anytime"
		print(
			f"{idx}. [{block}] {task.title} for {pet_name} "
			f"({task.duration_minutes} min, priority={task.priority})"
		)

	total_minutes = sum(task.duration_minutes for _, task in all_tasks)
	print("-" * 40)
	print(f"Total planned minutes: {total_minutes}")
	print(f"Owner available minutes: {owner.available_minutes_per_day}")


def priority_to_score(priority: str) -> int:
	priority_scores = {"low": 1, "medium": 2, "high": 3}
	return priority_scores.get(priority, 0)


if __name__ == "__main__":
	main()



