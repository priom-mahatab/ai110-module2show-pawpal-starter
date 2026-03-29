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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
