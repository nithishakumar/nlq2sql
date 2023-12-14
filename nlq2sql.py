from nltk.corpus import wordnet
import spacy
import numpy as np

 
class nlq2sql():
    """NLQ to SQL Query Translator."""

    def __init__(self, text, table, attributes, nlp, nlp_ner, rule='rule1'):
        # the natural language query 
        self.nlq = text
        # attributes (column names) associated with the table
        temp = set()
        for attr in attributes:
            temp.add(attr.lower())
        self.attributes = temp
        # maps where attributes to their corresponding values
        self.whereAttributes = {}
        # maps select attributes to their corresponding aggregate functions
        self.selectAttributes = {}
        # table name
        self.table = table
        self.doc = None
        self.doc_ner = None
        # spaCy's tokenization & POS tagging model
        self.nlp = nlp
        # custom named entity recognition model
        self.nlp_ner = nlp_ner
        # either rule 1,  2, or 3
        self.rule = rule
        self.comparisonOperators = []
        # words representing a specific operator (assume default operator is =)
        self.operatorWords = {}
        self.operatorWords[">"] = {"greater", "greatest", "more", "higher", "highest", "above", 
                                   "exceeding", "beyond", "over", "excess", "upwards", "larger", 
                                   "largest", "bigger", "biggest", "after", "later", "latest", "past"
                                   }
        self.operatorWords["<"] = {"less", "lesser", "least", "lower", "lowest", "below", "before", 
                                   "under", "prior", "smaller", "smallest", "early", "earlier", 
                                   "soonest", "beneath", "not more", "fewer"
                                   }
        

    def tokenize_and_ner(self):
        """Tokenize text and perform named entity recognition to tag values as 'SELECT' or 'CONSTRAINT'."""
        self.doc = self.nlp(self.nlq)
        self.doc_ner = self.nlp_ner(self.nlq)
    
    def is_attribute(self, token):
        """Return the attribute's name the token corresponds to and None otherwise."""
        token = token.lower()
        return token in self.attributes
    
    def get_all_attributes(self):
        """Map the start and end indices of each attribute in the NLQ to the attributeName."""
        attributes = {}
        for attr in self.attributes:
            attrStart = self.nlq.lower().find(attr.lower())
            if attrStart != -1:
                attrEnd = attrStart + len(attr) - 1
                attributes[(attrStart, attrEnd)] = attr
        return attributes

    def classify_attributes_rule1(self):
        """Classify attributes as SELECT type or WHERE type based on rule 1 (read report for rule 1)."""
        attributes = self.get_all_attributes()
        self.whereAttributes = {}
        self.selectAttributes = {}
        for entity in self.doc_ner.ents:
            # Select attributes
            if entity.label_ == "SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = ''
                 continue
            # ignore values that are actually attributes
            if self.is_attribute(entity.text):
                continue
            entStart = self.nlq.lower().find(entity.text.lower())
            entEnd = entStart + len(entity.text) - 1
            # find the closest attribute to the Entity's position 
            # (measure distance in characters)
            minDiff = len(self.nlq)
            minAttr = None
            for pos, attr in attributes.items():
                # if attribute is a part of the value, it is the minAttr
                if attr.lower() in entity.text.lower():
                    minAttr = attr
                    break
                attrStart, attrEnd = pos
                currDiff = None
                if attrEnd < entStart:
                    currDiff = entStart - attrEnd
                if attrStart > entEnd:
                    currDiff = attrStart - entEnd
                if currDiff != None and currDiff <= minDiff:
                    minDiff = currDiff
                    minAttr = attr
            if minAttr != None:
                self.whereAttributes[minAttr] = entity.text
    
    def classify_attributes_rule2(self):
        """Classify attributes as SELECT type or WHERE type based on rule 2 (read report for rule 2)."""
        self.whereAttributes = {}
        self.selectAttributes = {}
        lowerCaseNlq = self.nlq.lower()
        for entity in self.doc_ner.ents:
            if entity.label_ == "SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = ''
                 continue
            # ignore select attributes and values that are actually attributes
            if self.is_attribute(entity.text):
                continue
            # Define the words that should not be split
            lowerCaseEntity = entity.text.lower()
            special_cases = [{"ORTH": lowerCaseEntity, "NORM": lowerCaseEntity}]
            indicator = False
            for attr in self.attributes:
                attr = attr.lower()
                # if attribute is a part of the value, it is the minAttr
                if attr in lowerCaseEntity:
                    self.whereAttributes[attr] = entity.text
                    indicator = True
                    break
                special_cases.append({"ORTH": attr, "NORM": attr})
            # stop finding minAttr if attribute was a part of the value
            if indicator:
                continue
            # Add special case rules to prevent splitting certain words
            rules = self.nlp.tokenizer.rules
            for spCase in special_cases:
                rules[spCase['ORTH']] = [spCase]
            self.nlp.tokenizer.rules = rules
            entDoc = self.nlp(lowerCaseNlq)
            minDiff = len(self.nlq)
            minAttr = None
            entPos = 0
            entTokens = []
            for token in entDoc:
                if token.pos_ not in {"SYM", "PUNCT"}:
                    entTokens.append(token.text)
            for i in range(len(entTokens)):
                if entTokens[i] == lowerCaseEntity:
                    entPos = i
            # find the closest attribute to the Entity's position 
            # (measure distance in words)
            for i in range(len(entTokens)):
                if i != entPos and self.is_attribute(entTokens[i]):
                    currDiff = abs(entPos - i)
                    if currDiff < minDiff:
                        minDiff = currDiff
                        minAttr = entTokens[i]
            if minAttr != None:
                self.whereAttributes[minAttr] = entity.text
            for spCase in special_cases:
                del rules[spCase['ORTH']]
            self.nlp.tokenizer.rules = rules

    def classify_attributes_rule3(self):
        """Classify attributes as SELECT type or WHERE type based on rule 1 (read report for rule 1)."""
        attributes = self.get_all_attributes()
        self.whereAttributes = {}
        self.selectAttributes = {}
        for entity in self.doc_ner.ents:
            # Select attributes
            if entity.label_ == "SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = ''
                 continue
            if entity.label_ == "COUNT SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = "COUNT"
                 continue
            if entity.label_ == "AVG SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = "AVG"
                 continue
            if entity.label_ == "MAX SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = "MAX"
                 continue
            if entity.label_ == "AVG SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = "MIN"
                 continue
            if entity.label_ == "SUM SELECT" and self.is_attribute(entity.text.lower()):
                 self.selectAttributes[entity.text] = "SUM"
                 continue
            # ignore values that are actually attributes
            if self.is_attribute(entity.text):
                continue
            entStart = self.nlq.lower().find(entity.text.lower())
            entEnd = entStart + len(entity.text) - 1
            # find the closest attribute to the Entity's position 
            # (measure distance in characters)
            minDiff = len(self.nlq)
            minAttr = None
            for pos, attr in attributes.items():
                # if attribute is a part of the value, it is the minAttr
                if attr.lower() in entity.text.lower():
                    minAttr = attr
                    break
                attrStart, attrEnd = pos
                currDiff = None
                if attrEnd < entStart:
                    currDiff = entStart - attrEnd
                if attrStart > entEnd:
                    currDiff = attrStart - entEnd
                if currDiff != None and currDiff <= minDiff:
                    minDiff = currDiff
                    minAttr = attr
            if minAttr != None:
                self.whereAttributes[minAttr] = entity.text
    
    def check_tree(self, operatorWord, whereDict):
        """Find the parent for an operator word and return True if it has no parent or if its parent is a WHERE attribute or value."""
        flag = False
        parent = ""
        self.doc = self.nlp(self.nlq)
        
        for token in self.doc:
            for child in token.children:
              if child.text.lower() == operatorWord.lower():
                parent = token.text.lower()
                flag = True
                break
            if flag:
              break

        if parent == "":
            return True

        for attr, value in self.whereDict.items(): 
            if parent in attr.lower() or parent in value.lower():
              return True

        return False

            
    def has_multiple_where_attributes(self, words_in_query, whereDict):
        """Assign comparison operators to queries with multiple WHERE attributes using depepdency parsing."""
        count = 0
        self.doc = self.nlp(self.nlq)

        # loop through every operator word that is in the nlq
        for key, operTuple in words_in_query.items():
            # loop through all WHERE attributes and values to see which ones 
            # connect to the operator words
            for attr, value in whereDict.items():
                attr_words = attr.split()
                attr_words = [word.lower() for word in attr_words]
                value_words = value.split()
                value_words = [word.lower() for word in value_words]
                for token in self.doc:
                    # check which attribute the current operator word might connect to
                    if token.text.lower() in attr_words:
                        for word in attr_words:
                            if word == token.text.lower():
                                for child in token.children:
                                    if child.text.lower() == operTuple[1].lower:
                                        self.comparisonOperators[count] = operTuple[0]

                    # check which value the current operator word might connect to
                    elif token.text.lower() in value_words:
                        for word in value_words:
                            if word == token.text.lower():
                                for child in token.children:
                                    if child.text.lower() == operTuple[1].lower:
                                        self.comparisonOperators[count] = operTuple[0]

            count += 1
            
    def determine_operator(self, whereDict):
        """Predict the comparison operator for each WHERE clause"""
        # if there are no WHERE attributes, no operator needed
        if len(whereDict) == 0:
          return
        # making the default operator for each WHERE clause "="
        for i in range(len(whereDict)):
          self.comparisonOperators.append("=")
        
        # step 1: iterate through all operator words and store all matches
        words_in_query = {}
        count = 0
        for operator, words in self.operatorWords.items():
          for operator_word in words:
            if operator_word in self.nlq.lower():
              words_in_query[count] = (operator, operator_word)
              count += 1

        # step 2: determine the operator for each where clause
        # case 1: if no matches were found, we stick to the default for all WHERE clauses
        if len(words_in_query) == 0:
          return
      
        # case 2: if one WHERE clause and one operator word, use dependency 
        # parsing to find the correct operator
        if len(words_in_query) == 1 and len(whereDict) == 1:
          assignOperator = self.check_tree(words_in_query[0][1])
          if assignOperator:
            self.comparisonOperators[0] = words_in_query[0][0]
          return
      
        # case 3: if there are multiple WHERE clauses, use dependency parsing 
        # to find the operator for each clause
        if len(words_in_query) > 1:
            self.has_multiple_where_attributes(words_in_query)

    def create_select_statement(self):
        """Create Select Statement via values, attributes, """
        sqlQuery = ""
        if len(self.selectAttributes) == 0:
            sqlQuery = f"SELECT * FROM {self.table}"
        else:
            selectAttrList = []
            for attr, aggr in self.selectAttributes.items():
                if aggr != '':
                    selectAttrList.append(aggr + " " + attr)
                else:
                    selectAttrList.append(attr)
            sqlQuery = f"SELECT {', '.join(selectAttrList)} FROM {self.table}"
        if len(self.whereAttributes) > 0:
            sqlQuery = sqlQuery + " WHERE"
            whereClauses = []
            for attr, value in self.whereAttributes.items():
                whereClauses.append(f"{attr} = {value}")
            sqlQuery = f"{sqlQuery} {' AND '.join(whereClauses)}"
        return sqlQuery
    
    def get_sql_query(self):
        self.tokenize_and_ner()
        if self.rule == 'rule1':
          self.classify_attributes_rule1()
        elif self.rule == 'rule2':
          self.classify_attributes_rule2()
        else:
          self.classify_attributes_rule3()
        return self.create_select_statement()
    
    def get_similarity(self, v1, v2):
        """Get cosine similarity between vectors v1 and v2."""
        similarity = None
        dotProduct = np.dot(v1, v2)
        v1Mag = np.linalg.norm(v1)
        v2Mag = np.linalg.norm(v2)
        similarity = dotProduct / (v1Mag * v2Mag)
        return similarity
    
    def get_word_embedding(self, word, embed):
        """Return the average word embedding of the given word."""
        doc = self.nlp(word)
        temp = None
        indicator = True
        count = 0
        for token in doc:
            # embedding for word not found
            if token.text.lower() not in embed:
                return None
            count += 1
            if indicator:
                temp = embed[token.text.lower()]
            else:
                indicator = False
                temp += embed[token.text.lower()]
        return temp / count
    
    def get_most_similar_attribute(self, value, embed):
        """Return the attribute that is most similar to the value."""
        valueEmbedding = self.get_word_embedding(value, embed)
        maxSimilarity = -1
        mostSimilarAttr = None
        if valueEmbedding is None:
            return None
        for attr in self.attributes:
            attributeEmbedding = self.get_word_embedding(attr, embed)
            if attributeEmbedding is None:
                continue
            attributeSimilarity = self.get_similarity(valueEmbedding, attributeEmbedding)
            if attributeSimilarity > maxSimilarity:
                maxSimilarity = attributeSimilarity
                mostSimilarAttr = attr
        return mostSimilarAttr
