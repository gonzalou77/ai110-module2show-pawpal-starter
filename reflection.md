# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    Below was the initial design
    PawPal+ Class Design

Class	Role	Key Responsibilities
Pet	Data model	Stores species, name, age, special needs
Owner	Data model	Stores name, available hours, preferences; owns one or more Pets
Task	Data model	Represents a care task: title, duration, priority, category (feeding, walk, vet, etc.)
Scheduler	Logic engine	Takes an Owner + their Pet(s) + a list of Tasks, applies constraints, and produces an ordered daily plan

- What classes did you include, and what responsibilities did you assign to each?
    I included all 4 classes: Pet, Owner, Task, and Scheduler.
    In short, Pets included species, name, age, etc.; Owner included: add task, check daily schedule;
    Task just assigns priority, duration, categorym, etc; and Scheduler generates the schedule, deletes, or edits the  schedule.

**b. Design changes**

- Did your design change during implementation?
    Yes, below is how i changed it

1) Pet
    - Attributes
        1) Species (limited to 'Dog' or 'Cat')
        2) Name
        3) Date of Birth
        4) Breed
        5) 'Gotcha Day' Date
        6) Next Vet Visit
        7) Flea & Tick Prevention (Include Heartworm Prevention if Dog) due date
    - Method
        1) Check Feeding Schedule
        2) Water Refill Notification
        3) Vaccination Schedule Check
        4) Daily Schedule Check
2) Task
    - Attributes
        1) Frequency
        2) Time
        3) Priority
        4) Status
        5) Duration
        6) Urgency
    - Method
        1) Add Task
        2) Remove Task
        3) Edit Task
3) Owner
    - Attributes
        1) Name
        2) Number of Pets
        3) Availability
        4) Age
    - Method
        1) Check Feeding Schedule
        2) Check Pet Info
        3) Vaccination Schedule Check
        4) Daily Schedule Check
        5) Vet Visit Schedule
4) Scheduler
    - Attributes
        1) Today's Schedule
        2) Deferred Tasks
        3) Conflicts
        4) Vet Visits
    - Method
        1) Generate Schedule
        2) Sort Schedule
        3) Edit Schedule
The proposed design from Claude is below and i did change it during implementation
- If yes, describe at least one change and why you made it.
    I would like my pawpal+ app to give me good comprehensive information on the care of pets, including their gotcha day and birthday


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
