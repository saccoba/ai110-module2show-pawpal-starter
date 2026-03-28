# PawPal+ Project Reflection

## 1. System Design
 Ans: 1. Enter owner and pet information
 . The user should be able to input basic details about   themselves and their pet.
 Ans: 2. Add and manage tasks
 . User can add/edit pet care tasks such as feeding, walking, med etc.
 . Each task should include: Duration, and Priority.
 Ans: 3. Generate and view a daily plan
 . The system should create a daily schedule base on:
 ...Time
 ...Priority
 The user should then be able to view the plan clearly.
**a. Initial design**

- Briefly describe your initial UML design.
Ans: Owner- This class represent the pet owner using the app, includes; name, available time, preferences.
Pet-This class represent a pet that nedds care. it includes pet name, pet type or species, age, breed, care notes
Task- This class represent one care activity. It includes feeding, walking, medication, grooming.
Schedule- This class represents daily plan. Such as the date, list of tasks, and total time.
Scheduler- This class was the planning logic, or the brain of the system. It include organized tasks, check time limits, sort them, and  build a daily plan.


- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Ans: Scheduler constraints considered: The scheduler already tracks key core constraint and is easy to extend.
- Why is that tradeoff reasonable for this scenario?
Ans: I choosed constraints that directly enable basic daily planning first (time, completed status, recurrence), then add guard rails (overlap warning), and postpone richer "soft constraints".


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
