"""
Add Data Science Quizzes - Levels 3, 4, and 5
This script adds 60 questions for Data Science specialization (Advanced scenarios through Strategic)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_data_science_advanced_quizzes():
    db = SessionLocal()
    try:
        # Get Data Science specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Data Science"
        ).first()
        
        if not specialization:
            print("Error: Data Science specialization not found")
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
        
        # Level 3: Advanced Scenarios (20 questions)
        level_3_questions = [
            ("What is the difference between 'Supervised' and 'Unsupervised' learning?",
             ["Supervised learning uses labeled data (features and targets); Unsupervised learning uses unlabeled data (features only) to find patterns.",
              "Supervised learning is for regression; Unsupervised learning is for classification.",
              "Supervised learning is complex; Unsupervised learning is simple.",
              "Supervised learning requires a 'supervisor' (a human); Unsupervised does not.",
              "Supervised learning is for numbers; Unsupervised learning is for text."],
             0, "Supervised learning uses labeled data with known outcomes, while unsupervised learning finds patterns in unlabeled data."),
            
            ("Which of the following is an example of an 'Unsupervised' learning task?",
             ["Predicting house prices based on features (Linear Regression).",
              "Classifying emails as 'spam' or 'not spam' (Classification).",
              "Grouping customers into different segments based on their purchase behavior (Clustering).",
              "Predicting if a customer will default on a loan (Classification).",
              "Both A and B."],
             2, "Clustering is an unsupervised learning task that groups similar data points without labeled outcomes."),
            
            ("What is the 'K-Means' algorithm?",
             ["A popular 'clustering' algorithm (unsupervised) that groups data into 'K' number of clusters.",
              "A 'classification' algorithm (supervised) for predicting categories.",
              "A 'regression' algorithm (supervised) for predicting values.",
              "A method for cleaning data.",
              "A method for feature engineering."],
             0, "K-Means is an unsupervised clustering algorithm that partitions data into K distinct clusters."),
            
            ("What is a 'confusion matrix'?",
             ["A table used to evaluate the performance of a classification model, showing True Positives, True Negatives, False Positives, and False Negatives.",
              "A matrix that is very confusing to read.",
              "A chart for visualizing regression results.",
              "A data structure in Pandas.",
              "A method for clustering data."],
             0, "A confusion matrix is a table showing the four outcomes of classification predictions for model evaluation."),
            
            ("What is 'Precision' in a confusion matrix?",
             ["Of all the actual positive cases, how many did the model predict correctly?",
              "Of all the cases the model predicted as positive, how many were actually positive?",
              "The overall accuracy of the model.",
              "The number of True Positives.",
              "The number of False Negatives."],
             1, "Precision measures the proportion of positive predictions that were actually correct."),
            
            ("What is 'Recall' in a confusion matrix?",
             ["Of all the actual positive cases, how many did the model predict correctly?",
              "Of all the cases the model predicted as positive, how many were actually positive?",
              "The overall accuracy of the model.",
              "The number of True Negatives.",
              "The number of False Positives."],
             0, "Recall measures the proportion of actual positive cases that were correctly identified by the model."),
            
            ("When would you prioritize 'Recall' over 'Precision'?",
             ["In an email spam filter (you don't want to miss important emails).",
              "In a medical diagnosis for a serious disease (it's more important to find all actual cases, even if you get some false positives).",
              "When the cost of a false positive is very high.",
              "When the cost of a false negative is very low.",
              "When the dataset is perfectly balanced."],
             1, "For serious diseases, high recall is critical to find all actual cases, even if it means some false alarms."),
            
            ("What is the 'F1-Score'?",
             ["The average of Precision and Recall.",
              "The harmonic mean of Precision and Recall, providing a single score that balances both.",
              "The same as Accuracy.",
              "The product of Precision and Recall.",
              "A measure of how fast a model is."],
             1, "F1-Score is the harmonic mean of precision and recall, providing a balanced metric for model performance."),
            
            ("What is 'K-Fold Cross-Validation'?",
             ["A method for training a model K times.",
              "A technique where the training data is split into 'K' folds; the model is trained on K-1 folds and tested on the remaining fold, rotating K times.",
              "A method for splitting data into a train and test set just once.",
              "A type of clustering algorithm.",
              "A method for visualizing data in K dimensions."],
             1, "K-Fold Cross-Validation splits data into K parts, training on K-1 and testing on 1, rotating K times for robust evaluation."),
            
            ("What is 'hyperparameter tuning'?",
             ["The process of the model learning its parameters (like weights) from the data.",
              "The process of finding the optimal 'settings' (hyperparameters, like 'K' in k-NN) for a model to improve its performance.",
              "The process of cleaning the data.",
              "The process of tuning a server to be 'hyper' fast.",
              "The process of visualizing high-dimensional data."],
             1, "Hyperparameter tuning optimizes model settings (like K in K-Means) that are set before training."),
            
            ("What is 'Grid Search'?",
             ["A method for searching a grid-like dataset.",
              "A common hyperparameter tuning technique that exhaustively tries every combination of specified hyperparameter values.",
              "A data visualization technique.",
              "A method for cleaning data.",
              "A type of database query."],
             1, "Grid Search systematically tries all combinations of specified hyperparameter values to find the best model configuration."),
            
            ("What is a 'Random Forest'?",
             ["An ensemble machine learning model that operates by building a multitude of Decision Trees and outputting their combined (e.g., average or mode) prediction.",
              "A single, very deep Decision Tree.",
              "A clustering algorithm.",
              "A linear regression model.",
              "A visualization of a forest."],
             0, "Random Forest is an ensemble method that combines multiple decision trees for improved prediction accuracy."),
            
            ("What is 'dimensionality reduction'?",
             ["The process of adding more features (dimensions) to a dataset.",
              "The process of reducing the number of features (dimensions) in a dataset, while trying to retain as much information as possible.",
              "The process of visualizing data in 2D or 3D.",
              "A method for data cleaning.",
              "A way to make a model more complex."],
             1, "Dimensionality reduction reduces the number of features while preserving important information to improve model performance."),
            
            ("What is 'Principal Component Analysis' (PCA)?",
             ["A popular unsupervised algorithm for dimensionality reduction.",
              "A popular algorithm for classification.",
              "A popular algorithm for regression.",
              "A method for data cleaning.",
              "A method for hyperparameter tuning."],
             0, "PCA is a dimensionality reduction technique that transforms data into principal components ordered by variance."),
            
            ("In Pandas, what does the .groupby() method do?",
             ["It sorts the DataFrame by a specific column.",
              "It deletes a group of columns.",
              "It splits the data into groups based on some criteria (e.g., a column value) so you can perform aggregate functions (like mean, sum) on them.",
              "It creates a new column.",
              "It joins two DataFrames together."],
             2, "The .groupby() method groups data by specified criteria to enable aggregate operations on each group."),
            
            ("In Pandas, what does the .merge() method do?",
             ["It calculates the mean of a column.",
              "It splits the DataFrame into groups.",
              "It combines two DataFrames based on a common column, similar to a SQL JOIN.",
              "It deletes rows with missing values.",
              "It plots the data."],
             2, "The .merge() method combines two DataFrames based on common columns, similar to SQL JOIN operations."),
            
            ("What is 'Natural Language Processing' (NLP)?",
             ["A field of AI that helps computers understand, interpret, and generate human language.",
              "A method for visualizing text data.",
              "A type of SQL database.",
              "A programming language that is 'natural' to read.",
              "A data cleaning technique."],
             0, "NLP is a field of AI focused on enabling computers to understand, interpret, and generate human language."),
            
            ("What is 'tokenization' in NLP?",
             ["The process of converting text into a secret code.",
              "The process of visualizing text.",
              "The process of breaking down a piece of text into smaller units, such as words or sentences (called 'tokens').",
              "The process of checking for spelling errors.",
              "A machine learning model for text."],
             2, "Tokenization breaks text into smaller units (tokens) like words or sentences for NLP processing."),
            
            ("What is 'TF-IDF'?",
             ["A type of machine learning model.",
              "A numerical statistic that reflects how important a word is to a document in a collection (corpus).",
              "A data visualization technique.",
              "A Python library for NLP.",
              "A method for cleaning text data."],
             1, "TF-IDF (Term Frequency-Inverse Document Frequency) measures word importance in documents relative to a corpus."),
            
            ("What is 'Logistic Regression'?",
             ["A machine learning algorithm used for classification problems (it predicts a probability).",
              "A machine learning algorithm used for regression problems.",
              "A machine learning algorithm used for clustering.",
              "A method for data cleaning.",
              "A method for visualizing data."],
             0, "Logistic Regression is a classification algorithm that predicts probabilities for binary or multiclass outcomes."),
        ]
        
        quiz_3 = models.Quiz(
            title="Data Science - Advanced Scenarios",
            description="Advanced ML concepts: supervised vs unsupervised learning, evaluation metrics, and NLP basics",
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
        
        # Level 4: Expert & Specialization (20 questions)
        level_4_questions = [
            ("What is 'Gradient Boosting' (e.g., XGBoost, LightGBM)?",
             ["An ensemble learning technique that builds models (typically decision trees) sequentially, where each new model corrects the errors of the previous ones.",
              "A type of Linear Regression.",
              "A clustering algorithm.",
              "A method for dimensionality reduction.",
              "A type of neural network."],
             0, "Gradient Boosting builds models sequentially, with each new model correcting errors from previous ones."),
            
            ("What is a 'Neural Network'?",
             ["A computing system inspired by the biological neural networks that constitute animal brains, used for complex pattern recognition.",
              "A data visualization technique.",
              "A data cleaning method.",
              "A type of SQL database.",
              "A data structure in Python."],
             0, "Neural Networks are computing systems inspired by biological brains, used for complex pattern recognition tasks."),
            
            ("What is 'Deep Learning'?",
             ["A subfield of machine learning based on artificial neural networks with multiple layers (deep architectures).",
              "A method for learning about 'deep' topics.",
              "A type of data visualization.",
              "A clustering algorithm.",
              "A data cleaning technique."],
             0, "Deep Learning uses neural networks with multiple layers (deep architectures) for complex learning tasks."),
            
            ("What is a 'hyperparameter'?",
             ["A parameter learned by the model during training (e.g., weights in a linear regression).",
              "A parameter set by the data scientist before training (e.g., the 'K' in K-Means).",
              "A very 'hyper' or unstable parameter.",
              "The target variable.",
              "A feature in the dataset."],
             1, "Hyperparameters are settings configured before training (like K in K-Means), not learned from data."),
            
            ("What is the main problem with using 'accuracy' as a metric for an imbalanced dataset?",
             ["It is too complex to calculate.",
              "It can be misleadingly high if the model simply predicts the majority class all the time.",
              "It only works for regression, not classification.",
              "It cannot be used for deep learning models.",
              "It is not a well-known metric."],
             1, "For imbalanced data, accuracy can be misleadingly high by always predicting the majority class."),
            
            ("What are 'SMOTE' (Synthetic Minority Over-sampling Technique)?",
             ["A technique for handling imbalanced datasets by over-sampling the minority class (creating synthetic new samples).",
              "A technique for under-sampling the majority class.",
              "A type of machine learning model.",
              "A data visualization technique.",
              "A method for feature engineering."],
             0, "SMOTE creates synthetic samples of the minority class to handle imbalanced datasets."),
            
            ("What is the 'curse of dimensionality'?",
             ["A phenomenon where having too many features (dimensions) makes data sparse, models harder to train, and performance worse.",
              "The difficulty of visualizing data in more than 3 dimensions.",
              "A type of error in a neural network.",
              "A problem with clustering algorithms only.",
              "A problem with regression models only."],
             0, "The curse of dimensionality occurs when too many features make data sparse and models difficult to train effectively."),
            
            ("What is 'A/B Testing'?",
             ["A statistical method of comparing two versions (A and B) of something (e.g., a website) to determine which one performs better.",
              "A type of machine learning model.",
              "A method for cleaning data.",
              "A data visualization technique.",
              "A method for hyperparameter tuning."],
             0, "A/B Testing compares two versions statistically to determine which performs better."),
            
            ("What is a 'p-value' in statistical hypothesis testing?",
             ["The probability that the model is correct.",
              "The probability of observing the data (or something more extreme) if the null hypothesis is true.",
              "The 'precision-value' of a model.",
              "The impact of a feature.",
              "The accuracy of a test."],
             1, "A p-value is the probability of observing the data (or more extreme) assuming the null hypothesis is true."),
            
            ("What is a 'Time Series' dataset?",
             ["A dataset where values are recorded in alphabetical order.",
              "A dataset where values are recorded at different time intervals (e.g., daily stock prices, monthly sales).",
              "A dataset with no order.",
              "A dataset used for clustering.",
              "A dataset used for NLP."],
             1, "Time Series data contains values recorded at different time intervals, like daily stock prices."),
            
            ("What is 'feature scaling' (e.g., Standardization, Normalization)?",
             ["The process of adding more features.",
              "The process of removing features.",
              "The process of transforming numerical features to a common scale, which is important for algorithms like k-NN or SVM.",
              "The process of one-hot encoding.",
              "The process of visualizing features."],
             2, "Feature scaling transforms numerical features to a common scale, important for distance-based algorithms."),
            
            ("What is the main difference between 'Standardization' and 'Normalization'?",
             ["Standardization scales data to a mean of 0 and std dev of 1; Normalization scales data to a range (e.g., 0 to 1).",
              "Standardization scales data to a range (e.g., 0 to 1); Normalization scales data to a mean of 0 and std dev of 1.",
              "Standardization is for text; Normalization is for numbers.",
              "Standardization is for regression; Normalization is for classification.",
              "There is no difference."],
             0, "Standardization scales to mean=0 and std=1; Normalization scales to a range like 0 to 1."),
            
            ("What is an 'ROC Curve' (Receiver Operating Characteristic)?",
             ["A plot that shows the performance of a classification model by plotting the True Positive Rate against the False Positive Rate at various threshold settings.",
              "A plot for regression models.",
              "A plot for clustering models.",
              "A data visualization for time series.",
              "A type of 'rock' music for data scientists."],
             0, "ROC Curve plots True Positive Rate vs False Positive Rate to evaluate classification model performance."),
            
            ("What does 'AUC' (Area Under the Curve) represent for an ROC curve?",
             ["The area of the dataset.",
              "A single number (from 0 to 1) that summarizes the model's ability to distinguish between positive and negative classes. A higher AUC is better.",
              "The speed of the model.",
              "The complexity of the model.",
              "The amount of data used."],
             1, "AUC summarizes a model's ability to distinguish between classes, with higher values indicating better performance."),
            
            ("What is 'TensorFlow'?",
             ["A popular open-source library developed by Google, primarily used for deep learning and neural networks.",
              "A data manipulation library like Pandas.",
              "A data visualization library.",
              "A database.",
              "A clustering algorithm."],
             0, "TensorFlow is Google's open-source library primarily used for deep learning and neural networks."),
            
            ("What is 'PyTorch'?",
             ["An open-source machine learning library (developed by Facebook) known for its flexibility and use in research, especially for deep learning.",
              "A data manipulation library.",
              "A data visualization library.",
              "A database.",
              "A regression algorithm."],
             0, "PyTorch is Facebook's flexible open-source library popular in research for deep learning applications."),
            
            ("What is 'word embedding' (e.g., Word2Vec, GloVe)?",
             ["A visualization of words.",
              "A technique in NLP where words are represented as dense numerical vectors in a multi-dimensional space.",
              "A method for counting words.",
              "A method for checking spelling.",
              "A type of machine learning model."],
             1, "Word embeddings represent words as dense numerical vectors in multi-dimensional space for NLP tasks."),
            
            ("What is a 'Support Vector Machine' (SVM)?",
             ["A supervised learning model that finds an optimal 'hyperplane' to separate data into different classes.",
              "A clustering algorithm.",
              "A deep learning model.",
              "A database.",
              "A data visualization tool."],
             0, "SVM is a supervised learning model that finds an optimal hyperplane to separate classes."),
            
            ("What is 'bias' in the context of a machine learning model?",
             ["The error introduced by approximating a real-world problem with a model that is too simple (leading to underfitting).",
              "The model's sensitivity to small fluctuations in the training data (leading to overfitting).",
              "The model's preference for one outcome over another.",
              "The model's speed.",
              "The model's accuracy."],
             0, "Bias is error from using a model that is too simple to capture the underlying pattern (underfitting)."),
            
            ("What is 'variance' in the context of a machine learning model?",
             ["The error introduced by a model that is too simple.",
              "The error from a model's sensitivity to small fluctuations in the training data (leading to overfitting).",
              "The model's preference for one outcome over another.",
              "The model's speed.",
              "The model's accuracy."],
             1, "Variance is error from a model being too sensitive to training data fluctuations (overfitting)."),
        ]
        
        quiz_4 = models.Quiz(
            title="Data Science - Expert & Specialization",
            description="Expert concepts: ensemble methods, deep learning, model evaluation, and advanced ML techniques",
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
            ("A business wants to know which customers are likely to churn (leave). What type of machine learning problem is this?",
             ["A binary classification problem (predicting 'churn' or 'not churn').",
              "A clustering problem (grouping customers).",
              "A regression problem (predicting how much they will spend).",
              "A dimensionality reduction problem.",
              "An NLP problem."],
             0, "Customer churn prediction is a binary classification problem: churn vs. not churn."),
            
            ("A business wants to segment its customers into different groups to create targeted marketing. What type of machine learning problem is this?",
             ["A classification problem.",
              "A clustering problem (unsupervised).",
              "A regression problem.",
              "A time-series forecasting problem.",
              "An A/B testing problem."],
             1, "Customer segmentation is an unsupervised clustering problem to find natural groupings."),
            
            ("What is 'MLOps' (Machine Learning Operations)?",
             ["A set of practices that aims to deploy and maintain machine learning models in production reliably and efficiently.",
              "A specific machine learning algorithm.",
              "A data visualization tool.",
              "A data cleaning technique.",
              "A type of database."],
             0, "MLOps is a set of practices for deploying and maintaining ML models in production reliably."),
            
            ("What is 'ethical AI' or 'responsible AI'?",
             ["A focus on ensuring AI systems are fair, unbiased, transparent, and accountable.",
              "An AI that is cheap to run.",
              "An AI that is very fast.",
              "An AI that is 100% accurate.",
              "An AI that can write its own code."],
             0, "Ethical AI focuses on fairness, transparency, accountability, and avoiding bias in AI systems."),
            
            ("What is 'algorithmic bias'?",
             ["When an AI model produces results that are systematically prejudiced due to biased assumptions in the algorithm or biased training data.",
              "The bias-variance trade-off.",
              "A model that is too simple (underfitting).",
              "A model that is too complex (overfitting).",
              "A model that is 100% fair."],
             0, "Algorithmic bias occurs when models produce systematically prejudiced results due to biased data or assumptions."),
            
            ("How would you explain a complex model's prediction to a non-technical business stakeholder?",
             ["By explaining the mathematical formulas in detail.",
              "By using explainable AI (XAI) techniques like SHAP values to show which features (e.g., 'high purchase frequency') were most important for the prediction.",
              "By telling them the model is a 'black box' and they just have to trust it.",
              "By showing them the 10,000-line Python script.",
              "By giving them the model's accuracy score and nothing else."],
             1, "Use explainable AI techniques like SHAP to show which features drove the prediction in business terms."),
            
            ("What is a 'data pipeline'?",
             ["A physical pipe that transports data.",
              "A series of automated steps that extract, transform, and load (ETL) data from a source to a destination (like a data warehouse).",
              "A machine learning model.",
              "A data visualization.",
              "A type of database."],
             1, "A data pipeline automates the ETL process from data sources to destinations like data warehouses."),
            
            ("What is a 'data warehouse'?",
             ["A small database on a laptop.",
              "A large, central repository of data that is optimized for analysis and reporting (OLAP), often containing historical data from many sources.",
              "A CSV file.",
              "A machine learning model.",
              "A data visualization tool."],
             1, "A data warehouse is a central repository optimized for analysis, containing historical data from multiple sources."),
            
            ("What is a 'data lake'?",
             ["A large, central repository that stores raw data in its native format, often used for data exploration and machine learning.",
              "A highly structured database like a data warehouse.",
              "A small CSV file.",
              "A machine learning model.",
              "A data visualization."],
             0, "A data lake stores raw data in its native format for exploration and ML, unlike structured data warehouses."),
            
            ("You've built a model with 95% accuracy. What is the first question you should ask before deploying it?",
             ["How can I make it 96% accurate?",
              "What is the baseline accuracy? (e.g., if 94% of customers don't churn, a model that always predicts 'no churn' is 94% accurate).",
              "What programming language is it written in?",
              "Can I run it on my laptop?",
              "What is the F1-Score?"],
             1, "Always check baseline accuracy first - high accuracy may be meaningless if the baseline is already high."),
            
            ("What is the 'bias-variance trade-off'?",
             ["A model with high bias is always better.",
              "A model with high variance is always better.",
              "A fundamental concept that as a model's complexity increases, its bias decreases but its variance increases (and vice-versa). The goal is to find a balance.",
              "The trade-off between a model being 'biased' (unfair) and 'varied' (random).",
              "A trade-off between model speed and accuracy."],
             2, "As model complexity increases, bias decreases but variance increases. Balance is key to avoid under/overfitting."),
            
            ("What is 'model deployment'?",
             ["The process of training a machine learning model.",
              "The process of cleaning data.",
              "The process of integrating a trained model into an existing application (e.g., as an API) so it can make predictions on new, real-world data.",
              "The process of visualizing model results.",
              "The process of deleting a model."],
             2, "Model deployment integrates a trained model into applications (like APIs) for real-world predictions."),
            
            ("What is a 'Transformer' model (e.g., BERT, GPT)?",
             ["A deep learning architecture (used in NLP) that relies heavily on 'self-attention' mechanisms to understand context and relationships in text.",
              "A model that transforms data from one format to another.",
              "A type of clustering algorithm.",
              "A type of regression algorithm.",
              "A data visualization tool."],
             0, "Transformers use self-attention mechanisms to understand context and relationships in NLP tasks."),
            
            ("A business wants to predict next month's sales. What type of machine learning problem is this?",
             ["A time-series forecasting problem (a type of regression).",
              "A classification problem.",
              "A clustering problem.",
              "An NLP problem.",
              "A dimensionality reduction problem."],
             0, "Sales forecasting is a time-series prediction problem, which is a type of regression."),
            
            ("What is a common way to evaluate a clustering model (like K-Means), since it has no 'labels'?",
             ["Using Accuracy and Precision.",
              "Using a metric like the 'Silhouette Score,' which measures how similar an object is to its own cluster compared to other clusters.",
              "By manually looking at every cluster.",
              "Using the R-squared value.",
              "Using the p-value."],
             1, "Silhouette Score measures cluster quality by comparing within-cluster similarity to between-cluster differences."),
            
            ("What is 'reinforcement learning'?",
             ["A type of supervised learning.",
              "A type of unsupervised learning.",
              "An area of machine learning where an 'agent' learns to make optimal decisions by taking actions in an environment to maximize a cumulative 'reward'.",
              "A method for making a model 'stronger' by adding more data.",
              "A method for cleaning data."],
             2, "Reinforcement learning trains agents to make optimal decisions by maximizing cumulative rewards through trial and error."),
            
            ("What is a 'feature store'?",
             ["A central repository for documenting, storing, and sharing features for machine learning models across an organization.",
              "A store that sells new features for your models.",
              "A database for storing raw data.",
              "A data visualization tool.",
              "A machine learning model."],
             0, "A feature store is a central repository for documenting, storing, and sharing ML features across teams."),
            
            ("What is the business value of a data science model?",
             ["How complex and mathematically interesting it is.",
              "Its ability to drive a business outcome, such as increasing revenue, reducing costs, or improving customer satisfaction.",
              "Its accuracy score (e.g., 99% accuracy).",
              "The number of features it uses.",
              "The programming language it is written in."],
             1, "A model's business value comes from driving outcomes like revenue, cost reduction, or customer satisfaction."),
            
            ("What is 'model drift'?",
             ["When a model's performance degrades over time because the real-world data it's seeing in production has changed from the data it was trained on.",
              "When a model 'drifts' from one server to another.",
              "A method for improving model performance.",
              "A data visualization technique.",
              "A type of data cleaning."],
             0, "Model drift occurs when production data changes from training data, degrading model performance over time."),
            
            ("You have to choose between a simple, interpretable model (like Logistic Regression) and a complex, 'black box' model (like a Deep Neural Network) that is 2% more accurate. How do you decide?",
             ["Always choose the complex model for the best accuracy.",
              "Always choose the simple model because it's easier.",
              "It depends on the business problem. For high-stakes decisions (e.g., loan approval, medical), interpretability and fairness (the simple model) may be more important than a small accuracy boost.",
              "Ask the frontend team what they prefer.",
              "Flip a coin."],
             2, "For high-stakes decisions, interpretability and fairness often outweigh small accuracy gains from complex models."),
        ]
        
        quiz_5 = models.Quiz(
            title="Data Science - Strategic & Architectural",
            description="Strategic ML: business applications, MLOps, ethical AI, model deployment, and real-world decision making",
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
        print("\n✅ Successfully added Data Science quizzes (Levels 3-5 complete!)")
        print(f"Total questions added: {len(level_3_questions) + len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_data_science_advanced_quizzes()
