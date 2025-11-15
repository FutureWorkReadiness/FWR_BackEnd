"""
Add Backend Development Quizzes - Levels 4 and 5
This script adds 40 questions for Backend Development specialization (Expert through Strategic)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_backend_dev_advanced_quizzes():
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
            ("What is 'caching' and when would you use a tool like Redis?",
             ["Caching is storing copies of frequently accessed data (e.g., database results) in a temporary, fast-access location (like Redis) to reduce load and improve speed.",
              "Caching is a way to log all API requests.",
              "Caching is a tool for writing unit tests.",
              "Caching is the process of hashing passwords.",
              "Caching is a type of database, like SQL."],
             0, "Caching stores frequently accessed data in fast memory (like Redis) to reduce database load and improve response times."),
            
            ("What is a 'message queue' (e.g., RabbitMQ, Kafka)?",
             ["A database for storing chat messages.",
              "A service that allows different parts of an application (e.g., microservices) to communicate asynchronously by sending messages to a queue.",
              "A type of API.",
              "A load balancer.",
              "A tool for managing API documentation."],
             1, "Message queues enable asynchronous communication between services by queuing messages for processing."),
            
            ("What is 'Docker' and what problem does it solve for backend developers?",
             ["A text editor for backend code.",
              "A tool that 'containerizes' an application and its dependencies, ensuring it runs the same way everywhere (e.g., on a developer's laptop and in production).",
              "A database management tool.",
              "A code testing framework.",
              "A brand of server hardware."],
             1, "Docker containerizes applications with their dependencies, ensuring consistent behavior across all environments."),
            
            ("What is a 'CI/CD pipeline'?",
             ["A database connection string.",
              "An automated process (e.g., using Jenkins, GitHub Actions) that builds, tests, and deploys code changes.",
              "A type of network protocol.",
              "A security feature for APIs.",
              "A way to manage user permissions."],
             1, "CI/CD pipelines automate the building, testing, and deployment of code changes."),
            
            ("What is the main difference between a 'monolithic' architecture and a 'microservices' architecture?",
             ["A monolith is for frontend; microservices are for backend.",
              "A monolith is built in one large codebase; microservices break the application into many small, independent services.",
              "A monolith uses SQL; microservices use NoSQL.",
              "A monolith is modern; microservices are old.",
              "A monolith is secure; microservices are not."],
             1, "Monolithic architecture uses one large codebase, while microservices split functionality into independent services."),
            
            ("What is a 'load balancer'?",
             ["A tool that checks for errors in your code.",
              "A server that distributes incoming network traffic across multiple backend servers to improve responsiveness and reliability.",
              "A database feature for balancing data.",
              "A security tool for blocking hackers.",
              "A tool for managing environment variables."],
             1, "Load balancers distribute traffic across multiple servers to improve performance and reliability."),
            
            ("What is 'unit testing' in a backend context?",
             ["Testing the entire application from end to end.",
              "Manually testing the API with a tool like Postman.",
              "Testing a single, isolated 'unit' of code (e.g., one function, one class) to ensure it works correctly.",
              "Testing the frontend user interface.",
              "A performance test to see how many units it can handle."],
             2, "Unit testing tests individual functions or classes in isolation to verify correct behavior."),
            
            ("What is 'integration testing' in a backend context?",
             ["Testing a single function.",
              "Testing how multiple 'units' or services work together (e.g., does the API route correctly call the database service?).",
              "Testing the user interface.",
              "A test to see if a new developer can integrate with the team.",
              "Manually testing the application."],
             1, "Integration testing verifies that multiple components or services work together correctly."),
            
            ("What is a 'WebSocket' and how does it differ from HTTP?",
             ["It is a more secure version of HTTP.",
              "It is a protocol that allows for two-way, persistent communication between a client and server (ideal for real-time apps like chat).",
              "It is a tool for styling web pages.",
              "It is a database for storing web data.",
              "It is another name for a REST API."],
             1, "WebSocket enables bidirectional, persistent connections for real-time communication, unlike HTTP's request-response model."),
            
            ("What is a 'reverse proxy' (e.g., Nginx)?",
             ["A proxy that hides the client's identity.",
              "A server that sits in front of the main backend server, handling tasks like load balancing, SSL termination, and caching.",
              "A type of database.",
              "A tool for debugging code in reverse.",
              "A security attack."],
             1, "A reverse proxy sits in front of backend servers, handling load balancing, SSL, caching, and request routing."),
            
            ("What is 'rate limiting' and why is it important for a public API?",
             ["A way to make your API run faster.",
              "A process of limiting how many requests a user can make in a given time, to prevent abuse and ensure stability.",
              "A feature for ranking API users.",
              "A tool for testing API speed.",
              "A database optimization technique."],
             1, "Rate limiting restricts the number of requests per time period to prevent abuse and maintain API stability."),
            
            ("What does 'ACID' stand for in the context of SQL database transactions?",
             ["Atomicity, Consistency, Isolation, Durability",
              "Authenticate, Commit, Isolate, Deploy",
              "Asynchronous, Consistent, Integrated, Deployed",
              "A secure, coded, integrated database",
              "All, Combined, In, Data"],
             0, "ACID ensures reliable database transactions: Atomicity, Consistency, Isolation, and Durability."),
            
            ("What is the 'CAP Theorem' in distributed systems?",
             ["A theorem stating that a distributed system can only provide two of three guarantees: Consistency, Availability, and Partition tolerance.",
              "A security protocol for APIs.",
              "A rule for naming database tables.",
              "A theorem about CPU processing limits.",
              "A method for caching data."],
             0, "CAP Theorem states distributed systems can only guarantee two of: Consistency, Availability, Partition tolerance."),
            
            ("What is 'database sharding'?",
             ["A way to encrypt a database.",
              "A scaling technique that splits a large database into smaller, faster, more manageable parts (shards).",
              "A security attack on a database.",
              "The process of deleting old data.",
              "A way to create a backup of a database."],
             1, "Sharding horizontally partitions a database into smaller, faster shards for better scalability."),
            
            ("What is 'Infrastructure as Code' (IaC) (e.g., Terraform, CloudFormation)?",
             ["Writing your backend code directly in assembly language.",
              "A 'dummy' infrastructure used for testing.",
              "The process of managing and provisioning infrastructure (e.g., servers, databases, networks) through machine-readable definition files, rather than manual setup.",
              "A type of AI that writes code for you.",
              "A way to store your entire application in a single file."],
             2, "IaC manages infrastructure through code files rather than manual configuration, enabling version control and automation."),
            
            ("How would you begin to debug a memory leak in a Node.js application?",
             ["By restarting the server, as this permanently fixes memory leaks.",
              "By using a profiler or heapdump tool to take snapshots of the memory and analyze what objects are not being garbage collected.",
              "By deleting all console.log statements.",
              "By blaming the frontend team.",
              "By adding more RAM to the server."],
             1, "Use profilers and heap dumps to identify objects not being garbage collected to find memory leaks."),
            
            ("What is 'gRPC'?",
             ["A modern, high-performance API framework (often used in microservices) that uses HTTP/2 and Protocol Buffers.",
              "A graphical tool for managing React projects.",
              "A type of SQL database.",
              "A security protocol for encrypting data.",
              "A text editor for backend developers."],
             0, "gRPC is a high-performance RPC framework using HTTP/2 and Protocol Buffers, common in microservices."),
            
            ("What is 'serverless' computing (e.g., AWS Lambda, Google Cloud Functions)?",
             ["A backend with no servers, as all logic runs in the browser.",
              "A model where a cloud provider manages the server infrastructure, and you only provide the code (functions) which run on-demand.",
              "An old-fashioned way of programming from the 1980s.",
              "A server that has no operating system.",
              "A type of frontend framework."],
             1, "Serverless computing abstracts server management - you provide functions that run on-demand on cloud infrastructure."),
            
            ("What is 'database normalization'?",
             ["The process of making a database 'normal' by deleting all strange data.",
              "The process of structuring a SQL database to reduce data redundancy and improve data integrity.",
              "A way to make a NoSQL database behave like a SQL database.",
              "A scaling technique.",
              "A security feature."],
             1, "Normalization structures databases to minimize redundancy and improve data integrity through proper table design."),
            
            ("What is an 'idempotent' operation in the context of an API?",
             ["An operation that is very slow and inefficient.",
              "An operation that has no effect on the database.",
              "An operation that can be called multiple times with the same input, but will only change the state once. (e.g., DELETE /user/123).",
              "An operation that creates a new resource every time it is called.",
              "An operation that is not secure."],
             2, "Idempotent operations produce the same result when called multiple times with the same parameters."),
        ]
        
        quiz_4 = models.Quiz(
            title="Backend Development - Expert & Specialization",
            description="Expert topics: caching, Docker, microservices, testing, WebSockets, gRPC, and advanced architecture",
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
            ("Design a simple system to handle a 'forgot password' flow. What are the key components and steps?",
             ["1. User requests reset. 2. Backend generates a single-use, expiring token. 3. Token is stored (hashed) in the DB. 4. Send token in an email link. 5. User clicks link. 6. Backend validates token. 7. User provides new password.",
              "1. User requests reset. 2. Backend sends the user's old password in an email.",
              "1. User requests reset. 2. Backend generates a permanent token that never expires. 3. User provides new password.",
              "1. User requests reset. 2. Backend temporarily deletes the user's account. 3. User signs up again.",
              "1. User requests reset. 2. Backend asks the user for their new password immediately and saves it."],
             0, "Secure password reset uses single-use, expiring tokens sent via email to verify user identity."),
            
            ("Your application's API is experiencing slow read queries. What are the first three things you would investigate?",
             ["1. The frontend CSS. 2. The user's internet speed. 3. The color of the buttons.",
              "1. Check for missing database indexes. 2. Check for 'N+1 query' problems. 3. Analyze slow queries (e.g., EXPLAIN ANALYZE) to see if they can be optimized.",
              "1. Restart the server. 2. Restart the database. 3. Restart the user's computer.",
              "1. Blame the DevOps team. 2. Blame the network. 3. Blame the hardware.",
              "1. Immediately switch from SQL to NoSQL. 2. Rewrite the entire API in a different language. 3. Buy a faster server."],
             1, "Investigate missing indexes, N+1 queries, and analyze query execution plans to optimize slow reads."),
            
            ("A startup asks you to build their backend. What factors influence your choice between a monolith and microservices?",
             ["A monolith is always better because it's simpler.",
              "Microservices are always better because they are 'modern.'",
              "The choice depends on team size, project complexity, and scalability needs. A monolith is faster to start; microservices are more flexible for large, complex systems.",
              "The choice depends on the frontend framework (e.g., React requires microservices).",
              "The choice depends on the color of the startup's logo."],
             2, "Architecture choice depends on team size, complexity, and scalability - monoliths are simpler to start, microservices scale better."),
            
            ("What is a 'SQL injection' attack, and what is the best way to prevent it?",
             ["An attack where a user inputs malicious SQL code into a form field to dump the database; prevented by using prepared statements (parameterized queries).",
              "An attack where a user 'injects' a new server; prevented by a firewall.",
              "An attack where a user 'injects' JavaScript; prevented by hashing passwords.",
              "An attack where a user 'injects' SQL code; prevented by validating user input on the frontend.",
              "An attack where a user steals the SQL database file; prevented by rate limiting."],
             0, "SQL injection exploits unsafe queries - prevent it with parameterized queries/prepared statements."),
            
            ("Design a simple URL shortener service (like bit.ly). What would the database schema and API endpoints look like?",
             ["A urls table with id, original_url, and short_code. Endpoints: POST /shorten and GET /:short_code.",
              "A users table only. Endpoint: GET /users.",
              "A urls table with the full HTML of the original page. Endpoint: POST /copy_page.",
              "A urls table with short_code only. Endpoints: GET /all_urls and DELETE /all_urls.",
              "No database needed; just use a large JSON file."],
             0, "URL shortener needs a urls table with id, original_url, short_code, and endpoints for creating and redirecting."),
            
            ("What is 'horizontal scaling' (scaling out) vs. 'vertical scaling' (scaling up)?",
             ["Horizontal is adding more code; vertical is adding more features.",
              "Horizontal is adding more machines (e.g., more servers); vertical is adding more power (e.g., more RAM/CPU) to one machine.",
              "Horizontal is for SQL; vertical is for NoSQL.",
              "Horizontal is for frontend; vertical is for backend.",
              "Horizontal is fast; vertical is slow."],
             1, "Horizontal scaling adds more servers; vertical scaling adds more resources (CPU/RAM) to existing servers."),
            
            ("What is 'event-driven architecture'?",
             ["An architecture based on user click events.",
              "A system where services communicate by producing and consuming 'events' (messages about a state change), often via a message queue.",
              "A monolith architecture.",
              "An architecture that only runs during special events.",
              "A type of database."],
             1, "Event-driven architecture uses events (state changes) and message queues for asynchronous service communication."),
            
            ("You need to process millions of image uploads, resize them into 3 different formats, and store them. How would you design this system to be scalable and responsive?",
             ["Do all the resizing in the API request synchronously and make the user wait.",
              "1. The API receives the image and immediately uploads it to a storage bucket (e.g., S3). 2. It sends a 'resize' job to a message queue. 3. A separate 'worker' service reads from the queue, does the resizing, and saves the new versions.",
              "Store all the images directly in the SQL database.",
              "Tell the user to resize the images on their computer before uploading.",
              "Use a serverless function for the API, but do the resizing in the same function."],
             1, "Use async processing: upload to storage, queue resize jobs, process with worker services for scalability."),
            
            ("What is 'database replication' (master-slave) and what is its primary benefit?",
             ["The process of creating multiple copies (replicas) of a database. It improves read performance and provides high availability.",
              "A security attack where a hacker replicates your database.",
              "A 'master' database that controls all the 'slave' APIs.",
              "A way to delete data from a database.",
              "A method for encrypting the database."],
             0, "Database replication creates copies for improved read performance and high availability through redundancy."),
            
            ("What is a 'blue-green deployment' strategy?",
             ["A deployment where you use blue and green servers.",
              "A strategy where you have two identical production environments ('blue' and 'green'). You deploy to the 'green' environment, test it, and then switch traffic from 'blue' (old) to 'green' (new).",
              "A deployment that is very 'green' (environmentally friendly).",
              "A strategy where you deploy only on Tuesdays.",
              "A strategy where you test code in the 'blue' environment and deploy in the 'green' one."],
             1, "Blue-green deployment maintains two environments, deploying to one while the other serves traffic, then switching."),
            
            ("What is 'OAuth 2.0'?",
             ["A specific username and password for an API.",
              "A type of database.",
              "An open standard for delegated authorization. It allows users to grant a third-party app limited access to their resources (e.g., 'Sign in with Google').",
              "A new version of HTTP.",
              "A security attack."],
             2, "OAuth 2.0 is an authorization framework allowing third-party limited access without sharing credentials."),
            
            ("How would you design the database tables for a 'friends list' feature in a social media app?",
             ["One users table with a column called friends that stores a (bad) comma-separated list.",
              "A users table and a friendships table. friendships has user_id_1, user_id_2, and status (e.g., 'pending', 'accepted').",
              "A users table and a friends table, where friends has every possible combination of users.",
              "Just one users table and no way to link them.",
              "A friends table with user_name and friend_name (bad, as names can change)."],
             1, "Use a users table and friendships junction table with user_id_1, user_id_2, and status for relationship tracking."),
            
            ("What are the key trade-offs of using GraphQL instead of REST for a new, large-scale project?",
             ["REST is always better because it's simpler.",
              "GraphQL is always better because it's newer.",
              "GraphQL gives frontend flexibility (no over-fetching), but adds backend complexity (schema, resolvers). REST is simple and well-understood, but can lead to many endpoints.",
              "REST is for frontend, GraphQL is for backend.",
              "GraphQL doesn't work with SQL databases."],
             2, "GraphQL offers flexibility and avoids over-fetching but adds complexity; REST is simpler but less flexible."),
            
            ("What is a 'Distributed Denial-of-Service' (DDoS) attack and what are common mitigation strategies?",
             ["An attack where one person steals all the data. Mitigated by hashing passwords.",
              "An attack where a service is flooded with traffic from many sources to overwhelm it. Mitigated by services like Cloudflare, rate limiting, and firewalls.",
              "An attack where a user 'denies' they made a request. Mitigated by logging.",
              "An attack where the database is deleted. Mitigated by backups.",
              "An attack where the server is physically stolen."],
             1, "DDoS attacks flood services with traffic - mitigate with CDNs, rate limiting, and traffic filtering."),
            
            ("What is the 'eventual consistency' model in distributed systems?",
             ["A model where the system is 'eventually' correct, but is wrong most of the time.",
              "A model guaranteeing that if no new updates are made, all replicas of a database will eventually converge to the same value.",
              "A model where the system is 'consistent' during events.",
              "A model where data is never consistent.",
              "A model where data is always 100% consistent, immediately (that is 'strong consistency')."],
             1, "Eventual consistency ensures that without new updates, all replicas will converge to the same state over time."),
            
            ("You are designing a new, public-facing REST API. What are the three most important security concerns to address from day one?",
             ["1. Authentication (who is this?), 2. Authorization (what can they do?), and 3. Input Validation (e.g., prevent SQL injection).",
              "1. The color scheme, 2. The API documentation, 3. The server's brand name.",
              "1. Making it as fast as possible, 2. Making it as cheap as possible, 3. Using a cool name.",
              "1. Hashing passwords, 2. Hashing passwords again, 3. Hashing passwords a third time.",
              "1. Making all endpoints GET requests, 2. Storing all data in one file, 3. Never using a database."],
             0, "Critical security concerns: authentication (identity), authorization (permissions), and input validation (injection prevention)."),
            
            ("What are the key performance indicators (KPIs) you would monitor for a high-traffic backend service?",
             ["1. Error Rate (e.g., 5xx, 4xx), 2. Latency (response time), 3. Throughput (requests per second).",
              "1. Number of code comments, 2. Number of developers, 3. Number of meetings.",
              "1. The frontend's Lighthouse score.",
              "1. How many new users sign up per day.",
              "1. The total cost of the server."],
             0, "Monitor error rates, latency (response time), and throughput (requests/sec) for backend performance."),
            
            ("What is a 'canary release'?",
             ["A release where you only deploy the code to servers in the Canary Islands.",
              "A strategy where you release the new version to a small subset of users (e.g., 5%), monitor for errors, and then gradually roll it out to everyone.",
              "A 'dead' release (like a canary in a coal mine) that fails.",
              "A release that is very 'loud' and announced to all users.",
              "Another name for a 'blue-green' deployment."],
             1, "Canary releases deploy to a small user subset first, monitoring for issues before full rollout."),
            
            ("What is a 'service-oriented architecture' (SOA)?",
             ["An older architectural pattern (a precursor to microservices) where applications are built from a collection of distinct, loosely-coupled 'services.'",
              "An architecture where you only use 'serverless' functions.",
              "An architecture where every developer is focused on 'customer service.'",
              "A monolithic architecture.",
              "A type of hardware."],
             0, "SOA is an architectural pattern using loosely-coupled services, a precursor to microservices."),
            
            ("Your API is used by a mobile app with unreliable internet. What strategies can you implement on the backend to support this?",
             ["Tell the mobile app user to get better internet.",
              "Make all API endpoints idempotent, support data compression, and design the API to allow for partial or 'delta' updates.",
              "Send all data as large, uncompressed video files.",
              "Block all users with slow internet connections.",
              "Re-build the entire backend on the user's phone."],
             1, "Support unreliable connections with idempotent endpoints, compression, and delta/partial update support."),
        ]
        
        quiz_5 = models.Quiz(
            title="Backend Development - Strategic & Architectural",
            description="Strategic design: system architecture, scalability, security, deployment strategies, and real-world problem solving",
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
        print("\n✅ Successfully added Backend Development quizzes (Levels 4-5 complete!)")
        print(f"Total questions added: {len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_backend_dev_advanced_quizzes()
