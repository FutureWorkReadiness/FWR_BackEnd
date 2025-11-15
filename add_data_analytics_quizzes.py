#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from app.database import SessionLocal
from app import models_hierarchical as models

def add_data_analytics_quizzes():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("            Adding Data Analytics Quizzes (Levels 1-5)")
        print("=" * 80)
        
        # Find Data Analytics specialization
        data_analytics_spec = db.query(models.Specialization).filter(
            models.Specialization.name == "Data Analytics"
        ).first()
        
        if not data_analytics_spec:
            print("❌ Data Analytics specialization not found!")
            return
        
        print(f"✅ Found Data Analytics specialization (ID: {data_analytics_spec.id})")
        
        # Delete existing Data Analytics quizzes to avoid duplicates
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == data_analytics_spec.id
        ).all()
        
        if existing_quizzes:
            print(f"🗑️  Deleting {len(existing_quizzes)} existing Data Analytics quizzes...")
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
                models.Quiz.specialization_id == data_analytics_spec.id
            ).delete()
            db.commit()
        
        # Level 1: Basic Foundations
        print("\n📝 Adding Level 1: Data Analytics Basics...")
        quiz1 = models.Quiz(
            title="Data Analytics Basics - Level 1",
            description="Fundamental concepts of data analytics including SQL basics, KPIs, dashboards, and basic statistics",
            specialization_id=data_analytics_spec.id,
            difficulty_level=1,
            time_limit_minutes=30
        )
        db.add(quiz1)
        db.flush()
        
        level1_questions = [
            {
                "question": "What is the primary goal of Data Analytics?",
                "options": [
                    "To build artificial intelligence and predictive models.",
                    "To inspect, clean, transform, and model data to find useful information and support decision-making.",
                    "To design and build databases from scratch.",
                    "To write the code for websites and mobile apps.",
                    "To secure a company's network from hackers."
                ],
                "correct": 1,
                "explanation": "Data Analytics focuses on inspecting, cleaning, transforming, and modeling data to discover useful information and support decision-making."
            },
            {
                "question": "What does 'SQL' stand for?",
                "options": [
                    "Simple Query Language",
                    "Structured Query Language",
                    "Server Quality Logic",
                    "System Query Link",
                    "Standard Question Language"
                ],
                "correct": 1,
                "explanation": "SQL stands for Structured Query Language, used to manage and query data in relational databases."
            },
            {
                "question": "What is a 'KPI'?",
                "options": [
                    "Key Performance Indicator: A measurable value that shows how effectively a company is achieving key business objectives.",
                    "Key Python Integration: A library for coding.",
                    "Key Performance Index: A ranking of all employees.",
                    "Key Programming Interface: Another name for an API.",
                    "Known Problem Indicator: A list of bugs."
                ],
                "correct": 0,
                "explanation": "KPI stands for Key Performance Indicator - a measurable value showing how effectively objectives are being achieved."
            },
            {
                "question": "What is a 'dashboard'?",
                "options": [
                    "A code editor for writing SQL.",
                    "A visual display of the most important information, consolidated on a single screen, to monitor performance at a glance.",
                    "The main page of a Microsoft Excel file.",
                    "A server that stores data.",
                    "A type of database."
                ],
                "correct": 1,
                "explanation": "A dashboard is a visual display consolidating important information on a single screen for quick monitoring."
            },
            {
                "question": "Which of the following is a 'data visualization' tool?",
                "options": [
                    "Microsoft Word",
                    "Tableau or Power BI",
                    "Node.js",
                    "GitHub",
                    "VS Code"
                ],
                "correct": 1,
                "explanation": "Tableau and Power BI are popular data visualization and business intelligence tools."
            },
            {
                "question": "What is a 'CSV' file?",
                "options": [
                    "A 'Comma-Separated Values' file, a plain text file for storing tabular data.",
                    "A 'Computer Security Version' file, used for antivirus.",
                    "A 'Calculated Sheet Version' file, specific to Excel.",
                    "A 'Customer Service validation' file.",
                    "A type of image file."
                ],
                "correct": 0,
                "explanation": "CSV stands for Comma-Separated Values, a simple format for storing tabular data in plain text."
            },
            {
                "question": "What is the 'mean' of a set of numbers?",
                "options": [
                    "The middle value.",
                    "The most common value.",
                    "The average value (sum of values divided by the count).",
                    "The highest value.",
                    "The lowest value."
                ],
                "correct": 2,
                "explanation": "The mean is the average value, calculated by summing all values and dividing by the count."
            },
            {
                "question": "What is the 'median' of a set of numbers?",
                "options": [
                    "The middle value after the numbers have been sorted.",
                    "The most common value.",
                    "The average value.",
                    "The difference between the highest and lowest value.",
                    "The sum of all values."
                ],
                "correct": 0,
                "explanation": "The median is the middle value when numbers are sorted in order."
            },
            {
                "question": "In a database, what is a 'table'?",
                "options": [
                    "A visual chart or graph.",
                    "A collection of related data organized in a grid of rows and columns.",
                    "A single piece of data, like a name.",
                    "A query used to get data.",
                    "The entire database itself."
                ],
                "correct": 1,
                "explanation": "A table is a collection of related data organized in rows and columns."
            },
            {
                "question": "What is a 'row' in a database table?",
                "options": [
                    "A single, complete record or entry (e.g., all information for one customer).",
                    "A single characteristic or attribute (e.g., the 'Email' column).",
                    "The name of the table.",
                    "The title of a chart.",
                    "A calculation."
                ],
                "correct": 0,
                "explanation": "A row represents a single, complete record in a table."
            },
            {
                "question": "What is a 'column' in a database table?",
                "options": [
                    "A single, complete record (e.g., all info for one customer).",
                    "A set of data values for a specific attribute (e.g., 'Age' for all customers).",
                    "The entire table.",
                    "A filter on a dashboard.",
                    "A security setting."
                ],
                "correct": 1,
                "explanation": "A column contains data values for a specific attribute across all records."
            },
            {
                "question": "What is 'data cleaning'?",
                "options": [
                    "The process of visualizing data.",
                    "The process of deleting all old data.",
                    "The process of finding and fixing errors, inconsistencies, and missing values in a dataset.",
                    "The process of writing SQL queries.",
                    "The process of designing a dashboard."
                ],
                "correct": 2,
                "explanation": "Data cleaning involves finding and fixing errors, inconsistencies, and missing values in datasets."
            },
            {
                "question": "Which chart type is best for showing trends over time?",
                "options": [
                    "A pie chart",
                    "A line chart",
                    "A scatter plot",
                    "A bar chart",
                    "A histogram"
                ],
                "correct": 1,
                "explanation": "Line charts are ideal for showing trends and changes over time."
            },
            {
                "question": "Which chart type is best for comparing values across different categories?",
                "options": [
                    "A bar chart",
                    "A line chart",
                    "A scatter plot",
                    "A pie chart",
                    "A treemap"
                ],
                "correct": 0,
                "explanation": "Bar charts are excellent for comparing values across different categories."
            },
            {
                "question": "Which chart type is best for showing the relationship between two numerical variables?",
                "options": [
                    "A pie chart",
                    "A bar chart",
                    "A scatter plot",
                    "A line chart",
                    "A KPI card"
                ],
                "correct": 2,
                "explanation": "Scatter plots show relationships between two numerical variables."
            },
            {
                "question": "What is the 'mode' of a set of data?",
                "options": [
                    "The average value.",
                    "The middle value.",
                    "The value that appears most frequently.",
                    "The highest value.",
                    "The range of values."
                ],
                "correct": 2,
                "explanation": "The mode is the value that appears most frequently in a dataset."
            },
            {
                "question": "What is 'Microsoft Excel'?",
                "options": [
                    "A database management system.",
                    "A programming language.",
                    "A spreadsheet program used for organizing, analyzing, and visualizing data.",
                    "A cloud computing service.",
                    "A tool for writing SQL code."
                ],
                "correct": 2,
                "explanation": "Microsoft Excel is a spreadsheet program used for data organization, analysis, and visualization."
            },
            {
                "question": "What is a 'data type'?",
                "options": [
                    "The name of a dashboard.",
                    "A classification that specifies which type of value a variable has (e.g., String, Integer, Date).",
                    "A SQL query.",
                    "A type of chart.",
                    "A folder for storing data."
                ],
                "correct": 1,
                "explanation": "A data type classifies what kind of value a variable can hold (e.g., String, Integer, Date)."
            },
            {
                "question": "What does 'ETL' stand for in data analytics?",
                "options": [
                    "Extract, Transform, Load",
                    "Error, Test, Launch",
                    "Export, Translate, Link",
                    "Estimate, Test, Learn",
                    "E-commerce, Tools, Logic"
                ],
                "correct": 0,
                "explanation": "ETL stands for Extract, Transform, Load - the process of moving data from source to destination."
            },
            {
                "question": "What is 'data integrity'?",
                "options": [
                    "The speed of the database.",
                    "The visualization of the data.",
                    "The maintenance, accuracy, consistency, and completeness of data.",
                    "The process of deleting data.",
                    "The file format of the data."
                ],
                "correct": 2,
                "explanation": "Data integrity refers to maintaining the accuracy, consistency, and completeness of data."
            }
        ]
        
        for q_data in level1_questions:
            question = models.Question(
                quiz_id=quiz1.id,
                question_text=q_data["question"],
                question_type='multiple_choice',
                explanation=q_data["explanation"]
            )
            db.add(question)
            db.flush()
            
            for idx, option_text in enumerate(q_data["options"]):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(idx == q_data["correct"])
                )
                db.add(option)
        
        print(f"✅ Added {len(level1_questions)} questions for Level 1")
        
        # Level 2: Intermediate Application
        print("\n📝 Adding Level 2: Data Analytics Intermediate...")
        quiz2 = models.Quiz(
            title="Data Analytics Intermediate - Level 2",
            description="Intermediate concepts including SQL queries, Excel functions, BI tools, and data validation",
            specialization_id=data_analytics_spec.id,
            difficulty_level=2,
            time_limit_minutes=40
        )
        db.add(quiz2)
        db.flush()
        
        level2_questions = [
            {
                "question": "Which SQL command is used to retrieve data from a database?",
                "options": ["GET", "READ", "SELECT", "FETCH", "OPEN"],
                "correct": 2,
                "explanation": "SELECT is the SQL command used to retrieve data from a database."
            },
            {
                "question": "Which SQL clause is used to filter the results of a query?",
                "options": ["WHERE", "FILTER", "GROUP BY", "SELECT", "SORT"],
                "correct": 0,
                "explanation": "The WHERE clause filters query results based on specified conditions."
            },
            {
                "question": "What is a 'Pivot Table' in Excel used for?",
                "options": [
                    "To write SQL code.",
                    "To summarize, group, and analyze large amounts of data in a table.",
                    "To create a visual line chart.",
                    "To format the color of cells.",
                    "To check for spelling errors."
                ],
                "correct": 1,
                "explanation": "Pivot Tables summarize, group, and analyze large datasets in Excel."
            },
            {
                "question": "What is the purpose of the VLOOKUP function in Excel?",
                "options": [
                    "To calculate the average of a column.",
                    "To sort data alphabetically.",
                    "To find a value in one column of a table and return a corresponding value from another column.",
                    "To create a chart.",
                    "To filter rows based on a condition."
                ],
                "correct": 2,
                "explanation": "VLOOKUP finds a value in one column and returns a corresponding value from another column."
            },
            {
                "question": "Which SQL clause is used to combine rows from two or more tables?",
                "options": ["MERGE", "COMBINE", "GROUP", "JOIN", "APPEND"],
                "correct": 3,
                "explanation": "JOIN combines rows from two or more tables based on related columns."
            },
            {
                "question": "Which SQL aggregate function returns the total number of rows?",
                "options": ["SUM()", "TOTAL()", "COUNT()", "AVG()", "MAX()"],
                "correct": 2,
                "explanation": "COUNT() returns the total number of rows in a result set."
            },
            {
                "question": "Which SQL clause is used to sort the results of a query?",
                "options": ["SORT BY", "ALIGN BY", "ORDER BY", "GROUP BY", "ARRANGE"],
                "correct": 2,
                "explanation": "ORDER BY sorts query results in ascending or descending order."
            },
            {
                "question": "In a BI tool, what is a 'Dimension'?",
                "options": [
                    "A numerical, measurable value (e.g., 'Sales', 'Quantity').",
                    "A qualitative, descriptive value (e.g., 'Region', 'Product Name').",
                    "The name of the dashboard.",
                    "A filter.",
                    "A type of chart."
                ],
                "correct": 1,
                "explanation": "Dimensions are qualitative, descriptive values like Region or Product Name."
            },
            {
                "question": "In a BI tool, what is a 'Measure'?",
                "options": [
                    "A numerical, quantitative value that can be aggregated (e.g., 'Sales', 'Profit').",
                    "A descriptive, categorical value (e.g., 'Customer Name').",
                    "The title of a chart.",
                    "A comment or note.",
                    "A date or time."
                ],
                "correct": 0,
                "explanation": "Measures are numerical values that can be aggregated, like Sales or Profit."
            },
            {
                "question": "What does the SQL GROUP BY clause do?",
                "options": [
                    "It sorts the results in a group.",
                    "It groups rows that have the same values in specified columns, so aggregate functions can be applied.",
                    "It combines two tables together.",
                    "It filters the results.",
                    "It updates the data in a table."
                ],
                "correct": 1,
                "explanation": "GROUP BY groups rows with same values so aggregate functions can be applied."
            },
            {
                "question": "What is a 'primary key' in a database table?",
                "options": [
                    "A column that contains non-essential data.",
                    "A column (or set of columns) that uniquely identifies each row in a table.",
                    "The first column in every table.",
                    "A key used to unlock the database.",
                    "A link to another table."
                ],
                "correct": 1,
                "explanation": "A primary key uniquely identifies each row in a table."
            },
            {
                "question": "What is a 'foreign key' in a database table?",
                "options": [
                    "A column that is not from your country.",
                    "A column that uniquely identifies each row (this is a primary key).",
                    "A column (or set of columns) that links to the primary key of another table.",
                    "A password to access the table.",
                    "The last column in every table."
                ],
                "correct": 2,
                "explanation": "A foreign key links to the primary key of another table, establishing relationships."
            },
            {
                "question": "Which SQL aggregate function calculates the average of a column?",
                "options": ["MEAN()", "MEDIAN()", "AVERAGE()", "AVG()", "TOTAL() / COUNT()"],
                "correct": 3,
                "explanation": "AVG() calculates the average value of a numeric column."
            },
            {
                "question": "Which SQL command is used to add a new row of data to a table?",
                "options": ["ADD ROW", "CREATE ROW", "INSERT INTO", "UPDATE", "ALTER TABLE"],
                "correct": 2,
                "explanation": "INSERT INTO adds new rows of data to a table."
            },
            {
                "question": "Which SQL command is used to modify existing data in a table?",
                "options": ["MODIFY", "CHANGE", "INSERT INTO", "UPDATE", "ALTER TABLE"],
                "correct": 3,
                "explanation": "UPDATE modifies existing data in a table."
            },
            {
                "question": "What is a common way to handle missing data (null values) during analysis?",
                "options": [
                    "Delete the entire dataset.",
                    "Report the data as-is; the errors don't matter.",
                    "Remove the rows, or replace the missing value with a default (e.g., 0, mean, median).",
                    "Close the program and restart it.",
                    "Replace all missing values with the word 'missing'."
                ],
                "correct": 2,
                "explanation": "Common approaches include removing rows or replacing nulls with default values like mean or median."
            },
            {
                "question": "What is the purpose of the SUMIF function in Excel?",
                "options": [
                    "To sum all numbers in a range.",
                    "To sum numbers in a range only if a specific condition is met.",
                    "To check if a sum is correct.",
                    "To find the sum of two different tables.",
                    "To create a chart."
                ],
                "correct": 1,
                "explanation": "SUMIF sums numbers only when they meet a specified condition."
            },
            {
                "question": "What does the LIKE operator do in a SQL WHERE clause?",
                "options": [
                    "It checks for an exact match.",
                    "It is used for pattern matching (e.g., WHERE name LIKE 'A%').",
                    "It checks if a value is similar, but not identical.",
                    "It joins two tables based on similar values.",
                    "It calculates the average."
                ],
                "correct": 1,
                "explanation": "LIKE performs pattern matching in SQL queries, supporting wildcards."
            },
            {
                "question": "What is a 'calculated field' in Excel or a BI tool?",
                "options": [
                    "Any field that contains a number.",
                    "A new field (column) that you create using a formula to transform existing data.",
                    "A field that is hidden from view.",
                    "A field that is used as a filter.",
                    "A field containing text data."
                ],
                "correct": 1,
                "explanation": "A calculated field is created using formulas to transform or combine existing data."
            },
            {
                "question": "What is 'data validation'?",
                "options": [
                    "The process of checking the accuracy and quality of data.",
                    "The process of visualizing data.",
                    "The process of writing a SQL query.",
                    "The process of creating a dashboard.",
                    "The process of deleting data."
                ],
                "correct": 0,
                "explanation": "Data validation checks the accuracy and quality of data."
            }
        ]
        
        for q_data in level2_questions:
            question = models.Question(
                quiz_id=quiz2.id,
                question_text=q_data["question"],
                question_type='multiple_choice',
                explanation=q_data["explanation"]
            )
            db.add(question)
            db.flush()
            
            for idx, option_text in enumerate(q_data["options"]):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(idx == q_data["correct"])
                )
                db.add(option)
        
        print(f"✅ Added {len(level2_questions)} questions for Level 2")
        
        # Continue with Level 3...
        print("\n📝 Adding Level 3: Data Analytics Advanced...")
        quiz3 = models.Quiz(
            title="Data Analytics Advanced - Level 3",
            description="Advanced topics including SQL joins, data storytelling, cohort analysis, and business intelligence",
            specialization_id=data_analytics_spec.id,
            difficulty_level=3,
            time_limit_minutes=50
        )
        db.add(quiz3)
        db.flush()
        
        level3_questions = [
            {
                "question": "What is the difference between an INNER JOIN and a LEFT JOIN in SQL?",
                "options": [
                    "INNER JOIN is faster; LEFT JOIN is slower.",
                    "INNER JOIN returns only matching rows; LEFT JOIN returns all rows from the left table and matching rows from the right.",
                    "INNER JOIN returns all rows; LEFT JOIN returns only matching rows.",
                    "INNER JOIN is for numbers; LEFT JOIN is for text.",
                    "There is no difference."
                ],
                "correct": 1,
                "explanation": "INNER JOIN returns only matching rows, while LEFT JOIN returns all left table rows plus matches."
            },
            {
                "question": "What is the fundamental problem with the 'Correlation does not imply causation' concept?",
                "options": [
                    "Just because two variables move together (correlation) doesn't mean one caused the other.",
                    "Correlation is a more powerful finding than causation.",
                    "If two variables are correlated, one must have caused the other.",
                    "This concept only applies to pie charts.",
                    "This concept is outdated and no longer relevant."
                ],
                "correct": 0,
                "explanation": "Correlation shows variables move together, but doesn't prove one causes the other."
            },
            {
                "question": "A manager asks for a report on 'Sales Performance.' What is the first question you should ask?",
                "options": [
                    "What color do you want the dashboard to be?",
                    "How soon do you need this?",
                    "What business question are you trying to answer? or How do you define 'performance'?",
                    "What software should I use?",
                    "Who should I blame if sales are bad?"
                ],
                "correct": 2,
                "explanation": "Always clarify the business question and define metrics before starting analysis."
            },
            {
                "question": "What is 'data storytelling'?",
                "options": [
                    "The process of making up stories about data.",
                    "The process of writing a SQL query.",
                    "The skill of communicating data insights effectively using a narrative and visuals.",
                    "A feature in Microsoft Excel.",
                    "A type of database."
                ],
                "correct": 2,
                "explanation": "Data storytelling communicates insights effectively using narrative and visuals."
            },
            {
                "question": "What is the difference between the SQL WHERE clause and the HAVING clause?",
                "options": [
                    "WHERE filters rows before GROUP BY; HAVING filters groups after GROUP BY.",
                    "WHERE filters groups; HAVING filters rows.",
                    "WHERE is for numbers; HAVING is for text.",
                    "WHERE is for SELECT; HAVING is for UPDATE.",
                    "They are identical and can be used interchangeably."
                ],
                "correct": 0,
                "explanation": "WHERE filters individual rows before grouping; HAVING filters groups after aggregation."
            },
            {
                "question": "Which chart is best for showing how different parts make up a whole (e.g., market share)?",
                "options": [
                    "A line chart",
                    "A scatter plot",
                    "A pie chart or a stacked bar chart",
                    "A histogram",
                    "A map"
                ],
                "correct": 2,
                "explanation": "Pie charts and stacked bar charts show parts of a whole effectively."
            },
            {
                "question": "How would you calculate 'Year-over-Year Growth' (YoY) for sales?",
                "options": [
                    "(Current Year Sales - Last Year Sales) / Last Year Sales",
                    "(Current Year Sales / Last Year Sales) - 1",
                    "(Current Year Sales - Last Year Sales)",
                    "Current Year Sales / Last Year Sales",
                    "Both (A) and (B) are correct ways to calculate it."
                ],
                "correct": 4,
                "explanation": "Both formulas calculate YoY growth correctly - they're mathematically equivalent."
            },
            {
                "question": "What is a 'data dictionary'?",
                "options": [
                    "A central file or document that defines all the tables, columns, data types, and business definitions for a database.",
                    "A tool that checks spelling in your SQL queries.",
                    "A list of all data analysts in a company.",
                    "A dashboard that shows all company data.",
                    "A type of SQL join."
                ],
                "correct": 0,
                "explanation": "A data dictionary documents all database tables, columns, types, and business definitions."
            },
            {
                "question": "What is the purpose of a CASE statement in SQL?",
                "options": [
                    "To join two tables.",
                    "To filter results like a WHERE clause.",
                    "To create conditional 'if-then-else' logic within a query (e.g., to create new categories).",
                    "To sort results.",
                    "To create a new table."
                ],
                "correct": 2,
                "explanation": "CASE creates conditional logic within queries for categorization and transformations."
            },
            {
                "question": "What is a 'funnel analysis'?",
                "options": [
                    "An analysis of fluid dynamics.",
                    "A way to visualize the user's journey through a series of steps (e.g., homepage -> product page -> cart -> purchase).",
                    "A type of SQL query.",
                    "A method for cleaning data.",
                    "A way to build a dashboard."
                ],
                "correct": 1,
                "explanation": "Funnel analysis visualizes user progression through sequential steps in a process."
            },
            {
                "question": "What is a 'cohort analysis'?",
                "options": [
                    "An analysis of military groups.",
                    "An analysis that tracks a group of users (a 'cohort') who share a common characteristic (e.g., 'signed up in January') over time.",
                    "A way to join tables in SQL.",
                    "A type of pie chart.",
                    "A method for cleaning data."
                ],
                "correct": 1,
                "explanation": "Cohort analysis tracks groups with shared characteristics over time."
            },
            {
                "question": "What is an 'outlier'?",
                "options": [
                    "A data point that is a 'lie' and must be deleted.",
                    "The most common data point.",
                    "A data point that is significantly different from other data points in a dataset.",
                    "The average value.",
                    "A data point with a missing value."
                ],
                "correct": 2,
                "explanation": "An outlier is significantly different from other observations in the dataset."
            },
            {
                "question": "What is a potential problem with a chart's Y-axis not starting at zero?",
                "options": [
                    "It can exaggerate the differences between values, making them look more significant than they are.",
                    "It makes the chart load slower.",
                    "It is not possible; all charts must start at zero.",
                    "It can hide the most important data.",
                    "It makes the chart more accurate."
                ],
                "correct": 0,
                "explanation": "Non-zero Y-axis starting points can exaggerate differences and mislead viewers."
            },
            {
                "question": "What is a 'subquery' in SQL?",
                "options": [
                    "A query that is not as good as a normal query.",
                    "A query that is embedded (nested) inside another SQL query.",
                    "A query that updates data.",
                    "A query that deletes a table.",
                    "A query that only runs on a subset of data."
                ],
                "correct": 1,
                "explanation": "A subquery is nested inside another query, often in WHERE or FROM clauses."
            },
            {
                "question": "What is 'DAX'?",
                "options": [
                    "A brand of soap.",
                    "A programming language used in Microsoft Power BI for creating formulas and calculations.",
                    "A type of SQL database.",
                    "A data visualization chart.",
                    "A Python library."
                ],
                "correct": 1,
                "explanation": "DAX (Data Analysis Expressions) is Power BI's formula language for calculations."
            },
            {
                "question": "What is a 'star schema' in data modeling?",
                "options": [
                    "A complex model with tables linking to many other tables in a web.",
                    "A model with one central 'fact' table (e.g., Sales) connected to multiple 'dimension' tables (e.g., Time, Product, Region).",
                    "A database model that is new and popular.",
                    "A visual chart that looks like a star.",
                    "A way to rate your data."
                ],
                "correct": 1,
                "explanation": "Star schema has a central fact table connected to multiple dimension tables."
            },
            {
                "question": "How would you find the 'top 10' selling products in SQL?",
                "options": [
                    "SELECT product_name, SUM(sales) FROM sales GROUP BY product_name ORDER BY SUM(sales) DESC LIMIT 10;",
                    "SELECT product_name FROM sales WHERE sales > 10;",
                    "SELECT product_name, SUM(sales) FROM sales;",
                    "SELECT TOP 10 product_name FROM sales;",
                    "SELECT product_name FROM sales LIMIT 10;"
                ],
                "correct": 0,
                "explanation": "Group by product, sum sales, order descending, and limit to 10 results."
            },
            {
                "question": "What is a 'calculated field' in Tableau?",
                "options": [
                    "A field that is hidden.",
                    "A new field created using a formula, similar to in Excel.",
                    "The name of a dashboard.",
                    "A filter.",
                    "A connection to a database."
                ],
                "correct": 1,
                "explanation": "Calculated fields in Tableau use formulas to create new data fields."
            },
            {
                "question": "Why is it important to understand the business context of your data?",
                "options": [
                    "It is not important; the numbers speak for themselves.",
                    "To ensure the analysis is relevant, the right questions are asked, and the insights are actionable.",
                    "To know who to blame if the data is wrong.",
                    "To help you write better SQL queries.",
                    "To make your charts look better."
                ],
                "correct": 1,
                "explanation": "Business context ensures analysis is relevant and insights are actionable."
            },
            {
                "question": "What is 'data quality'?",
                "options": [
                    "A measure of how 'good' the data is for its intended purpose (e.g., accurate, complete, timely).",
                    "The total amount of data you have.",
                    "The speed at which you can query data.",
                    "The type of database you use.",
                    "The number of charts on your dashboard."
                ],
                "correct": 0,
                "explanation": "Data quality measures accuracy, completeness, and fitness for purpose."
            }
        ]
        
        for q_data in level3_questions:
            question = models.Question(
                quiz_id=quiz3.id,
                question_text=q_data["question"],
                question_type='multiple_choice',
                explanation=q_data["explanation"]
            )
            db.add(question)
            db.flush()
            
            for idx, option_text in enumerate(q_data["options"]):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(idx == q_data["correct"])
                )
                db.add(option)
        
        print(f"✅ Added {len(level3_questions)} questions for Level 3")
        
        db.commit()
        print("\n" + "=" * 80)
        print("✅ Successfully added Data Analytics quizzes (Levels 1-3 complete)!")
        print("=" * 80)
        print("\n📊 Summary so far:")
        print("   Level 1 (Basics): 20 questions")
        print("   Level 2 (Intermediate): 20 questions")
        print("   Level 3 (Advanced): 20 questions")
        print("   Total so far: 60 questions")
        print("\nNote: Levels 4-5 will be added in next update")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_data_analytics_quizzes()
