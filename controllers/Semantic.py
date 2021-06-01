class Semantic:
    def __init__(self):
        self.symbol_table = []
        self.functions_table = {}
        self.current_token_value = 0


    def analyze(self, symbol_table, rules, tokens_list, functions_table= None):
        self.symbol_table = symbol_table
        if functions_table is not None:
            self.functions_table = functions_table
        for rule in rules:
            if rule == 'structExtends':
                self.structExtends(tokens_list)
            elif rule == 'methodDeclaredFirst':
                self.methodDeclaredFirst(tokens_list)
            elif rule == 'functionCallParameters':
                self.functionCallParameters(tokens_list)
            elif rule == 'notAllowAConstraintToReceiveValue':
                self.notAllowAConstraintToReceiveValue(tokens_list)
            elif rule == 'verifyIfIdentifierExists':
                self.verifyIfIdentifierExists(tokens_list)

    def printSemanticError(self, lineNumber, errorType, got):
        texto = f"SEMANTIC ERROR on line {lineNumber}. {errorType} - {got}"
        return texto

    def getTokenValue(self, token):
        return token.getValue()   

    def nextToken(self,tokens):
        tkn = tokens[self.current_token_value]
        self.current_token_value+=1
        return tkn
    
    def hasNextToken(self,tokens):
        return True if self.current_token_value < len(tokens) else False

    def isVariableDeclaredInsideFunction(self, function_name, variable_name):
        local_symbols = self.symbol_table["local"]
        for simbolo in local_symbols[function_name]:
            if simbolo.getIdentifier() == variable_name:
                return True
        return False

    def getSymbol(self, scope, name, function_name = None):
        if scope == 'local':
            function_variables = self.symbol_table['local'][function_name]
            for variable in function_variables:
                if variable.getIdentifier() == name:
                    return variable
        return None


    def areTwoVariablesWithTheSameType(self, variable1, variable2):
        return True if variable1.getTokenType() == variable2.getTokenType() else False
        




    #Rules


    # Uma struct tem que herdar de outra struct existente.
    def structExtends(self, tokens):
        values = list(map(self.getTokenValue,tokens))
        if 'extends' in values:
            index = values.index('extends')
            index+=1
            if values[index] not in self.symbol_table["local"]:
                print(self.printSemanticError(tokens[index].current_line, "A struct should only extends another struct if the second one exists", tokens[index].getValue()))

    
    # Uma function ou procedure tem que ser declarada antes de a utilizar.

    def methodDeclaredFirst(self, tokens):
        values = list(map(self.getTokenValue,tokens))
        if values[0] not in self.symbol_table["local"]:
            print(self.printSemanticError(tokens[0].current_line, "A function/procedure should be declared before call",tokens[0].getValue()+"()"))



    # A função tem que ser chamada com a quantidade de parâmetros e tipos corretos

    def functionCallParameters(self, tokens):
        current_context = tokens.pop(0)
        values = list(map(self.getTokenValue,tokens))
        function_call_name = values.pop(0)
        tokens.pop(0)
        current_parameter_index = 0
        total_parameters_function = len(self.functions_table[function_call_name].getParameters()) if function_call_name in self.functions_table else 0
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
            if token.getValue() == ')':
                break
            if token.getType() == 'IDE':
                if current_parameter_index >= total_parameters_function:
                    print(self.printSemanticError(token.current_line, "You passed more arguments than the function needs",token.getValue()))
                    break
                if(not self.isVariableDeclaredInsideFunction(current_context, token.getValue())):
                    print(self.printSemanticError(token.current_line, "A variable must be declared first before it's used on a function call",token.getValue()))
                    break
                function_parameter = self.functions_table[function_call_name].getParameters()[current_parameter_index]
                value_symbol = self.getSymbol('local', token.getValue(),current_context)
                if(not self.areTwoVariablesWithTheSameType(value_symbol, function_parameter)):
                    print(self.printSemanticError(token.current_line, "Function/procedure call with the wrong parameter type",token.getValue()))
                current_parameter_index+=1
        if current_parameter_index < total_parameters_function:
                    print(self.printSemanticError(token.current_line, "You passed less arguments than the function needs",token.getValue()))
        self.current_token_value = 0


    # Não é possível atribuir um valor a uma constante, após a sua declaração.

    def notAllowAConstraintToReceiveValue(self,tokens):
        current_context = tokens.pop(0)
        values = list(map(self.getTokenValue,tokens))
        variable_name = values.pop(0)
        variable_token = tokens.pop(0)
        variable_symbol = self.getSymbol('local',variable_name,current_context)
        if variable_symbol!= None:
            if variable_symbol.isAConstSymbol():
                print(self.printSemanticError(variable_token.current_line, "You cannot assign values to const variables after its declaration ",variable_token.getValue()))



#TODO VERIFICAR ESCOPO GLOBAL
    def verifyIfIdentifierExists(self, tokens):
        identifier = tokens[0]
        encontrado = False
        if identifier.getValue() not in self.symbol_table['local']:
            for global_symbol in self.symbol_table['global']:
                if identifier.getValue() == global_symbol.getIdentifier():
                    encontrado = True
            for estrutura_local in self.symbol_table['local']:
                for simbolo in self.symbol_table['local'][estrutura_local]:
                    if identifier.getValue() == simbolo.getIdentifier():
                        encontrado = True
                if estrutura_local in self.functions_table:
                    for parametro in self.functions_table[estrutura_local].getParameters():
                        if identifier.getValue() == parametro.getIdentifier():
                            encontrado = True

        else:
            encontrado = True
        if not encontrado:
            print(self.printSemanticError(identifier.current_line, "An identifier must be initialized before use ",identifier.getValue()))

            




        




        
   









