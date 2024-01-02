# NLQ to SQL Translator
Natural Language Query (NLQ) to Structured Query Language (SQL) Translator

EECS 487 Final Project, Fall 2023

Nithisha Nantha Kumar and Rushabh Shah

# About

Database Management Systems are an integral part of offices across the world. Companies within and outside the tech industry have endless data that needs to be stored, organized, and retrieved. One of the most common ways to do so has been writing Structured Query Language (SQL). While SQL is one of the most widely sought-after skills today, ranked 5th by Stack Overflow’s [annual survey](https://survey.stackoverflow.co/2023/#section-admired-and-desired-programming-scripting-and-markup-languages) of almost 90,000 people, non-programmers often find themselves in a position where they have to write SQL code. That is where our project comes in. Our Natural Language to SQL Query Translator aims to generate accurate SQL SELECT statements given a Natural Language Query (NLQ) to aid users who do not have in-depth knowledge of the topic. Our system takes in the schema (which refers to a relevant table and its column names) and an NLQ and creates an appropriate SQL statement. 


For instance, given the NLQ "Which province is grey and bell electorate in?" and the list of attributes ['Member', 'Electorate', 'Province', 'MPs term', 'Election date'], our system will output the SQL query "SELECT province FROM table WHERE Electorate = Grey and Bell".

# Directory Structure

1. **Training.ipynb:** This notebook contains our code to train our custom named-entity recognition (NER) models with the spaCy library.
2. **Evaluation.ipynb:** This notebook contains our code to evaluate our Natural Language Query (NLQ) to Structured Query Language (SQL) translator system.
3. **nlq2sql.py:** This file contains a class definition with the main functions to generate an SQL query from an NLQ.
7. **sqlExtract.py:** This file contains code to extract information from an SQL query, like the WHERE attributes, SELECT attributes, and values for evaluation purposes.
4. **model-best-no-aggr:** This directory consists of files associated with our custom named-recognition (NER) model without support for aggregate functions, that is, it only tags words in the NLQ as either "SELECT" or "CONSTRAINT".
5. **model-best:** This directory consists of files associated with our second custom NER model with support for aggregate functions. It will tag SELECT attributes specifically as "COUNT SELECT" if associated with the COUNT SQL function, "MAX SELECT" for MAX, and so on. Other supported aggregate functions are "MIN", "AVG", and "SUM". The model also tags words in NLQs which are select attributes as just "SELECT" if not associated with an aggregate function and values in the NLQ as "CONSTRAINT".
6. **base_config.cfg and config.cfg:** These are configuration files that we used to define features of our NER models during training, like the initial learning rate, batch size, the optimizer, and more. See Training.ipynb for more details.
8. **mannual_annotations.json:** This file contains manually annotated data to test our code that automatically annotates training data.
9. **training_data.json and validation_data.json:** These files contain annotated training/validation data for our custom NER model.
10. **training_data.spacy and validation_data.spacy:** These files contain our training/validation data as a .spacy file for training with the spaCy library.


