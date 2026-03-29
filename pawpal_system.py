from dataclasses import dataclass, field, replace
from typing import Any


@dataclass
class Owner:
	owner_id: str = ""
	name: str = ""
	available_minutes_per_day: int = 0
	preferences: dict[str, Any] = field(default_factory=dict)
	preferred_task_order: list[str] = field(default_factory=list)
	pets: list["Pet"] = field(default_factory=list)

	def update_available_time(self, minutes: int) -> None:
		"""Update the owner's available care time for the day."""
		self.available_minutes_per_day = max(0, int(minutes))

	def set_preference(self, key: str, value: Any) -> None:
		"""Set a named care preference for the owner."""
		self.preferences[key] = value

	def can_fit(self, duration_minutes: int) -> bool:
		"""Return whether a task duration fits the owner's time budget."""
		return int(duration_minutes) <= self.available_minutes_per_day

	def get_profile_summary(self) -> str:
		"""Return a short human-readable summary of the owner profile."""
		return (
			f"Owner {self.name} has {self.available_minutes_per_day} care minutes/day "
			f"for {len(self.pets)} pet(s)."
		)

	def add_pet(self, pet: "Pet") -> None:
		"""Add a pet to the owner's pet list."""
		if all(existing.pet_id != pet.pet_id for existing in self.pets):
			self.pets.append(pet)


@dataclass
class Pet:
	pet_id: str = ""
	name: str = ""
	species: str = ""
	age_years: int = 0
	special_needs: list[str] = field(default_factory=list)
	medical_notes: str = ""
	tasks: list["Task"] = field(default_factory=list)

	def add_special_need(self, need: str) -> None:
		"""Record a special care need for the pet."""
		clean_need = need.strip()
		if clean_need:
			self.special_needs.append(clean_need)

	def requires_medication(self) -> bool:
		"""Return whether the pet currently needs medication."""
		combined_notes = " ".join(self.special_needs).lower() + f" {self.medical_notes.lower()}"
		return "med" in combined_notes

	def get_care_profile(self) -> str:
		"""Return a short summary of the pet's care profile."""
		needs = ", ".join(self.special_needs) if self.special_needs else "none"
		return f"{self.name} ({self.species}, {self.age_years}y) special needs: {needs}"

	def add_task(self, task: "Task") -> None:
		"""Add a care task to this pet's task list."""
		if not task.pet_id:
			task.pet_id = self.pet_id
		if not task.pet_name:
			task.pet_name = self.name
		self.tasks.append(task)


@dataclass
class Task:
	task_id: str = ""
	title: str = ""
	category: str = ""
	duration_minutes: int = 0
	priority: str = "medium"
	status: str = "pending"
	required: bool = False
	preferred_time_block: str = ""
	notes: str = ""
	pet_id: str = ""
	pet_name: str = ""
	recurrence: str = "none"
	occurrences: int = 1
	parent_task_id: str = ""
	scheduled_start_minute: int | None = None

	def validate(self) -> bool:
		"""Validate task fields and return whether the task is usable."""
		if not self.title.strip() or self.duration_minutes <= 0:
			return False
		if self.priority.lower() not in {"low", "medium", "high"}:
			return False
		if self.status.lower() not in {"pending", "completed", "complete", "done"}:
			return False
		if self.recurrence not in {"none", "daily", "weekly"}:
			return False
		return True

	def priority_score(self) -> int:
		"""Return a numeric score representing task priority."""
		return {"low": 1, "medium": 2, "high": 3}.get(self.priority.lower(), 0)

	def to_display_row(self) -> dict[str, Any]:
		"""Convert the task into a display-friendly dictionary row."""
		return {
			"task_id": self.task_id,
			"title": self.title,
			"pet": self.pet_name,
			"duration_minutes": self.duration_minutes,
			"priority": self.priority,
			"status": self.status,
			"time_block": self.preferred_time_block or "anytime",
			"recurrence": self.recurrence,
		}

	def is_high_priority(self) -> bool:
		"""Return whether this task is marked as high priority."""
		return self.priority.lower() == "high"

	def mark_complete(self) -> None:
		"""Mark the task as completed."""
		self.status = "completed"


class Scheduler:
	def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
		self.owner = owner
		self.pet = pet
		self.tasks = tasks
		self.daily_plan: list[dict[str, Any]] = []
		self.unscheduled_tasks: list[Task] = []
		self.reasoning_log: list[str] = []

	def generate_schedule(self) -> list[dict[str, Any]]:
		"""Build and return a daily schedule from available tasks."""
		self.daily_plan = []
		self.unscheduled_tasks = []
		self.reasoning_log = []

		expanded = self.expand_recurring_tasks(self.tasks, days=1)
		feasible = self.apply_constraints(expanded)
		ranked = self.rank_tasks(feasible)
		self.daily_plan = self.build_time_order(ranked)

		conflicts = self.detect_conflicts(self.daily_plan)
		for first_id, second_id in conflicts:
			self.reasoning_log.append(f"Conflict detected between {first_id} and {second_id}.")

		return self.daily_plan

	def rank_tasks(self, tasks: list[Task] | None = None) -> list[Task]:
		"""Rank tasks according to priority and scheduling rules."""
		tasks_to_rank = tasks if tasks is not None else self.tasks
		time_order = {"morning": 0, "afternoon": 1, "evening": 2, "": 3}
		return sorted(
			tasks_to_rank,
			key=lambda task: (
				time_order.get(task.preferred_time_block, 3),
				-task.priority_score(),
				task.duration_minutes,
				task.title.lower(),
			),
		)

	def apply_constraints(self, tasks: list[Task]) -> list[Task]:
		"""Filter tasks based on owner time and other constraints."""
		valid = [task for task in tasks if task.validate()]
		status_filtered = [
			task for task in valid if task.status.lower() not in {"completed", "complete", "done"}
		]
		return status_filtered

	def build_time_order(self, tasks: list[Task]) -> list[dict[str, Any]]:
		"""Order selected tasks into a time-based daily plan."""
		plan: list[dict[str, Any]] = []
		used_minutes = 0
		block_start = {"morning": 8 * 60, "afternoon": 12 * 60, "evening": 17 * 60, "": 9 * 60}
		block_cursor = dict(block_start)

		for task in tasks:
			if used_minutes + task.duration_minutes > self.owner.available_minutes_per_day:
				self.unscheduled_tasks.append(task)
				self.reasoning_log.append(
					f"Skipped '{task.title}' because it exceeds available owner time."
				)
				continue

			block = task.preferred_time_block if task.preferred_time_block in block_start else ""
			start_minute = task.scheduled_start_minute
			if start_minute is None:
				start_minute = block_cursor[block]
			end_minute = start_minute + task.duration_minutes

			if self._overlaps_existing(start_minute, end_minute, plan):
				self.unscheduled_tasks.append(task)
				self.reasoning_log.append(
					f"Skipped '{task.title}' due to conflict at {self._format_time(start_minute)}."
				)
				continue

			plan_entry = {
				"task_id": task.task_id,
				"title": task.title,
				"pet_id": task.pet_id,
				"pet_name": task.pet_name,
				"time_block": block or "anytime",
				"start_minute": start_minute,
				"end_minute": end_minute,
				"duration_minutes": task.duration_minutes,
				"priority": task.priority,
				"status": task.status,
			}
			plan.append(plan_entry)
			used_minutes += task.duration_minutes
			block_cursor[block] = max(block_cursor[block], end_minute)

		return sorted(plan, key=lambda row: row["start_minute"])

	def explain_plan(self) -> list[str]:
		"""Return explanation notes for scheduling decisions."""
		if not self.reasoning_log and self.daily_plan:
			return ["Plan created successfully with no detected conflicts."]
		return self.reasoning_log

	def get_unscheduled_tasks(self) -> list[Task]:
		"""Return tasks that were not included in the final schedule."""
		return self.unscheduled_tasks

	def sort_tasks_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
		"""Sort tasks by preferred block then explicit start time when available."""
		tasks_to_sort = tasks if tasks is not None else self.tasks
		time_order = {"morning": 0, "afternoon": 1, "evening": 2, "": 3}
		return sorted(
			tasks_to_sort,
			key=lambda task: (
				time_order.get(task.preferred_time_block, 3),
				task.scheduled_start_minute if task.scheduled_start_minute is not None else 24 * 60,
				task.title.lower(),
			),
		)

	def filter_tasks(
		self,
		pet_id: str | None = None,
		pet_name: str | None = None,
		status: str | None = None,
		tasks: list[Task] | None = None,
	) -> list[Task]:
		"""Filter tasks by pet id/name and by status."""
		filtered = list(tasks if tasks is not None else self.tasks)
		if pet_id:
			filtered = [task for task in filtered if task.pet_id == pet_id]
		if pet_name:
			name_norm = pet_name.strip().lower()
			filtered = [task for task in filtered if task.pet_name.lower() == name_norm]
		if status:
			status_norm = status.strip().lower()
			filtered = [task for task in filtered if task.status.lower() == status_norm]
		return filtered

	def expand_recurring_tasks(self, tasks: list[Task] | None = None, days: int = 1) -> list[Task]:
		"""Expand recurring tasks into occurrences visible within the given day window."""
		tasks_to_expand = tasks if tasks is not None else self.tasks
		expanded: list[Task] = []

		for task in tasks_to_expand:
			recurrence = task.recurrence.lower()
			max_occurrences = max(1, int(task.occurrences))
			if recurrence == "none":
				expanded.append(task)
				continue

			if recurrence == "daily":
				repeat_count = min(max(1, days), max_occurrences)
			elif recurrence == "weekly":
				repeat_count = min(((max(1, days) - 1) // 7) + 1, max_occurrences)
			else:
				expanded.append(task)
				continue

			for occurrence_index in range(repeat_count):
				if occurrence_index == 0:
					expanded.append(task)
					continue

				clone = replace(task)
				clone.parent_task_id = task.task_id
				clone.task_id = f"{task.task_id}-r{occurrence_index + 1}"
				if clone.notes:
					clone.notes = f"{clone.notes} | occurrence {occurrence_index + 1}"
				else:
					clone.notes = f"occurrence {occurrence_index + 1}"
				expanded.append(clone)

		return expanded

	def detect_conflicts(self, plan: list[dict[str, Any]] | None = None) -> list[tuple[str, str]]:
		"""Detect overlapping schedule windows in a plan."""
		items = list(plan if plan is not None else self.daily_plan)
		sorted_items = sorted(items, key=lambda row: row.get("start_minute", 0))
		conflicts: list[tuple[str, str]] = []

		for index in range(1, len(sorted_items)):
			previous = sorted_items[index - 1]
			current = sorted_items[index]
			if previous["end_minute"] > current["start_minute"]:
				conflicts.append((previous["task_id"], current["task_id"]))

		return conflicts

	def _overlaps_existing(
		self,
		start_minute: int,
		end_minute: int,
		existing_plan: list[dict[str, Any]],
	) -> bool:
		for row in existing_plan:
			if start_minute < row["end_minute"] and end_minute > row["start_minute"]:
				return True
		return False

	def _format_time(self, minute_of_day: int) -> str:
		hour = minute_of_day // 60
		minute = minute_of_day % 60
		return f"{hour:02d}:{minute:02d}"
