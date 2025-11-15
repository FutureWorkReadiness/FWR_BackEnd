"""
Add Database Administration Quizzes - Levels 1, 2, and 3
This script adds 60 questions for Database Administration specialization
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_database_admin_quizzes():
    db = SessionLocal()
    try:
        # Get Database Administration specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Database Administration (DBA)"
        ).first()
        
        if not specialization:
            print("Error: Database Administration (DBA) specialization not found")
            print("Checking available specializations...")
            all_specs = db.query(models.Specialization).all()
            for spec in all_specs:
                if "database" in spec.name.lower() or "data" in spec.name.lower():
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
            ('What does "DBA" stand for?',
             ["Data Backup and Access",
              "Database Administrator",
              "Database Application",
              "Data by Algorithm",
              "Database Allocation"],
             1, "DBA stands for Database Administrator - the professional responsible for managing databases."),
            
            ('What is a "database"?',
             ["A computer program for browsing the internet.",
              "A physical server.",
              "An organized collection of structured data, stored electronically.",
              "A single spreadsheet file.",
              "A type of programming language."],
             2, "A database is an organized collection of structured data stored electronically for easy access and management."),
            
            ('What does "RDBMS" stand for?',
             ["Relational Database Management System",
              "Real-time Data Management Service",
              "Remote Database Mainframe System",
              "Relational Data Backup System",
              "Real-time Database Module"],
             0, "RDBMS stands for Relational Database Management System - software for managing relational databases."),
            
            ('What is "SQL"?',
             ["A type of server hardware.",
              "A standard language for communicating with and managing relational databases.",
              "A security protocol.",
              "A data visualization tool.",
              "A type of database backup."],
             1, "SQL (Structured Query Language) is the standard language for managing and querying relational databases."),
            
            ('What is a "table" in a database?',
             ["A visual report or dashboard.",
              "A single piece of data, like a name.",
              "A data structure that organizes information into rows and columns.",
              "A user's password.",
              "A connection to the database."],
             2, "A database table organizes data into rows (records) and columns (attributes)."),
            
            ('What is a "column" in a database table?',
             ["A single, complete record (e.g., all data for one user).",
              "A single attribute or field of data (e.g., 'Email' or 'Age').",
              "The entire database.",
              "A security permission.",
              "A backup file."],
             1, "A column represents a single attribute or field in a table (e.g., Name, Email, Age)."),
            
            ('What is a "row" in a database table?',
             ["A single attribute or field (e.g., the 'Name' column).",
              "A single, complete record or entry (e.g., all data for one user).",
              "The name of the table.",
              "A type of data (e.g., text).",
              "A SQL command."],
             1, "A row represents a single complete record or entry in a table."),
            
            ('What is a "primary key"?',
             ["A column that is used for sorting data.",
              "A column (or columns) that uniquely identifies each row in a table.",
              "The main password to the database.",
              "The first column in every table.",
              "A key that links to another table."],
             1, "A primary key is a column (or set of columns) that uniquely identifies each row in a table."),
            
            ('What is a "foreign key"?',
             ["A key that is not from your country.",
              "A column that uniquely identifies each row (this is a primary key).",
              "A column in one table that links to the primary key of another table.",
              "A password to access the table.",
              "The last column in every table."],
             2, "A foreign key is a column that references the primary key of another table, creating relationships."),
            
            ('What is a "data type"?',
             ["A type of chart (e.g., bar, pie).",
              "A classification that specifies the type of data a column can hold (e.g., INT, VARCHAR, DATE).",
              "The name of the database.",
              "A SQL command.",
              "A user's role."],
             1, "Data types specify what kind of data a column can store (e.g., INT, VARCHAR, DATE, BOOLEAN)."),
            
            ('What is a "query"?',
             ["A request sent to the database to retrieve, add, or modify data.",
              "A table of data.",
              "A database backup.",
              "A security vulnerability.",
              "A user's permission."],
             0, "A query is a request to retrieve, add, modify, or delete data from a database."),
            
            ('What does "DDL" stand for in SQL?',
             ["Data Deletion Language",
              "Data Definition Language (e.g., CREATE, ALTER, DROP)",
              "Data Duplication Language",
              "Database Download Logic",
              "Data Manipulation Language"],
             1, "DDL (Data Definition Language) includes commands like CREATE, ALTER, and DROP for defining database structures."),
            
            ('What does "DML" stand for in SQL?',
             ["Data Model Language",
              "Database Management Logic",
              "Data Manipulation Language (e.g., SELECT, INSERT, UPDATE, DELETE)",
              "Data Migration Language",
              "Data Definition Language"],
             2, "DML (Data Manipulation Language) includes commands like SELECT, INSERT, UPDATE, and DELETE for data manipulation."),
            
            ('What does "NULL" represent in a database?',
             ["The number zero (0).",
              "An empty string (\"\").",
              "The absence of a value, or an unknown value.",
              "A \"false\" boolean value.",
              "An error in the data."],
             2, "NULL represents the absence of a value or an unknown value - distinct from zero or empty string."),
            
            ('What is the basic purpose of an "index"?',
             ["To secure the database from hackers.",
              "To back up the data.",
              "To create a table.",
              "To speed up the retrieval of data (queries) from a table.",
              "To delete data."],
             3, "Indexes speed up data retrieval by creating optimized lookup structures."),
            
            ('What is "data integrity"?',
             ["The speed of the database.",
              "The overall accuracy, completeness, and consistency of data.",
              "The process of backing up data.",
              "The physical size of the database.",
              "The programming language used."],
             1, "Data integrity ensures data is accurate, complete, and consistent throughout its lifecycle."),
            
            ('What is a "database backup"?',
             ["A tool for speeding up queries.",
              "A copy of the database, used to restore it in case of data loss.",
              "A user's password.",
              "A firewall.",
              "A table of data."],
             1, "A database backup is a copy of the database used for recovery in case of data loss or corruption."),
            
            ('What is a "schema"?',
             ["A single SQL query.",
              "The logical structure or \"blueprint\" of a database (e.g., tables, columns, keys).",
              "A user account.",
              "A data visualization.",
              "A backup file."],
             1, "A schema is the logical structure or blueprint of a database, defining tables, columns, and relationships."),
            
            ('What does "DCL" stand for in SQL?',
             ["Data Cleaning Language",
              "Data Connection Language",
              "Data Control Language (e.g., GRANT, REVOKE)",
              "Data Column Language",
              "Data Creation Language"],
             2, "DCL (Data Control Language) includes commands like GRANT and REVOKE for managing access permissions."),
            
            ('What is a "NoSQL" database?',
             ["A database that has no security.",
              "A database that does not use a relational (table-based) model.",
              "A database that cannot be queried.",
              "An old, outdated type of database.",
              "A database that only stores numbers."],
             1, "NoSQL databases use non-relational models (document, key-value, graph, etc.) instead of tables."),
        ]
        
        quiz_1 = models.Quiz(
            title="Database Administration - Basic Foundations",
            description="Fundamentals: DBA role, RDBMS, SQL, tables, keys, data types, schemas, and basic database concepts",
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
            ("Which SQL command is used to retrieve all columns from a table named Employees?",
             ["GET * FROM Employees;",
              "SELECT Employees;",
              "READ * FROM Employees;",
              "SELECT * FROM Employees;",
              "SELECT ALL FROM Employees;"],
             3, "SELECT * FROM Employees; retrieves all columns from the Employees table."),
            
            ("Which SQL clause is used to filter the results of a SELECT statement?",
             ["FILTER BY",
              "WHERE",
              "GROUP BY",
              "IF",
              "LIMIT"],
             1, "The WHERE clause filters query results based on specified conditions."),
            
            ("Which SQL command is used to add a new row of data to a table?",
             ["ADD ROW",
              "CREATE ROW",
              "INSERT INTO",
              "UPDATE",
              "NEW ROW"],
             2, "INSERT INTO adds new rows to a table."),
            
            ("Which SQL command is used to modify existing data in a table?",
             ["MODIFY",
              "CHANGE",
              "INSERT INTO",
              "UPDATE",
              "ALTER TABLE"],
             3, "UPDATE modifies existing data in a table."),
            
            ("Which SQL command is used to delete a row from a table?",
             ["REMOVE ROW FROM ... WHERE ...;",
              "DELETE FROM ... WHERE ...;",
              "DROP ROW FROM ... WHERE ...;",
              "TRUNCATE ... WHERE ...;",
              "CLEAR ROW FROM ... WHERE ...;"],
             1, "DELETE FROM ... WHERE ... removes specific rows from a table."),
            
            ("Which SQL command is used to create a new table?",
             ["NEW TABLE ...",
              "BUILD TABLE ...",
              "INSERT TABLE ...",
              "ALTER TABLE ...",
              "CREATE TABLE ..."],
             4, "CREATE TABLE creates a new table with specified columns and data types."),
            
            ("Which SQL command is used to add a new column to an existing table?",
             ["ALTER TABLE ... ADD COLUMN ...",
              "UPDATE TABLE ... ADD COLUMN ...",
              "CREATE COLUMN ... ON ...",
              "MODIFY TABLE ... ADD ...",
              "INSERT COLUMN ... INTO ..."],
             0, "ALTER TABLE ... ADD COLUMN ... adds a new column to an existing table."),
            
            ("Which SQL command completely removes a table (and all its data) from the database?",
             ["DELETE TABLE ...",
              "REMOVE TABLE ...",
              "TRUNCATE TABLE ...",
              "DROP TABLE ...",
              "CLEAR TABLE ..."],
             3, "DROP TABLE completely removes a table and all its data from the database."),
            
            ("Which SQL clause is used to sort the result set?",
             ["SORT BY",
              "ORDER BY",
              "GROUP BY",
              "ALIGN BY",
              "WHERE"],
             1, "ORDER BY sorts query results in ascending or descending order."),
            
            ("Which SQL aggregate function returns the total number of rows?",
             ["SUM()",
              "TOTAL()",
              "COUNT(*)",
              "ROWS()",
              "MAX()"],
             2, "COUNT(*) returns the total number of rows in a result set."),
            
            ("Which SQL aggregate function calculates the average of a numerical column?",
             ["MEAN()",
              "MEDIAN()",
              "AVG()",
              "AVERAGE()",
              "CALCULATE()"],
             2, "AVG() calculates the average value of a numerical column."),
            
            ("Which SQL clause is used with aggregate functions to group rows with the same values?",
             ["ORDER BY",
              "GROUP BY",
              "WHERE",
              "JOIN",
              "CLUSTER BY"],
             1, "GROUP BY groups rows with the same values, often used with aggregate functions."),
            
            ("Which SQL command is used to combine rows from two tables based on a related column?",
             ["MERGE",
              "COMBINE",
              "JOIN",
              "CONNECT",
              "RELATE"],
             2, "JOIN combines rows from two or more tables based on related columns."),
            
            ("What is the difference between DELETE and TRUNCATE?",
             ["DELETE removes rows one by one (and can be filtered); TRUNCATE removes all rows at once (and is faster).",
              "DELETE removes a table; TRUNCATE removes a row.",
              "DELETE is permanent; TRUNCATE can be undone.",
              "DELETE removes all rows; TRUNCATE removes only some.",
              "There is no difference."],
             0, "DELETE can be filtered and logs each deletion; TRUNCATE removes all rows quickly without logging."),
            
            ("Which SQL command is used to give a user permission to SELECT data?",
             ["ALLOW SELECT ON ... TO ...;",
              "GRANT SELECT ON ... TO ...;",
              "CREATE USER ... WITH SELECT;",
              "SET PERMISSION SELECT ON ... TO ...;",
              "AUTHORIZE SELECT ON ... TO ...;"],
             1, "GRANT SELECT ON ... TO ... gives a user permission to query data."),
            
            ("Which SQL command is used to remove a user's permission?",
             ["REMOVE",
              "DELETE",
              "DENY",
              "UNGRANT",
              "REVOKE"],
             4, "REVOKE removes previously granted permissions from a user."),
            
            ("Which SQL command is used to create an index?",
             ["CREATE INDEX ... ON ... (...);",
              "ADD INDEX ... ON ... (...);",
              "CREATE NEW INDEX ...;",
              "ALTER TABLE ... ADD INDEX ...;",
              "INDEX TABLE ... (...);"],
             0, "CREATE INDEX ... ON ... creates an index on specified columns to improve query performance."),
            
            ("What is a LEFT JOIN?",
             ["It returns only the rows that match in both tables.",
              "It returns all rows from the left table, and the matched rows from the right table.",
              "It returns all rows from the right table, and the matched rows from the left table.",
              "It returns all rows from both tables.",
              "It returns only the rows on the \"left\" side of the database."],
             1, "LEFT JOIN returns all rows from the left table plus matched rows from the right table."),
            
            ("Which operator is used for pattern matching in a WHERE clause?",
             ["MATCH",
              "LIKE",
              "SIMILAR",
              "REGEX",
              "CONTAINS"],
             1, "LIKE is used for pattern matching with wildcards (% and _) in WHERE clauses."),
            
            ("What does the DISTINCT keyword do in a SELECT statement?",
             ["It sorts the results.",
              "It returns only unique (non-duplicate) values for a column.",
              "It counts the number of rows.",
              "It joins two tables.",
              "It makes the query run faster."],
             1, "DISTINCT returns only unique values, removing duplicates from the result set."),
        ]
        
        quiz_2 = models.Quiz(
            title="Database Administration - Intermediate Application",
            description="SQL commands: SELECT, INSERT, UPDATE, DELETE, JOINs, aggregate functions, permissions, and indexes",
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
            ("What is the difference between the WHERE clause and the HAVING clause?",
             ["WHERE filters rows before grouping; HAVING filters groups after grouping.",
              "WHERE filters groups; HAVING filters rows.",
              "WHERE is for SELECT; HAVING is for UPDATE.",
              "WHERE is for numbers; HAVING is for text.",
              "They are identical."],
             0, "WHERE filters rows before aggregation; HAVING filters grouped results after aggregation."),
            
            ('What is a "transaction" in a database?',
             ["A single SQL query.",
              "A sequence of one or more database operations (e.g., INSERT, UPDATE) that are treated as a single, atomic unit.",
              "A backup of the database.",
              "A user's permission.",
              "The financial cost of a query."],
             1, "A transaction is a set of operations treated as a single unit - all succeed or all fail (atomicity)."),
            
            ('What does "ACID" stand for?',
             ["Access, Control, Integrity, Data",
              "Atomicity, Consistency, Isolation, Durability",
              "Authorize, Commit, Isolate, Delete",
              "A secure, coded, integrated database",
              "Asynchronous, Concurrent, Independent, Data"],
             1, "ACID: Atomicity, Consistency, Isolation, Durability - key properties of database transactions."),
            
            ('What is "database normalization"?',
             ["The process of making a database \"normal\" by deleting all old data.",
              "The process of organizing data in a database to reduce redundancy and improve data integrity.",
              "The process of adding more indexes to a database.",
              "The process of backing up a database.",
              "The process of encrypting a database."],
             1, "Normalization organizes data to reduce redundancy and improve integrity through structured design."),
            
            ('What is a "view" in SQL?',
             ["A physical copy of a table.",
              "A virtual table based on the result-set of a stored SQL query.",
              "A user's permission.",
              "A visual dashboard.",
              "A database log file."],
             1, "A view is a virtual table created from a saved query - no data duplication."),
            
            ('What is a "stored procedure"?',
             ["A backup file that is \"stored\" safely.",
              "A set of pre-compiled SQL statements that are stored in the database and can be executed as a single unit.",
              "A table that stores procedures.",
              "A type of database user.",
              "A log of all past queries."],
             1, "Stored procedures are pre-compiled SQL code stored in the database for reuse and efficiency."),
            
            ('What is a "trigger"?',
             ["A type of security attack.",
              "A stored procedure that automatically executes (fires) in response to a specific event (e.g., INSERT, UPDATE).",
              "A button on a dashboard.",
              "A hardware device for a server.",
              "A manual backup process."],
             1, "Triggers automatically execute in response to database events like INSERT, UPDATE, or DELETE."),
            
            ('What is a "subquery"?',
             ["A query that is not as good as a normal query.",
              "A query that is embedded (nested) inside another SQL query.",
              "A query that updates data.",
              "A query that only runs on a subset of data.",
              "A query that is saved as a view."],
             1, "A subquery is a query nested inside another query, often used in WHERE or FROM clauses."),
            
            ('What is a "full backup"?',
             ["A backup of only the new or changed files.",
              "A complete copy of the entire database.",
              "A backup of only the database schema.",
              "A backup of only the transaction log.",
              "A backup that is \"full\" and has no more space."],
             1, "A full backup creates a complete copy of the entire database."),
            
            ('What is a "differential backup"?',
             ["A backup of only the data that has changed since the last full backup.",
              "A backup of only the data that has changed since the last backup of any kind.",
              "A complete copy of the database.",
              "A backup of only the transaction log.",
              "A backup that is \"different\" every time."],
             0, "Differential backups capture only changes since the last full backup."),
            
            ("What is the purpose of the EXPLAIN or EXPLAIN PLAN command?",
             ["To \"explain\" the data in a table.",
              "To get help on a SQL command.",
              "To show the execution plan (how the database will run the query), used for performance tuning.",
              "To describe the table schema.",
              "To create a database diagram."],
             2, "EXPLAIN shows how the database will execute a query, helping with performance optimization."),
            
            ("Why can too many indexes be bad for performance?",
             ["They slow down SELECT queries.",
              "They take up too much disk space and slow down write operations (e.g., INSERT, UPDATE).",
              "They cause security vulnerabilities.",
              "They corrupt the data.",
              "They cannot be bad; more indexes are always better."],
             1, "Too many indexes consume disk space and slow down INSERT/UPDATE operations that must update all indexes."),
            
            ('What is the difference between a "clustered" and "non-clustered" index?',
             ["A clustered index is for a cluster of servers; a non-clustered index is for one server.",
              "A clustered index defines the physical order of the data; a non-clustered index is a separate structure that points to the data.",
              "A clustered index is slow; a non-clustered index is fast.",
              "A clustered index is for text; a non-clustered index is for numbers.",
              "There is no difference."],
             1, "Clustered indexes determine physical data order; non-clustered indexes are separate lookup structures."),
            
            ('What is the purpose of a "transaction log"?',
             ["A log of all users who have logged in.",
              "A log of all slow queries.",
              "A serial record of all changes made to the database, used for recovery.",
              "A file that stores the database schema.",
              "A backup file."],
             2, "Transaction logs record all database changes, enabling recovery and maintaining data consistency."),
            
            ('What is "denormalization"?',
             ["The process of making a database \"abnormal\" or corrupt.",
              "The process of intentionally adding redundant data to a normalized database to improve query performance.",
              "The process of deleting data.",
              "Another name for normalization.",
              "A security attack."],
             1, "Denormalization intentionally adds redundancy to improve read performance at the cost of some integrity."),
            
            ("What is the difference between UNION and UNION ALL?",
             ["UNION selects all rows; UNION ALL selects only some.",
              "UNION removes duplicate rows; UNION ALL includes all rows, including duplicates.",
              "UNION is for joining tables; UNION ALL is for joining databases.",
              "UNION is fast; UNION ALL is slow.",
              "There is no difference."],
             1, "UNION removes duplicates; UNION ALL keeps all rows including duplicates (faster)."),
            
            ('What is a "composite key"?',
             ["A key made of two or more columns, used together to uniquely identify a row.",
              "A key that is stored in a separate file.",
              "A key that is encrypted.",
              "Another name for a foreign key.",
              "A key that is not reliable."],
             0, "A composite key uses multiple columns together to uniquely identify rows."),
            
            ('What is a "CHECK constraint"?',
             ["A constraint that \"checks\" if a user has permission.",
              "A rule that limits the values that can be placed in a column (e.g., Age > 18).",
              "A constraint that checks if a primary key is unique.",
              "A constraint that checks for viruses.",
              "A constraint that links to a foreign key."],
             1, "CHECK constraints enforce business rules by limiting acceptable values in a column."),
            
            ('What is a "CTE" (Common Table Expression)?',
             ["A \"Critical Table Error.\"",
              "A temporary, named result set that you can reference within a SELECT, INSERT, UPDATE, or DELETE statement.",
              "A permanent table.",
              "A tool for database cleaning.",
              "A type of index."],
             1, "CTEs are temporary named result sets that improve query readability and organization."),
            
            ('What is an "incremental backup"?',
             ["A backup of only the data that has changed since the last backup (full, differential, or incremental).",
              "A backup of only the data that has changed since the last full backup.",
              "A complete copy of the database.",
              "A backup that slowly \"increments\" in size.",
              "A backup of only the transaction log."],
             0, "Incremental backups capture only changes since the last backup of any type."),
        ]
        
        quiz_3 = models.Quiz(
            title="Database Administration - Advanced Scenarios",
            description="Advanced concepts: transactions (ACID), normalization, views, stored procedures, triggers, backups, and optimization",
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
        print("\n✅ Successfully added Database Administration quizzes (Levels 1-3 complete!)")
        print(f"Total questions added: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_database_admin_quizzes()
