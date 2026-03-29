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

	def get_pet(self, pet_id: str) -> "Pet | None":
		"""Return the pet with the given ID, or None if no match exists."""
		return next((pet for pet in self.pets if pet.pet_id == pet_id), None)

	def remove_pet(self, pet_id: str) -> bool:
		"""Remove a pet by ID and return whether a pet was removed."""
		pet = self.get_pet(pet_id)
		if pet is None:
			return False
		self.pets.remove(pet)
		return True

	def update_pet(
		self,
		pet_id: str,
		name: str | None = None,
		species: str | None = None,
		age_years: int | None = None,
		special_needs: list[str] | None = None,
		medical_notes: str | None = None,
	) -> bool:
		"""Update editable fields for a pet and return whether the pet was found."""
		pet = self.get_pet(pet_id)
		if pet is None:
			return False

		pet.update_profile(
			name=name,
			species=species,
			age_years=age_years,
			special_needs=special_needs,
			medical_notes=medical_notes,
		)
		return True


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

	def update_profile(
		self,
		name: str | None = None,
		species: str | None = None,
		age_years: int | None = None,
		special_needs: list[str] | None = None,
		medical_notes: str | None = None,
	) -> None:
		"""Update editable pet profile fields."""
		if name is not None:
			self.name = name.strip()
		if species is not None:
			self.species = species.strip()
		if age_years is not None:
			self.age_years = max(0, int(age_years))
		if special_needs is not None:
			self.special_needs = [need.strip() for need in special_needs if need.strip()]
		if medical_notes is not None:
			self.medical_notes = medical_notes.strip()

		# Keep task labels aligned when pet name changes.
		for task in self.tasks:
			task.pet_name = self.name

	def get_task(self, task_id: str) -> "Task | None":
		"""Return a task by ID, or None if not found."""
		return next((task for task in self.tasks if task.task_id == task_id), None)

	def remove_task(self, task_id: str) -> bool:
		"""Remove task by ID and return whether a task was removed."""
		task = self.get_task(task_id)
		if task is None:
			return False
		self.tasks.remove(task)
		return True

	def update_task(
		self,
		task_id: str,
		title: str | None = None,
		category: str | None = None,
		duration_minutes: int | None = None,
		priority: str | None = None,
		status: str | None = None,
		required: bool | None = None,
		preferred_time_block: str | None = None,
		notes: str | None = None,
		recurrence: str | None = None,
		occurrences: int | None = None,
		scheduled_start_minute: int | None = None,
		scheduled_start_hhmm: str | None = None,
	) -> bool:
		"""Update a task by ID and return whether update succeeded validation."""
		task = self.get_task(task_id)
		if task is None:
			return False

		original = replace(task)

		if title is not None:
			task.title = title
		if category is not None:
			task.category = category
		if duration_minutes is not None:
			task.duration_minutes = int(duration_minutes)
		if priority is not None:
			task.priority = priority
		if status is not None:
			task.status = status
		if required is not None:
			task.required = bool(required)
		if preferred_time_block is not None:
			task.preferred_time_block = preferred_time_block
		if notes is not None:
			task.notes = notes
		if recurrence is not None:
			task.recurrence = recurrence
		if occurrences is not None:
			task.occurrences = max(1, int(occurrences))
		if scheduled_start_minute is not None:
			task.scheduled_start_minute = int(scheduled_start_minute)
		if scheduled_start_hhmm is not None:
			task.scheduled_start_hhmm = scheduled_start_hhmm

		if not task.validate():
			task.title = original.title
			task.category = original.category
			task.duration_minutes = original.duration_minutes
			task.priority = original.priority
			task.status = original.status
			task.required = original.required
			task.preferred_time_block = original.preferred_time_block
			task.notes = original.notes
			task.recurrence = original.recurrence
			task.occurrences = original.occurrences
			task.scheduled_start_minute = original.scheduled_start_minute
			task.scheduled_start_hhmm = original.scheduled_start_hhmm
			return False

		task.pet_id = self.pet_id
		task.pet_name = self.name
		return True


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
	scheduled_start_hhmm: str = ""

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
		if self.scheduled_start_hhmm and not self._is_valid_hhmm(self.scheduled_start_hhmm):
			return False
		return True

	def _is_valid_hhmm(self, value: str) -> bool:
		parts = value.strip().split(":")
		if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
			return False
		hour = int(parts[0])
		minute = int(parts[1])
		return 0 <= hour <= 23 and 0 <= minute <= 59

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

	def mark_complete(self) -> "Task | None":
		"""Mark the task as completed and create next recurring instance if needed."""
		self.status = "completed"
		return self.create_next_occurrence()

	def create_next_occurrence(self) -> "Task | None":
		"""Create and return the next recurring task instance when recurrence is enabled."""
		recurrence_mode = self.recurrence.lower()
		if recurrence_mode not in {"daily", "weekly"}:
			return None

		base_id = self.parent_task_id or self._get_base_recurrence_id()
		next_index = self._get_recurrence_index() + 1

		next_task = replace(self)
		next_task.parent_task_id = base_id
		next_task.task_id = f"{base_id}-next-{next_index}"
		next_task.status = "pending"
		next_task.notes = self._append_recurrence_note(next_task.notes, recurrence_mode)
		return next_task

	def _get_base_recurrence_id(self) -> str:
		"""Extract the base task ID from a recurrence chain ID (e.g., 'task-1-next-5' -> 'task-1')."""
		if "-next-" in self.task_id:
			return self.task_id.split("-next-")[0]
		return self.task_id

	def _get_recurrence_index(self) -> int:
		"""Return the occurrence index from task ID (e.g., 'task-1-next-5' -> 5), or 0 if not a recurrence."""
		if "-next-" not in self.task_id:
			return 0
		suffix = self.task_id.rsplit("-next-", maxsplit=1)[-1]
		if suffix.isdigit():
			return int(suffix)
		return 0

	def _append_recurrence_note(self, existing_notes: str, recurrence_mode: str) -> str:
		"""Append a recurrence annotation to existing notes, or create new notes if empty."""
		note = f"auto-created next {recurrence_mode} occurrence"
		if existing_notes:
			return f"{existing_notes} | {note}"
		return note


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
			start_minute = self._resolve_task_start_minute(task)
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

	def complete_task(self, task_id: str) -> Task | None:
		"""Mark a task complete and append the next recurring instance when relevant."""
		task = next((item for item in self.tasks if item.task_id == task_id), None)
		if task is None:
			return None

		next_task = task.mark_complete()
		if next_task and all(item.task_id != next_task.task_id for item in self.tasks):
			self.tasks.append(next_task)
			self.reasoning_log.append(
				f"Created next recurring task instance '{next_task.task_id}' after completing '{task_id}'."
			)
		return next_task

	def sort_tasks_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
		"""Sort tasks by preferred block then explicit start time when available."""
		tasks_to_sort = tasks if tasks is not None else self.tasks
		time_order = {"morning": 0, "afternoon": 1, "evening": 2, "": 3}

		def start_key(task: Task) -> int:
			start_minute = self._resolve_task_start_minute(task)
			return start_minute if start_minute is not None else 24 * 60

		return sorted(
			tasks_to_sort,
			key=lambda task: (
				time_order.get(task.preferred_time_block, 3),
				start_key(task),
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

	def filter_tasks_by_completion_or_pet_name(
		self,
		completion_status: str | None = None,
		pet_name: str | None = None,
		tasks: list[Task] | None = None,
	) -> list[Task]:
		"""Return tasks matching completion status and/or pet name.

		When both filters are provided, a task is included if either filter matches.
		"""
		items = list(tasks if tasks is not None else self.tasks)
		status_norm = completion_status.strip().lower() if completion_status else None
		pet_name_norm = pet_name.strip().lower() if pet_name else None

		if not status_norm and not pet_name_norm:
			return items

		results: list[Task] = []
		for task in items:
			status_match = bool(status_norm and task.status.lower() == status_norm)
			pet_match = bool(pet_name_norm and task.pet_name.lower() == pet_name_norm)
			if status_match or pet_match:
				results.append(task)
		return results

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
		"""Check if a proposed time window overlaps with any scheduled task in the plan."""
		for row in existing_plan:
			if start_minute < row["end_minute"] and end_minute > row["start_minute"]:
				return True
		return False

	def _format_time(self, minute_of_day: int) -> str:
		hour = minute_of_day // 60
		minute = minute_of_day % 60
		return f"{hour:02d}:{minute:02d}"

	def _resolve_task_start_minute(self, task: Task) -> int | None:
		"""Resolve the effective start time: prefer HH:MM format, fall back to numeric minutes."""
		parsed = self._parse_hhmm_to_minute(task.scheduled_start_hhmm)
		if parsed is not None:
			return parsed
		return task.scheduled_start_minute

	def _parse_hhmm_to_minute(self, value: str) -> int | None:
		"""Convert HH:MM string (e.g., '08:30') to minutes since midnight (e.g., 510); return None if invalid."""
		if not value:
			return None
		parts = value.strip().split(":")
		if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
			return None
		hour = int(parts[0])
		minute = int(parts[1])
		if not (0 <= hour <= 23 and 0 <= minute <= 59):
			return None
		return (hour * 60) + minute
