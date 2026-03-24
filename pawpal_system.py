from dataclasses import dataclass, field
from typing import Any


@dataclass
class Owner:
	owner_id: str = ""
	name: str = ""
	available_minutes_per_day: int = 0
	preferences: dict[str, Any] = field(default_factory=dict)
	preferred_task_order: list[str] = field(default_factory=list)

	def update_available_time(self, minutes: int) -> None:
		pass

	def set_preference(self, key: str, value: Any) -> None:
		pass

	def can_fit(self, duration_minutes: int) -> bool:
		pass

	def get_profile_summary(self) -> str:
		pass


@dataclass
class Pet:
	pet_id: str = ""
	name: str = ""
	species: str = ""
	age_years: int = 0
	special_needs: list[str] = field(default_factory=list)
	medical_notes: str = ""

	def add_special_need(self, need: str) -> None:
		pass

	def requires_medication(self) -> bool:
		pass

	def get_care_profile(self) -> str:
		pass


@dataclass
class Task:
	task_id: str = ""
	title: str = ""
	category: str = ""
	duration_minutes: int = 0
	priority: str = "medium"
	required: bool = False
	preferred_time_block: str = ""
	notes: str = ""

	def validate(self) -> bool:
		pass

	def priority_score(self) -> int:
		pass

	def to_display_row(self) -> dict[str, Any]:
		pass

	def is_high_priority(self) -> bool:
		pass


class Scheduler:
	def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
		self.owner = owner
		self.pet = pet
		self.tasks = tasks
		self.daily_plan: list[dict[str, Any]] = []
		self.unscheduled_tasks: list[Task] = []
		self.reasoning_log: list[str] = []

	def generate_schedule(self) -> list[dict[str, Any]]:
		pass

	def rank_tasks(self) -> list[Task]:
		pass

	def apply_constraints(self, tasks: list[Task]) -> list[Task]:
		pass

	def build_time_order(self, tasks: list[Task]) -> list[dict[str, Any]]:
		pass

	def explain_plan(self) -> list[str]:
		pass

	def get_unscheduled_tasks(self) -> list[Task]:
		pass
