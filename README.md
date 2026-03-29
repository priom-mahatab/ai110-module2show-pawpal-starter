# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Your PawPal+ scheduler includes these key algorithmic features:

- **Time-based sorting**: Tasks are reordered by preferred time block (morning, afternoon, evening) and exact start time (HH:MM format), ensuring a logical daily flow.
- **Flexible filtering**: Filter tasks by pet name, completion status, or both using explicit AND/OR logic to quickly find relevant tasks.
- **Recurring task auto-expansion**: Daily and weekly recurring tasks are intelligently expanded for a given time window and marked with parent task links.
- **Recurrence completion workflow**: When a recurring task is marked complete, the next instance is automatically created and appended, maintaining the recurrence chain.
- **Conflict detection**: The scheduler detects overlapping time windows and logs conflicts or skips conflicting tasks from the final plan.
- **Owner time budgeting**: Tasks are filtered to never exceed the owner's available care minutes per day.
- **HH:MM start time support**: Tasks can specify start times in human-readable HH:MM format (e.g., "08:30") for precise scheduling.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest
```

### Test coverage

The test suite (20 tests) verifies:

- **Task completion & recurrence**: Marking tasks complete generates next occurrences with correct IDs and parent links
- **Chronological ordering**: Tasks sort correctly by preferred time block and scheduled start time (both HH:MM and minute formats)
- **Recurring task expansion**: Daily and weekly tasks expand properly within specified time windows
- **Filtering**: Tasks filter by pet name, completion status, and combinations using AND/OR logic
- **Conflict detection**: The scheduler identifies overlapping time windows and skips conflicting tasks
- **Schedule building**: Tasks are ordered into a time-based daily plan respecting owner availability and priorities

### Reliability confidence: ⭐⭐⭐⭐ (4/5)

**Why 4 stars?** All 20 core tests pass, covering the most critical scheduling behaviors (recurring tasks, time ordering, conflict detection, and filtering). The system reliably handles daily workflows and multi-pet scenarios. However, edge cases like unusual recurrence patterns, extreme time windows, or concurrent overlapping recurrences could use additional coverage for production use.
