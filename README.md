# NLQ to SQL Translator
Natural Language Query (NLQ) to Structured Query Language (SQL) Translator | EECS 487 Final Project, FA 2023 | Nithisha Nantha Kumar and Rushabh Shah

Relational database management systems (RDBMS) are widely used to store data in several applications. Users must learn how to write SQL queries to easily use an RDBMS for retrieving data. Understanding the fundamentals of SQL and becoming proficient in the language to write queries can be tedious and time-consuming. To address this issue, we have created nlq2sql, an NLP model-based system allowing users to input natural language text in English and attributes (table column names). The system will then translate this text into a valid SQL SELECT query that can be used in an RDBMS. 

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


