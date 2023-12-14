

class sqlExtract():
    """Extract SQL Data (attributes and values) from the given SQL Query."""

    def __init__(self, sqlQuery):
        self.sqlQuery = sqlQuery
        self.aggrFunctions = ['AVG', 'MIN', 'MAX', 'COUNT', 'SUM']
    
    def fetch_where_attr(self):
        """Fetch all where attributes from the SQL query."""
        whereIdx = self.sqlQuery.find("WHERE")
        whereClause = self.sqlQuery[whereIdx + len('WHERE '):].strip()
        tokens = whereClause.split()
        whereAttr = []
        whereAttrValue = {}
        i = 0
        while i < len(tokens):
            attr = tokens[i]
            j = i + 1
            while j < len(tokens) and tokens[j] not in {'=', 'AND', '<', '>'}:
                attr = attr + " " + tokens[j]
                j += 1
            whereAttr.append(attr)
            value = ""
            # skip operators
            while j < len(tokens) and tokens[j] in {'=', '<', '>', ' '}:
                j += 1
            while j < len(tokens) and tokens[j] != 'AND':
                # remove double quotes in the value
                if tokens[j] not in {'"'}:
                    value = value + " " + tokens[j]
                j += 1
            whereAttrValue[attr] = value.strip()
            i = j
            i += 1
        return whereAttr, whereAttrValue
    
    def fetch_select_attr(self):
        """Fetch all select attributes from the SQL query."""
        selectClause = self.sqlQuery[len('SELECT'):].strip()
        fromIdx = selectClause.find('FROM')
        selectClause = selectClause[:fromIdx - 1]
        tokens = selectClause.split(",")
        selectAttr = {}
        for i in range(len(tokens)):
            associatedAggrFunc = ''
            for aggrFunc in self.aggrFunctions:
              if aggrFunc in tokens[i]:
                tokens[i] = tokens[i].replace(aggrFunc, '')
                associatedAggrFunc = aggrFunc
                break
            tokens[i] = tokens[i].strip()
            selectAttr[tokens[i]] = associatedAggrFunc
        return selectAttr

    def fetch_comparison_operator(self):
        """Fetch all the comparison operators from the SQL query."""
        trueOperators = []
        allOperators = [' = ', ' > ', ' < ']
    
        whereIdx = self.sqlQuery.find('WHERE')
        if whereIdx == -1:
          return trueOperators
    
        for operator in allOperators:
          index = 0
          while True:
            operatorIdx = self.sqlQuery.find(operator, index)
            if operatorIdx == -1:
              break
            trueOperators.append((operatorIdx, operator))
            index = operatorIdx + len(operator)
    
        trueOperators = sorted(trueOperators, key=lambda x: x[0])
    
        trueOperatorsList = []
        for operatorTuple in trueOperators:
          trueOperatorsList.append(operatorTuple[1].strip())
    
        return trueOperatorsList