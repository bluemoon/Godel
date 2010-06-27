class Groundings:
    def __init__(self):
        self.variableScope_stack = []
        self.Groundings = {}
        
    def variableScope(self, attribute=None):
        ## Attribute needs to be a dictionary!
        if attribute:
            self.variableScope_stack.append((attribute, self.Groundings))
        else:
            self.variableScope_stack.append(self.Groundings)
            
        del self.Groundings
        self.Groundings = {}
        
    def isGround(self, variable):
        if self.Groundings.has_key(variable):
            return True
        else:
            return False
        
    def groundVariable(self, variable, value, attribute=None):
        assert variable
        assert value
        
        self.Groundings[variable] = value

    def getGrounding(self, variable):
        if self.isGround(variable):
            return self.Groundings[variable]
        else:
            return False

    def getScopeByAttr(self, attribute):
        for scope in self.variableScope_stack:
            ## has to actually have an attribute
            if len(scope) > 1:
                currentAttribute = scope[0]
                if currentAttribute.has_key(attribute):
                    return currentAttribute[attribute]

        ## we have to exhaust all first
        return False

    def getGroundings(self):
        return self.Groundings
                
        
