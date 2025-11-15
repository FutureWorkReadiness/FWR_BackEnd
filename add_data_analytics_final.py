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
        
        # Delete existing Data Analytics quizzes
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == data_analytics_spec.id
        ).all()
        
        if existing_quizzes:
            print(f"🗑️  Deleting {len(existing_quizzes)} existing Data Analytics quizzes...")
            for quiz in existing_quizzes:
                db.query(models.QuizAttempt).filter(
                    models.QuizAttempt.quiz_id == quiz.id
                ).delete()
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
        
        # LEVEL 1: Basic Foundations
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
            ("What is the primary goal of Data Analytics?", 
             ["To build artificial intelligence and predictive models.", 
              "To inspect, clean, transform, and model data to find useful information and support decision-making.", 
              "To design and build databases from scratch.", 
              "To write the code for websites and mobile apps.", 
              "To secure a company's network from hackers."], 
             1, "Data Analytics focuses on inspecting, cleaning, transforming, and modeling data to discover useful information and support decision-making."),
            
            ("What does 'SQL' stand for?", 
             ["Simple Query Language", "Structured Query Language", "Server Quality Logic", "System Query Link", "Standard Question Language"], 
             1, "SQL stands for Structured Query Language, used to manage and query data in relational databases."),
            
            ("What is a 'KPI'?", 
             ["Key Performance Indicator: A measurable value that shows how effectively a company is achieving key business objectives.", 
              "Key Python Integration: A library for coding.", 
              "Key Performance Index: A ranking of all employees.", 
              "Key Programming Interface: Another name for an API.", 
              "Known Problem Indicator: A list of bugs."], 
             0, "KPI stands for Key Performance Indicator - a measurable value showing how effectively objectives are being achieved."),
            
            ("What is a 'dashboard'?", 
             ["A code editor for writing SQL.", 
              "A visual display of the most important information, consolidated on a single screen, to monitor performance at a glance.", 
              "The main page of a Microsoft Excel file.", 
              "A server that stores data.", 
              "A type of database."], 
             1, "A dashboard is a visual display consolidating important information on a single screen for quick monitoring."),
            
            ("Which of the following is a 'data visualization' tool?", 
             ["Microsoft Word", "Tableau or Power BI", "Node.js", "GitHub", "VS Code"], 
             1, "Tableau and Power BI are popular data visualization and business intelligence tools."),
            
            ("What is a 'CSV' file?", 
             ["A 'Comma-Separated Values' file, a plain text file for storing tabular data.", 
              "A 'Computer Security Version' file, used for antivirus.", 
              "A 'Calculated Sheet Version' file, specific to Excel.", 
              "A 'Customer Service validation' file.", 
              "A type of image file."], 
             0, "CSV stands for Comma-Separated Values, a simple format for storing tabular data in plain text."),
            
            ("What is the 'mean' of a set of numbers?", 
             ["The middle value.", "The most common value.", "The average value (sum of values divided by the count).", "The highest value.", "The lowest value."], 
             2, "The mean is the average value, calculated by summing all values and dividing by the count."),
            
            ("What is the 'median' of a set of numbers?", 
             ["The middle value after the numbers have been sorted.", "The most common value.", "The average value.", "The difference between the highest and lowest value.", "The sum of all values."], 
             0, "The median is the middle value when numbers are sorted in order."),
            
            ("In a database, what is a 'table'?", 
             ["A visual chart or graph.", "A collection of related data organized in a grid of rows and columns.", "A single piece of data, like a name.", "A query used to get data.", "The entire database itself."], 
             1, "A table is a collection of related data organized in rows and columns."),
            
            ("What is a 'row' in a database table?", 
             ["A single, complete record or entry (e.g., all information for one customer).", "A single characteristic or attribute (e.g., the 'Email' column).", "The name of the table.", "The title of a chart.", "A calculation."], 
             0, "A row represents a single, complete record in a table."),
            
            ("What is a 'column' in a database table?", 
             ["A single, complete record (e.g., all info for one customer).", "A set of data values for a specific attribute (e.g., 'Age' for all customers).", "The entire table.", "A filter on a dashboard.", "A security setting."], 
             1, "A column contains data values for a specific attribute across all records."),
            
            ("What is 'data cleaning'?", 
             ["The process of visualizing data.", "The process of deleting all old data.", "The process of finding and fixing errors, inconsistencies, and missing values in a dataset.", "The process of writing SQL queries.", "The process of designing a dashboard."], 
             2, "Data cleaning involves finding and fixing errors, inconsistencies, and missing values in datasets."),
            
            ("Which chart type is best for showing trends over time?", 
             ["A pie chart", "A line chart", "A scatter plot", "A bar chart", "A histogram"], 
             1, "Line charts are ideal for showing trends and changes over time."),
            
            ("Which chart type is best for comparing values across different categories?", 
             ["A bar chart", "A line chart", "A scatter plot", "A pie chart", "A treemap"], 
             0, "Bar charts are excellent for comparing values across different categories."),
            
            ("Which chart type is best for showing the relationship between two numerical variables?", 
             ["A pie chart", "A bar chart", "A scatter plot", "A line chart", "A KPI card"], 
             2, "Scatter plots show relationships between two numerical variables."),
            
            ("What is the 'mode' of a set of data?", 
             ["The average value.", "The middle value.", "The value that appears most frequently.", "The highest value.", "The range of values."], 
             2, "The mode is the value that appears most frequently in a dataset."),
            
            ("What is 'Microsoft Excel'?", 
             ["A database management system.", "A programming language.", "A spreadsheet program used for organizing, analyzing, and visualizing data.", "A cloud computing service.", "A tool for writing SQL code."], 
             2, "Microsoft Excel is a spreadsheet program used for data organization, analysis, and visualization."),
            
            ("What is a 'data type'?", 
             ["The name of a dashboard.", "A classification that specifies which type of value a variable has (e.g., String, Integer, Date).", "A SQL query.", "A type of chart.", "A folder for storing data."], 
             1, "A data type classifies what kind of value a variable can hold (e.g., String, Integer, Date)."),
            
            ("What does 'ETL' stand for in data analytics?", 
             ["Extract, Transform, Load", "Error, Test, Launch", "Export, Translate, Link", "Estimate, Test, Learn", "E-commerce, Tools, Logic"], 
             0, "ETL stands for Extract, Transform, Load - the process of moving data from source to destination."),
            
            ("What is 'data integrity'?", 
             ["The speed of the database.", "The visualization of the data.", "The maintenance, accuracy, consistency, and completeness of data.", "The process of deleting data.", "The file format of the data."], 
             2, "Data integrity refers to maintaining the accuracy, consistency, and completeness of data.")
        ]
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level1_questions):
            question = models.Question(
                quiz_id=quiz1.id,
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
        
        print(f"✅ Added {len(level1_questions)} questions for Level 1")
        
        # LEVEL 2: Intermediate Application
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
            ("Which SQL command is used to retrieve data from a database?", 
             ["GET", "READ", "SELECT", "FETCH", "OPEN"], 
             2, "SELECT is the SQL command used to retrieve data from a database."),
            
            ("Which SQL clause is used to filter the results of a query?", 
             ["WHERE", "FILTER", "GROUP BY", "SELECT", "SORT"], 
             0, "The WHERE clause filters query results based on specified conditions."),
            
            ("What is a 'Pivot Table' in Excel used for?", 
             ["To write SQL code.", "To summarize, group, and analyze large amounts of data in a table.", "To create a visual line chart.", "To format the color of cells.", "To check for spelling errors."], 
             1, "Pivot Tables summarize, group, and analyze large datasets in Excel."),
            
            ("What is the purpose of the VLOOKUP function in Excel?", 
             ["To calculate the average of a column.", "To sort data alphabetically.", "To find a value in one column of a table and return a corresponding value from another column.", "To create a chart.", "To filter rows based on a condition."], 
             2, "VLOOKUP finds a value in one column and returns a corresponding value from another column."),
            
            ("Which SQL clause is used to combine rows from two or more tables?", 
             ["MERGE", "COMBINE", "GROUP", "JOIN", "APPEND"], 
             3, "JOIN combines rows from two or more tables based on related columns."),
            
            ("Which SQL aggregate function returns the total number of rows?", 
             ["SUM()", "TOTAL()", "COUNT()", "AVG()", "MAX()"], 
             2, "COUNT() returns the total number of rows in a result set."),
            
            ("Which SQL clause is used to sort the results of a query?", 
             ["SORT BY", "ALIGN BY", "ORDER BY", "GROUP BY", "ARRANGE"], 
             2, "ORDER BY sorts query results in ascending or descending order."),
            
            ("In a BI tool, what is a 'Dimension'?", 
             ["A numerical, measurable value (e.g., 'Sales', 'Quantity').", "A qualitative, descriptive value (e.g., 'Region', 'Product Name').", "The name of the dashboard.", "A filter.", "A type of chart."], 
             1, "Dimensions are qualitative, descriptive values like Region or Product Name."),
            
            ("In a BI tool, what is a 'Measure'?", 
             ["A numerical, quantitative value that can be aggregated (e.g., 'Sales', 'Profit').", "A descriptive, categorical value (e.g., 'Customer Name').", "The title of a chart.", "A comment or note.", "A date or time."], 
             0, "Measures are numerical values that can be aggregated, like Sales or Profit."),
            
            ("What does the SQL GROUP BY clause do?", 
             ["It sorts the results in a group.", "It groups rows that have the same values in specified columns, so aggregate functions can be applied.", "It combines two tables together.", "It filters the results.", "It updates the data in a table."], 
             1, "GROUP BY groups rows with same values so aggregate functions can be applied."),
            
            ("What is a 'primary key' in a database table?", 
             ["A column that contains non-essential data.", "A column (or set of columns) that uniquely identifies each row in a table.", "The first column in every table.", "A key used to unlock the database.", "A link to another table."], 
             1, "A primary key uniquely identifies each row in a table."),
            
            ("What is a 'foreign key' in a database table?", 
             ["A column that is not from your country.", "A column that uniquely identifies each row (this is a primary key).", "A column (or set of columns) that links to the primary key of another table.", "A password to access the table.", "The last column in every table."], 
             2, "A foreign key links to the primary key of another table, establishing relationships."),
            
            ("Which SQL aggregate function calculates the average of a column?", 
             ["MEAN()", "MEDIAN()", "AVERAGE()", "AVG()", "TOTAL() / COUNT()"], 
             3, "AVG() calculates the average value of a numeric column."),
            
            ("Which SQL command is used to add a new row of data to a table?", 
             ["ADD ROW", "CREATE ROW", "INSERT INTO", "UPDATE", "ALTER TABLE"], 
             2, "INSERT INTO adds new rows of data to a table."),
            
            ("Which SQL command is used to modify existing data in a table?", 
             ["MODIFY", "CHANGE", "INSERT INTO", "UPDATE", "ALTER TABLE"], 
             3, "UPDATE modifies existing data in a table."),
            
            ("What is a common way to handle missing data (null values) during analysis?", 
             ["Delete the entire dataset.", "Report the data as-is; the errors don't matter.", "Remove the rows, or replace the missing value with a default (e.g., 0, mean, median).", "Close the program and restart it.", "Replace all missing values with the word 'missing'."], 
             2, "Common approaches include removing rows or replacing nulls with default values like mean or median."),
            
            ("What is the purpose of the SUMIF function in Excel?", 
             ["To sum all numbers in a range.", "To sum numbers in a range only if a specific condition is met.", "To check if a sum is correct.", "To find the sum of two different tables.", "To create a chart."], 
             1, "SUMIF sums numbers only when they meet a specified condition."),
            
            ("What does the LIKE operator do in a SQL WHERE clause?", 
             ["It checks for an exact match.", "It is used for pattern matching (e.g., WHERE name LIKE 'A%').", "It checks if a value is similar, but not identical.", "It joins two tables based on similar values.", "It calculates the average."], 
             1, "LIKE performs pattern matching in SQL queries, supporting wildcards."),
            
            ("What is a 'calculated field' in Excel or a BI tool?", 
             ["Any field that contains a number.", "A new field (column) that you create using a formula to transform existing data.", "A field that is hidden from view.", "A field that is used as a filter.", "A field containing text data."], 
             1, "A calculated field is created using formulas to transform or combine existing data."),
            
            ("What is 'data validation'?", 
             ["The process of checking the accuracy and quality of data.", "The process of visualizing data.", "The process of writing a SQL query.", "The process of creating a dashboard.", "The process of deleting data."], 
             0, "Data validation checks the accuracy and quality of data.")
        ]
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level2_questions):
            question = models.Question(
                quiz_id=quiz2.id,
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
        
        print(f"✅ Added {len(level2_questions)} questions for Level 2")
        
        db.commit()
        print("\n" + "=" * 80)
        print("✅ Successfully added Data Analytics quizzes (Levels 1-2 complete)!")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   Level 1 (Basics): 20 questions")
        print("   Level 2 (Intermediate): 20 questions")
        print("   Total: 40 questions across 2 quizzes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_data_analytics_quizzes()

# This file will be regenerated completely with all 5 levels
