class Symbol:
    
    '''
        Simbolo que está dentro da tabela de simbolos. Seus conteúdos:
        - Identificador (o nome da variável)
        - Tipo (se é uma variável ou função)
        - Tipo de token (identificador)
        - Parametros - opcional (caso seja uma função e tenha parâmetros, ele terá uma lista de parâmetros
        nos quais estão inclusas em uma nova tabela de símbolos.)
        - Valor que está associado a ele (caso exista uma atribuição)
    '''
    
    def __init__(self,identifier, identifier_type, token_type):
        self.identifier = identifier
        self.identifier_type = identifier_type
        self.token_type = token_type
        self.parameters = []
        self.value = ''
        self.isConst = False
        self.assignment_type = ''
        self.scope = ''
        self.isArray = False
        self.isProcedure = False
        

    def setAssignmentType(self,type):
        self.assignment_type = type
    
    def getAssignmentType(self):
        return self.assignment_type

    def getIsArray(self):
        return self.isArray
    
    def setIsArray(self, array):
        self.isArray = array

    def getIsProcedure(self):
        return self.isProcedure

    def setIsProcedure(self, procedure):
        self.isProcedure = procedure

    def isAConstSymbol(self):
        return self.isConst

    def addParameters(self, symbol):
        self.parameters.append(symbol)

    def getIdentifier(self):
        return self.identifier

    def getIdentifierType(self):
        return self.identifier_type

    def removeParameters(self, symbol):
        self.parameters.remove(symbol)

    def addValue(self, value):
        self.value = value

    def setIsConst(self, const):
        self.isConst = const
    
    def getTokenType(self):
        return self.token_type

    def getParameters(self):
        return self.parameters

    def getValue(self):
        return self.value

    def getScope(self):
        return self.scope

    def setScope(self, scope):
        self.scope = scope

    def toString(self):
        print(f"{self.identifier} {self.identifier_type} {self.token_type} {self.value}")



