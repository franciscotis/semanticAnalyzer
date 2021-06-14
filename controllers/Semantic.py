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
            elif rule == 'checkBooleanCondition':
                self.verifyIfBooleanExpressionIsCorrect(tokens_list)
            elif rule == 'notAllowBooleanAndStringIncrements':
                self.notAllowBooleanAndStringIncrements(tokens_list)
            elif rule == 'checkTypeComparation':
                self.notAllowComparationBetweenDifferentTypesOfVariables(tokens_list)
            elif rule == 'verifyIfArithmeticExpressionIsCorrect':
                self.verifyIfArithmeticExpressionIsCorrect(tokens_list)
            elif rule == 'notAllowAssignNotInitializedVariable':
                self.notAllowAssignNotInitializedVariable(tokens_list)
            elif rule == 'verifyIfVetorIndexIsInteger':
                self.verifyIfVetorIndexIsInteger(tokens_list)
            elif rule == 'verifyIfGlobalVariableAlreadyExists':
                self.verifyIfGlobalVariableAlreadyExists(tokens_list)


    def printSemanticError(self, lineNumber, errorType, got):
        texto = f"SEMANTIC ERROR on line {lineNumber}. {errorType} - {got}"
        return texto

    def getTokenValue(self, token):
        return token.getValue()   

    def nextToken(self,tokens):
        tkn = tokens[self.current_token_value]
        self.current_token_value+=1
        return tkn
    
    def peekNextToken(self, tokens):
        if self.hasNextToken(tokens):
            return tokens[self.current_token_value]
        else:
            return None 
    
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

    def isRelational(self, token):
        return True if token == '==' or token == '!=' or token == '>' or token == '>=' or token == '<' or token == '<=' else False

    def isLogical(self, token):
        return True if token == '&&' or token == '||' else False

    def isArithmetic(self, token):
        return True if token == '+' or token == '-' or token == '*' or token == '/' else False

    def getExpression(self, tokens):
        expressao = ''.join(tokens)
        return expressao
        

    # ======================================================= Rules =======================================================  #
    # TODO: 1 - Index de vetor/matriz tem que ser um número inteiro
    def verifyIfVetorIndexIsInteger(self, tokens):
        #Número - ok 
        #Expressão
        #Retorno de função
        #identificador

        tokens2 = tokens.copy()
        current_context = tokens2[0]
        tokens2 = tokens2[1:]
        values = list(map(self.getTokenValue,tokens2))
        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            if token.getType() == "NRO":
                if '.' in token.getValue():
                    print(self.printSemanticError(token.current_line, "An array index must be integer ",self.getExpression(values)))
                    return
            if token.getType() == 'ART':
                if token.getValue() == '/':
                    print(self.printSemanticError(token.current_line, "An array index must be integer ",self.getExpression(values)))
                    return
            if token.getType() == 'IDE':
                symbol = self.getSymbol('global', token.getValue())
                if not symbol:
                    symbol = self.getSymbol('local', token.getValue(), current_context)
                    if not symbol:
                        symbol = self.functions_table[token.getValue()]
                if symbol is not None:
                    if symbol.getAssignmentType() !='INT':
                        print(self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                        return
        self.current_token_value = 0
        

    # 2 - Variável ou constante tem que ser inicializada antes de a utilizar.
    #TODO VERIFICAR ESCOPO GLOBAL
    def verifyIfIdentifierExists(self, tokens):
        identifier = tokens[0]
        encontrado = False
        if identifier.getValue() in self.functions_table:
            encontrado = True
        elif identifier.getValue() not in self.symbol_table['local']:
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


    # 3 - Uma function ou procedure tem que ser declarada antes de a utilizar.
    def methodDeclaredFirst(self, tokens):
        values = list(map(self.getTokenValue,tokens))
        print(values)
        if values[0] not in self.functions_table:
            print(self.printSemanticError(tokens[0].current_line, "A function/procedure should be declared before call",tokens[0].getValue()+"()"))

    # 4 - Uma struct tem que herdar de outra struct existente.
    def structExtends(self, tokens):
        values = list(map(self.getTokenValue,tokens))
        if 'extends' in values:
            index = values.index('extends')
            index+=1
            if values[index] not in self.symbol_table["local"]:
                print(self.printSemanticError(tokens[index].current_line, "A struct should only extends another struct if the second one exists", tokens[index].getValue()))


    # TODO: 5 - Sobrecarga realmente tem que ser sobrecarga (e não sobrescrita).
    def verifyIfOverloadExists(self, tokens):
        pass
        
    
    # 6 - A função tem que ser chamada com a quantidade de parâmetros e tipos corretos
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


    # TODO: 7 - Expressões tem que ser realizadas entre valores de tipos coerentes (int + string = erro). [FINALIZAR]
    def verifyIfArithmeticExpressionIsCorrect(self, tokens):
        current_context = tokens[0]
        tokens = tokens[1:]
        values = list(map(self.getTokenValue,tokens))
        previous_symbol = ''
        has_arithmetic = False
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
            if token.getType() == 'IDE':
                symbol = self.getSymbol('local', token.getValue(), current_context)
                if not symbol:
                    symbol = self.getSymbol('global', token.getValue())
                    if not symbol:
                        symbol = self.functions_table[token.getValue()]
                        if not symbol:
                            print(self.printSemanticError(token.current_line, "An identifier must be initialized before use ",token.getValue()))
                if has_arithmetic:
                    if  previous_symbol != '' and symbol is not None and previous_symbol.getAssignmentType() != symbol.getAssignmentType():
                        print(self.printSemanticError(token.current_line, "Expressions must be performed between values of coherent types",self.getExpression(values)))
                        has_arithmetic = False
                if (symbol is not None and previous_symbol!= '' and previous_symbol.getIdentifier() != symbol.getIdentifier()) or symbol is not None and previous_symbol == '':
                    previous_symbol = symbol
            elif token.getType() == 'ART':
                if self.isArithmetic(token.getValue()):
                    has_arithmetic = True
                
        self.current_token_value = 0


        

    # 8 - Itens de condição em if e while tem que ser booleanos.
    def verifyIfBooleanExpressionIsCorrect(self, tokens):
        if type(tokens[0]) == str:
            current_context = tokens[0]
        values = list(map(self.getTokenValue,tokens[1:]))
        tokens = tokens[1:]
        expressao_valida = False
        has_boolean = False
        last_token = tokens[1]
        expressions_list = []
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
           # print(token.getType())
            last_token = token
            if token.getType() == 'IDE' or token.getType() == 'PRE':
                symbol = self.getSymbol('local', token.getValue(), current_context)
                if not symbol:
                    symbol = self.getSymbol('global', token.getValue())
                    if not symbol:
                        if (token.getType() == 'PRE' and (token.getValue() == 'true' or token.getValue() == 'false')):
                            has_boolean = True
                else:
                    if (symbol.getValue() == 'true' or symbol.getValue() == 'false'):
                        has_boolean = True
            elif token.getType() == 'REL':
                if self.isRelational(token.getValue()):
                    expressao_valida = True
            elif token.getType() == 'LOG':
                if self.isLogical(token.getValue()):
                    expressions_list.append(has_boolean or expressao_valida)
                    has_boolean = False
                    expressao_valida = False
            elif token.getType() == 'DEL':
                if token.getValue() == ')':
                    if self.peekNextToken(tokens) is not None:
                        if (self.peekNextToken(tokens).getValue() != ')' and not self.isRelational(self.peekNextToken(tokens).getValue()) and not self.isArithmetic(self.peekNextToken(tokens).getValue())):
                            expressions_list.append(has_boolean or expressao_valida)
                            has_boolean = False
                            expressao_valida = False
                    else:
                        expressions_list.append(has_boolean or expressao_valida)
                        has_boolean = False
                        expressao_valida = False                  
        self.current_token_value = 0
        if len(expressions_list) == 0:
            expressions_list.append(False)
        if(False in expressions_list ):
            print(self.printSemanticError(last_token.current_line, "An condition must have a boolean value ",self.getExpression(values)))
    

    # TODO: 10 - Se declarar uma variável como um tipo, não pode atribuir um valor de outro tipo nela
    def verifyVariableTypeAssignment(self, tokens):
        pass

    
    # 13 - Não é possível atribuir um valor a uma constante, após a sua declaração.
    def notAllowAConstraintToReceiveValue(self,tokens):
        tokens2 = tokens.copy()
        current_context = tokens2.pop(0)
        values = list(map(self.getTokenValue,tokens2))
        variable_name = values.pop(0)
        variable_token = tokens2.pop(0)
        variable_symbol = self.getSymbol('local',variable_name,current_context)
        if variable_symbol!= None:
            if variable_symbol.isAConstSymbol():
                print(self.printSemanticError(variable_token.current_line, "You cannot assign values to const variables after its declaration ",variable_token.getValue()))


    # Um identificador deve ser declarado antes de seu uso


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


    # 14 - Não é possível realizar a comparação de valores de tipos diferentes.

    def notAllowComparationBetweenDifferentTypesOfVariables(self, tokens):
        if type(tokens[0]) == str:
            current_context = tokens[0]
        values = list(map(self.getTokenValue,tokens[1:]))
        last_token = tokens[0]
        current_type = ''
        relational_value = False
        tokens = tokens[1:]
        valor_verdadeiro = True
        expressions_list = []
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
            last_token = token
            if token.getType() == 'IDE' or token.getType() == 'PRE':
                symbol = self.getSymbol('local', token.getValue(), current_context)
                if relational_value and current_type != '':
                    if type(current_type)  == str:
                        if symbol and symbol.getAssignmentType() != current_type:
                            valor_verdadeiro = False
                            relational_value = False
                    elif symbol and symbol.getAssignmentType() != current_type.getAssignmentType():
                        valor_verdadeiro = False
                        relational_value = False
                if type(current_type)  == str:
                    if (symbol and current_type!= '' and current_type!= symbol.getIdentifier()) or (symbol and current_type == ''):
                        current_type = symbol
                elif (symbol and current_type!= '' and current_type.getIdentifier()!= symbol.getIdentifier()) or (symbol and current_type == ''):
                    current_type = symbol
                if not symbol:
                    symbol = self.getSymbol('global', token.getValue())
                    if (symbol and current_type.getIdentifier()!= symbol.getIdentifier()) or (symbol and current_type == ''):
                        current_type = symbol
                    if symbol and current_type.getIdentifier()!= symbol.getIdentifier():
                        valor_verdadeiro = False
                        relational_value = False
                    if not symbol:
                        if (token.getType() == 'PRE' and (token.getValue() == 'true' or token.getValue() == 'false')):
                            current_type = 'BOOLEAN'
                            if 'BOOLEAN' != current_type:
                                valor_verdadeiro = False
                                relational_value = False
            elif token.getType() == 'REL':
                if self.isRelational(token.getValue()):
                    relational_value = True
            elif token.getType() == 'LOG':
                if self.isLogical(token.getValue()):
                    expressions_list.append(valor_verdadeiro)
                    valor_verdadeiro = True
                    current_type = '' 
            elif token.getValue() == ')':
                expressions_list.append(valor_verdadeiro)
        if False in expressions_list:
            print(self.printSemanticError(last_token.current_line, "You can't compare two different kinds of variables",self.getExpression(values)))


    def notAllowAssignNotInitializedVariable(self, tokens):
        tokens2 = tokens.copy()
        function_name = tokens2.pop(0)
        identifier1, identifier2 = tokens2[0], tokens2[2]        
        symbol1 = self.getSymbol('local', identifier1.getValue(), function_name)
        symbol2 = self.getSymbol('local', identifier2.getValue(), function_name)
        
        if(not symbol1 or not symbol2): return
        if(symbol2.getValue()==''):
            print(self.printSemanticError(identifier1.current_line, "An identifier must be initialized before assign to a variable", identifier2.getValue()))
        elif(symbol1.getTokenType()!=symbol2.getTokenType()):
            print(self.printSemanticError(identifier1.current_line, "Variables must be the same type", identifier2.getValue()))
    
    def notAllowBooleanAndStringIncrements(self, tokens):
        tokens2 = tokens.copy()
        function_name = tokens2.pop(0)
        values = list(map(self.getTokenValue, tokens2))
        
        index  = values.index('++') if('++' in values) else values.index('--')
        token1, token2 = tokens2[index-1], tokens2[index+1]
        identifier = token1 if(token1.getType()=='IDE') else token2
        
        symbol = self.getSymbol('local', identifier.getValue(), function_name)
        
        if(not symbol): return
        if(symbol.getAssignmentType()=='BOOLEAN' or symbol.getAssignmentType()=='STRING'):
            print(self.printSemanticError(identifier.current_line, "You cannot increment/decrement boolean or string variables ", identifier.getValue()))
    

    def verifyIfGlobalVariableAlreadyExists(self, tokens):
        identifier, inside_method, inside_struct, current_method = tokens[0], tokens[1], tokens[2], tokens[3]
        encontrado = False
        if inside_method or inside_struct:
            tabela_metodo = self.symbol_table['local'][current_method]
            for simbolo in tabela_metodo:
                if identifier.getValue() == simbolo.getIdentifier():
                    encontrado = True
        else:
            for simbolo in self.symbol_table['global']:
                if identifier.getValue() == simbolo.getIdentifier():
                    encontrado = True
        
        if encontrado:
            print(self.printSemanticError(identifier.current_line, f'{ "Local" if inside_method or inside_struct else "Global"} Variable already declared ',identifier.getValue()))
        
