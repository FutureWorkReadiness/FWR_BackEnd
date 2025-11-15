"""
Add Data Analytics Quizzes - Levels 3, 4, and 5
This script adds the remaining 60 questions for Data Analytics specialization
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_data_analytics_advanced_quizzes():
    db = SessionLocal()
    try:
        # Get Data Analytics specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Data Analytics"
        ).first()
        
        if not specialization:
            print("Error: Data Analytics specialization not found")
            return
        
        print(f"Found specialization: {specialization.name} (ID: {specialization.id})")
        
        # Delete existing quizzes for levels 3, 4, and 5
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == specialization.id,
            models.Quiz.difficulty_level.in_([3, 4, 5])
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
        print(f"Deleted {len(existing_quizzes)} existing quizzes for levels 3-5")
        
        # Level 3: Advanced (20 questions)
        level_3_questions = [
            ("What is the main difference between INNER JOIN and LEFT JOIN?", 
             ["INNER JOIN returns all rows from both tables", "LEFT JOIN returns all rows from the left table and matching rows from the right", "They are identical", "LEFT JOIN is faster"],
             1, "LEFT JOIN returns all rows from the left table and matched rows from the right table, while INNER JOIN only returns matching rows."),
            
            ("In data analysis, what does 'correlation does not imply causation' mean?",
             ["Correlation and causation are the same thing", "Just because two variables are correlated doesn't mean one causes the other", "Causation always implies correlation", "Neither correlation nor causation matter"],
             1, "Two variables can be correlated without one causing the other - there may be other factors or coincidence."),
            
            ("What is a composite key in a database?",
             ["A key made of multiple columns", "A key that opens multiple locks", "A primary key only", "A foreign key only"],
             0, "A composite key is a primary key composed of multiple columns used to uniquely identify a row."),
            
            ("What does ETL stand for in data warehousing?",
             ["Extract, Transform, Load", "Execute, Test, Launch", "Evaluate, Track, Learn", "Export, Transfer, List"],
             0, "ETL is the process of Extracting data from sources, Transforming it to fit business needs, and Loading it into a data warehouse."),
            
            ("What is the purpose of data normalization in databases?",
             ["To make data bigger", "To reduce redundancy and improve data integrity", "To make queries slower", "To delete data"],
             1, "Normalization organizes data to reduce redundancy and dependency, improving data integrity and efficiency."),
            
            ("What is a star schema in data warehousing?",
             ["A schema shaped like a star", "A fact table surrounded by dimension tables", "A type of data visualization", "A security protocol"],
             1, "A star schema has a central fact table connected to multiple dimension tables, resembling a star shape."),
            
            ("What is the difference between a fact table and a dimension table?",
             ["There is no difference", "Fact tables contain measurements, dimension tables contain descriptive attributes", "Dimension tables are larger", "Fact tables only store text"],
             1, "Fact tables store quantitative data (metrics), while dimension tables store descriptive attributes (context)."),
            
            ("What is data granularity?",
             ["The level of detail in data", "The size of the database", "The speed of queries", "The number of users"],
             0, "Granularity refers to the level of detail or summarization in data - fine granularity means detailed data, coarse means summarized."),
            
            ("What is a slowly changing dimension (SCD)?",
             ["A dimension that changes very slowly", "A method for tracking changes in dimension tables over time", "A performance issue", "A type of error"],
             1, "SCD is a technique for managing and tracking changes to dimension table data over time in a data warehouse."),
            
            ("What is the purpose of indexing in a database?",
             ["To make the database larger", "To improve query performance by creating quick lookup structures", "To delete old data", "To backup data"],
             1, "Indexes create data structures that allow the database to find data faster, improving query performance."),
            
            ("What is a cohort analysis?",
             ["Analyzing groups of users who share common characteristics over time", "Analyzing a single user", "A type of chart", "A database backup method"],
             0, "Cohort analysis groups users by shared characteristics (like sign-up date) and analyzes their behavior over time."),
            
            ("What does OLAP stand for?",
             ["Online Analytical Processing", "Offline Analysis Platform", "Open Language Analysis Protocol", "Operational Load Analysis Process"],
             0, "OLAP is Online Analytical Processing, used for complex analytical queries on multidimensional data."),
            
            ("What is data lineage?",
             ["The age of data", "The tracking of data's origins and transformations", "The size of data", "The speed of data processing"],
             1, "Data lineage tracks where data comes from, how it moves through systems, and what transformations are applied."),
            
            ("What is the purpose of a data catalog?",
             ["To organize and document data assets in an organization", "To delete old data", "To create backups", "To slow down queries"],
             0, "A data catalog is an inventory of data assets with metadata, making it easier to discover and understand available data."),
            
            ("What is a funnel analysis in analytics?",
             ["Analyzing the steps users take to complete a goal", "A type of chart shape", "A database design pattern", "A backup strategy"],
             0, "Funnel analysis tracks user progression through sequential steps (like signup → activation → purchase) to identify drop-off points."),
            
            ("What is the difference between a data lake and a data warehouse?",
             ["No difference", "Data lakes store raw unstructured data, warehouses store structured processed data", "Data lakes are smaller", "Data warehouses are always cloud-based"],
             1, "Data lakes store raw, unstructured data in its native format, while data warehouses store structured, processed data optimized for analysis."),
            
            ("What is sampling in data analysis?",
             ["Deleting data", "Selecting a subset of data to represent the whole dataset", "Backing up data", "Encrypting data"],
             1, "Sampling involves selecting a representative subset of data for analysis when working with the full dataset is impractical."),
            
            ("What is data profiling?",
             ["Creating user profiles", "Analyzing data to understand its structure, quality, and content", "Deleting profiles", "Sharing data"],
             1, "Data profiling examines data to understand its structure, content, quality, and relationships to identify issues and patterns."),
            
            ("What does 'data storytelling' mean?",
             ["Writing fiction with data", "Communicating insights from data in a compelling narrative way", "Creating data visualizations only", "Storing data stories"],
             1, "Data storytelling combines data, visualizations, and narrative to communicate insights effectively to stakeholders."),
            
            ("What is the purpose of data governance?",
             ["To manage and ensure quality, security, and compliance of data", "To delete old data", "To make data public", "To slow down analysis"],
             0, "Data governance establishes policies and processes to ensure data quality, security, privacy, and regulatory compliance."),
        ]
        
        quiz_3 = models.Quiz(
            title="Data Analytics - Advanced",
            description="Advanced concepts in data analysis, SQL joins, and data warehousing",
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
        
        print(f"Added Level 3 (Advanced): {len(level_3_questions)} questions")
        
        # Level 4: Expert (20 questions)
        level_4_questions = [
            ("What is a window function in SQL?",
             ["A function that opens windows", "A function that performs calculations across rows related to the current row", "A visualization tool", "A backup function"],
             1, "Window functions perform calculations across a set of rows related to the current row, without collapsing the result set."),
            
            ("What does PARTITION BY do in a window function?",
             ["Deletes partitions", "Divides rows into partitions for separate calculations", "Creates new tables", "Backs up data"],
             1, "PARTITION BY divides the result set into partitions to which the window function is applied separately."),
            
            ("What is a Common Table Expression (CTE)?",
             ["A temporary result set that can be referenced in a SELECT, INSERT, UPDATE, or DELETE statement", "A permanent table", "A visualization", "A backup method"],
             0, "A CTE is a temporary named result set defined within a query that exists only for that query's duration."),
            
            ("What is the difference between ROW_NUMBER() and RANK()?",
             ["No difference", "ROW_NUMBER assigns unique numbers, RANK can have ties with gaps", "RANK is faster", "ROW_NUMBER is deprecated"],
             1, "ROW_NUMBER assigns unique sequential numbers, while RANK assigns the same number to ties and skips subsequent numbers."),
            
            ("What is a recursive CTE?",
             ["A CTE that calls itself to process hierarchical data", "A CTE that runs forever", "A type of loop", "A backup strategy"],
             0, "A recursive CTE references itself to process hierarchical or tree-structured data through iterative execution."),
            
            ("What is the purpose of HAVING clause in SQL?",
             ["Same as WHERE", "To filter results after GROUP BY aggregation", "To create tables", "To delete data"],
             1, "HAVING filters grouped results after aggregation, while WHERE filters rows before grouping."),
            
            ("What is the difference between UNION and UNION ALL?",
             ["No difference", "UNION removes duplicates, UNION ALL keeps all rows", "UNION ALL is slower", "They work on different data types"],
             1, "UNION removes duplicate rows from the combined result, while UNION ALL includes all rows including duplicates."),
            
            ("What is a subquery?",
             ["A query nested inside another query", "A broken query", "A backup query", "A visualization query"],
             0, "A subquery is a query nested within another SQL statement, used to provide data for the outer query."),
            
            ("What is the purpose of the CASE statement in SQL?",
             ["To create conditional logic in queries", "To change database case", "To backup data", "To delete records"],
             0, "CASE provides conditional logic in SQL, allowing different values to be returned based on specified conditions."),
            
            ("What is a self-join?",
             ["A table joined with itself", "An automatic join", "A broken join", "A backup join"],
             0, "A self-join joins a table to itself, useful for comparing rows within the same table or finding hierarchical relationships."),
            
            ("What is the difference between OLTP and OLAP systems?",
             ["No difference", "OLTP handles transactions, OLAP handles analytics", "OLAP is faster", "OLTP is newer"],
             1, "OLTP (Online Transaction Processing) handles day-to-day operations, while OLAP (Online Analytical Processing) handles complex analytical queries."),
            
            ("What is a materialized view?",
             ["A regular view", "A view that stores query results physically for faster access", "A deleted view", "A backup view"],
             1, "A materialized view stores the query result set physically, improving performance for complex queries that are frequently executed."),
            
            ("What is data denormalization?",
             ["The opposite of normalization, intentionally adding redundancy for performance", "An error in the database", "Deleting data", "Backing up data"],
             0, "Denormalization intentionally introduces redundancy to improve read performance, trading storage and update complexity for query speed."),
            
            ("What is a surrogate key?",
             ["An artificial key created for uniquely identifying records", "A natural key", "A deleted key", "A backup key"],
             0, "A surrogate key is an artificial identifier (like an auto-increment ID) used instead of a natural key to uniquely identify records."),
            
            ("What is the purpose of EXPLAIN in SQL?",
             ["To explain SQL to beginners", "To show the execution plan of a query", "To delete data", "To backup queries"],
             1, "EXPLAIN shows how the database will execute a query, helping identify performance issues and optimization opportunities."),
            
            ("What is a bitmap index?",
             ["An index using bitmaps for efficient storage of low-cardinality columns", "An image index", "A backup index", "A deleted index"],
             0, "A bitmap index uses bit arrays for efficient indexing of columns with few distinct values, common in data warehouses."),
            
            ("In Python pandas, what does the groupby() function do?",
             ["Deletes groups", "Groups data by specified columns for aggregation", "Creates visualizations", "Backs up data"],
             1, "groupby() splits data into groups based on specified columns, allowing aggregate operations on each group."),
            
            ("What is the purpose of pivot tables?",
             ["To rotate your monitor", "To reshape and summarize data for analysis", "To delete data", "To backup tables"],
             1, "Pivot tables reorganize and summarize data, allowing you to view different perspectives by rotating rows to columns."),
            
            ("What is a calculated field in Tableau?",
             ["A field that automatically calculates its value based on other fields", "A deleted field", "A backup field", "A static field"],
             0, "A calculated field creates new data from existing data using formulas, functions, or expressions."),
            
            ("What is an LOD (Level of Detail) expression in Tableau?",
             ["A detailed description", "An expression that computes values at different levels of granularity", "A backup method", "A deletion tool"],
             1, "LOD expressions compute values at specified levels of detail, independent of the visualization's aggregation level."),
        ]
        
        quiz_4 = models.Quiz(
            title="Data Analytics - Expert",
            description="Expert-level SQL, window functions, CTEs, and advanced analytics",
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
        
        print(f"Added Level 4 (Expert): {len(level_4_questions)} questions")
        
        # Level 5: Master (20 questions)
        level_5_questions = [
            ("What is the difference between descriptive and predictive analytics?",
             ["No difference", "Descriptive explains what happened, predictive forecasts what will happen", "Predictive is always accurate", "Descriptive uses AI"],
             1, "Descriptive analytics analyzes historical data to understand what happened, while predictive analytics uses models to forecast future outcomes."),
            
            ("What is prescriptive analytics?",
             ["Analytics that prescribes medicine", "Analytics that recommends actions to achieve desired outcomes", "Basic reporting", "Data visualization"],
             1, "Prescriptive analytics recommends specific actions to take based on data analysis and predictions to optimize outcomes."),
            
            ("What is A/B testing?",
             ["Testing two versions to see which performs better", "Testing alphabetically", "A type of backup", "A deletion method"],
             0, "A/B testing compares two versions (A and B) to determine which performs better based on specific metrics."),
            
            ("What is statistical significance in A/B testing?",
             ["How important the test is", "The likelihood that results are not due to chance", "The test duration", "The sample size"],
             1, "Statistical significance indicates the probability that observed differences between variants are real and not due to random chance."),
            
            ("What is a p-value?",
             ["The probability of observing results at least as extreme as those observed, assuming the null hypothesis is true", "The primary value", "The perfect value", "The Python value"],
             0, "A p-value measures the probability of obtaining results as extreme as observed if the null hypothesis were true. Lower p-values suggest stronger evidence against the null hypothesis."),
            
            ("What is the null hypothesis?",
             ["A hypothesis that is null", "The hypothesis that there is no effect or difference", "The alternative hypothesis", "The proven hypothesis"],
             1, "The null hypothesis assumes no relationship or effect exists between variables - it's what we test against."),
            
            ("What is a confidence interval?",
             ["How confident you feel", "A range of values likely to contain the true population parameter", "A time interval", "A backup interval"],
             1, "A confidence interval provides a range of plausible values for a population parameter with a specified level of confidence (e.g., 95%)."),
            
            ("What is time series analysis?",
             ["Analyzing data points collected over time to identify patterns and trends", "Analyzing time zones", "A clock analysis", "A backup schedule"],
             0, "Time series analysis examines data points ordered chronologically to identify trends, seasonality, and patterns over time."),
            
            ("What is seasonality in time series data?",
             ["Data about seasons", "Regular patterns that repeat at fixed intervals", "Random fluctuations", "Deleted data"],
             1, "Seasonality refers to predictable patterns that repeat at regular intervals (daily, weekly, monthly, yearly) in time series data."),
            
            ("What is a moving average?",
             ["An average that moves", "A technique to smooth time series data by averaging values over a rolling window", "A backup method", "A deletion technique"],
             1, "A moving average calculates the average of data points within a sliding time window to smooth short-term fluctuations and highlight trends."),
            
            ("What is churn analysis?",
             ["Analyzing butter production", "Analyzing the rate at which customers stop using a service", "Analyzing employee turnover only", "A backup analysis"],
             1, "Churn analysis examines why and when customers stop using a product or service to identify patterns and reduce customer loss."),
            
            ("What is RFM analysis?",
             ["Random Forest Model", "Recency, Frequency, Monetary analysis for customer segmentation", "Really Fast Method", "Regression Factor Model"],
             1, "RFM analyzes customers based on Recency (last purchase), Frequency (purchase count), and Monetary value to segment and target them effectively."),
            
            ("What is customer lifetime value (CLV)?",
             ["How long a customer lives", "The predicted total revenue from a customer over their entire relationship", "The customer's age", "The first purchase value"],
             1, "CLV estimates the total revenue a business can expect from a customer throughout their entire relationship with the company."),
            
            ("What is attribution modeling?",
             ["Giving credit to team members", "Determining which marketing touchpoints get credit for conversions", "A backup model", "A deletion method"],
             1, "Attribution modeling assigns credit to different marketing touchpoints that contributed to a conversion or sale."),
            
            ("What is the difference between correlation and regression?",
             ["No difference", "Correlation measures relationship strength, regression predicts one variable from another", "Regression is always better", "Correlation uses more data"],
             1, "Correlation measures the strength of relationship between variables, while regression models the relationship to predict one variable from others."),
            
            ("What is multivariate testing?",
             ["Testing multiple variables simultaneously", "Testing one variable", "A backup test", "A deletion test"],
             0, "Multivariate testing tests multiple variables and their combinations simultaneously to determine which combination performs best."),
            
            ("What is data-driven decision making?",
             ["Making decisions based on intuition", "Making decisions based on data analysis rather than intuition", "Making random decisions", "Delaying all decisions"],
             1, "Data-driven decision making uses data analysis, metrics, and evidence to guide business decisions rather than relying solely on intuition."),
            
            ("What is the purpose of data visualization?",
             ["To make data pretty", "To communicate data insights effectively through visual representations", "To hide data", "To delete data"],
             1, "Data visualization transforms data into visual formats (charts, graphs) to make patterns, trends, and insights easier to understand and communicate."),
            
            ("What is a data-driven culture?",
             ["A culture that ignores data", "An organizational culture that values data in decision-making at all levels", "A culture of data scientists only", "A backup culture"],
             1, "A data-driven culture prioritizes data and analytics in decision-making across the organization, empowering all employees to use data."),
            
            ("What is the ROI (Return on Investment) of analytics?",
             ["The cost of analytics tools", "The value gained from analytics relative to its cost", "The number of analysts", "The amount of data stored"],
             1, "ROI of analytics measures the business value and benefits gained from analytics initiatives relative to their cost and resources invested."),
        ]
        
        quiz_5 = models.Quiz(
            title="Data Analytics - Master",
            description="Master-level analytics concepts, statistical methods, and business impact",
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
        
        print(f"Added Level 5 (Master): {len(level_5_questions)} questions")
        
        db.commit()
        print("\n✅ Successfully added Data Analytics quizzes (Levels 3-5 complete!)")
        print(f"Total questions added: {len(level_3_questions) + len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_data_analytics_advanced_quizzes()
