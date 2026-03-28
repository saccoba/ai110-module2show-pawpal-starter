# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML included five classes: `Owner` (pet owner details and available time), `Pet` (pet name, species, age, breed, care notes), `Task` (a single care activity such as feeding or walking), `Schedule` (a daily plan holding a date, task list, and total time), and `Scheduler` (the planning brain that sorted tasks and built the daily plan).

- What classes did you include, and what responsibilities did you assign to each?

| Class | Responsibility |
|---|---|
| `Owner` | Store owner name and preferences; hold a list of pets |
| `Pet` | Store pet details; own and manage its task list |
| `Task` | Represent one care activity with duration, frequency, and completion state |
| `Schedule` | Hold a dated list of planned tasks (initial design only) |
| `Scheduler` | Retrieve, sort, filter, and validate tasks across all pets |

**b. Design changes**

Yes, the design changed in two meaningful ways during implementation:

1. **`Schedule` was removed.** The initial design included a separate `Schedule` class to hold a dated plan. During implementation this turned out to be unnecessary — `Scheduler.get_schedule_summary()` and the filtering methods covered all the same ground without the added complexity of a separate date-aware object.

2. **`Task` gained `start_time` and `completed`.** The initial `Task` only tracked duration and priority. Once conflict detection was added, `start_time: Optional[str]` became essential. `completed: bool` was needed to support recurring task requeue logic and the completion filter in the UI.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three core constraints:

- **Time (duration)** — Tasks are sorted by how long they take so owners can see at a glance which tasks are quick vs. time-intensive.
- **Completion status** — `get_tasks(completed=...)` separates done tasks from pending ones, keeping the daily view focused on what still needs to happen.
- **Time-slot overlap** — `get_conflict_warning()` checks whether a new task's start time and duration would overlap with any already-scheduled task for the same pet.

I prioritized these three because they are the minimum needed for a real daily plan to be useful and conflict-free. Softer constraints like owner preference or pet energy level were deliberately deferred to keep the core logic clean and fully testable.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One key tradeoff is that **conflict detection warns but does not block**. `get_conflict_warning()` returns a warning string; it does not raise an exception or prevent the task from being added. A user who dismisses the warning can still create an overlapping schedule.

- Why is that tradeoff reasonable for this scenario?

This is reasonable because a pet care app should assist the owner, not override their judgment. There are legitimate reasons to schedule tasks close together. Blocking outright would be too restrictive; warning gives the owner the information and leaves the decision to them. I chose constraints that directly enable basic daily planning first (time, completed status, recurrence), then added guard rails (overlap warning), and postponed richer soft constraints for a future iteration.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project?

I used Claude and Copilot throughout the project in three main ways:

1. **Edge case discovery** — I asked Claude to review `pawpal_system.py` and identify the most important edge cases to test. This surfaced cases I had not considered, such as tasks sharing an exact time boundary (adjacent but not overlapping), completing a recurring task twice, and calling `mark_task_complete()` with a pet name that does not exist.

2. **Test drafting** — After agreeing on a list of behaviors to verify, I asked Claude to write the pytest functions. This accelerated coverage from 8 tests to 46 tests while keeping each test focused on a single behavior.

3. **UML reconciliation** — After the build was complete, I asked Claude to compare the final code against my initial diagram and list every method or relationship that needed to be added or corrected, giving me a precise checklist rather than a manual diff.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were specific and code-grounded: *"Based on this file, what edge cases should I test?"* worked much better than open-ended questions because it gave Claude something concrete to reason about rather than generating generic suggestions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When Claude generated the initial conflict detection test, it only tested two tasks starting at the exact same time. I did not accept this as sufficient — same-start-time is the obvious case, but partial overlap (a task starting mid-way through an existing one) is the more realistic bug.

- How did you evaluate or verify what the AI suggested?

I asked Claude to add a second test covering partial overlap (`08:00–09:00` vs `08:30–09:00`), then manually traced through `_time_str_to_minutes()` to confirm the boundary arithmetic was correct before accepting the test. Verifying the logic by hand — not just running the test — gave me confidence that the test was actually catching the right behavior.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The final suite of 46 tests covers:

- **Task methods** — `mark_complete`, `mark_incomplete`, `update_task` (full, partial, and negative-time error), `get_summary`
- **Pet methods** — `add_task`, `remove_task` (found, not found, case-insensitive), `get_completed_tasks`, `get_incomplete_tasks`, `get_pet_summary`
- **Owner methods** — `add_pet`, `remove_pet`, `get_pet`, `get_all_tasks`, `get_owner_summary`
- **Scheduler — sorting** — chronological time string order, ascending/descending duration sort, empty and single-element lists, case-insensitive alphabetical sort
- **Scheduler — recurrence** — daily auto-queue, weekly auto-queue, non-recurring stays single, case-insensitive frequency, completing a task twice, unknown pet, unknown task
- **Scheduler — conflict detection** — exact overlap, partial overlap, adjacent (no conflict), no `start_time`, unknown pet
- **Scheduler — filtering** — by status, by pet, combined, no filters, unknown pet

- Why were these tests important?

The recurrence and conflict logic are the highest-risk behaviors — a silent bug there would cause double-bookings or lost tasks that the owner relies on daily. Testing these explicitly made it safe to refactor and extend the code without fear of breaking core scheduling guarantees.

**b. Confidence**

- How confident are you that your scheduler works correctly?

Confidence level: high for implemented behaviors, moderate for untested paths. All 46 tests pass and cover the main happy paths and the edge cases identified during design review.

- What edge cases would you test next if you had more time?

1. **Multi-pet conflict isolation** — verify a conflict on one pet's schedule does not trigger a warning for a different pet.
2. **Very long task chains** — completing a recurring task many times to confirm no performance or state degradation.
3. **`update_task` after completion** — editing a task already marked complete to confirm state stays consistent.
4. **UI-level integration** — automated Streamlit tests to verify conflict warning and requeue flows work end-to-end.

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is the test suite. Starting from 8 basic tests and systematically expanding to 46 by asking "what edge cases does this logic have?" produced a suite that genuinely validates the scheduler's behavior rather than just confirming the happy path. Every assumption I examined during that process — including the duplicate method definitions discovered in `pawpal_system.py` — was caught before it could cause a silent bug in the app.

**b. What you would improve**

If I had another iteration I would redesign the recurrence system to be date-aware. Currently `mark_task_complete()` appends a new copy of the task with no scheduled date — the structure is correct but incomplete. Adding a `due_date` field to `Task` and having the scheduler auto-set the next due date (today + 1 for daily, today + 7 for weekly) would make the plan genuinely useful across multiple days, not just within a single session.

**c. Key takeaway**

The most important thing I learned is that AI is most useful as a structured thinking partner, not an answer machine. The best results came from giving Claude a specific file and a specific question — "what edge cases does this method have?" or "what methods are untested?" — and then evaluating the suggestions against the actual code rather than accepting them at face value. When I stayed in that loop (ask → review → verify → decide), the AI accelerated work significantly. When I skipped the verify step, I risked shipping tests that passed trivially rather than tests that actually found real bugs.
