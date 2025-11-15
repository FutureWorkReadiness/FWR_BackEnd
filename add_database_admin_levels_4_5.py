"""
Add Database Administration Quizzes - Levels 4 and 5
This script adds 40 questions for Database Administration specialization (Expert through Strategic)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_database_admin_advanced_quizzes():
    db = SessionLocal()
    try:
        # Get Database Administration specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Database Administration (DBA)"
        ).first()
        
        if not specialization:
            print("Error: Database Administration (DBA) specialization not found")
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
            ('What is a "database lock"?',
             ["A physical lock on the server room.",
              "A mechanism to prevent two users from modifying the same piece of data at the same time (concurrency control).",
              "A security feature that \"locks\" a user out.",
              "A type of encryption key.",
              "A backup file."],
             1, "Database locks are concurrency control mechanisms that prevent conflicting simultaneous data modifications."),
            
            ('What is a "deadlock"?',
             ["A situation where a database server has crashed.",
              "A situation where two or more transactions are \"stuck,\" each waiting for the other to release a lock.",
              "A security vulnerability.",
              "A corrupt backup file.",
              "A lock on a user account."],
             1, "Deadlocks occur when transactions wait for each other to release locks, creating a circular dependency."),
            
            ('What is "SQL injection" and what is the best way to prevent it?',
             ["An attack where malicious SQL is \"injected\" into a query; prevented by using prepared statements (parameterized queries).",
              "An attack where a user \"injects\" JavaScript; prevented by a firewall.",
              "An attack where a server is flooded with traffic; prevented by rate limiting.",
              "An attack where a user steals a backup; prevented by encryption.",
              "An attack where a database is deleted; prevented by GRANT/REVOKE."],
             0, "SQL injection exploits unvalidated input; parameterized queries safely separate data from SQL code."),
            
            ('What is "database replication"?',
             ["The process of creating multiple copies of a database (replicas), often on different servers, for high availability and read scalability.",
              "A security attack where a hacker replicates your database.",
              "A \"master\" database that controls all the \"slave\" APIs.",
              "The process of creating a single backup.",
              "A method for encrypting the database."],
             0, "Replication creates synchronized database copies across servers for availability and performance."),
            
            ('What is "database clustering"?',
             ["A group of databases that are all \"clustered\" in one location.",
              "A group of servers (nodes) that work together as a single system to provide high availability and load balancing.",
              "A type of index.",
              "A security feature.",
              "The process of sharding a database."],
             1, "Clustering connects multiple servers that work together for high availability and load distribution."),
            
            ('What is "database sharding"?',
             ["A way to encrypt a database.",
              "A \"horizontal partitioning\" technique that splits a large database into smaller, faster parts (shards).",
              "A security attack on a database.",
              "The process of deleting old data.",
              "A way to create a backup of a database."],
             1, "Sharding horizontally partitions data across multiple databases to improve scalability and performance."),
            
            ('What is the difference between "OLTP" and "OLAP"?',
             ["OLTP is for analytics; OLAP is for transactions.",
              "OLTP (Online Transaction Processing) is for fast, day-to-day operations; OLAP (Online Analytical Processing) is for complex analysis.",
              "OLTP is old; OLAP is new.",
              "OLTP is for backups; OLAP is for recovery.",
              "There is no difference."],
             1, "OLTP handles transactional operations; OLAP handles complex analytical queries on historical data."),
            
            ('What is a "data warehouse"?',
             ["A small database on a laptop.",
              "A large, central repository of data, optimized for analysis and reporting (OLAP), that integrates data from many sources.",
              "A single Excel file.",
              "A tool for data visualization.",
              "A server for hosting a website."],
             1, "Data warehouses centralize and integrate data from multiple sources for analytical processing."),
            
            ('What is "Point-in-Time Recovery" (PITR)?',
             ["The ability to recover a database exactly as it was at a specific time (e.g., 9:15 AM), usually by using backups and transaction logs.",
              "The ability to recover only one \"point\" of data.",
              "A backup that is taken at a specific \"point in time.\"",
              "A type of security attack.",
              "A tool for query optimization."],
             0, "PITR restores databases to any specific moment using backups and transaction logs."),
            
            ('What is a "query optimizer"?',
             ["A tool that rewrites your SQL queries to be more efficient.",
              "A hardware device that speeds up a server.",
              "A component of the database that determines the most efficient way to execute a query.",
              "A DBA who specializes in writing fast queries.",
              "A type of index."],
             2, "Query optimizers analyze and choose the most efficient execution plan for SQL queries."),
            
            ('What is a "connection pool"?',
             ["A \"pool\" of water used to cool a server.",
              "A cache of database connections that are kept open and reused, reducing the overhead of opening/closing connections.",
              "A group of users who are allowed to connect.",
              "A type of network security group.",
              "A table that lists all database connections."],
             1, "Connection pools maintain reusable database connections to reduce connection overhead."),
            
            ('What is "Transparent Data Encryption" (TDE)?',
             ["Encryption that is \"transparent\" and easy to break.",
              "A feature that encrypts the entire database at rest (on the disk) without the application needing to be aware of it.",
              "Encryption of data as it travels over the network (e.g., SSL/TLS).",
              "A tool for encrypting passwords.",
              "A type of firewall."],
             1, "TDE encrypts data files on disk transparently, without requiring application changes."),
            
            ('What is "auditing" in a database context?',
             ["The process of checking the database for financial errors.",
              "The process of tracking and logging specific database events (e.g., who accessed what data at what time).",
              "The process of optimizing a query.",
              "The process of backing up a database.",
              "The process of installing a database."],
             1, "Database auditing tracks and logs access and operations for security and compliance."),
            
            ('What is a "column-store" index/database?',
             ["A database that only stores one column.",
              "A database that stores data by column rather than by row, which is highly efficient for analytical (OLAP) queries.",
              "A database that is stored in an Excel column.",
              "A type of encrypted index.",
              "A standard row-based (row-store) database."],
             1, "Column-store databases organize data by columns, optimizing analytical query performance."),
            
            ('What is "Multi-Version Concurrency Control" (MVCC)?',
             ["A \"concurrency control\" method where readers do not block writers, by showing them a \"snapshot\" of the data.",
              "A tool for managing multiple \"versions\" of a database.",
              "A security protocol.",
              "A backup strategy.",
              "A type of database clustering."],
             0, "MVCC allows concurrent reads and writes by maintaining multiple data versions (snapshots)."),
            
            ('What is a "Disaster Recovery" (DR) plan?',
             ["A plan for how to prevent all disasters.",
              "A plan for how to restore IT infrastructure (including databases) at a secondary site after a major disaster.",
              "A plan for firing employees after a disaster.",
              "A plan for backing up a single file.",
              "A plan for managing a security breach."],
             1, "DR plans define procedures for restoring IT systems after catastrophic failures or disasters."),
            
            ('What is a "hot standby" vs. a "cold standby"?',
             ["A hot standby is a server that is overheating.",
              "A hot standby is a replica server that is on and ready to take over; a cold standby is a server that is off and must be started.",
              "A hot standby is for summer; a cold standby is for winter.",
              "A hot standby is a backup; a cold standby is a live server.",
              "A hot standby is insecure; a cold standby is secure."],
             1, "Hot standbys are active and ready for immediate failover; cold standbys require startup time."),
            
            ('What is "capacity planning"?',
             ["The process of planning how many users can access the database.",
              "The process of monitoring and forecasting resource usage (e.g., disk, CPU, RAM) to ensure the database can meet future demand.",
              "The process of cleaning up old data to free \"capacity.\"",
              "The process of designing a new database.",
              "The process of planning a backup."],
             1, "Capacity planning forecasts resource needs to ensure databases can handle future growth."),
            
            ('What is a "maintenance plan"?',
             ["A plan for physically cleaning the server room.",
              "A set of automated tasks (e.g., backups, index rebuilds, integrity checks) that run on a schedule to keep the database healthy.",
              "A plan for updating the database software.",
              "A plan for training DBAs.",
              "A user's guide to the database."],
             1, "Maintenance plans automate routine tasks like backups, index optimization, and integrity checks."),
            
            ('What is "Role-Based Access Control" (RBAC)?',
             ["A method of managing permissions by assigning users to \"roles\" (e.g., \"Analyst,\" \"Admin\") and then granting permissions to those roles.",
              "A method where every user gets their own specific permissions.",
              "A security attack.",
              "A type of database.",
              "A hardware device for access control."],
             0, "RBAC simplifies permission management by assigning rights to roles rather than individual users."),
        ]
        
        quiz_4 = models.Quiz(
            title="Database Administration - Expert & Specialization",
            description="Expert DBA: locks, deadlocks, SQL injection, replication, clustering, sharding, OLTP/OLAP, PITR, TDE, MVCC, and DR",
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
            ("What are the key factors when choosing a SQL vs. a NoSQL database for a new project?",
             ["SQL is for old projects; NoSQL is for new projects.",
              "SQL is for simple data; NoSQL is for complex data.",
              "The choice depends on data structure (schema-on-write vs. schema-on-read), scalability needs, and consistency (ACID) requirements.",
              "SQL is for small data; NoSQL is for \"big data.\"",
              "The choice depends on the programming language being used."],
             2, "Choose based on schema flexibility, scalability requirements, and ACID consistency needs."),
            
            ("You need to design a database schema for a simple blog (with users, posts, and comments). What are the key tables and relationships?",
             ["One big table for users, posts, and comments.",
              "Users (PK: user_id), Posts (PK: post_id, FK: user_id), Comments (PK: comment_id, FK: post_id, FK: user_id).",
              "Posts (PK: post_id) and Comments (PK: comment_id).",
              "Users (PK: user_id) and Posts_and_Comments (PK: id).",
              "Blog (PK: id, Text: all_data)."],
             1, "Normalized design: Users table, Posts with user FK, Comments with post and user FKs."),
            
            ("A developer reports that a specific query is running very slowly. What are your first five steps to troubleshoot it?",
             ["1. Restart the server. 2. Blame the network. 3. Blame the developer. 4. Add more RAM. 5. Delete old data.",
              "1. Get the query. 2. Run an EXPLAIN PLAN. 3. Check for missing/unused indexes. 4. Check for table scans. 5. Check for out-of-date statistics.",
              "1. Ask the user to run it at night. 2. Tell the developer to rewrite the app. 3. Switch to NoSQL. 4. Buy a new server. 5. Defragment the disk.",
              "1. Check the firewall. 2. Check the user's password. 3. Check the transaction log. 4. Run a full backup. 5. Update the server OS.",
              "1. Add indexes to every column. 2. Denormalize the tables. 3. Drop all constraints. 4. Give the user admin rights. 5. Restart the query."],
             1, "Systematic approach: get query, analyze execution plan, check indexes, look for scans, verify statistics."),
            
            ("What is the business case for \"denormalization\"? When would you strategically use it?",
             ["Never; it is a bad practice.",
              "When you want to save disk space.",
              "In a read-heavy (OLAP) system where query performance is more important than data redundancy, and JOINs are too costly.",
              "In a write-heavy (OLTP) system to make INSERTs faster.",
              "When you are first designing the database and don't know the schema."],
             2, "Denormalize in read-heavy systems when JOIN performance costs outweigh redundancy concerns."),
            
            ('What is a "High Availability" (HA) strategy, and how does it differ from "Disaster Recovery" (DR)?',
             ["HA is about surviving a disaster; DR is about surviving a component failure.",
              "HA is about automatic recovery from component failure (e.g., clustering); DR is about manual recovery from a site-wide disaster (e.g., restoring backups).",
              "They are the same thing.",
              "HA is a backup plan; DR is a replication plan.",
              "HA is for software; DR is for hardware."],
             1, "HA addresses component failures with automatic failover; DR addresses catastrophic site failures."),
            
            ('What is the "CAP Theorem," and why is it important for distributed databases?',
             ["A theorem stating a distributed system can only provide two of three guarantees: Consistency, Availability, and Partition Tolerance.",
              "A theorem about CPU processing (Capacity, Availability, Performance).",
              "A rule for naming database tables.",
              "A security protocol for APIs.",
              "A method for caching data."],
             0, "CAP Theorem: distributed systems must choose between consistency, availability, and partition tolerance."),
            
            ('What are the pros and cons of using a "Database-as-a-Service" (DBaaS) like AWS RDS vs. a self-managed server?',
             ["DBaaS is more expensive and complex; self-managed is cheaper and easier.",
              "DBaaS is easier (handles patches, backups); self-managed gives you full control but requires more admin overhead.",
              "DBaaS is less secure; self-managed is more secure.",
              "DBaaS is for small data; self-managed is for big data.",
              "There are no pros to using DBaaS."],
             1, "DBaaS reduces operational overhead but costs more; self-managed offers control with higher admin burden."),
            
            ('What is a "database migration" strategy, and how would you perform one with minimal downtime?',
             ["A strategy for moving data; best way is to shut down the app for a weekend.",
              "A strategy for changing database vendors; best way is to use a \"blue-green\" deployment or \"log-shipping\" replication.",
              "A strategy for deleting old data.",
              "A strategy for backing up data.",
              "A strategy for hiring a new DBA."],
             1, "Minimize downtime using blue-green deployments or continuous replication strategies."),
            
            ('What is a "data retention policy," and what is the DBA\'s role in enforcing it?',
             ["A policy for how long to \"retain\" employees; the DBA has no role.",
              "A business/legal rule for how long data must be kept; the DBA implements it using automated scripts to archive or delete old data.",
              "A policy for how much data a user can \"retain\" in their head.",
              "A policy about database backups.",
              "A policy for how many tables a database can \"retain.\""],
             1, "DBAs implement retention policies through automated archival and deletion scripts."),
            
            ('What is "data governance"?',
             ["The process of governing a country using data.",
              "The overall management of the availability, usability, integrity, and security of data in an enterprise.",
              "A type of database.",
              "A dashboard for executives.",
              "A SQL command."],
             1, "Data governance manages data quality, security, availability, and compliance across the organization."),
            
            ("How would you design a backup strategy for a critical 24/7 e-commerce database?",
             ["One full backup every night.",
              "A daily full backup, combined with differential backups every hour, and transaction log backups every 10 minutes.",
              "One full backup per month.",
              "Just use replication; no backups are needed.",
              "A weekly full backup."],
             1, "Critical systems need layered backups: daily full, hourly differential, frequent transaction logs."),
            
            ('What is a "database fire drill" and why is it crucial?',
             ["A drill for how to evacuate the server room during a fire.",
              "A scheduled test of your entire disaster recovery plan, including restoring backups to a test server, to prove you can recover.",
              "A security test to see if your firewall works.",
              "A performance test.",
              "A meeting to discuss what to do in a disaster."],
             1, "Fire drills test DR procedures by actually restoring backups to verify recovery capability."),
            
            ("How would you architecturally secure a new database server?",
             ["Put it on the public internet, but with a very strong password.",
              "Place it in a private subnet, use a firewall/security groups, enable TDE, enforce SSL, and use RBAC.",
              "Just install antivirus software on it.",
              "Give the 'sa' (admin) password to all developers.",
              "Turn on auditing and nothing else."],
             1, "Layer security: network isolation, firewalls, encryption (TDE/SSL), and role-based access control."),
            
            ('What is the strategic trade-off of using "read replicas"?',
             ["Pro: Improves read performance. Con: Costs more money.",
              "Pro: Improves read performance. Con: Can have \"replication lag\" (stale data) and adds complexity.",
              "Pro: Improves write performance. Con: Slows down reads.",
              "Pro: More secure. Con: Slower performance.",
              "There are no trade-offs; they are always better."],
             1, "Read replicas improve read scalability but introduce replication lag and operational complexity."),
            
            ('What is the DBA\'s main responsibility in a "root cause analysis" (RCA) after a database outage?',
             ["To find which developer or user to blame for the outage.",
              "To provide all relevant logs and metrics to help identify the technical cause of the failure.",
              "To write the final report for the executives.",
              "To immediately buy a new server.",
              "To restore the database from backup (this is part of recovery, not RCA)."],
             1, "DBAs provide technical evidence (logs, metrics) to help identify root causes of failures."),
            
            ('How would you strategically implement a "least privilege" security model?',
             ["Give everyone \"read-only\" access to everything.",
              "Give no one access to anything.",
              "Start with no permissions, create \"roles\" for each job function, grant only the minimum permissions needed to those roles, and assign users to roles.",
              "Give everyone \"admin\" rights, but tell them not to do anything bad.",
              "Use a single \"app\" user for all developers and applications."],
             2, "Least privilege: start with zero access, create role-based permissions, grant only necessary rights."),
            
            ('What is the DBA\'s role in a "CI/CD pipeline"?',
             ["The DBA has no role; it is a DevOps process.",
              "To manage and automate database schema changes (migrations) and test them to ensure they don't break the application.",
              "To manually approve every single deployment.",
              "To run the application's unit tests.",
              "To build the application code."],
             1, "DBAs manage automated database migrations and testing within CI/CD workflows."),
            
            ('What is the difference between "horizontal scaling" and "vertical scaling" for a database?',
             ["Horizontal is adding more code; vertical is adding more features.",
              "Horizontal is adding more servers (e.g., sharding/clustering); vertical is adding more power (e.g., CPU/RAM) to one server.",
              "Horizontal is for SQL; vertical is for NoSQL.",
              "Horizontal is for frontend; vertical is for backend.",
              "Horizontal is fast; vertical is slow."],
             1, "Horizontal scaling adds servers (sharding/clustering); vertical scaling adds resources to existing servers."),
            
            ('What is a "fill factor" in an index, and what is the strategic trade-off of setting it?',
             ["How \"full\" the database is; set it to 100% to save space.",
              "The percentage of space on an index page to fill; 100% is good for reads, but a lower value (e.g., 80%) is better for write-heavy tables to reduce page splits.",
              "A setting for how full the transaction log can get.",
              "A setting for how much RAM the database can use.",
              "There is no trade-off; it should always be 100%."],
             1, "Fill factor balances read performance (100%) vs. write performance (lower values reduce page splits)."),
            
            ('What is a database "isolation level" and what is the trade-off of using "Serializable"?',
             ["A setting for how \"isolated\" a server is; Serializable is the most secure.",
              "A setting that controls \"concurrency\"; Serializable is the strongest (prevents all issues), but it kills performance by using many locks.",
              "A setting for backups; Serializable means one at a time.",
              "A setting for users; Serializable means only one user can connect.",
              "There is no trade-off; Serializable is always the best."],
             1, "Serializable isolation prevents all concurrency issues but severely impacts performance through locking."),
        ]
        
        quiz_5 = models.Quiz(
            title="Database Administration - Strategic & Architectural",
            description="Strategic DBA: SQL vs NoSQL, schema design, performance troubleshooting, HA vs DR, CAP theorem, DBaaS, migration, governance, security architecture, scaling",
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
        print("\n✅ Successfully added Database Administration quizzes (Levels 4-5 complete!)")
        print(f"Total questions added: {len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_database_admin_advanced_quizzes()
