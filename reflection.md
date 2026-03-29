# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    - I have 4 classes: Owner, Pet, Task, and Scheduler. An Owner can have multiple Pets and a Pet can have multiple Tasks. Scheduler depends on Owner, Pet, and Task objects to generate a plan.
- What classes did you include, and what responsibilities did you assign to each?
    - Owner: stores owner info and constraints such as available time, if they can fit a task, and care preferences.
    - Pet: stores pet profile details (name, species, age/notes) that may affect care needs.
    - Task: represents a care action (walk, feeding, meds) with duration and priority. 
    - Scheduler: Takes an instance of Owner, Pet, Task and generates a feasible plan.
- Core Actions: A user should be able to:
    - Add a Pet.
    - Edit the attributes of a Pet.
    - Filter tasks which are feasible at a given instance.

**b. Design changes**

- Did your design change during implementation?
    - Yes.
- If yes, describe at least one change and why you made it.
    - Owner class now has a pets attribute and add_pet method since a household can have multiple pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - My scheduler considers owner time limits, task priority, preferred time blocks (morning/afternoon/evening), HH:MM start times when provided, task completion status, recurrence rules (daily/weekly), and basic conflict detection for overlaps.
- How did you decide which constraints mattered most?
    - I prioritized feasibility first, then quality. Feasibility means the plan must fit the owner's available minutes and avoid invalid or completed tasks. After that, I optimize for usefulness by ordering tasks by time block and start time, then priority so critical tasks are still emphasized.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - A key tradeoff is using a deterministic sort-and-filter strategy instead of a complex global optimization algorithm. This approach is simpler and predictable, but it may not always find the absolute best possible schedule in every edge case.
- Why is that tradeoff reasonable for this scenario?
    - It is reasonable because pet owners need clear and fast plans that are easy to trust and debug. For this project scope, readable logic and consistent behavior are more valuable than heavy optimization complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - I used VS Code Copilot in multiple ways: brainstorming UML boundaries (which class should own what), generating class skeletons, creating method stubs, drafting tests for core behaviors, and debugging import/session-state integration issues in Streamlit. During implementation, Copilot was most effective for turning high-level scheduling rules into concrete method structures quickly.
- What kinds of prompts or questions were most helpful?
    - The most helpful prompts were specific and constraint-driven, for example: "implement only app.py and keep logic layer unchanged", "add minimal tests for this exact behavior", and "review missing relationships and potential bottlenecks". Prompts that clearly scoped the file, goal, and non-goals gave cleaner outputs.

- Which Copilot features were most effective for building your scheduler?
    - Chat-based design iteration and code review were most useful for scheduler architecture, while inline suggestions helped speed up repetitive model-method code. Copilot was especially effective when I asked for small, testable increments (ranking, filtering, conflict checks) instead of a single large implementation.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - I rejected an early suggestion to push too much behavior into one place and instead kept class responsibilities separate: Owner/Pet/Task handle domain data and mutations, while Scheduler orchestrates planning. This kept the design cleaner and avoided a "god method" style implementation.
- How did you evaluate or verify what the AI suggested?
    - I verified suggestions by checking UML consistency, running pytest for behavior-level confidence, and manually validating Streamlit session-state behavior in the UI. If a suggestion violated class boundaries or made testing harder, I modified it before accepting.

- How did using separate chat sessions for different phases help you stay organized?
    - Separate sessions helped me avoid context mixing and keep decisions traceable. I used one phase for UML/design, one for implementation, one for tests/debugging, and one for UI integration. That structure made prompts clearer and reduced accidental scope creep.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
    - I learned that AI can accelerate coding, but architecture quality still depends on human judgment. My role was to define boundaries, enforce consistency, and choose tradeoffs. The best results came from treating Copilot as a fast collaborator while I remained accountable for system design decisions.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - I tested task completion and recurrence chaining, chronological ordering by time block and explicit HH:MM/minute start times, recurring task expansion (daily/weekly), filtering by pet and completion status (including AND/OR helper behavior), conflict detection for overlapping windows, and schedule construction under owner time limits.
- Why were these tests important?
    - These tests cover the core correctness risks in a scheduler: wrong ordering, invalid inclusion of completed tasks, recurrence bugs, and time-overlap issues. They also protected key mutation flows (updating/removing pets and tasks) so UI actions map to reliable model behavior.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - I am highly confident for the project scope (about 4/5 confidence). The current suite validates the most important planning behaviors and all tests are passing, so the main daily workflow is stable and predictable.
- What edge cases would you test next if you had more time?
    - Next I would test unusual recurrence combinations (large occurrence counts and weekly boundaries), tighter conflict scenarios with many same-block tasks, malformed or partial HH:MM inputs, and stress cases where many tasks compete for a very small owner time budget.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I am most satisfied with how the domain model and scheduler pipeline stayed clean as features grew. The system evolved from basic class stubs into a multi-pet planner with recurrence, conflict detection, and filtering while keeping responsibilities separated.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - I would improve global optimization in schedule building (for example, smarter rescheduling instead of simple skip-on-conflict), add stronger input validation boundaries directly in all mutation paths, and expand UI controls for editing/deleting with clearer reasoning traces for each scheduling decision.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - My key takeaway is that clear architecture decisions come first: AI can accelerate implementation, but maintainability comes from human ownership of boundaries, test strategy, and tradeoffs.
