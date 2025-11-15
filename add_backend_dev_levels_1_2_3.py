"""
Add Backend Development Quizzes - Levels 1, 2, and 3
This script adds 60 questions for Backend Development specialization (Basic through Advanced)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_backend_dev_quizzes():
    db = SessionLocal()
    try:
        # Get Backend Development specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Backend Development"
        ).first()
        
        if not specialization:
            print("Error: Backend Development specialization not found")
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
            ("What is the primary role of a 'backend' in a web application?",
             ["To define the style, color, and layout of a website.",
              "To manage the server, application logic, and database.",
              "To create the clickable buttons and forms in a browser.",
              "To store files directly on the user's computer.",
              "To optimize the website for search engines."],
             1, "The backend manages the server, application logic, and database - the 'behind the scenes' functionality."),
            
            ("What does 'API' stand for?",
             ["Application Programming Interface",
              "Advanced Programming Integration",
              "Application Protocol Instance",
              "Automated Programming Interaction",
              "Application Process Information"],
             0, "API stands for Application Programming Interface, which allows different software to communicate."),
            
            ("What does 'HTTP' stand for?",
             ["HyperText Transfer Protocol",
              "High-Tech Transfer Program",
              "HyperText Transmission Protocol",
              "Hyper-Terminal Transfer Policy",
              "Home Terminal Transfer Protocol"],
             0, "HTTP stands for HyperText Transfer Protocol, the foundation of data communication on the web."),
            
            ("What is the main purpose of a 'database'?",
             ["To style a web page.",
              "To write the business logic of an application.",
              "To store, organize, and retrieve data efficiently.",
              "To handle user click events.",
              "To display images and videos."],
             2, "A database stores, organizes, and retrieves data efficiently for applications."),
            
            ("What is the role of a 'server' in backend development?",
             ["A computer that runs the backend software and listens for requests.",
              "A text editor for writing code.",
              "The user's web browser (like Chrome or Firefox).",
              "A program that designs the user interface.",
              "A file that contains all the HTML code."],
             0, "A server is a computer that runs backend software and listens for requests from clients."),
            
            ("What is 'JSON'?",
             ["A type of programming language for styling.",
              "A database management system.",
              "A lightweight format for storing and transporting data, often used in APIs.",
              "A backend framework for Python.",
              "A type of server."],
             2, "JSON (JavaScript Object Notation) is a lightweight data format commonly used in APIs."),
            
            ("What is the basic difference between a 'client' and a 'server'?",
             ["The client runs on a Mac, and the server runs on Windows.",
              "The client is the backend, and the server is the frontend.",
              "The client (e.g., a browser) requests data, and the server (backend) provides it.",
              "The client stores data, and the server displays data.",
              "The client writes code, and the server runs code."],
             2, "The client requests data (like a browser), and the server provides the data in response."),
            
            ("What does 'SQL' stand for?",
             ["Structured Query Language",
              "Simple Query Logic",
              "Server-Side Query Language",
              "System Query Link",
              "Structured Question Logic"],
             0, "SQL stands for Structured Query Language, used to communicate with databases."),
            
            ("What is an 'HTTP Request'?",
             ["A message sent by the server to the client.",
              "A message sent by the client (e.g., browser) to the server, asking for data.",
              "A type of database.",
              "A file containing HTML and CSS.",
              "An error in the code."],
             1, "An HTTP Request is a message from the client to the server asking for data or an action."),
            
            ("What is an 'HTTP Response'?",
             ["A message sent by the server back to the client, containing the requested data (or an error).",
              "A message sent by the client to the server.",
              "A JavaScript function.",
              "A command to restart the server.",
              "A user's click on a button."],
             0, "An HTTP Response is the server's reply to the client, containing data or error information."),
            
            ("Which of the following is a popular programming language used for backend development?",
             ["HTML", "CSS", "Python", "React", "SASS"],
             2, "Python is a popular backend programming language, while HTML/CSS are for frontend."),
            
            ("What is 'localhost'?",
             ["The public, live website on the internet.",
              "A standard name that refers to your own computer (127.0.0.1).",
              "A popular hosting provider.",
              "A type of database.",
              "A security protocol."],
             1, "Localhost (127.0.0.1) refers to your own computer, used for local development."),
            
            ("What is a 'port number' (e.g., 3000, 8080, 5432)?",
             ["A specific 'door' on a server that a software application listens on for requests.",
              "The total number of users allowed on a server.",
              "The version number of the backend software.",
              "A type of error code.",
              "The line number where your code is running."],
             0, "A port number is like a 'door' on a server that an application uses to listen for requests."),
            
            ("What is a 'database schema'?",
             ["The total amount of data stored.",
              "The blueprint or structure of a database (e.g., table names, column names, data types).",
              "A query used to get data.",
              "The password to access the database.",
              "A backup file of the database."],
             1, "A database schema is the blueprint defining the structure, tables, columns, and relationships."),
            
            ("What is an 'HTTP status code'?",
             ["A number sent in a response that indicates the status of the request (e.g., success, error, not found).",
              "The line number of an error in the code.",
              "The total number of users on the server.",
              "The version of the HTTP protocol.",
              "A secret code to access the API."],
             0, "HTTP status codes indicate the result of a request (200=success, 404=not found, 500=error, etc.)."),
            
            ("What does the HTTP status code 200 generally mean?",
             ["Not Found", "Server Error", "OK (The request was successful)", "Unauthorized", "Bad Request"],
             2, "Status code 200 means the request was successful."),
            
            ("What does the HTTP status code 404 generally mean?",
             ["OK", "Server Error", "Not Found (The requested resource could not be found)", "Unauthorized", "Moved Permanently"],
             2, "Status code 404 means the requested resource was not found on the server."),
            
            ("What is a 'route' or 'endpoint' in a backend application?",
             ["The main function that starts the server.",
              "A specific URL path (e.g., /api/users) that performs a specific function.",
              "A file that contains all the HTML.",
              "The connection cable to the internet.",
              "A database table."],
             1, "A route/endpoint is a specific URL path that triggers a specific backend function."),
            
            ("What does the acronym 'CRUD' stand for?",
             ["Create, Read, Update, Delete",
              "Connect, Run, Update, Debug",
              "Create, Route, Understand, Deploy",
              "Call, Read, Use, Destroy",
              "Code, Review, Undo, Deploy"],
             0, "CRUD stands for Create, Read, Update, Delete - the four basic database operations."),
            
            ("What is a 'query parameter' in a URL?",
             ["The main domain name (e.g., https://www.google.com/search?q=google.com).",
              "The HTTP method (e.g., GET, POST).",
              "The part after the ? (e.g., id=123) used to filter or pass data.",
              "The password to access the website.",
              "The protocol (e.g., https://)."],
             2, "Query parameters come after the ? in a URL (e.g., ?id=123) to pass data to the server."),
        ]
        
        quiz_1 = models.Quiz(
            title="Backend Development - Basic Foundations",
            description="Fundamental backend concepts: servers, APIs, databases, HTTP, and basic terminology",
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
            ("What is the main difference between an HTTP GET and POST request?",
             ["GET is for sending data, POST is for retrieving data.",
              "GET retrieves data (and passes data in the URL), POST submits new data (and passes data in the request body).",
              "GET is secure, POST is not secure.",
              "GET is for databases, POST is for APIs.",
              "There is no difference; they are interchangeable."],
             1, "GET retrieves data with parameters in URL, POST submits data in the request body."),
            
            ("Which SQL command is used to retrieve all data from a table named users?",
             ["GET * FROM users;", "SELECT * FROM users;", "READ * FROM users;", "FETCH users ALL;", "SELECT users ALL;"],
             1, "SELECT * FROM users; is the SQL command to retrieve all data from a table."),
            
            ("Which SQL command is used to add a new user to a users table?",
             ["ADD INTO users (name) VALUES ('Alice');",
              "CREATE USER 'Alice' IN users;",
              "INSERT INTO users (name) VALUES ('Alice');",
              "UPDATE users SET name = 'Alice';",
              "NEW USER ('Alice') IN users;"],
             2, "INSERT INTO is the SQL command to add new records to a table."),
            
            ("In a REST API, which HTTP method is typically used to update an existing resource (e.g., change a user's name)?",
             ["GET", "POST", "UPDATE", "PUT or PATCH", "REFRESH"],
             3, "PUT (full update) or PATCH (partial update) are used to modify existing resources."),
            
            ("In a REST API, which HTTP method is typically used to delete a resource?",
             ["GET", "POST", "DELETE", "REMOVE", "STOP"],
             2, "DELETE is the HTTP method used to remove a resource."),
            
            ("What is the purpose of a try...catch block in backend code?",
             ["To write database queries.",
              "To define API routes.",
              "To handle errors gracefully without crashing the server.",
              "To loop through an array of data.",
              "To create a new function."],
             2, "try...catch blocks handle errors gracefully to prevent server crashes."),
            
            ("What is a 'foreign key' in a SQL database?",
             ["A key used to encrypt the database.",
              "The main ID for a table (that is a Primary Key).",
              "A field in one table that uniquely identifies a row of another table, linking them.",
              "A key that is not from your country.",
              "A type of index."],
             2, "A foreign key links two tables by referencing the primary key of another table."),
            
            ("What is the purpose of an index in a database table?",
             ["To significantly speed up data retrieval (queries) on specific columns.",
              "To define the data type of a column.",
              "To create a backup of the table.",
              "To provide a numbered list of all rows.",
              "To delete data from the table."],
             0, "Indexes speed up data retrieval by creating efficient lookup structures on columns."),
            
            ("How would you select only the name column from a users table where the age is 30?",
             ["SELECT * FROM users WHERE age = 30;",
              "SELECT name FROM users WHERE age = 30;",
              "GET name FROM users WHERE age = 30;",
              "SELECT name FROM users (age = 30);",
              "SELECT name WHERE age = 30 FROM users;"],
             1, "SELECT name FROM users WHERE age = 30; retrieves only the name column with the condition."),
            
            ("What is 'hashing' in the context of user passwords?",
             ["Encrypting a password so it can be decrypted later.",
              "Hiding the password file.",
              "Storing the password in plain text.",
              "Running a one-way algorithm to turn a password into a unique, fixed-length string that cannot be reversed.",
              "Deleting the password after the user logs out."],
             3, "Hashing is a one-way algorithm that creates a unique string that cannot be reversed."),
            
            ("Why should you never store plain text passwords in a database?",
             ["It takes up too much storage space.",
              "It is slower to query.",
              "If the database is breached, an attacker will have all user passwords.",
              "It is not supported by SQL.",
              "It makes user login too fast."],
             2, "Storing plain text passwords is a security risk - breaches expose all user credentials."),
            
            ("What is the body of an HTTP POST request used for?",
             ["To specify the URL of the API.",
              "To carry the data (e.g., JSON payload) being sent to the server.",
              "To store the HTTP status code.",
              "To store the authentication token.",
              "It is not used for anything."],
             1, "The request body carries the data payload (like JSON) being sent to the server."),
            
            ("What is the WHERE clause used for in a SQL query?",
             ["To specify which table to query.",
              "To filter the results based on a condition.",
              "To sort the results.",
              "To join two tables.",
              "To specify which columns to return."],
             1, "WHERE clause filters query results based on specified conditions."),
            
            ("What is the main difference between SQL and NoSQL databases?",
             ["SQL is free; NoSQL is paid.",
              "SQL stores data in tables (structured); NoSQL is non-relational (e.g., document-based) and more flexible.",
              "SQL is for backend; NoSQL is for frontend.",
              "SQL is old; NoSQL is new.",
              "SQL is fast; NoSQL is slow."],
             1, "SQL uses structured tables, while NoSQL is flexible and non-relational (documents, key-value, etc.)."),
            
            ("What is an 'environment variable' (e.g., in a .env file)?",
             ["A variable that stores the weather.",
              "A variable that is hard-coded directly into the application logic.",
              "A configuration variable (e.g., API key, database password) stored outside the application code.",
              "A global variable in the frontend.",
              "A type of CSS variable."],
             2, "Environment variables store configuration (API keys, passwords) outside the code for security."),
            
            ("What is a JOIN clause used for in SQL?",
             ["To combine rows from two or more tables based on a related column.",
              "To join two different databases together.",
              "To add a new user to a table.",
              "To filter results.",
              "To connect to the database."],
             0, "JOIN combines rows from multiple tables based on related columns."),
            
            ("How do you parse a JSON string named jsonString into a JavaScript object?",
             ["JSON.parse(jsonString)",
              "JSON.stringify(jsonString)",
              "jsonString.toObject()",
              "new Object(jsonString)",
              "JSON.load(jsonString)"],
             0, "JSON.parse() converts a JSON string into a JavaScript object."),
            
            ("What does the HTTP status code 500 generally mean?",
             ["OK", "Not Found", "Internal Server Error (The server encountered an unexpected error).", "Unauthorized", "Bad Request"],
             2, "Status code 500 indicates an internal server error - something went wrong on the server."),
            
            ("What is 'middleware' in a backend framework (like Express.js)?",
             ["A function that runs in the middle of a request-response cycle, often used for logging, authentication, or parsing.",
              "Software that is halfway between frontend and backend.",
              "The database.",
              "A type of testing software.",
              "A code editor."],
             0, "Middleware functions execute during the request-response cycle for tasks like logging or authentication."),
            
            ("In the route /users/123, what is 123 typically referred to as?",
             ["A query parameter", "A path parameter (or route parameter)", "A header", "The request body", "A cookie"],
             1, "123 is a path/route parameter embedded in the URL path."),
        ]
        
        quiz_2 = models.Quiz(
            title="Backend Development - Intermediate Application",
            description="Intermediate concepts: HTTP methods, SQL queries, security, middleware, and REST APIs",
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
            ("A user tries to sign up with an email that already exists in the database. What is the most appropriate HTTP status code to return?",
             ["200 OK", "404 Not Found", "409 Conflict", "500 Internal Server Error", "301 Moved Permanently"],
             2, "409 Conflict is appropriate when a resource already exists (like a duplicate email)."),
            
            ("What is a 'JWT' (JSON Web Token)?",
             ["A way to store JSON files in a database.",
              "A compact, secure way to represent a user's identity (authentication) that is passed between the client and server.",
              "A JavaScript framework for building APIs.",
              "A type of NoSQL database.",
              "A testing tool for web tokens."],
             1, "JWT is a secure, compact token format for representing user identity in authentication."),
            
            ("What is the main difference between async/await and using .then() callbacks for asynchronous operations?",
             ["async/await is older and slower; .then() is modern and faster.",
              "async/await allows you to write asynchronous code that looks synchronous, making it easier to read.",
              "async/await can handle errors, while .then() cannot.",
              "async/await is for databases; .then() is for APIs.",
              "There is no functional difference."],
             1, "async/await syntax makes asynchronous code look synchronous, improving readability."),
            
            ("What is an 'ORM' (Object-Relational Mapper) like Prisma, Sequelize, or Django ORM?",
             ["A tool that lets you write SQL queries using programming language objects and methods, instead of writing raw SQL.",
              "A tool for optimizing database memory.",
              "A type of database.",
              "A monitoring tool for API traffic.",
              "A hardware component of a server."],
             0, "ORMs let you interact with databases using objects and methods instead of raw SQL."),
            
            ("What is the 'N+1 query problem'?",
             ["An error where you write one query, but it needs N+1 tables.",
              "A performance issue where you execute one query to get N items, and then N additional queries to get related data for each item.",
              "A security vulnerability.",
              "The process of testing your API N+1 times.",
              "A good practice for optimizing databases."],
             1, "N+1 problem: 1 query gets N items, then N more queries fetch related data - very inefficient."),
            
            ("How do you write a SQL query to get all posts and the name of the user who wrote them, from posts and users tables?",
             ["SELECT * FROM posts; SELECT * FROM users;",
              "SELECT * FROM posts MERGE users ON posts.user_id = users.id;",
              "SELECT posts.*, users.name FROM posts JOIN users ON posts.user_id = users.id;",
              "SELECT posts, users.name FROM posts, users;",
              "GET posts, users.name WHERE posts.user_id = users.id;"],
             2, "JOIN links tables together; SELECT specifies which columns to retrieve from each."),
            
            ("What is a 'data model' in a NoSQL database like MongoDB?",
             ["The rigid schema of tables and columns.",
              "The physical server model.",
              "The structure of the data inside a 'document' (e.g., a JSON object), defining its fields and types.",
              "A mathematical formula for querying data.",
              "A 3D model of the database."],
             2, "In NoSQL, a data model defines the structure of documents (like JSON objects) and their fields."),
            
            ("What is a primary advantage of 'GraphQL' over 'REST'?",
             ["It is much faster because it uses a different protocol than HTTP.",
              "It allows the client to request exactly the data it needs, in a single request, preventing over-fetching.",
              "It is older and more stable than REST.",
              "It is more secure by default.",
              "It can only be used with React frontends."],
             1, "GraphQL lets clients request exactly the data needed in one request, avoiding over/under-fetching."),
            
            ("What is the purpose of a package.json file in a Node.js project?",
             ["It contains the main application code.",
              "It stores all the API secrets and environment variables.",
              "It lists project metadata, dependencies (libraries), and scripts (e.g., npm start).",
              "It is the database schema.",
              "It is a log file for all API requests."],
             2, "package.json lists project metadata, dependencies, and scripts for Node.js projects."),
            
            ("What is a 'database transaction'?",
             ["A single SQL query.",
              "A sequence of one or more database operations that are treated as a single unit: either they all succeed, or they all fail.",
              "The process of selling a database.",
              "A backup of the database.",
              "The financial cost of a database."],
             1, "A transaction groups operations into a single unit - all succeed or all fail (atomicity)."),
            
            ("What is 'salting' a password, and why is it important in addition to hashing?",
             ["Adding a random string to each password before hashing it, to prevent 'rainbow table' attacks.",
              "Deleting the password after a set time.",
              "Encrypting the entire database.",
              "Adding the username to the password before hashing.",
              "Storing passwords on a different 'salty' server."],
             0, "Salting adds random data to passwords before hashing to prevent rainbow table attacks."),
            
            ("What does app.use(express.json()) do in an Express.js application?",
             ["It starts the server.",
              "It defines an API endpoint for JSON data.",
              "It is middleware that parses incoming requests with JSON payloads (e.g., from a POST request).",
              "It connects the application to a JSON-based database.",
              "It converts all outgoing responses to JSON."],
             2, "express.json() middleware parses incoming JSON payloads from request bodies."),
            
            ("What is 'CORS' (Cross-Origin Resource Sharing)?",
             ["A type of database.",
              "A backend programming language.",
              "A security mechanism in browsers that restricts a frontend in one domain from making requests to a backend in a different domain.",
              "A method for styling web pages.",
              "A testing framework."],
             2, "CORS is a browser security feature controlling cross-domain requests between frontend and backend."),
            
            ("A user tries to log in with a correct email but an incorrect password. What is the most appropriate HTTP status code to return?",
             ["404 Not Found (This is insecure, as it reveals the email doesn't exist)",
              "500 Internal Server Error",
              "200 OK (with an error message in the body)",
              "401 Unauthorized or 400 Bad Request",
              "409 Conflict"],
             3, "401 Unauthorized is appropriate for failed authentication attempts."),
            
            ("How do you write a SQL query to get the count of all users in the users table?",
             ["SELECT ALL users;", "SELECT COUNT(*) FROM users;", "COUNT users;", "SELECT users.length;", "SELECT * FROM users.count;"],
             1, "SELECT COUNT(*) FROM users; returns the total number of rows in the table."),
            
            ("What is a 'database migration'?",
             ["A set of scripts that manage and version-control the database schema (e.g., adding a table, changing a column).",
              "Moving the database from one server to another.",
              "A backup of the database.",
              "A tool for optimizing query speed.",
              "A type of SQL query."],
             0, "Migrations are version-controlled scripts that track and apply database schema changes."),
            
            ("What is the main difference between the PUT and PATCH HTTP methods?",
             ["PUT updates data; PATCH deletes data.",
              "PUT is for new resources; PATCH is for existing resources.",
              "PUT replaces the entire resource; PATCH applies a partial update to the resource.",
              "PUT is secure; PATCH is not.",
              "There is no difference."],
             2, "PUT replaces the entire resource, PATCH applies partial updates to specific fields."),
            
            ("What is 'dependency injection'?",
             ["A security attack where a hacker injects malicious code.",
              "A design pattern where a component's dependencies (e.g., a database connection, a service) are 'injected' from the outside rather than created internally.",
              "The process of installing libraries like npm install.",
              "A way to make your code dependent on a specific framework.",
              "A tool for managing environment variables."],
             1, "Dependency injection is a pattern where dependencies are provided externally, improving testability."),
            
            ("What is the difference between 'authentication' and 'authorization'?",
             ["Authentication is for new users; authorization is for existing users.",
              "Authentication is proving who you are (e.g., login); authorization is verifying what you are allowed to do (e.g., admin access).",
              "Authentication is for APIs; authorization is for databases.",
              "They are the same thing.",
              "Authentication is for the frontend; authorization is for the backend."],
             1, "Authentication verifies identity (who you are), authorization verifies permissions (what you can do)."),
            
            ("What is a 'webhook'?",
             ["An API endpoint that you call to get data.",
              "A user's hook for catching fish.",
              "An automated message (an HTTP callback) sent from one app to another when an event happens (e.g., a payment is completed).",
              "A type of testing framework.",
              "A security vulnerability."],
             2, "A webhook is an automated HTTP callback sent when an event occurs in one application to notify another."),
        ]
        
        quiz_3 = models.Quiz(
            title="Backend Development - Advanced Scenarios",
            description="Advanced backend: JWTs, ORMs, GraphQL, transactions, migrations, and authentication patterns",
            specialization_id=specialization.id,
            difficulty_level=3,
            time_limit_minutes=30
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
        print("\n✅ Successfully added Backend Development quizzes (Levels 1-3 complete!)")
        print(f"Total questions added: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_backend_dev_quizzes()
