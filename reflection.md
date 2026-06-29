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
    Yes, below is how it was generated in the uml_draft.mmd file.

classDiagram
    class Pet {
        +String species
        +String name
        +Date date_of_birth
        +String breed
        +Date gotcha_day
        +Date next_vet_visit
        +Date flea_tick_due
        +Date heartworm_due
        +check_feeding_schedule() void
        +water_refill_notification() void
        +vaccination_schedule_check() void
        +daily_schedule_check() void
    }

    class Task {
        +String frequency
        +Time time
        +String priority
        +String status
        +int duration
        +String urgency
        +Owner owner
        +Pet pet
    }

    class Owner {
        +String name
        +int number_of_pets
        +List availability
        +int age
        +check_feeding_schedule() void
        +check_pet_info() void
        +vaccination_schedule_check() void
        +daily_schedule_check() void
        +vet_visit_schedule() void
        +add_task(task Task) void
        +remove_task(task Task) void
        +edit_task(task Task) void
    }

    class Scheduler {
        +List todays_schedule
        +List deferred_tasks
        +List conflicts
        +List vet_visits
        +generate_schedule() void
        +sort_schedule() void
        +edit_schedule() void
    }

    Owner "1" --> "1..*" Pet : owns
    Owner "1" --> "0..*" Task : manages
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler "1" --> "0..*" Task : organizes
    Pet "1" --> "0..*" Task : has care tasks


    Below is how AI changed it after asking if it had noticed any logic bottlenecks or missing relationships (uml_AI_Updated.mmd file):
    classDiagram
    class Pet {
        +String species
        +String name
        +Date date_of_birth
        +String breed
        +Date gotcha_day
        +Date next_vet_visit
        +Date flea_tick_due
        +Date heartworm_due
        +check_feeding_schedule() void
        +water_refill_notification() void
        +vaccination_schedule_check() void
        +daily_schedule_check() void
    }

    class Task {
        +String title
        +String frequency
        +Time time
        +String priority
        +String status
        +int duration
        +String urgency
        +Owner owner
        +Pet pet
    }

    class Owner {
        +String name
        +int number_of_pets
        +int age
        +List availability
        +List pets
        +List tasks
        +check_feeding_schedule() void
        +check_pet_info() void
        +vaccination_schedule_check() void
        +daily_schedule_check() void
        +vet_visit_schedule() void
        +add_task(task Task) void
        +remove_task(task Task) void
        +edit_task(task Task) void
    }

    class Scheduler {
        +Owner owner
        +List~Task~ todays_schedule
        +List~Task~ deferred_tasks
        +List~Task~ conflicts
        +List~Task~ vet_visits
        +generate_schedule() void
        +sort_schedule() void
        +edit_schedule() void
    }

    Owner "1" --> "1..*" Pet : owns
    Owner "1" --> "0..*" Task : manages
    Scheduler "1" --> "1" Owner : schedules for
    Scheduler "1" --> "0..*" Task : organizes
    Pet "1" --> "0..*" Task : has care tasks

- If yes, describe at least one change and why you made it.
    Several referencing relationships were noted as missing and critical to logic flow. There were four in total but ill include two for briefness:

    Owner has no way to hold references to its Pet objects — the UML says Owner 1 --> 1..* Pet but
    there's no pets list attribute on Owner. Same for tasks — Owner 1 --> 0..* Task but no tasks list. The relationship arrows exist in the UML but the attributes that would implement them don't.
    
    Scheduler has no reference to the Pet objects it's scheduling for — it only knows about the Owner. To build a real schedule it'll need to reach the pets somehow.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    My scheduler mainly considers time and priority as the main constraints.
- How did you decide which constraints mattered most?
    I have a pet of my own and I would personally prioritize both time and priorit.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    It does not take into account preferences
- Why is that tradeoff reasonable for this scenario?
    Preference is very subjective and upto an owner and we should not hard code it as such as that would make the app inflexible to the owner's specific taste
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    I used AI primarily for design brain storming.
- What kinds of prompts or questions were most helpful?
    Few shot prompts were the most helpful as it added more context to the prompt and help mitigate hidden assumptions that might have been detrimental to the functionality of the app
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    The main suggestion i typically did not accept was running the app before I was ready to run it. Another was the implementation of the main.py file. The CLI output was not initially helpful as the output did not show a proper before and after output which would indicate proper functionality of the sorting and filtering methods.
- How did you evaluate or verify what the AI suggested?
    I evaluated the AI suggestions by using the main.py file. This was instrumental to determining whether added features  were in fact functional or not
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    Sorting and filtering
- Why were these tests important?
    I needed to ensure that sorting by scheduling time and filtering by tasks was done correctly as they were essential to the functionality and utility of the app.
**b. Confidence**

- How confident are you that your scheduler works correctly?
    I am very confident that it works correctly.
- What edge cases would you test next if you had more time?
    I would test for edge cases where there are duplicate tasks with different priority settings.
    Additionally, I would test for pets with conflicting veterinary doctor visits.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied by the object oriented architecting of the logic and connection to the streamlit UI. This was the most efficient and enjoyable time i had developing a streamlit app

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add features that would change the UI layour OR provide limited pre written tasks and schedules for exotic pets as different pets have highly specific and niche needs.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
contextualization is an important part of designing systems with AI. Without proper context or specificity, hidden assumptions cannot be mitigated properly.