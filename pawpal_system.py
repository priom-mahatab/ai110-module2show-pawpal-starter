from dataclasses import dataclass, field
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
		pass

	def set_preference(self, key: str, value: Any) -> None:
		"""Set a named care preference for the owner."""
		pass

	def can_fit(self, duration_minutes: int) -> bool:
		"""Return whether a task duration fits the owner's time budget."""
		pass

	def get_profile_summary(self) -> str:
		"""Return a short human-readable summary of the owner profile."""
		pass

	def add_pet(self, pet: "Pet") -> None:
		"""Add a pet to the owner's pet list."""
		pass


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
		pass

	def requires_medication(self) -> bool:
		"""Return whether the pet currently needs medication."""
		pass

	def get_care_profile(self) -> str:
		"""Return a short summary of the pet's care profile."""
		pass

	def add_task(self, task: "Task") -> None:
		"""Add a care task to this pet's task list."""
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

	def validate(self) -> bool:
		"""Validate task fields and return whether the task is usable."""
		pass

	def priority_score(self) -> int:
		"""Return a numeric score representing task priority."""
		pass

	def to_display_row(self) -> dict[str, Any]:
		"""Convert the task into a display-friendly dictionary row."""
		pass

	def is_high_priority(self) -> bool:
		"""Return whether this task is marked as high priority."""
		pass

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
		pass

	def rank_tasks(self) -> list[Task]:
		"""Rank tasks according to priority and scheduling rules."""
		pass

	def apply_constraints(self, tasks: list[Task]) -> list[Task]:
		"""Filter tasks based on owner time and other constraints."""
		pass

	def build_time_order(self, tasks: list[Task]) -> list[dict[str, Any]]:
		"""Order selected tasks into a time-based daily plan."""
		pass

	def explain_plan(self) -> list[str]:
		"""Return explanation notes for scheduling decisions."""
		pass

	def get_unscheduled_tasks(self) -> list[Task]:
		"""Return tasks that were not included in the final schedule."""
		pass
