#!/usr/bin/env python3
"""
Add comprehensive Frontend Development quizzes to the database
Organized by difficulty levels 1-5
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_frontend_quizzes():
    """Add all Frontend Development quizzes"""
    db = SessionLocal()
    
    try:
        # Get Frontend Development specialization (ID should be 1)
        frontend_spec = db.query(models.Specialization).filter(
            models.Specialization.name == "Frontend Development"
        ).first()
        
        if not frontend_spec:
            print("❌ Frontend Development specialization not found!")
            return
        
        print(f"✅ Found Frontend Development specialization (ID: {frontend_spec.id})")
        
        # Delete existing Frontend Development quizzes to avoid duplicates
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == frontend_spec.id
        ).all()
        
        if existing_quizzes:
            print(f"🗑️  Deleting {len(existing_quizzes)} existing Frontend Development quizzes...")
            for quiz in existing_quizzes:
                # Delete quiz attempts first
                db.query(models.QuizAttempt).filter(
                    models.QuizAttempt.quiz_id == quiz.id
                ).delete()
                # Delete associated questions and options
                for question in quiz.questions:
                    db.query(models.QuestionOption).filter(
                        models.QuestionOption.question_id == question.id
                    ).delete()
                db.query(models.Question).filter(
                    models.Question.quiz_id == quiz.id
                ).delete()
            db.query(models.Quiz).filter(
                models.Quiz.specialization_id == frontend_spec.id
            ).delete()
            db.commit()
        
        # Level 1: HTML, CSS, JavaScript Basics (20 questions)
        print("\n📝 Adding Level 1: Frontend Development Basics...")
        quiz_level_1 = models.Quiz(
            title="Frontend Development Basics - Level 1",
            description="Fundamental concepts of frontend development including HTML, CSS, and JavaScript basics",
            specialization_id=frontend_spec.id,
            difficulty_level=1,
            is_active=True,
            time_limit_minutes=30,
            passing_score=70.0
        )
        db.add(quiz_level_1)
        db.commit()
        db.refresh(quiz_level_1)
        
        level_1_questions = [
            {
                "text": "What does HTML stand for?",
                "options": [
                    ("HyperText Markup Language", True),
                    ("HighText Machine Language", False),
                    ("HyperText and Links Markup", False),
                    ("HyperTool Multi-Language", False),
                    ("Home Tool Markup Language", False)
                ]
            },
            {
                "text": "What is the primary purpose of CSS?",
                "options": [
                    ("To add interactivity and behavior to a website.", False),
                    ("To define the structure and content of a web page.", False),
                    ("To style the visual presentation of a web page.", True),
                    ("To manage server-side operations and databases.", False),
                    ("To optimize the website for search engines.", False)
                ]
            },
            {
                "text": "Which programming language is primarily used to add behavior and interactivity to websites?",
                "options": [
                    ("HTML", False),
                    ("CSS", False),
                    ("Python", False),
                    ("JavaScript", True),
                    ("SQL", False)
                ]
            },
            {
                "text": "Which HTML tag is used to create a hyperlink (a clickable link)?",
                "options": [
                    ("<link>", False),
                    ("<a>", True),
                    ("<href>", False),
                    ("<p>", False),
                    ("<ul>", False)
                ]
            },
            {
                "text": "In CSS, how would you select all elements with a class name of 'highlight'?",
                "options": [
                    ("#highlight", False),
                    ("highlight", False),
                    (".highlight", True),
                    ("*highlight", False),
                    ("<highlight>", False)
                ]
            },
            {
                "text": "Which HTML tag is used to define the main content of an HTML document (the part visible to the user)?",
                "options": [
                    ("<head>", False),
                    ("<body>", True),
                    ("<html>", False),
                    ("<title>", False),
                    ("<content>", False)
                ]
            },
            {
                "text": "What CSS property is used to change the text color of an element?",
                "options": [
                    ("text-color", False),
                    ("font-color", False),
                    ("background-color", False),
                    ("color", True),
                    ("text-style", False)
                ]
            },
            {
                "text": "What is the purpose of the alt attribute on an <img> tag?",
                "options": [
                    ("To set the alignment of the image.", False),
                    ("To provide alternative text if the image cannot be displayed.", True),
                    ("To link the image to another URL.", False),
                    ("To set the title of the image, which appears on hover.", False),
                    ("To define the source URL of the image.", False)
                ]
            },
            {
                "text": "In JavaScript, what keyword is used to declare a variable that cannot be reassigned?",
                "options": [
                    ("var", False),
                    ("let", False),
                    ("const", True),
                    ("static", False),
                    ("final", False)
                ]
            },
            {
                "text": "Which of these is NOT a core component of the CSS Box Model?",
                "options": [
                    ("Margin", False),
                    ("Border", False),
                    ("Padding", False),
                    ("Content", False),
                    ("Display", True)
                ]
            },
            {
                "text": "What does a <!DOCTYPE html> declaration do?",
                "options": [
                    ("It comments out the entire HTML document.", False),
                    ("It tells the browser that the document is an HTML5 page.", True),
                    ("It links a JavaScript file to the document.", False),
                    ("It creates the main heading for the page.", False),
                    ("It is an old, optional tag that is no longer used.", False)
                ]
            },
            {
                "text": "Which HTML tag is considered 'semantic,' meaning it describes its content's meaning?",
                "options": [
                    ("<div>", False),
                    ("<span>", False),
                    ("<article>", True),
                    ("<b>", False),
                    ("<i>", False)
                ]
            },
            {
                "text": "How do you add an inline comment in JavaScript?",
                "options": [
                    ("<!-- comment -->", False),
                    ("/* This is a comment */", False),
                    ("// This is a comment", True),
                    ("# This is a comment", False),
                    ("' This is a comment", False)
                ]
            },
            {
                "text": "What is the term for designing a website to look good on all devices, from desktops to mobile phones?",
                "options": [
                    ("Responsive Design", True),
                    ("Fixed Design", False),
                    ("Adaptive Design", False),
                    ("Fluid Design", False),
                    ("Mobile-First Design", False)
                ]
            },
            {
                "text": "Which CSS property controls the spacing inside an element's border?",
                "options": [
                    ("margin", False),
                    ("border-spacing", False),
                    ("spacing", False),
                    ("padding", True),
                    ("outline", False)
                ]
            },
            {
                "text": "In CSS, which selector has the highest specificity (priority)?",
                "options": [
                    ("An ID selector (e.g., #my-id)", True),
                    ("A class selector (e.g., .my-class)", False),
                    ("An element selector (e.g., p)", False),
                    ("A universal selector (e.g., *)", False),
                    ("An attribute selector (e.g., [type='text'])", False)
                ]
            },
            {
                "text": "What is the correct HTML tag for the largest heading?",
                "options": [
                    ("<h6>", False),
                    ("<heading>", False),
                    ("<head>", False),
                    ("<h1>", True),
                    ("<main>", False)
                ]
            },
            {
                "text": "What is the 'DOM' in the context of frontend development?",
                "options": [
                    ("Digital Object Model", False),
                    ("Data Object Model", False),
                    ("Document Object Model", True),
                    ("Dynamic Object Manipulation", False),
                    ("Domain Object Mainframe", False)
                ]
            },
            {
                "text": "Which HTML tag is used to create an unordered list (i.e., a bulleted list)?",
                "options": [
                    ("<ol>", False),
                    ("<ul>", True),
                    ("<li>", False),
                    ("<list>", False),
                    ("<dl>", False)
                ]
            },
            {
                "text": "What is the correct way to link an external CSS stylesheet in an HTML file?",
                "options": [
                    ("Inside the <body> with <style src='style.css'>", False),
                    ("Inside the <head> with <link rel='stylesheet' href='style.css'>", True),
                    ("Inside the <head> with <script src='style.css'>", False),
                    ("Inside the <body> with <link rel='stylesheet' href='style.css'>", False),
                    ("Inside the <head> with <style link='style.css'>", False)
                ]
            }
        ]
        
        add_questions(db, quiz_level_1.id, level_1_questions)
        print(f"✅ Added {len(level_1_questions)} questions for Level 1")
        
        # Level 2: Intermediate (20 questions)
        print("\n📝 Adding Level 2: Frontend Development Intermediate...")
        quiz_level_2 = models.Quiz(
            title="Frontend Development Intermediate - Level 2",
            description="Intermediate frontend concepts including DOM manipulation, events, and JavaScript fundamentals",
            specialization_id=frontend_spec.id,
            difficulty_level=2,
            is_active=True,
            time_limit_minutes=40,
            passing_score=70.0
        )
        db.add(quiz_level_2)
        db.commit()
        db.refresh(quiz_level_2)
        
        level_2_questions = [
            {
                "text": "What is the practical difference between == and === in JavaScript?",
                "options": [
                    ("== compares for value only, while === compares for both value and type.", True),
                    ("== is for numbers and === is for strings.", False),
                    ("== assigns a value, while === compares a value.", False),
                    ("== is the old way and === is the new, faster way.", False),
                    ("There is no practical difference; they do the same thing.", False)
                ]
            },
            {
                "text": "How would you select an element with the ID main-title using JavaScript?",
                "options": [
                    ("document.querySelector('.main-title')", False),
                    ("document.getElementByClass('main-title')", False),
                    ("document.getElementById('main-title')", True),
                    ("document.querySelector('main-title')", False),
                    ("document.getElement('main-title')", False)
                ]
            },
            {
                "text": "What does the CSS property box-sizing: border-box; do?",
                "options": [
                    ("It makes the border and padding part of the element's total width and height.", True),
                    ("It adds a border around the element's margin.", False),
                    ("It automatically calculates the width and height based on the content.", False),
                    ("It centers the element vertically and horizontally.", False),
                    ("It removes all padding and margin from the element.", False)
                ]
            },
            {
                "text": "Which CSS selector would target only the <p> elements that are direct children of a <div>?",
                "options": [
                    ("div p", False),
                    ("div > p", True),
                    ("div + p", False),
                    ("div.p", False),
                    ("div ~ p", False)
                ]
            },
            {
                "text": "How do you add a 'click' event listener to a button with the ID btn in JavaScript?",
                "options": [
                    ("btn.onClick = function() { ... }", False),
                    ("const btn = document.getElementById('btn'); btn.addEventListener('click', functionName);", True),
                    ("const btn = document.getElementById('btn'); btn.listen('click', functionName);", False),
                    ("<button id='btn' onclick='functionName()'>Click</button>", False),
                    ("const btn = document.querySelector('btn'); btn.addEvent('click', functionName);", False)
                ]
            },
            {
                "text": "What is the difference between display: block; and display: inline; in CSS?",
                "options": [
                    ("block elements are for text, and inline elements are for images.", False),
                    ("block elements start on a new line and take up the full available width, while inline elements do not.", True),
                    ("block elements can have margin, but inline elements cannot.", False),
                    ("block elements cannot be nested, while inline elements can.", False),
                    ("block elements are static, while inline elements can be moved with position.", False)
                ]
            },
            {
                "text": "Given the JavaScript const fruit = ['Apple', 'Banana', 'Cherry'];, how would you access 'Banana'?",
                "options": [
                    ("fruit(1)", False),
                    ("fruit.1", False),
                    ("fruit[1]", True),
                    ("fruit[2]", False),
                    ("fruit.get(1)", False)
                ]
            },
            {
                "text": "What is the purpose of the method attribute on an HTML <form> tag?",
                "options": [
                    ("It specifies the URL where the form data will be sent.", False),
                    ("It defines the JavaScript function to run on submission.", False),
                    ("It specifies the HTTP method (e.g., GET or POST) to use when submitting the form.", True),
                    ("It defines which input fields are required.", False),
                    ("It sets the visual styling and layout of the form.", False)
                ]
            },
            {
                "text": "Which CSS property would you use to create space outside an element's border?",
                "options": [
                    ("padding", False),
                    ("margin", True),
                    ("border-spacing", False),
                    ("outline", False),
                    ("box-shadow", False)
                ]
            },
            {
                "text": "What will this JavaScript code do? document.getElementById('header').style.color = 'blue';",
                "options": [
                    ("It will change the background color of the 'header' element to blue.", False),
                    ("It will select the 'header' element and change its text color to blue.", True),
                    ("It will add a blue border to the 'header' element.", False),
                    ("It will check if the 'header' element's color is blue and return true or false.", False),
                    ("The code will fail because .style.color is not valid syntax.", False)
                ]
            },
            {
                "text": "Which of these is the correct syntax for a 'template literal' in JavaScript, used for embedding variables in a string?",
                "options": [
                    ('"Hello, " + name + "!"', False),
                    ("'Hello, {name}!'", False),
                    ("`Hello, ${name}!`", True),
                    ("('Hello, ' + name + '!')", False),
                    ("`Hello, [name]!`", False)
                ]
            },
            {
                "text": "In CSS, what does position: absolute; do to an element?",
                "options": [
                    ("It centers the element on the page.", False),
                    ("It removes the element from the normal document flow and positions it relative to its nearest positioned ancestor.", True),
                    ("It fixes the element to the viewport, so it doesn't move when scrolling.", False),
                    ("It makes the element's position relative to its own default position in the flow.", False),
                    ("It makes the element a block-level element.", False)
                ]
            },
            {
                "text": "Given const user = { name: 'Alex', age: 30 };, how would you access Alex's age?",
                "options": [
                    ("user['age']", True),
                    ("user(age)", False),
                    ("user.get('age')", False),
                    ("user[age]", False),
                    ("user[1]", False)
                ]
            },
            {
                "text": "Which CSS selector targets an <input> element with a type attribute set to text?",
                "options": [
                    ("input.text", False),
                    ("input[type='text']", True),
                    ("input:text", False),
                    ("input#text", False),
                    ("text(input)", False)
                ]
            },
            {
                "text": "What is the purpose of the alt attribute in an <img> tag?",
                "options": [
                    ("It provides a title for the image that appears on hover.", False),
                    ("It provides alternative text for screen readers and when the image fails to load.", True),
                    ("It defines the URL or path to the image file.", False),
                    ("It sets the alignment (left, right, center) of the image.", False),
                    ("It specifies a lower-resolution version of the image to load first.", False)
                ]
            },
            {
                "text": "How do you write a 'fat arrow' function in JavaScript?",
                "options": [
                    ("function myFunction() { ... }", False),
                    ("const myFunction => () { ... }", False),
                    ("const myFunction = () => { ... }", True),
                    ("const myFunction = function() => { ... }", False),
                    ("myFunction: () => { ... }", False)
                ]
            },
            {
                "text": "In CSS, what is the difference between visibility: hidden; and display: none;?",
                "options": [
                    ("There is no difference; both hide the element.", False),
                    ("display: none; hides the element, while visibility: hidden; deletes it from the DOM.", False),
                    ("display: none; removes the element from the layout, while visibility: hidden; hides it but leaves its space.", True),
                    ("visibility: hidden; is for text, and display: none; is for images.", False),
                    ("display: none; is permanent, but visibility: hidden; can be toggled with JavaScript.", False)
                ]
            },
            {
                "text": "Which CSS pseudo-class is used to style an element when the user's mouse is over it?",
                "options": [
                    (":active", False),
                    (":focus", False),
                    (":hover", True),
                    (":on", False),
                    (":mouse", False)
                ]
            },
            {
                "text": "What is the correct HTML tag to use for a self-contained piece of content, like a blog post or a news article, that could be distributed independently?",
                "options": [
                    ("<div>", False),
                    ("<section>", False),
                    ("<article>", True),
                    ("<aside>", False),
                    ("<main>", False)
                ]
            },
            {
                "text": "How would you change the text inside an element with the ID message to 'Hello World'?",
                "options": [
                    ("document.getElementById('message').value = 'Hello World';", False),
                    ("document.getElementById('message').innerHTML = 'Hello World';", True),
                    ("document.getElementById('message').text = 'Hello World';", False),
                    ("document.querySelector('#message').setAttribute('text', 'Hello World');", False),
                    ("document.getElementById('message').write('Hello World');", False)
                ]
            }
        ]
        
        add_questions(db, quiz_level_2.id, level_2_questions)
        print(f"✅ Added {len(level_2_questions)} questions for Level 2")
        
        # Level 3: Advanced (20 questions)
        print("\n📝 Adding Level 3: Frontend Development Advanced...")
        quiz_level_3 = models.Quiz(
            title="Frontend Development Advanced - Level 3",
            description="Advanced frontend topics including Flexbox, Grid, array methods, async operations, and security",
            specialization_id=frontend_spec.id,
            difficulty_level=3,
            is_active=True,
            time_limit_minutes=50,
            passing_score=70.0
        )
        db.add(quiz_level_3)
        db.commit()
        db.refresh(quiz_level_3)
        
        level_3_questions = [
            {
                "text": "How do you center a child element both vertically and horizontally inside a parent container using CSS Flexbox?",
                "options": [
                    ("parent { display: flex; justify-content: center; align-items: center; }", True),
                    ("parent { display: flex; flex-direction: column; }", False),
                    ("parent { display: grid; } child { margin: auto; }", False),
                    ("parent { display: flex; vertical-align: middle; text-align: center; }", False),
                    ("parent { display: flex; align-content: center; flex-wrap: wrap; }", False)
                ]
            },
            {
                "text": "You have an array const numbers = [1, 2, 3, 4, 5];. How do you create a new array containing only the even numbers?",
                "options": [
                    ("const evens = numbers.map(num => num % 2 === 0);", False),
                    ("const evens = numbers.forEach(num => num % 2 === 0);", False),
                    ("const evens = numbers.filter(num => num % 2 === 0);", True),
                    ("const evens = numbers.find(num => num % 2 === 0);", False),
                    ("let evens = []; for(num in numbers) { if(num % 2 === 0) { evens.push(num); } }", False)
                ]
            },
            {
                "text": "What is the primary purpose of the .then() block when using the JavaScript fetch API?",
                "options": [
                    ("To catch and handle any errors that occur during the request.", False),
                    ("To define the URL of the API endpoint.", False),
                    ("To handle the successful response after the asynchronous request completes.", True),
                    ("To send the data (payload) to the API.", False),
                    ("To run code immediately, before the fetch call is made.", False)
                ]
            },
            {
                "text": "Why is it generally better to use a <button> tag for a clickable action instead of a <div> with a JavaScript click event?",
                "options": [
                    ("Because <div> elements cannot have click events.", False),
                    ("Because <button> is automatically focusable, can be triggered by 'Enter'/'Space', and is recognized by screen readers.", True),
                    ("Because <button> elements can be styled more easily with CSS.", False),
                    ("Because <button> is a non-semantic tag, and <div> is semantic.", False),
                    ("Because <div> click events are slower than <button> click events.", False)
                ]
            },
            {
                "text": "Which CSS Grid syntax creates a 3-column layout where the middle column is twice as wide as the two outer columns?",
                "options": [
                    ("grid-template-columns: 25% 50% 25%;", False),
                    ("grid-template-columns: 1fr 2fr 1fr;", True),
                    ("grid-columns: 1 2 1;", False),
                    ("grid-template-rows: 1fr 2fr 1fr;", False),
                    ("grid-template-columns: repeat(3, 1fr 2fr);", False)
                ]
            },
            {
                "text": "You have an array const names = ['alice', 'bob', 'charlie'];. How do you create a new array ['ALICE', 'BOB', 'CHARLIE']?",
                "options": [
                    ("const upper = names.map(name => name.toUpperCase());", True),
                    ("const upper = names.filter(name => name.toUpperCase());", False),
                    ("const upper = names.forEach(name => name.toUpperCase());", False),
                    ("const upper = names.toUpperCase();", False),
                    ("let upper = []; for(let i=0; i<names.length; i++) { names[i].toUpperCase(); }", False)
                ]
            },
            {
                "text": "In CSS, what is the key difference between position: absolute; and position: relative;?",
                "options": [
                    ("relative elements are removed from the document flow, while absolute elements are not.", False),
                    ("absolute elements are positioned relative to the viewport, while relative elements are positioned relative to the <body>.", False),
                    ("relative elements remain in the normal flow, while absolute elements are removed from the flow and positioned relative to their nearest positioned ancestor.", True),
                    ("absolute elements cannot be moved with top/left, while relative elements can.", False),
                    ("relative is for layout and absolute is for text.", False)
                ]
            },
            {
                "text": "In a fetch request, why does the response.json() method also require a .then() or await?",
                "options": [
                    ("Because it needs to convert a JavaScript object into a JSON string.", False),
                    ("Because the response body arrives as a data stream and must be fully read and parsed asynchronously.", True),
                    ("Because it is an old method that is no longer used.", False),
                    ("Because it needs to add the data to localStorage.", False),
                    ("It does not require a .then(); only the initial fetch does.", False)
                ]
            },
            {
                "text": "Which CSS syntax correctly applies a red background only when the screen width is 800px or less?",
                "options": [
                    ("if (screen.width <= 800px) { body { background: red; } }", False),
                    ("@media query (width <= 800px) { body { background: red; } }", False),
                    ("@media screen (min-width: 800px) { body { background: red; } }", False),
                    ("@media screen (max-width: 800px) { body { background: red; } }", True),
                    ("body { @media (max-width: 800px) { background: red; } }", False)
                ]
            },
            {
                "text": "What is the purpose of an aria-label attribute in HTML?",
                "options": [
                    ("To provide an accessible name for an element when a visible text label is not present (e.g., an icon-only button).", True),
                    ("To provide a visible label for a form <input>.", False),
                    ("To define a new JavaScript variable.", False),
                    ("To hide an element from screen readers completely.", False),
                    ("To link to an external ARIA stylesheet.", False)
                ]
            },
            {
                "text": "Which of these CSS selectors has the highest specificity?",
                "options": [
                    (".container p.text", False),
                    ("#main-content p", True),
                    ("body div p.text", False),
                    ("p.text.highlight", False),
                    ("div p", False)
                ]
            },
            {
                "text": "You have 3 <div> elements inside a flex container. By default, they are in a row. How do you make them stack vertically?",
                "options": [
                    ("display: grid;", False),
                    ("flex-wrap: wrap;", False),
                    ("align-items: center;", False),
                    ("flex-flow: vertical;", False),
                    ("flex-direction: column;", True)
                ]
            },
            {
                "text": "What is the 'spread operator' (...) used for in this code: const arr2 = [...arr1];?",
                "options": [
                    ("It creates a reference, where arr2 points to the same array as arr1.", False),
                    ("It creates a new array (arr2) containing a shallow copy of all items from arr1.", True),
                    ("It gets the last item from arr1.", False),
                    ("It converts arr1 into an object.", False),
                    ("It deletes all items from arr1.", False)
                ]
            },
            {
                "text": "Which of the following values is 'falsy' in JavaScript?",
                "options": [
                    ('"0" (the string \'0\')', False),
                    ("[] (an empty array)", False),
                    ("{} (an empty object)", False),
                    ("NaN (Not a Number)", True),
                    ('"false" (the string \'false\')', False)
                ]
            },
            {
                "text": "What is 'object destructuring' in JavaScript?",
                "options": [
                    ("The process of converting an object into a JSON string.", False),
                    ("A syntax for unpacking properties from an object into distinct variables (e.g., const { name } = user;).", True),
                    ("A way to delete properties from an object.", False),
                    ("A way to combine two objects into one.", False),
                    ("A method for finding errors in an object.", False)
                ]
            },
            {
                "text": "What is the security risk of using .innerHTML instead of .textContent to insert user-provided data?",
                "options": [
                    ("It can lead to a Cross-Site Scripting (XSS) attack if the data contains malicious <script> tags.", True),
                    ("It is much slower and can crash the browser.", False),
                    ("It can corrupt the browser's localStorage.", False),
                    ("It does not work in all browsers.", False),
                    ("There is no risk; .innerHTML automatically sanitizes all input.", False)
                ]
            },
            {
                "text": "How would you store a user's name, 'Alice', in the browser's localStorage?",
                "options": [
                    ("localStorage.add('username', 'Alice');", False),
                    ("document.cookie = 'username=Alice';", False),
                    ("localStorage('username') = 'Alice';", False),
                    ("sessionStorage.setItem('username', 'Alice');", False),
                    ("localStorage.setItem('username', 'Alice');", True)
                ]
            },
            {
                "text": "You have a JavaScript object: const user = { name: 'Alice' };. What must you do before storing it in localStorage?",
                "options": [
                    ("Nothing, localStorage.setItem('user', user); will store the object correctly.", False),
                    ("Convert it to a JSON string using JSON.stringify(user).", True),
                    ("Encrypt it using a password.", False),
                    ("Convert it to an array, as objects cannot be stored.", False),
                    ("Use localStorage.setObject('user', user); instead.", False)
                ]
            },
            {
                "text": "In CSS Flexbox, what does the property flex: 1; on a child element primarily do?",
                "options": [
                    ("It sets the element's max-width to 100px.", False),
                    ("It allows the element to grow and take up any available free space in the flex container.", True),
                    ("It makes the element 1px wide.", False),
                    ("It sets the element's opacity to 1.", False),
                    ("It forces the element to be the first item in the container.", False)
                ]
            },
            {
                "text": "What is the purpose of the await keyword in an async function?",
                "options": [
                    ("It is an old keyword that has been replaced by .then().", False),
                    ("It pauses the execution of the async function until a Promise is settled (resolved or rejected).", True),
                    ("It immediately rejects a Promise and throws an error.", False),
                    ("It converts a regular function into an async function.", False),
                    ("It makes the JavaScript code run faster by using multiple threads.", False)
                ]
            }
        ]
        
        add_questions(db, quiz_level_3.id, level_3_questions)
        print(f"✅ Added {len(level_3_questions)} questions for Level 3")
        
        # Level 4: Expert & Frameworks (20 questions - React focused)
        print("\n📝 Adding Level 4: Frontend Development Expert - React & Frameworks...")
        quiz_level_4 = models.Quiz(
            title="Frontend Development Expert - Level 4",
            description="Expert-level React framework concepts including hooks, components, routing, and state management",
            specialization_id=frontend_spec.id,
            difficulty_level=4,
            is_active=True,
            time_limit_minutes=60,
            passing_score=70.0
        )
        db.add(quiz_level_4)
        db.commit()
        db.refresh(quiz_level_4)
        
        level_4_questions = [
            {
                "text": "What is JSX?",
                "options": [
                    ("A database query language used by React.", False),
                    ("A CSS pre-processor for styling React components.", False),
                    ("A syntax extension for JavaScript that looks like HTML, used to describe UI structure.", True),
                    ("A JavaScript method for fetching API data.", False),
                    ("A built-in React component for handling user state.", False)
                ]
            },
            {
                "text": "In React, what is the primary difference between 'props' and 'state'?",
                "options": [
                    ("Props are used for functions; state is used for class components.", False),
                    ("Props are passed into a component from its parent, while state is managed within the component.", True),
                    ("Props can be changed by the child component, while state cannot.", False),
                    ("Props are for styling, while state is for logic.", False),
                    ("There is no difference; they are interchangeable.", False)
                ]
            },
            {
                "text": "What does the useState hook return?",
                "options": [
                    ("A single value representing the current state.", False),
                    ("An object with value and setValue properties.", False),
                    ("An array containing the current state value and a function to update it.", True),
                    ("A boolean indicating if the state has changed.", False),
                    ("Just a function to update the state.", False)
                ]
            },
            {
                "text": "Why are 'keys' important when rendering a list of elements using .map() in React?",
                "options": [
                    ("To provide a unique id for CSS styling.", False),
                    ("To help React identify which items have changed, been added, or been removed, optimizing rendering.", True),
                    ("To set the order of the items in the list.", False),
                    ("To make the list items clickable.", False),
                    ("They are not important and can be omitted.", False)
                ]
            },
            {
                "text": "How do you conditionally render a component? For example, show a <UserProfile> component only if isLoggedIn is true?",
                "options": [
                    ("<UserProfile if={isLoggedIn} />", False),
                    ("if (isLoggedIn) { <UserProfile /> }", False),
                    ("{isLoggedIn && <UserProfile />}", False),
                    ("isLoggedIn ? <UserProfile /> : null", False),
                    ("Both C and D are common, valid ways to do this.", True)
                ]
            },
            {
                "text": "What is the purpose of the useEffect hook?",
                "options": [
                    ("To handle user click events.", False),
                    ("To perform side effects in functional components, such as data fetching or DOM manipulation.", True),
                    ("To define the component's initial state.", False),
                    ("To create reusable functions within a component.", False),
                    ("To conditionally style a component.", False)
                ]
            },
            {
                "text": "You have a useEffect hook: useEffect(() => { ... }, []);. What does the empty dependency array [] signify?",
                "options": [
                    ("The effect will run on every re-render of the component.", False),
                    ("The effect will run only once, when the component first mounts (like componentDidMount).", True),
                    ("The effect will not run at all.", False),
                    ("The effect will run when the component unmounts.", False),
                    ("This syntax is invalid and will cause an error.", False)
                ]
            },
            {
                "text": "How do you pass a function called handleClick from a parent component App to a child component Button?",
                "options": [
                    ("<Button event={handleClick} />", False),
                    ("<Button onClick={handleClick} />", True),
                    ("<Button function={handleClick} />", False),
                    ("<Button>{handleClick}</Button>", False),
                    ("You cannot pass functions as props.", False)
                ]
            },
            {
                "text": "What is the 'Virtual DOM' in React?",
                "options": [
                    ("A browser feature that React hooks into.", False),
                    ("A in-memory representation of the real browser DOM, used by React to calculate the most efficient changes.", True),
                    ("Another name for the useState hook.", False),
                    ("A tool for debugging React applications.", False),
                    ("A secure, sandboxed DOM for running tests.", False)
                ]
            },
            {
                "text": "What is 'lifting state up' in React?",
                "options": [
                    ("Moving state from a child component to its parent component to share it between siblings.", True),
                    ("Storing your state in localStorage instead of in a component.", False),
                    ("Using the useState hook at the top of your function.", False),
                    ("Upgrading a class component's state to a functional component's hook.", False),
                    ("Moving state into a separate file.", False)
                ]
            },
            {
                "text": "What is the purpose of React Router?",
                "options": [
                    ("It optimizes the build process of a React app.", False),
                    ("It is a state management library like Redux.", False),
                    ("It handles client-side routing, allowing navigation between different 'pages' in a single-page application.", True),
                    ("It is a tool for writing unit tests for React components.", False),
                    ("It connects React to a backend server.", False)
                ]
            },
            {
                "text": "How would you update a user object in state without mutating the original state?",
                "options": [
                    ("const [user, setUser] = useState({ name: 'Alex' }); setUser(user.name = 'Bob');", False),
                    ("const [user, setUser] = useState({ name: 'Alex' }); setUser({ ...user, name: 'Bob' });", True),
                    ("const [user, setUser] = useState({ name: 'Alex' }); user.name = 'Bob'; setUser(user);", False),
                    ("const [user, setUser] = useState({ name: 'Alex' }); setUser({ name: 'Bob' });", False),
                    ("const [user, setUser] = useState({ name: 'Alex' }); setUser.name = 'Bob';", False)
                ]
            },
            {
                "text": "What is a 'controlled component' in React?",
                "options": [
                    ("A component that is only visible to logged-in users.", False),
                    ("A component that has its own internal state.", False),
                    ("A form element (like <input>) whose value is controlled by React state.", True),
                    ("A component that has been unit tested.", False),
                    ("A component that is imported from an external library.", False)
                ]
            },
            {
                "text": "What is the primary use of the React Context API?",
                "options": [
                    ("To fetch data from an external API.", False),
                    ("To provide a way to pass data through the component tree without having to pass props down manually at every level.", True),
                    ("To handle errors and crashes within the application.", False),
                    ("To define the component's visual style.", False),
                    ("To create a new React component.", False)
                ]
            },
            {
                "text": "How do you pass data from a child component back up to its parent component?",
                "options": [
                    ("You can't; data only flows from parent to child.", False),
                    ("By modifying the props object directly in the child.", False),
                    ("By using the useContext hook.", False),
                    ("The parent passes a callback function (as a prop) to the child, and the child calls that function with the data as an argument.", True),
                    ("By setting the data in localStorage.", False)
                ]
            },
            {
                "text": "What is the purpose of React.Fragment, often written as <> ... </>?",
                "options": [
                    ("It is a way to write comments in JSX.", False),
                    ("It is used to create a 'portal' to another DOM node.", False),
                    ("It lets you group a list of children without adding an extra <div> to the DOM.", True),
                    ("It is a component that marks its children for lazy loading.", False),
                    ("It is a way to define state that is shared between components.", False)
                ]
            },
            {
                "text": "What is 'prop drilling'?",
                "options": [
                    ("The process of passing data from a parent component to a deeply nested child through many intermediate components.", True),
                    ("A debugging technique to 'drill' into a component's props.", False),
                    ("A performance optimization for React.", False),
                    ("The act of using useState to manage props.", False),
                    ("An error that occurs when props are not defined.", False)
                ]
            },
            {
                "text": "What is the difference between useEffect and useLayoutEffect?",
                "options": [
                    ("useEffect runs asynchronously after the browser has painted, while useLayoutEffect runs synchronously before the browser paints.", True),
                    ("useEffect is for data fetching; useLayoutEffect is for styling.", False),
                    ("useEffect can have a dependency array; useLayoutEffect cannot.", False),
                    ("useLayoutEffect is the old version of useEffect.", False),
                    ("There is no difference; they are aliases.", False)
                ]
            },
            {
                "text": "Given <ProfileCard user={data} />, how would the ProfileCard component access the user object?",
                "options": [
                    ("function ProfileCard(props) { return <h1>{props.user.name}</h1>; }", True),
                    ("function ProfileCard(user) { return <h1>{user.name}</h1>; }", False),
                    ("function ProfileCard() { return <h1>{this.props.user.name}</h1>; }", False),
                    ("function ProfileCard() { return <h1>{props.data.name}</h1>; }", False),
                    ("function ProfileCard({ data }) { return <h1>{data.name}</h1>; }", False)
                ]
            },
            {
                "text": "What is the problem with this code? function Counter() { const [count, setCount] = useState(0); function handleIncrement() { setCount(count + 1); setCount(count + 1); } ... }",
                "options": [
                    ("You cannot call setCount more than once in a function.", False),
                    ("React 'batches' state updates, so count will only increment by 1, not 2, because both calls use the same count value from the initial render.", True),
                    ("This will cause an infinite loop.", False),
                    ("setCount must be awaited (e.g., await setCount(...)).", False),
                    ("This will increment the count by 2, but it is not good for performance.", False)
                ]
            }
        ]
        
        add_questions(db, quiz_level_4.id, level_4_questions)
        print(f"✅ Added {len(level_4_questions)} questions for Level 4")
        
        # Level 5: Strategic & Architectural (20 questions)
        print("\n📝 Adding Level 5: Strategic & Architectural...")
        quiz_level_5 = models.Quiz(
            title="Frontend Development Strategic - Level 5",
            description="Strategic and architectural concepts including TypeScript, performance, testing, security, and best practices",
            specialization_id=frontend_spec.id,
            difficulty_level=5,
            is_active=True,
            time_limit_minutes=70,
            passing_score=70.0
        )
        db.add(quiz_level_5)
        db.commit()
        db.refresh(quiz_level_5)
        
        level_5_questions = [
            {
                "text": "What is the primary business-level advantage of using TypeScript in a large-scale project?",
                "options": [
                    ("It makes the website run faster in the browser.", False),
                    ("It automatically writes unit tests for your code.", False),
                    ("It reduces bugs and improves maintainability by enforcing type safety, making code easier to refactor.", True),
                    ("It replaces the need for a module bundler like Webpack.", False),
                    ("It is the only way to use modern frameworks like React and Angular.", False)
                ]
            },
            {
                "text": "A user's Lighthouse report shows a poor 'Largest Contentful Paint' (LCP) score. Which of the following is the most likely cause and solution?",
                "options": [
                    ("The JavaScript bundle is too large, so it blocks the main thread.", False),
                    ("The main 'hero' image is a very large, unoptimized file that is slow to load.", True),
                    ("There are too many console.log() statements in the code.", False),
                    ("The website is not using a Service Worker.", False),
                    ("The CSS files are not minified.", False)
                ]
            },
            {
                "text": "What is 'tree shaking' in the context of a modern build process (e.g., Webpack, Vite)?",
                "options": [
                    ("A debugging process for finding errors in the component tree.", False),
                    ("A process that automatically removes unused code (dead code) from the final JavaScript bundle.", True),
                    ("A method for re-organizing the file structure of a project.", False),
                    ("A security scan that looks for vulnerable dependencies.", False),
                    ("A way to 'shake' the DOM to find performance bottlenecks.", False)
                ]
            },
            {
                "text": "When building a large application, when would you choose the Context API over a dedicated state library like Redux?",
                "options": [
                    ("When you need to manage complex, high-frequency updates, like in a stock trading app.", False),
                    ("When you need to pass 'global' data (like theme, user authentication) deeply down the component tree without prop drilling.", True),
                    ("When you need to store your state in localStorage.", False),
                    ("When you are working on a class-based component, as Redux is for functional components only.", False),
                    ("Context API is always better than Redux because it is built into React.", False)
                ]
            },
            {
                "text": "What is the primary philosophy of the 'React Testing Library' (RTL)?",
                "options": [
                    ("To test the internal implementation details of a component (e.g., 'does this component have the correct state?').", False),
                    ("To test how the component behaves from a user's perspective (e.g., 'can the user see this text?', 'can the user click this button?').", True),
                    ("To test the component's performance and speed.", False),
                    ("To test the component's styles and visual appearance (snapshot testing).", False),
                    ("To test the component's JavaScript code logic, but not its JSX.", False)
                ]
            },
            {
                "text": "What is the primary security risk of storing a JWT (JSON Web Token) in localStorage?",
                "options": [
                    ("It can be easily accessed by a Cross-Site Scripting (XSS) attack, allowing an attacker to steal the token.", True),
                    ("It takes up too much space and will slow the browser down.", False),
                    ("It will be deleted automatically when the user closes the browser tab.", False),
                    ("It cannot be shared between different browser tabs.", False),
                    ("It is not encrypted and can be read by anyone.", False)
                ]
            },
            {
                "text": "In the context of Server-Side Rendering (SSR) in a React application, what is 'hydration'?",
                "options": [
                    ("The process of the server fetching all the necessary data before sending the HTML.", False),
                    ("The process of the browser 'watering down' the JavaScript to make it run faster.", False),
                    ("The client-side JavaScript process of attaching event listeners to the static HTML sent by the server, making the page interactive.", True),
                    ("The process of storing assets in a browser cache.", False),
                    ("The process of compressing the HTML file on the server.", False)
                ]
            },
            {
                "text": "What is the 'micro-frontend' architectural pattern?",
                "options": [
                    ("A pattern where you only use very small, lightweight frameworks.", False),
                    ("A method of building the entire frontend application inside a single Web Component.", False),
                    ("An architectural style where a large frontend application is split into smaller, independently deployable 'micro-apps.'", True),
                    ("A CSS methodology for creating small, reusable component styles.", False),
                    ("A pattern where all state is stored in a single, global 'micro' object.", False)
                ]
            },
            {
                "text": "Why is it generally bad practice to use an array's index as a key when rendering a list in React, especially if the list is dynamic (can be re-ordered or filtered)?",
                "options": [
                    ("Because it is not a valid data type for a key; it must be a string.", False),
                    ("Because it can lead to incorrect state and rendering bugs when the list items change order.", True),
                    ("Because it is much slower than using a unique ID.", False),
                    ("Because it is not compliant with accessibility (WCAG) standards.", False),
                    ("Because it will throw a fatal error in production builds.", False)
                ]
            },
            {
                "text": "What is a 'Progressive Web App' (PWA)?",
                "options": [
                    ("A web application that is built using a special, 'progressive' version of JavaScript.", False),
                    ("A website that is still in development (a 'work in progress').", False),
                    ("A web app that uses a Service Worker, a manifest file, and HTTPS to provide an 'app-like' experience (e.g., offline capability, push notifications).", True),
                    ("An application that progressively 'gets harder' as the user interacts with it.", False),
                    ("A marketing term for any modern, single-page application.", False)
                ]
            },
            {
                "text": "What problem does the React.useMemo hook solve?",
                "options": [
                    ("It memoizes the result of an expensive calculation, preventing it from being re-run on every render unless its dependencies change.", True),
                    ("It fetches data from an API and 'memoizes' (caches) the response.", False),
                    ("It memoizes an entire component, preventing it from re-rendering (that is React.memo).", False),
                    ("It remembers the user's state even after they close the browser tab.", False),
                    ("It allows you to write memos (comments) in your code that are visible in the React DevTools.", False)
                ]
            },
            {
                "text": "What is the main difference between a unit test and an integration test in a frontend application?",
                "options": [
                    ("A unit test checks a single, isolated function or component; an integration test checks how multiple components work together.", True),
                    ("Unit tests are written in JavaScript; integration tests are written in TypeScript.", False),
                    ("Unit tests run in the browser; integration tests run on the server.", False),
                    ("Unit tests are fast and automated; integration tests are slow and manual.", False),
                    ("A unit test checks for bugs; an integration test checks for performance.", False)
                ]
            },
            {
                "text": "What is the BEM (Block, Element, Modifier) methodology in CSS?",
                "options": [
                    ("A JavaScript framework for building user interfaces.", False),
                    ("A naming convention for CSS classes (e.g., .card__title--primary) designed to create scoped, maintainable styles.", True),
                    ("A build tool that bundles, extends, and minifies CSS.", False),
                    ("A set of pre-built CSS components, similar to Bootstrap.", False),
                    ("A testing framework for visual regression.", False)
                ]
            },
            {
                "text": "What is a 'Cross-Site Request Forgery' (CSRF) attack, and how is it commonly mitigated?",
                "options": [
                    ("An attack where malicious scripts are injected into your site; mitigated by escaping data.", False),
                    ("An attack where an attacker tricks a logged-in user into sending an unwanted request; mitigated by using anti-CSRF tokens.", True),
                    ("An attack where a user is redirected to a fake version of your website; mitigated by using HTTPS.", False),
                    ("An attack where the server is flooded with requests; mitigated by rate-limiting.", False),
                    ("An attack where localStorage is stolen; mitigated by using HTTP-only cookies.", False)
                ]
            },
            {
                "text": "In an async function, what is the functional difference between using await and using .then()?",
                "options": [
                    ("await pauses the function execution, while .then() schedules a callback to run after the function has finished.", False),
                    ("await is linear, 'synchronous-looking' code, while .then() is a chain of callback functions. Both handle the promise.", False),
                    ("await can be used on any function, while .then() only works on fetch requests.", False),
                    ("await can handle errors, while .then() requires a separate .catch() block.", False),
                    ("B and D are both correct.", True)
                ]
            },
            {
                "text": "What is the 'bundle size' of a frontend application, and why is it a critical performance metric?",
                "options": [
                    ("The total number of files in the project's source code; it is not a performance metric.", False),
                    ("The physical size (in MB or KB) of the final JavaScript/CSS files sent to the user; larger bundles take longer to download, parse, and execute.", True),
                    ("The amount of memory the application uses in the browser; it is not related to download time.", False),
                    ("The number of components in the React component tree.", False),
                    ("The size of the node_modules folder.", False)
                ]
            },
            {
                "text": "What is an 'End-to-End' (E2E) test, and how does it differ from a unit or integration test?",
                "options": [
                    ("It is another name for a unit test.", False),
                    ("It tests a complete user workflow (e.g., 'login, add item to cart, checkout') by simulating a real user in a real browser.", True),
                    ("It only tests the API 'endpoints' and nothing on the frontend.", False),
                    ("It is a manual test done by a QA team.", False),
                    ("It tests the 'end' of the code (the last function) but not the beginning.", False)
                ]
            },
            {
                "text": "Why would you use a debounce function on an event listener (e.g., for a search bar's 'keyup' event)?",
                "options": [
                    ("To force the event to fire immediately, improving responsiveness.", False),
                    ("To limit how often the function is executed (e.g., 'wait until the user has stopped typing for 300ms') to prevent excessive API calls.", True),
                    ("To cancel the event completely and prevent it from firing.", False),
                    ("To add a 'bouncing' animation to the user interface.", False),
                    ("To log the event to the console for debugging.", False)
                ]
            },
            {
                "text": "What is a 'Service Worker' and what is its primary capability?",
                "options": [
                    ("A JavaScript file that runs in the browser and is used to manage and test other scripts.", False),
                    ("A backend script that 'serves' the frontend application.", False),
                    ("A JavaScript file that runs in the background, separate from the web page, allowing for features like network request interception (caching for offline use) and push notifications.", True),
                    ("A UI component that shows a 'loading' spinner while data is being fetched.", False),
                    ("A security policy that prevents XSS attacks.", False)
                ]
            },
            {
                "text": "You see 'layout thrashing' in your browser's performance profiler. What does this mean?",
                "options": [
                    ("The user is 'trashing' the UI by clicking too fast.", False),
                    ("The browser is forced to re-calculate the layout of the page multiple times in a single frame due to JavaScript rapidly reading and writing layout properties (e.g., offsetHeight, style.width).", True),
                    ("The CSS files are 'trashing' each other by overriding styles.", False),
                    ("The application is loading too many large image files at once.", False),
                    ("The JavaScript bundle is corrupted and needs to be rebuilt.", False)
                ]
            }
        ]
        
        add_questions(db, quiz_level_5.id, level_5_questions)
        print(f"✅ Added {len(level_5_questions)} questions for Level 5")
        
        print("\n" + "="*60)
        print("✅ Successfully added all Frontend Development quizzes!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   Level 1 (Basics): {len(level_1_questions)} questions")
        print(f"   Level 2 (Intermediate): {len(level_2_questions)} questions")
        print(f"   Level 3 (Advanced): {len(level_3_questions)} questions")
        print(f"   Level 4 (Expert - React): {len(level_4_questions)} questions")
        print(f"   Level 5 (Strategic): {len(level_5_questions)} questions")
        print(f"\n   Total: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions) + len(level_4_questions) + len(level_5_questions)} questions across 5 quizzes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def add_questions(db: Session, quiz_id: int, questions_data: list):
    """Helper function to add questions to a quiz"""
    for idx, q_data in enumerate(questions_data, 1):
        question = models.Question(
            quiz_id=quiz_id,
            question_text=q_data["text"],
            question_type="multiple_choice",
            points=1,
            order_index=idx,
            is_active=True
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Add options
        for opt_idx, (option_text, is_correct) in enumerate(q_data["options"], 1):
            option = models.QuestionOption(
                question_id=question.id,
                option_text=option_text,
                is_correct=is_correct,
                order_index=opt_idx
            )
            db.add(option)
        
        db.commit()


if __name__ == "__main__":
    print("="*60)
    print("Adding Frontend Development Quizzes (Levels 1-5)")
    print("="*60)
    add_frontend_quizzes()
