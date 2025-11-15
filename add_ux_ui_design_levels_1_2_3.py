"""
Add UX/UI Design Quizzes - Levels 1, 2, and 3
This script adds 60 questions for UX/UI Design specialization
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
        
        # Delete existing quizzes for levels 1, 2, and 3
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == specialization.id,
            models.Quiz.difficulty_level.in_([1, 2, 3])
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
        print(f"Deleted {len(existing_quizzes)} existing quizzes for levels 1-3")
        
        # Level 1: Basic Foundations (20 questions)
        level_1_questions = [
            ('What is the primary focus of "UX Design" (User Experience)?',
             ["It focuses on the visual look, such as colors and fonts, of an application.",
              "It focuses on the overall experience a user has with a product, including usability.",
              "It focuses on coding the frontend of the website using HTML and CSS.",
              "It focuses on writing the marketing copy and text for the application.",
              "It focuses on managing the server and database for the application."],
             1, "UX Design focuses on the overall user experience, including usability, accessibility, and satisfaction."),
            
            ('What is the primary focus of "UI Design" (User Interface)?',
             ["It focuses on the user's emotional journey and psychological experience.",
              "It focuses on the visual layout and graphical elements, like buttons and menus.",
              "It focuses on the backend server logic and database connections.",
              "It focuses on conducting user interviews and analyzing research data.",
              "It focuses on the information architecture and content hierarchy."],
             1, "UI Design focuses on the visual and interactive elements like buttons, menus, and layouts."),
            
            ('What is a "wireframe"?',
             ["A high-fidelity, full-color visual design of the final product.",
              "A basic, low-fidelity visual guide that represents the skeletal framework of a website.",
              "A piece of code that makes the website interactive for users.",
              "A final, clickable simulation of the application used for testing.",
              "A document containing all the text and copy for the application."],
             1, "Wireframes are low-fidelity sketches showing the basic structure and layout of a design."),
            
            ('What is a "prototype"?',
             ["A document that lists all the features for a future product.",
              "A final, coded version of the application that is ready to be sold.",
              "A simulation or sample version of a product used to test concepts or user flows.",
              "A low-fidelity sketch of the basic layout, often done on paper.",
              "A marketing plan for how the product will be launched."],
             2, "Prototypes are interactive simulations used to test concepts and user flows before development."),
            
            ('What is "usability"?',
             ["The measure of how visually attractive and appealing a design is.",
              "The measure of how easy a product is to use for its intended purpose.",
              "The number of features a product has.",
              "The total number of users who access the product each day.",
              "The process of coding the final application."],
             1, "Usability measures how easy and efficient a product is for users to accomplish their goals."),
            
            ('What is a "User Flow"?',
             ["A diagram showing the path a user takes through an application to complete a task.",
              "A type of animation that shows how a user \"flows\" from one screen to the next.",
              "A database table that lists all of the users of an application.",
              "A research method where a user describes their experience.",
              "A list of all the features a user has requested."],
             0, "User flows map the steps a user takes to complete tasks within an application."),
            
            ('What is a "mockup"?',
             ["A low-fidelity, basic layout sketch of a product.",
              "A high-fidelity, static, full-color design that represents the final product's look.",
              "A clickable, interactive simulation used for user testing.",
              "A piece of code that mocks the behavior of a backend server.",
              "A document containing user research and interview notes."],
             1, "Mockups are high-fidelity static designs showing the final visual appearance."),
            
            ('What is a "font"?',
             ["A set of printable or displayable text characters in a specific style (e.g., Arial, Times New Roman).",
              "The main title or heading on a webpage.",
              "A small, graphical icon used in a user interface.",
              "The color of the text in an application.",
              "A type of layout grid used in web design."],
             0, "Fonts are typeface styles that define the appearance of text characters."),
            
            ('What is a "color palette"?',
             ["The collection of all images and icons used in an application.",
              "The specific set of colors chosen for use in a brand or product's design.",
              "A design principle related to the spacing of elements.",
              "A document that describes the user's emotional state.",
              "The physical tool artists use to mix paints."],
             1, "Color palettes are curated sets of colors used consistently throughout a design."),
            
            ('What is a "button" in UI design?',
             ["An interactive element that a user clicks to perform an action.",
              "A static piece of text used for a title or heading.",
              "An image or photograph displayed on the page.",
              "A link that takes the user to a completely different website.",
              "A wireframe that shows the layout of a page."],
             0, "Buttons are interactive UI elements that trigger actions when clicked."),
            
            ('What is "Figma"?',
             ["A popular, collaborative interface design tool that runs in a browser.",
              "A programming language used to code websites.",
              "A type of database for storing user data.",
              "A project management tool for tracking tasks.",
              "A service for hosting live websites."],
             0, "Figma is a collaborative, browser-based design tool for creating interfaces and prototypes."),
            
            ('What is "Sketch"?',
             ["A database management system for designers.",
              "A project management tool for tracking tasks.",
              "A popular vector graphics editor for UI design, used primarily on macOS.",
              "A service for conducting user research and interviews.",
              "A framework for coding interactive prototypes."],
             2, "Sketch is a macOS vector design tool widely used for UI/UX design."),
            
            ('What is "Adobe XD"?',
             ["A tool for writing and editing website code.",
              "A vector-based design tool for web and mobile apps, part of the Adobe suite.",
              "A service for hosting and managing web servers.",
              "A tool for editing videos and adding special effects.",
              "A spreadsheet program for organizing design components."],
             1, "Adobe XD is a vector design and prototyping tool for web and mobile interfaces."),
            
            ('What is a "grid system" in UI design?',
             ["A set of invisible lines used to structure content and create a consistent layout.",
              "A security feature that locks users out of the system.",
              "A chart or graph used to display data.",
              "A list of all the pages in a website.",
              "A tool for testing the speed of an application."],
             0, "Grid systems provide structure and consistency through invisible alignment guides."),
            
            ('What is "white space" (or negative space)?',
             ["The parts of a design that are colored white.",
              "The empty, unmarked space between elements in a design, used to create breathing room.",
              "A type of error message that appears when a page is blank.",
              "A document used for writing down ideas.",
              "A specific font that is difficult to read."],
             1, "White space (negative space) is empty space that improves readability and visual hierarchy."),
            
            ('What is "responsive design"?',
             ["A design that responds to user clicks with fast animations.",
              "A design that learns and adapts to a user's personal preferences.",
              "A design approach that allows a layout to adapt to different screen sizes (e.g., desktop, mobile).",
              "A design that includes a chatbot to respond to user questions.",
              "A design that is visually very bright and colorful."],
             2, "Responsive design adapts layouts to work across different screen sizes and devices."),
            
            ('What is an "icon"?',
             ["A large, high-resolution photograph used as a background.",
              "A block of text that explains a feature.",
              "A small, simple graphic symbol used to represent an object, action, or idea.",
              "The main logo of a company.",
              "A clickable, interactive prototype of an application."],
             2, "Icons are small graphic symbols representing actions, objects, or concepts."),
            
            ('What is "typography"?',
             ["The art and technique of arranging type (text) to make it legible and appealing.",
              "The process of creating a high-fidelity mockup.",
              "The study of how users type on a keyboard.",
              "A type of user research method.",
              "A list of all the colors used in a design."],
             0, "Typography is the art of arranging text for readability and visual appeal."),
            
            ('What is "contrast" in UI design?',
             ["The difference between visual elements (e.g., light vs. dark) used to create emphasis.",
              "A design that is intentionally confusing and difficult to use.",
              "The process of comparing two different design mockups.",
              "A specific font style that is very thin.",
              "The total number of colors used in a design palette."],
             0, "Contrast uses visual differences (light/dark, size, color) to create emphasis and hierarchy."),
            
            ('What is "alignment"?',
             ["The process of making a design \"agree\" with the company's brand.",
              "The placement of visual elements so they line up along a common edge or center.",
              "A user's personal preference for a specific layout.",
              "A type of grid system used for mobile devices only.",
              "The process of getting all stakeholders to agree on a design."],
             1, "Alignment creates visual order by lining up elements along common edges or centers."),
        ]
        
        quiz_1 = models.Quiz(
            title="UX/UI Design - Basic Foundations",
            description="Design fundamentals: UX vs UI, wireframes, prototypes, usability, user flows, mockups, tools (Figma, Sketch, XD), typography, and design principles",
            specialization_id=specialization.id,
            difficulty_level=1,
            time_limit_minutes=25
        )
        db.add(quiz_1)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_1_questions):
            question = models.Question(
                quiz_id=quiz_1.id,
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
        
        print(f"Added Level 1 (Basic Foundations): {len(level_1_questions)} questions")
        
        # Level 2: Intermediate Application (20 questions)
        level_2_questions = [
            ("What is the primary goal of a usability test?",
             ["To determine if the visual design is aesthetically pleasing to users.",
              "To identify potential problems in a design by observing real users.",
              "To ask users what new features they would like to have in the product.",
              "To test if the website's backend server can handle a high load of traffic.",
              "To see if the user likes the brand's logo and color scheme."],
             1, "Usability tests observe real users to identify design problems and usability issues."),
            
            ('What is "visual hierarchy"?',
             ["The arrangement of elements to imply importance, guiding the user's eye.",
              "The list of all pages on a website, organized by section.",
              "The company's organizational chart for the design team.",
              "The specific font and color choices used in the application.",
              "The process of making a design look symmetrical and balanced."],
             0, "Visual hierarchy arranges elements to guide users' attention and indicate importance."),
            
            ("What is the main difference between a wireframe and a mockup?",
             ["A wireframe is interactive; a mockup is a static image.",
              "A wireframe focuses on layout (low-fidelity); a mockup focuses on visuals (high-fidelity).",
              "A wireframe is for mobile; a mockup is for desktop.",
              "A wireframe is built with code; a mockup is built in Figma.",
              "A wireframe is a final design; a mockup is just a basic sketch."],
             1, "Wireframes are low-fidelity layouts; mockups are high-fidelity visual designs."),
            
            ('What is a "user story"?',
             ["A short, simple description of a feature from the perspective of the user.",
              "A long, detailed biography of a target user (this is a persona).",
              "A review or testimonial from a real customer.",
              "A diagram showing the user's path (this is a user flow).",
              "A list of all the steps in a usability test."],
             0, "User stories describe features from the user's perspective (e.g., 'As a user, I want to...')."),
            
            ('What is "Fitt\'s Law"?',
             ["A design principle stating that colors should be bright and appealing.",
              "A design principle stating that a target (e.g., a button) should be large enough for users to click.",
              "A design principle stating that users prefer simple designs.",
              "A design principle stating that a user's \"fit\" with a product determines satisfaction.",
              "A design principle related to website loading speed."],
             1, "Fitts's Law states that larger, closer targets are faster and easier to click."),
            
            ('What is "Hick\'s Law"?',
             ["A principle stating that the time it takes to make a decision increases with the number of choices.",
              "A principle stating that users prefer designs they have seen before.",
              "A principle stating that a user's \"hiccups\" (errors) should be minimized.",
              "A principle stating that text should always be left-aligned.",
              "A principle stating that icons should always have text labels."],
             0, "Hick's Law states that more choices increase decision time."),
            
            ('What is the primary purpose of "user research"?',
             ["To create aesthetically pleasing visual designs.",
              "To understand user behaviors, needs, and motivations to inform design decisions.",
              "To test the website's code for bugs and errors.",
              "To build the final, high-fidelity mockups of an application.",
              "To decide which features the stakeholders want in the product."],
             1, "User research uncovers user needs, behaviors, and motivations to guide design."),
            
            ('What is a "heuristic evaluation"?',
             ["A method where a user tries to complete tasks on a prototype.",
              "A method where an expert inspects a design against a list of usability principles.",
              "A method where designers brainstorm new feature ideas.",
              "A final check of the code before a product is launched.",
              "A survey sent to users to gauge their overall satisfaction."],
             1, "Heuristic evaluation has experts review designs against established usability principles."),
            
            ('What is "accessibility" (a11y) in design?',
             ["The practice of making a design available on both mobile and desktop.",
              "The practice of making a design usable by people with disabilities.",
              "The practice of making a design \"accessible\" to a global audience with translation.",
              "The practice of ensuring a design is affordable for all users.",
              "The practice of making sure a website is easy to find on Google."],
             1, "Accessibility ensures designs are usable by people with disabilities."),
            
            ('What is a "call to action" (CTA)?',
             ["A prominent button or link designed to prompt the user to take a specific action.",
              "A phone number for the user to call for customer support.",
              "A notification that alerts the user to a new message.",
              "The main heading or title of a webpage.",
              "A user story that describes a specific action."],
             0, "CTAs are prominent elements (buttons/links) prompting users to take specific actions."),
            
            ('What is "information architecture" (IA)?',
             ["The practice of designing the server and database architecture.",
              "The structural design of shared information, organizing content so users can find it.",
              "The visual design of the user interface.",
              "The process of writing the code for a website.",
              "A document that lists all the information a user needs."],
             1, "Information architecture organizes and structures content for easy navigation and findability."),
            
            ('What is "kerning"?',
             ["The adjustment of space between individual characters in a piece of text.",
              "The adjustment of space between lines of text (this is leading).",
              "A specific type of font that is very bold.",
              "The process of choosing a color palette.",
              "A usability principle related to error messages."],
             0, "Kerning adjusts spacing between individual letter pairs for better readability."),
            
            ('What is "leading" (or line-height)?',
             ["The adjustment of space between individual characters.",
              "The main, \"leading\" piece of text on a page.",
              "The adjustment of space between lines of text.",
              "The line that \"leads\" a user's eye, created by alignment.",
              "The first item in a navigation menu."],
             2, "Leading (line-height) controls the vertical spacing between lines of text."),
            
            ('What is a "sitemap"?',
             ["A diagram showing the hierarchical structure of all pages in a website.",
              "A map showing the physical location of the company's data centers.",
              "A low-fidelity wireframe of the homepage.",
              "A visual design of a map interface, like Google Maps.",
              "A user flow that shows a user's path to a specific page."],
             0, "Sitemaps diagram the hierarchical structure and organization of website pages."),
            
            ('What is a "style guide"?',
             ["A document that outlines all the user personas and their stories.",
              "A document that defines the visual design standards (colors, fonts, etc.) for a brand.",
              "A clickable, high-fidelity prototype of an application.",
              "A user manual that guides a person on how to use the product.",
              "A list of all the pages in a sitemap."],
             1, "Style guides document visual standards like colors, fonts, and design patterns."),
            
            ('What is a "breadcrumb"?',
             ["A navigation aid that shows the user's current location in the site's hierarchy.",
              "A type of notification that appears briefly at the bottom of the screen.",
              "A user research method for tracking a user's \"trail.\"",
              "A small, unimportant feature in an application.",
              "A usability heuristic related to finding food-related content."],
             0, "Breadcrumbs show users their current location within the site hierarchy."),
            
            ('What is a "modal" (or modal dialog)?',
             ["A full-screen page that replaces the current page.",
              "A UI element that appears on top of the main content, disabling it until the user interacts.",
              "A type of navigation menu that slides in from the side.",
              "A notification that appears at the bottom of the screen.",
              "A wireframe that shows the \"mode\" of the user."],
             1, "Modals overlay main content, requiring user interaction before proceeding."),
            
            ('What is "affinity mapping"?',
             ["A research method for grouping and finding patterns in qualitative data (e.g., from interviews).",
              "A design technique for creating visually \"affiliated\" or similar elements.",
              "A UI layout where elements are arranged based on their \"affinity\" to each other.",
              "A way to map out a user flow based on their emotions.",
              "A test to see how much \"affinity\" a user has for a brand."],
             0, "Affinity mapping groups qualitative data to identify patterns and insights."),
            
            ('What is a "card" in UI design?',
             ["A UI component that groups related information in a flexible, box-like container.",
              "A modal dialog that appears on top of the content.",
              "A research method (this is \"card sorting\").",
              "A type of payment form for a credit card.",
              "A wireframe of a single screen."],
             0, "Cards are UI containers grouping related content in a flexible, modular format."),
            
            ('What is "empathy" in UX design?',
             ["The ability to understand and share the feelings of the user.",
              "A specific visual style that is soft and inviting.",
              "A set of usability heuristics.",
              "The process of agreeing with all of a user's feature requests.",
              "A type of user interface animation."],
             0, "Empathy means understanding and sharing users' feelings to design better experiences."),
        ]
        
        quiz_2 = models.Quiz(
            title="UX/UI Design - Intermediate Application",
            description="Design practice: usability testing, visual hierarchy, user stories, Fitts's/Hick's Law, research, accessibility, IA, typography, style guides, and empathy",
            specialization_id=specialization.id,
            difficulty_level=2,
            time_limit_minutes=30
        )
        db.add(quiz_2)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_2_questions):
            question = models.Question(
                quiz_id=quiz_2.id,
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
        
        print(f"Added Level 2 (Intermediate Application): {len(level_2_questions)} questions")
        
        # Level 3: Advanced Scenarios (20 questions)
        level_3_questions = [
            ('What is a "user-centered design" (UCD) process?',
             ["A design process that focuses on the business goals and stakeholder opinions.",
              "A design process that focuses on the visual aesthetics and brand identity.",
              "A design process that focuses on the user's needs and feedback at every stage.",
              "A design process that is led by the engineering team's technical constraints.",
              "A design process that copies the features of competitors."],
             2, "User-centered design prioritizes user needs and feedback throughout the design process."),
            
            ('What is a "user persona"?',
             ["A real-time log of a user's clicks and interactions on a live website.",
              "A fictional, composite character created to represent a key user type.",
              "A short biography of a stakeholder or member of the design team.",
              "A list of all the features a user has requested for the product.",
              "The final, high-fidelity mockup of the user's profile page."],
             1, "User personas are fictional characters representing key user types and their goals."),
            
            ('What is the main difference between "qualitative" and "quantitative" research?',
             ["Qualitative is numbers (e.g., surveys); Quantitative is \"why\" (e.g., interviews).",
              "Qualitative is \"why\" (e.g., interviews); Quantitative is numbers (e.g., analytics).",
              "Qualitative is for testing prototypes; Quantitative is for testing wireframes.",
              "Qualitative is fast and cheap; Quantitative is slow and expensive.",
              "Qualitative is for UI; Quantitative is for UX."],
             1, "Qualitative research explores 'why' (interviews); quantitative provides numerical data (metrics)."),
            
            ('What are "Jakob\'s Ten Usability Heuristics"?',
             ["A set of strict, inflexible rules that must be followed for all UI design.",
              "A list of ten popular design trends that are updated each year.",
              "A checklist of ten key features that every successful application must have.",
              "A set of broad, guiding principles for usable interface design.",
              "A list of ten common user types (personas) for software."],
             3, "Jakob Nielsen's heuristics are ten broad usability principles for interface design."),
            
            ('What is "WCAG"?',
             ["\"Web Content Accessibility Guidelines,\" a global standard for web accessibility.",
              "\"Website Color and Graphics,\" a set of rules for visual design.",
              "\"World Class Animation Group,\" a community for designers.",
              "\"Wireframe and Component Assembly,\" a design methodology.",
              "\"Web Coding and Grids,\" a framework for developers."],
             0, "WCAG (Web Content Accessibility Guidelines) are international accessibility standards."),
            
            ('What is an example of a "WCAG" guideline?',
             ["All text must be a specific font, like Arial.",
              "All websites must have a dark mode.",
              "All images must have alternative text (\"alt text\").",
              "All websites must load in under 3 seconds.",
              "All buttons must be circular."],
             2, "WCAG requires alt text for images to make content accessible to screen readers."),
            
            ('What is a "design system"?',
             ["A single Sketch or Figma file that contains all of the design mockups.",
              "A collection of reusable components, guided by standards, to build products.",
              "A software program used for creating wireframes and prototypes.",
              "The process of testing a design with users (usability testing).",
              "A document outlining the information architecture of a website."],
             1, "Design systems provide reusable components and standards for consistent product design."),
            
            ('What is "Atomic Design"?',
             ["A methodology for creating design systems by breaking UIs into \"atoms,\" \"molecules,\" \"organisms,\" etc.",
              "A design style that uses very small, \"atomic\" text and icons.",
              "A type of user research that breaks down a user's needs.",
              "A coding framework for building websites.",
              "A way to design for nuclear power plant interfaces."],
             0, "Atomic Design builds design systems from small components (atoms) to larger patterns (organisms)."),
            
            ('What is a "user journey map"?',
             ["A diagram showing the path a user takes to complete a task (this is a user flow).",
              "A visualization of a user's steps, feelings, and pain points throughout their interaction with a product.",
              "A sitemap that is personalized for a specific user.",
              "A high-fidelity mockup of the \"travel\" or \"maps\" section of an app.",
              "A list of all the features a user \"journeys\" through."],
             1, "User journey maps visualize the user's experience, including emotions and pain points."),
            
            ('What is "card sorting"?',
             ["A research method where users organize topics into groups to help create an information architecture.",
              "A design technique for laying out content in \"cards\" on a UI.",
              "A brainstorming method where designers write ideas on cards.",
              "A usability test where users are asked to find a \"card\" in the design.",
              "A project management tool for organizing design tasks."],
             0, "Card sorting helps create information architecture by having users group content."),
            
            ('What is the difference between "Open" and "Closed" card sorting?',
             ["\"Open\" is done online; \"Closed\" is done in person.",
              "\"Open\" lets users create their own category names; \"Closed\" uses predefined category names.",
              "\"Open\" is for stakeholders; \"Closed\" is for real users.",
              "\"Open\" is for websites; \"Closed\" is for mobile apps.",
              "\"Open\" has no limit on cards; \"Closed\" has a strict limit."],
             1, "Open card sorting lets users create categories; closed uses predefined categories."),
            
            ('What is a "heuristic" (as in "heuristic evaluation")?',
             ["A strict, unbreakable rule.",
              "A broad, experience-based \"rule of thumb\" or guideline.",
              "A type of error message.",
              "A new feature request.",
              "A specific visual design style."],
             1, "Heuristics are experience-based guidelines or rules of thumb, not strict rules."),
            
            ('What is the "Gestalt" principle of "Proximity"?',
             ["Objects that are close together are perceived as a group.",
              "Objects that look similar are perceived as a group.",
              "The human eye tends to follow the simplest path.",
              "The mind tends to see incomplete shapes as complete.",
              "An object in the foreground is seen as more important."],
             0, "Proximity: elements close together are perceived as related or grouped."),
            
            ('What is the "Gestalt" principle of "Similarity"?',
             ["Objects that are close together are perceived as a group.",
              "Objects that look similar (e.g., in color or shape) are perceived as a group.",
              "The human eye prefers \"similar\" or symmetrical designs.",
              "The mind tends to see incomplete shapes as complete.",
              "An object's importance is similar to its size."],
             1, "Similarity: elements that look alike are perceived as related or grouped."),
            
            ('What is "gamification"?',
             ["The process of designing a video game.",
              "The process of testing a design to see if it is \"game\" for launch.",
              "The application of game-like elements (e.g., points, badges) to a non-game product.",
              "A usability test where users \"play a game\" with the prototype.",
              "A design style that looks like a video game."],
             2, "Gamification applies game mechanics (points, badges, levels) to non-game contexts."),
            
            ('What is a "dark pattern"?',
             ["A UI design that uses a \"dark mode\" or dark color scheme.",
              "A UI pattern that is intentionally deceptive and tricks a user into an unintended action.",
              "A design that has not been finished or is still in the \"dark.\"",
              "A wireframe that has not been approved by stakeholders.",
              "A design that is hidden from most users."],
             1, "Dark patterns are deceptive UI designs that trick users into unintended actions."),
            
            ('What is "A/B testing"?',
             ["To ask users which design (A or B) they find more visually appealing.",
              "To test two versions of a design to see which one performs better on a specific metric.",
              "To test the \"accessibility\" and \"bugs\" (A and B) in a design.",
              "To allow users to choose between two different layouts (A or B) in their settings.",
              "To see if the \"A\" team of designers is better than the \"B\" team."],
             1, "A/B testing compares two design versions to determine which performs better."),
            
            ('What is "interaction design" (IxD)?',
             ["The practice of designing the social \"interactions\" between users.",
              "The practice of designing the interactive elements and behaviors of a product (e.g., animations, transitions).",
              "The practice of designing the database and server.",
              "The practice of designing the company's \"interaction\" with its customers.",
              "The practice of interviewing users."],
             1, "Interaction design focuses on interactive behaviors like animations, transitions, and feedback."),
            
            ('What is "mobile-first" design?',
             ["A strategy of designing the mobile version of a product before the desktop version.",
              "A strategy of designing only for mobile phones and not for desktops.",
              "A design style that looks like a mobile app, even on desktop.",
              "A business strategy to only sell mobile phones.",
              "A coding framework for building mobile apps."],
             0, "Mobile-first design starts with mobile layouts, then expands to larger screens."),
            
            ('What is a "hamburger menu"?',
             ["A navigation menu used for restaurant or food-delivery apps.",
              "A UI component that shows a list of different types of hamburgers.",
              "An icon (three stacked lines) that reveals a navigation menu when clicked.",
              "A \"dark pattern\" that tricks a user into ordering food.",
              "A full-screen menu that is always visible on the page."],
             2, "Hamburger menus use a three-line icon that expands to show navigation options."),
        ]
        
        quiz_3 = models.Quiz(
            title="UX/UI Design - Advanced Scenarios",
            description="Advanced design: UCD, personas, research types, Jakob's heuristics, WCAG, design systems, Atomic Design, journey maps, Gestalt principles, A/B testing, IxD",
            specialization_id=specialization.id,
            difficulty_level=3,
            time_limit_minutes=35
        )
        db.add(quiz_3)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_3_questions):
            question = models.Question(
                quiz_id=quiz_3.id,
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
        
        print(f"Added Level 3 (Advanced Scenarios): {len(level_3_questions)} questions")
        
        db.commit()
        print("\n✅ Successfully added UX/UI Design quizzes (Levels 1-3 complete!)")
        print(f"Total questions added: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_ux_ui_design_quizzes()
