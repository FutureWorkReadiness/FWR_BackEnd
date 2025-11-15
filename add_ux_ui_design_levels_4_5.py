"""
Add UX/UI Design Quizzes - Levels 4 and 5
This script adds 40 questions for UX/UI Design specialization
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_ux_ui_design_quizzes():
    db = SessionLocal()
    try:
        # Get UX Designer specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "UX Designer (User Experience)"
        ).first()
        
        if not specialization:
            print("Error: UX Designer (User Experience) specialization not found")
            print("Checking available specializations...")
            all_specs = db.query(models.Specialization).all()
            for spec in all_specs:
                if "ux" in spec.name.lower() or "ui" in spec.name.lower() or "design" in spec.name.lower():
                    print(f"  Found: {spec.name} (ID: {spec.id})")
            return
        
        print(f"Found specialization: {specialization.name} (ID: {specialization.id})")
        
        # Delete existing quizzes for levels 4 and 5
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == specialization.id,
            models.Quiz.difficulty_level.in_([4, 5])
        ).all()
        
        for quiz in existing_quizzes:
            # Delete quiz attempts first
            db.query(models.QuizAttempt).filter(
                models.QuizAttempt.quiz_id == quiz.id
            ).delete()
            
            # Delete question options
            for question in quiz.questions:
                db.query(models.QuestionOption).filter(
                    models.QuestionOption.question_id == question.id
                ).delete()
            
            # Delete questions
            db.query(models.Question).filter(
                models.Question.quiz_id == quiz.id
            ).delete()
            
            # Delete quiz
            db.query(models.Quiz).filter(models.Quiz.id == quiz.id).delete()
        
        db.commit()
        print(f"Deleted {len(existing_quizzes)} existing quizzes for levels 4-5")
        
        # Level 4: Expert & Specialization (20 questions)
        level_4_questions = [
            ('What is the "System Usability Scale" (SUS)?',
             ["A tool for measuring the physical \"scale\" or size of a design system.",
              "A quick, 10-question survey used to measure the perceived usability of a product.",
              "A set of guidelines for making a system scalable.",
              "A type of design system.",
              "A hardware device for testing system performance."],
             1, "SUS is a standardized 10-question survey for measuring perceived usability."),
            
            ('What is "design thinking"?',
             ["A specific visual style that is very minimalist and thoughtful.",
              "A five-stage, human-centered process for creative problem-solving (Empathize, Define, Ideate, Prototype, Test).",
              "The process of thinking about a design's colors and fonts.",
              "A software for managing design files.",
              "A set of usability heuristics."],
             1, "Design thinking is a human-centered, five-stage problem-solving framework."),
            
            ('What is the "ideate" stage of design thinking?',
             ["The stage where you test a prototype with real users.",
              "The stage where you build a high-fidelity mockup.",
              "The stage focused on brainstorming and generating a wide range of potential solutions.",
              "The stage where you research and empathize with your users.",
              "The stage where you define the core problem to be solved."],
             2, "The ideate stage focuses on brainstorming and generating many potential solutions."),
            
            ('What is a "design sprint"?',
             ["A long-term, multi-month project to build a new design system.",
              "A time-constrained (usually 5-day) process for answering critical business questions through design.",
              "The final, fast-paced coding \"sprint\" to launch a product.",
              "A type of font that looks like it's moving fast.",
              "A quick meeting to review and critique a design."],
             1, "Design sprints are typically 5-day processes for solving critical business questions through design."),
            
            ('What is the main difference between "divergent" and "convergent" thinking?',
             ["Divergent is generating many ideas; convergent is narrowing them down.",
              "Divergent is narrowing ideas; convergent is generating them.",
              "Divergent is for UI; convergent is for UX.",
              "Divergent is for designers; convergent is for developers.",
              "Divergent is logical; convergent is creative."],
             0, "Divergent thinking generates many ideas; convergent thinking narrows them down to the best options."),
            
            ('What is a "mental model"?',
             ["A visualization of a user's brain activity during a usability test.",
              "A user's internal belief about how a system works, based on their past experiences.",
              "A diagram of the designer's thought process.",
              "A type of user persona that focuses on psychology.",
              "A security model that prevents users from thinking of bad ideas."],
             1, "Mental models are users' internal beliefs about how systems work, shaped by past experiences."),
            
            ('What is the main difference between a "user flow" and a "user journey map"?',
             ["A flow is a simple path; a journey map includes emotions and pain points.",
              "A flow includes emotions; a journey map is a simple path.",
              "A flow is for desktop; a journey map is for mobile.",
              "A flow is a prototype; a journey map is a wireframe.",
              "A flow is a sitemap; a journey map is a persona."],
             0, "User flows show the path; journey maps add emotional context and pain points."),
            
            ('What is the purpose of "stakeholder interviews"?',
             ["To understand the needs and goals of the target users.",
              "To test the usability of a prototype with internal employees.",
              "To understand the business goals, constraints, and success criteria from key decision-makers.",
              "To sell the final design to the company's investors.",
              "To create a list of all stakeholders in a \"company map.\""],
             2, "Stakeholder interviews gather business goals, constraints, and success criteria from decision-makers."),
            
            ('What is "Guerilla" usability testing?',
             ["A highly structured, formal usability test conducted in a lab.",
              "A quick, informal method of testing with random users in a public place.",
              "A test that is \"at war\" with the current design.",
              "A test that uses animal-themed (e.g., gorilla) icons.",
              "A test that is conducted by the military."],
             1, "Guerrilla testing is quick, informal testing with random users in public spaces."),
            
            ('What is "eye-tracking" in user research?',
             ["A technology that measures and records where a user is looking on a screen.",
              "A design principle that ensures all elements are \"easy on the eyes.\"",
              "A test where an observer manually \"tracks\" a user's eyes.",
              "A UI component that follows the user's cursor.",
              "A security feature that scans a user's retina."],
             0, "Eye-tracking technology records where users look on a screen to understand attention patterns."),
            
            ('What is "microcopy"?',
             ["The small, instructional text in a UI (e.g., button labels, error messages).",
              "A very small, difficult-to-read font.",
              "A \"copy and paste\" function for small elements.",
              "A document containing all the legal text for an app.",
              "A type of user research note."],
             0, "Microcopy is the small, instructional text like button labels and error messages."),
            
            ('What is an "empathy map"?',
             ["A map that shows where users live.",
              "A collaborative tool for visualizing what a user \"says, thinks, feels, and does.\"",
              "A high-fidelity mockup of a user's profile.",
              "A chart that tracks a user's emotions over time.",
              "A list of all the features a user feels are \"empathetic.\""],
             1, "Empathy maps visualize what users say, think, feel, and do to build understanding."),
            
            ('What is a "component" in a design system?',
             ["A reusable UI element, like a button or a form field.",
              "A single, static mockup of one screen.",
              "A user persona.",
              "A document of usability test results.",
              "A project management task."],
             0, "Components are reusable UI elements like buttons, form fields, and cards."),
            
            ('What is a "design token"?',
             ["A \"token\" of appreciation for a good design.",
              "A password or \"token\" to access a design file.",
              "A core, indivisible design value (e.g., a specific color #FF0000, a font size 16px).",
              "A UI component, like a button or a card.",
              "A security feature for a design system."],
             2, "Design tokens are core values like specific colors, font sizes, and spacing units."),
            
            ('What is the difference between "prototyping" and "wireframing"?',
             ["Wireframing is about structure; prototyping is about interaction.",
              "Wireframing is interactive; prototyping is static.",
              "Wireframing is high-fidelity; prototyping is low-fidelity.",
              "Wireframing is done with code; prototyping is done in Figma.",
              "They are the same thing."],
             0, "Wireframing focuses on structure and layout; prototyping adds interaction and behavior."),
            
            ('What is a "diary study"?',
             ["A research method where users self-report their activities and experiences over a period of time.",
              "A study of a designer's personal diary.",
              "A usability test that is performed every day.",
              "A document containing all the notes from a design sprint.",
              "A UI for a \"diary\" or \"journal\" application."],
             0, "Diary studies have users self-report activities and experiences over time."),
            
            ('What is "ethnographic research"?',
             ["The study of ethnic and cultural backgrounds.",
              "The study of users in their natural environment to understand their behaviors.",
              "A usability test conducted in a formal lab.",
              "A survey sent to thousands of users.",
              "The process of designing for different cultures."],
             1, "Ethnographic research observes users in their natural environment to understand behaviors."),
            
            ('What is the "Kano Model"?',
             ["A model for prioritizing features based on their ability to satisfy users (e.g., Basic, Performance, Delighter).",
              "A model for designing information architecture.",
              "A model for creating a color palette.",
              "A specific type of design system.",
              "A usability testing method."],
             0, "The Kano Model categorizes features by satisfaction: Basic, Performance, and Delighter."),
            
            ('What is a "contextual inquiry"?',
             ["An interview with a user while they are performing a task in their normal environment.",
              "An interview with a stakeholder to understand business \"context.\"",
              "A usability test in a lab.",
              "A survey about a user's background.",
              "A method for analyzing competitors."],
             0, "Contextual inquiry involves interviewing users while they perform tasks in their natural environment."),
            
            ('What is a "design critique"?',
             ["A meeting where designers present their work and receive constructive feedback.",
              "A negative review of a product from a user.",
              "A heuristic evaluation.",
              "A usability test.",
              "A stakeholder interview."],
             0, "Design critiques are collaborative sessions for presenting work and receiving constructive feedback."),
        ]
        
        quiz_4 = models.Quiz(
            title="UX/UI Design - Expert & Specialization",
            description="Advanced methods: SUS, design thinking, design sprints, mental models, guerrilla testing, eye-tracking, empathy maps, design systems, Kano Model, research methods",
            specialization_id=specialization.id,
            difficulty_level=4,
            time_limit_minutes=35
        )
        db.add(quiz_4)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_4_questions):
            question = models.Question(
                quiz_id=quiz_4.id,
                question_text=question_text,
                question_type='multiple_choice',
                explanation=explanation,
                order_index=idx
            )
            db.add(question)
            db.flush()
            
            for opt_idx, option_text in enumerate(options):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(opt_idx == correct_idx),
                    order_index=opt_idx
                )
                db.add(option)
        
        print(f"Added Level 4 (Expert & Specialization): {len(level_4_questions)} questions")
        
        # Level 5: Strategic & Architectural (20 questions)
        level_5_questions = [
            ('What is a "key performance indicator" (KPI) for evaluating UX design?',
             ["The number of lines of code written by the development team.",
              "The personal opinion of the CEO about the color scheme.",
              "A measurable value, like \"Task Success Rate\" or \"System Usability Scale\" (SUS) score.",
              "The total number of hours the design team worked on the project.",
              "The specific design software (e.g., Figma, Sketch) used by the team."],
             2, "UX KPIs are measurable values like Task Success Rate, SUS score, or NPS."),
            
            ('What is the "HEART" framework from Google?',
             ["A framework for measuring the user experience (Happiness, Engagement, Adoption, Retention, Task Success).",
              "A design principle for creating \"emotional\" and \"heartfelt\" designs.",
              "A coding framework for building user interfaces.",
              "A usability heuristic related to error messages.",
              "A method for stakeholder interviews."],
             0, "HEART measures UX through Happiness, Engagement, Adoption, Retention, and Task Success."),
            
            ('What is the strategic disadvantage of a "dark pattern"?',
             ["It can erode user trust and damage the brand's long-term reputation.",
              "It is difficult to code and implement for developers.",
              "It only works on users who are not paying attention.",
              "It is not visually appealing.",
              "It does not work on mobile devices."],
             0, "Dark patterns erode user trust and damage long-term brand reputation."),
            
            ('What is the strategic role of a "UX Designer" on an Agile/Scrum team?',
             ["To provide final, polished mockups before the first sprint begins.",
              "To work outside the development team and hand off designs.",
              "To work iteratively with the team, providing just-in-time research, flows, and designs.",
              "To act as the \"Scrum Master\" and manage the project timeline.",
              "To test the code after the developers have finished building it."],
             2, "UX designers work iteratively with Agile teams, providing just-in-time research and designs."),
            
            ('What is the "Double Diamond" model of design?',
             ["A model that describes a design process of diverging and converging twice (Discover, Define, Develop, Deliver).",
              "A visual design style that uses two diamond shapes in the logo.",
              "A usability test that is \"twice as hard\" as a normal test.",
              "A type of design system.",
              "A pricing model for design software."],
             0, "The Double Diamond describes four phases: Discover, Define, Develop, Deliver (diverge-converge twice)."),
            
            ('What is "ethical design"?',
             ["The practice of designing products that meet all legal requirements.",
              "The practice of designing products that are visually appealing and trendy.",
              "The practice of considering the user's well-being and avoiding harm (e.g., addiction, bias).",
              "The practice of designing products that are free to use.",
              "The practice of donating a portion of profits to charity."],
             2, "Ethical design considers user well-being and avoids harm like addiction, manipulation, or bias."),
            
            ('What is "inclusive design"?',
             ["A design that includes as many features as possible.",
              "A design that is intended for everyone and considers the full range of human diversity.",
              "A design that is \"accessible\" (this is a component, but not the full definition).",
              "A design that is \"all-inclusive\" and costs one single price.",
              "A design process that \"includes\" all stakeholders in every meeting."],
             1, "Inclusive design considers the full range of human diversity and is intended for everyone."),
            
            ('What is a "jobs-to-be-done" (JTBD) framework?',
             ["A framework that focuses on the \"job\" (the underlying goal) a user is trying to accomplish.",
              "A project management tool for assigning \"jobs\" to designers.",
              "A list of all the job openings on the design team.",
              "A framework for designing the \"Careers\" page of a website.",
              "A usability test to see if a user can find a \"job\" in the app."],
             0, "JTBD focuses on the underlying goal or 'job' users are trying to accomplish."),
            
            ('How does a "design system" provide business value?',
             ["It makes the product look more beautiful and trendy.",
              "It increases efficiency and consistency, allowing teams to build and ship products faster.",
              "It replaces the need for user research.",
              "It allows a company to fire all of its junior designers.",
              "It guarantees that a product will be successful."],
             1, "Design systems increase efficiency and consistency, enabling faster product development."),
            
            ('What is "design governance"?',
             ["The process of \"governing\" a country using design principles.",
              "The process of managing and standardizing a design system to ensure it is used correctly.",
              "A legal team that \"governs\" what a designer can and cannot do.",
              "A type of design thinking.",
              "A security policy for design files."],
             1, "Design governance manages and standardizes design systems to ensure correct usage."),
            
            ('What is the main strategic difference between a "product designer" and a "UX designer"?',
             ["A product designer is more senior than a UX designer.",
              "A product designer is often more involved in the business strategy and product lifecycle.",
              "A product designer only works on physical \"products.\"",
              "A UX designer only does research, while a product designer only does visuals.",
              "There is no difference; the titles are completely interchangeable."],
             1, "Product designers are typically more involved in business strategy and the full product lifecycle."),
            
            ('What is "UX writing"?',
             ["The practice of writing the code for a website.",
              "The practice of writing the marketing \"copy\" for advertisements.",
              "The practice of crafting the UI \"microcopy\" to guide the user (this is related, but not the full definition).",
              "The practice of writing user manuals and documentation.",
              "The strategic practice of crafting all text a user encounters in a product."],
             4, "UX writing strategically crafts all text users encounter in a product."),
            
            ('What is the "Aha!" moment in UX?',
             ["The moment a designer \"Aha!\" thinks of a new idea.",
              "The point in a usability test where the user says \"Aha!\"",
              "The moment a user first understands the core value of a product.",
              "The moment a stakeholder (e.g., the CEO) finally approves a design.",
              "An error message that appears when a user makes a mistake."],
             2, "The 'Aha!' moment is when users first understand and experience the core product value."),
            
            ('What is a "UX metric"?',
             ["A quantitative score (e.g., SUS, NPS) used to track and measure the user experience.",
              "A qualitative quote from a user interview.",
              "A design principle related to the \"metric\" system.",
              "The number of designers on a team.",
              "The specific font size (metric) used in a design."],
             0, "UX metrics are quantitative measures like SUS, NPS, task success rate, and time-on-task."),
            
            ('What is the "Net Promoter Score" (NPS)?',
             ["A metric that measures a user's satisfaction with a specific task.",
              "A metric that measures a user's willingness to recommend a product to others.",
              "A metric that measures how fast a user can complete a task.",
              "A metric that measures a website's \"net\" profit.",
              "A metric that measures how \"new\" a user is."],
             1, "NPS measures users' willingness to recommend a product to others."),
            
            ('What is a "UX strategy"?',
             ["A document that outlines all the design principles (e.g., Gestalt).",
              "A detailed plan for a single, two-week design sprint.",
              "A long-term plan that connects the user experience to the overall business goals.",
              "The \"strategy\" a user employs to complete a task in a usability test.",
              "A plan for hiring and managing the design team."],
             2, "UX strategy is a long-term plan connecting user experience to business goals."),
            
            ('What is the "Task Success Rate" (TSR)?',
             ["The percentage of users who \"successfully\" rate the app 5 stars.",
              "The percentage of users who correctly and completely achieve a specific goal in a usability test.",
              "The \"success\" of the design team in meeting their project deadline.",
              "The \"rate\" at which a developer can code a new feature.",
              "The percentage of users who find the design \"successful.\""],
             1, "TSR measures the percentage of users who correctly and completely achieve a specific goal."),
            
            ('Why is it dangerous to only listen to "vocal users"?',
             ["Because they are \"vocal\" and their voices are too loud.",
              "Because they represent the \"silent majority\" of users.",
              "Because they often represent the extremes (lovers or haters) and not the average user.",
              "Because they are usually competitors trying to steal your ideas.",
              "Because they only give positive feedback."],
             2, "Vocal users often represent extremes and not the average user experience."),
            
            ('What is a "UX roadmap"?',
             ["A visualization of a user's \"road\" or journey (this is a journey map).",
              "A strategic plan that outlines the timeline and priorities for UX projects and improvements.",
              "A sitemap that uses a \"road\" metaphor.",
              "A document that lists all the \"stops\" (pages) a user visits.",
              "A plan for the design team's company \"road trip.\""],
             1, "UX roadmaps outline timelines and priorities for UX projects and improvements."),
            
            ('What is "Service Design"?',
             ["The design of a single digital product, like a mobile app.",
              "The design of the entire experience of a service, including all digital touchpoints, physical locations, and staff interactions.",
              "The design of the \"customer service\" department's scripts.",
              "The design of the \"Terms of Service\" legal document.",
              "The design of a server's architecture."],
             1, "Service design encompasses all touchpoints: digital, physical, and human interactions."),
        ]
        
        quiz_5 = models.Quiz(
            title="UX/UI Design - Strategic & Architectural",
            description="Strategic UX: KPIs, HEART framework, ethical/inclusive design, JTBD, design governance, UX strategy, metrics (NPS, TSR), service design, business alignment",
            specialization_id=specialization.id,
            difficulty_level=5,
            time_limit_minutes=40
        )
        db.add(quiz_5)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_5_questions):
            question = models.Question(
                quiz_id=quiz_5.id,
                question_text=question_text,
                question_type='multiple_choice',
                explanation=explanation,
                order_index=idx
            )
            db.add(question)
            db.flush()
            
            for opt_idx, option_text in enumerate(options):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(opt_idx == correct_idx),
                    order_index=opt_idx
                )
                db.add(option)
        
        print(f"Added Level 5 (Strategic & Architectural): {len(level_5_questions)} questions")
        
        db.commit()
        print("\n✅ Successfully added UX/UI Design quizzes (Levels 4-5 complete!)")
        print(f"Total questions added: {len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_ux_ui_design_quizzes()
