# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design included four classes: Owner, Pet, Task, and Scheduler. Owner was responsible for holding a list of pets. Pet was responsible for holding a list of tasks assigned to it. Task stored the details of a single care activity, including the title, time, and completion status. Scheduler was responsible for coordinating tasks across all pets and providing sorting, filtering, and conflict detection.

**b. Design changes**

Yes, the design changed during implementation. Originally, Pet stored tasks and also had scheduling methods like add_task and get_tasks that overlapped with Scheduler responsibilities. I moved scheduling logic into Scheduler so that Pet became a pure data class. I also simplified the Task class by removing the date field and replacing it with a time string, which was more practical for a daily schedule view. The Owner class was also simplified to only require a name, removing the email and phone fields that were not needed for the core functionality.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time as the main constraint when organizing tasks. Tasks are scheduled using specific time values, and sorting is based on chronological order. Another constraint is task completion status, which is used for filtering. Time was prioritized because the main purpose of the app is to help pet owners manage daily schedules efficiently.

**b. Tradeoffs**

One tradeoff the scheduler makes is using a simple string comparison for time sorting instead of parsing actual time objects. This keeps the code simple and readable, but it means the system assumes all times are entered in HH:MM format. If a user enters a time like "9:00" instead of "09:00", the sort order could be incorrect. This tradeoff is reasonable for this project because the app targets a single owner managing a small number of daily tasks, where strict time validation is less critical than keeping the code easy to understand and extend.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used throughout the project for multiple purposes. During the design phase, AI helped brainstorm which classes and methods to include and how to structure the relationships between them. During implementation, AI assisted with writing class stubs, filling in method logic, and catching issues like mutable default arguments in data classes. AI was also used for debugging when methods returned unexpected results, such as when task storage was duplicated across Pet and Scheduler. The most helpful prompts were specific and focused, such as asking to implement a single method or fix a specific behavior, rather than asking for the entire system at once.

**b. Judgment and verification**

There were moments where I did not accept AI suggestions directly. Some generated code included unnecessary complexity or features that were not required for the project. I evaluated the suggestions by testing the code, simplifying it when needed, and checking that it aligned with the project requirements. This helped me maintain control over the design instead of relying completely on AI.

---

## 4. Testing and Verification

**a. What you tested**

I tested core behaviors such as adding pets, adding tasks, marking tasks as complete, sorting tasks by time, and detecting scheduling conflicts. These tests were important to ensure that the system behaved correctly and that the different components interacted properly.

**b. Confidence**

I am confident that the core scheduling behaviors work correctly based on the passing tests. All six tests cover the primary use cases: creating objects, assigning tasks, marking completion, sorting by time, and detecting conflicts. If I had more time, I would test edge cases such as adding a task with an invalid time format, adding duplicate pets or tasks, filtering when no tasks exist, and ensuring conflict detection works correctly when three or more tasks share the same time slot.

---

## 5. Reflection

**a. What went well**

The part of this project I am most satisfied with is the Scheduler class. It started as a simple wrapper but grew into the most capable component in the system, handling sorting, filtering, and conflict detection in a clean and readable way. Keeping tasks as a single source of truth inside Scheduler, rather than splitting storage between Pet and Scheduler, made the logic much easier to reason about and test.

**b. What you would improve**

If I had another iteration, I would add priority levels to tasks so the scheduler could not only sort by time but also recommend which tasks to do first when there are conflicts. I would also improve the time input in the UI to use a proper time picker instead of a text field, which would prevent formatting errors. Adding the ability to edit or delete tasks would also make the app more practical for real use.

**c. Key takeaway**

One important thing I learned is that designing a system requires clear organization and separation of responsibilities between components. Working with AI tools also showed me that while AI can speed up development, it is important to review and refine its suggestions to ensure the final system is correct and efficient.
