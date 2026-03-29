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

## Features

The current implementation includes these scheduling and planning features:

- **Sorting by time**: Tasks are sorted by preferred time block (`morning`, `afternoon`, `evening`) and then by explicit start time when provided.
- **Priority-aware ranking**: Within planning, higher-priority tasks are favored before lower-priority tasks in the same scheduling context.
- **Constraint filtering**: Invalid tasks and already completed tasks are excluded before schedule construction.
- **Owner time budgeting**: The schedule enforces the owner's daily minute limit and pushes overflow tasks to an unscheduled list.
- **Conflict prevention + warnings**: Overlapping tasks are skipped during plan building, and conflict notes are surfaced in scheduler reasoning logs and UI warnings.
- **Task filtering tools**: Tasks can be filtered by pet and status with AND matching, plus an OR-based helper for completion status or pet name.
- **Daily/weekly recurrence expansion**: Recurring tasks can expand into visible occurrences for a chosen time window.
- **Recurrence continuation on completion**: Completing a recurring task automatically creates the next instance in the chain.
- **HH:MM parsing support**: Start times can be entered in HH:MM format and converted to minute-based scheduling.
- **Pet and task mutation methods**: Existing pets and tasks can be updated or removed through dedicated model methods (now wired into the Streamlit UI).

## Demo

![PawPal Demo 1](<images/Screenshot 2026-03-29 at 5.30.50 PM.png>)

![PawPal Demo 2](<images/Screenshot 2026-03-29 at 5.30.59 PM.png>)

![PawPal Demo 3](<images/Screenshot 2026-03-29 at 5.31.10 PM.png>)

![PawPal Demo 4](<images/Screenshot 2026-03-29 at 5.31.16 PM.png>)

![PawPal Demo 5](<images/Screenshot 2026-03-29 at 5.31.24 PM.png>)

![PawPal Demo 6](<images/Screenshot 2026-03-29 at 5.31.33 PM.png>)

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

The test suite (23 tests) verifies:

- **Task completion & recurrence**: Marking tasks complete generates next occurrences with correct IDs and parent links
- **Chronological ordering**: Tasks sort correctly by preferred time block and scheduled start time (both HH:MM and minute formats)
- **Recurring task expansion**: Daily and weekly tasks expand properly within specified time windows
- **Filtering**: Tasks filter by pet name, completion status, and combinations using AND/OR logic
- **Conflict detection**: The scheduler identifies overlapping time windows and skips conflicting tasks
- **Schedule building**: Tasks are ordered into a time-based daily plan respecting owner availability and priorities

### Reliability confidence: ⭐⭐⭐⭐ (4/5)

**Why 4 stars?** All 23 core tests pass, covering the most critical scheduling behaviors (recurring tasks, time ordering, conflict detection, filtering, and update/remove mutation flows). The system reliably handles daily workflows and multi-pet scenarios. However, edge cases like unusual recurrence patterns, extreme time windows, or concurrent overlapping recurrences could use additional coverage for production use.
