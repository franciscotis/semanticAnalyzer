from itertools import chain
from string import digits

class Semantic:
    def __init__(self):
        self.symbol_table = []
        self.functions_table = {}
        self.current_token_value = 0
        self.typedef_list = {}
        self.errors_list = []


    def analyze(self, symbol_table, rules, tokens_list, functions_table= None, typedef_list=None):
        try:
            self.symbol_table = symbol_table
            if functions_table is not None:
                self.functions_table = functions_table
            if typedef_list is not None:
                self.typedef_list = typedef_list
            for rule in rules:
                self.current_token_value = 0
                if rule == 'structExtends':
                    self.structExtends(tokens_list)
                elif rule == 'methodDeclaredFirst':
                    self.methodDeclaredFirst(tokens_list)
                elif rule == 'functionCallParameters':
                    self.functionCallParameters(tokens_list)
                elif rule == 'notAllowAConstraintToReceiveValue':
                    self.notAllowAConstraintToReceiveValue(tokens_list)
                elif rule == 'verifyIfIdentiffierExists':
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
                elif rule == 'typedefMustRedefineAllowedTypes':
                    self.typedefMustRedefineAllowedTypes(tokens_list)
                elif rule == 'typedefWithSameIdentifierAndDifferentScopes':
                    self.typedefWithSameIdentifierAndDifferentScopes(tokens_list)
                elif rule == 'methodOverloading':
                    self.methodOverloading(tokens_list)
                elif rule == 'startOverloading':
                    self.startOverloading(tokens_list)
                elif rule == 'verifyIfCallingAProcedureInsteadOfAFunction':
                    self.verifyIfCallingAProcedureInsteadOfAFunction(tokens_list)
                elif rule == 'verifyIfFunctionReturnIsEquivalent':
                    self.verifyIfFunctionReturnIsEquivalent(tokens_list)
                elif rule == 'verifyFuncionReturnType':
                    self.verifyFuncionReturnType(tokens_list)
                elif rule == 'verifyIfVetorAssignmentTypeIsValid':
                    self.verifyIfVetorAssignmentTypeIsValid(tokens_list)
            aux = self.errors_list if self.errors_list != None else []    
            self.errors_list = []
            return aux
        except:
            ("An error ocurred during the semantic analysis. Check your code for syntactic errors and try again")


    def printSemanticError(self, lineNumber, errorType, got):
        texto = f"SEMANTIC ERROR on line {lineNumber}. {errorType} - {got}"
        self.errors_list.append(texto)

    def returnErrors(self):
        return self.errors_list

    def getTokenValue(self, token):
        return token.getValue()   

    def getSymbolValue(self, symbol):
        return symbol.getTokenType()

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
            if function_name in self.symbol_table['local']:
                function_variables = self.symbol_table['local'][function_name]
                for variable in function_variables:
                    if variable.getIdentifier() == name:
                        return variable
        if scope == 'global':
            for variable in self.symbol_table['global']:
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

    def getDataType(self, token)->str:
        if(token.getValue()=='true' or token.getValue()=='true'): return 'BOOLEAN'
        if(token.getType()=='CAD'): return 'STRING'
        if('.' in token.getValue()): return 'REAL'
        if(token.getType()=='NRO'): return 'INT'
        return None

    def getExpression(self, tokens):
        expressao = ''.join(tokens)
        return expressao

    def getDeclaredStructNames(self):
        names = []
        for local in self.symbol_table['local']:
            if local not in self.functions_table:
                names.append(local)
        return names
        
    def getTypedefValues(self):
        return self.typedef_list.values()

    def getFunctionParamsOrder(self, params):
        param_list = []
        for param in params:
            param_list.append(param.getTokenType())
        return param_list

    def getAllFunctionsWithSimilarName(self, name):
        functions = []
        for func in self.functions_table:
            if name in func:
                functions.append(func)
        return functions

    def getQuantityOfParametersAndTypes(self, tokens, current_context= False):
        quantity = 0
        types  = []
        for token in tokens:
            if token.getType() == 'IDE' or token.getType() == 'NRO' or token.getType() =='CAD':
                quantity+=1
                if current_context is not None:
                    value_symbol = self.getSymbol('local', token.getValue(),current_context)
                else:
                    value_symbol = self.getSymbol('global', token.getValue())
                if token.getValue() == ';':
                    break
                if value_symbol is not None:
                    types.append(value_symbol.getTokenType())
                else:
                    if token.getType() == 'NRO':
                        if '.' in token.getValue():
                            types.append('real')
                        else:
                            types.append('int')
                    elif token.getType() == 'CAD':
                        types.append('string')
        return quantity, types


    def getQuantityOfParametersAndTypes2(self, tokens, current_context):
        quantity = 0
        types  = []
        for token in tokens:
            if token[1].getType() == 'IDE' or token[1].getType() == 'NRO' or token[1].getType() == 'CAD':
                quantity+=1
                if token[0] == 'local':
                    value_symbol = self.getSymbol('local', token[1].getValue(),current_context)
                elif token[0] == 'global':
                    value_symbol = self.getSymbol('global', token[1].getValue())
                elif token[0] == '':
                    value_symbol = self.getSymbol('local', token[1].getValue(),current_context)
                    if not value_symbol:
                        value_symbol = self.getSymbol('global', token[1].getValue())
                elif token[0] == 'struct':
                    if token[3] == 'local' or token[3] == '':
                        tkn = self.getSymbol('local', token[2], current_context)
                    elif token[3] == 'global':
                        tkn = self.getSymbol('global', token[2])
                    value_symbol = self.getSymbol('local',token[1].getValue(), tkn.getTokenType())  
                if token[1].getValue() == ';':
                    break
                if value_symbol is not None:
                    types.append(value_symbol.getTokenType())
                else:
                    if token[1].getType() == 'NRO':
                        if '.' in token[1].getValue():
                            types.append('real')
                        else:
                            types.append('int')
                    elif token[1].getType() == 'CAD':
                        types.append('string')
        return quantity, types


    def getQuantityOfParametersAndTypes3(self, tokens, current_context):
        quantity = 0
        types  = []
        for token in tokens:
            if token[1].getType() == 'IDE' or token[1].getType() == 'NRO' or token[1].getType() == 'CAD':
                quantity+=1
                if token[0] == 'local':
                    value_symbol = self.getSymbol('local', token[1].getValue(),current_context)
                elif token[0] == 'global':
                    value_symbol = self.getSymbol('global', token[1].getValue())
                elif token[0] == '':
                    value_symbol = self.getSymbol('local', token[1].getValue(),current_context)
                    if not value_symbol:
                        value_symbol = self.getSymbol('global', token[1].getValue())
                elif token[0] == 'struct':
                    if token[3] == 'local' or token[3] == '':
                        tkn = self.getSymbol('local', token[2], current_context)
                    elif token[3] == 'global':
                        tkn = self.getSymbol('global', token[2])
                    value_symbol = self.getSymbol('local',token[1].getValue(), tkn.getTokenType())  
                if token[1].getValue() == ';':
                    break
                if value_symbol is not None:
                    types.append(value_symbol)
                else:
                    if token[1].getType() == 'NRO':
                        if '.' in token[1].getValue():
                            types.append('real')
                        else:
                            types.append('int')
                    elif token[1].getType() == 'CAD':
                        types.append('string')
        return quantity, types

    
                



    # ======================================================= Rules =======================================================  #
    # TODO: 1 - Index de vetor/matriz tem que ser um número inteiro
    def verifyIfVetorIndexIsInteger(self, tokens):
        tokens2 = tokens.copy()
        #(tokens)
        is_local = False
        is_global = False
        current_context = tokens2[0]
        tokens2 = tokens2[1:]
        values = list(map(self.getTokenValue,tokens2))
        local_global = False
        first_local = False
        index_of_array_name = (values.index("["))-1
        tkns = tokens2[index_of_array_name:]
        is_struct = False
        struct_type = ''
        got_del = False
        while self.hasNextToken(tkns):
            token = self.nextToken(tkns)
            if token.getValue() == '.':
                got_del = True    
                if tkns[tkns.index(token)-1].getValue() == 'local' or tkns[tkns.index(token)-1].getValue() == 'global' and not first_local:
                    local_global = True
                    first_local = True
            else:
                if local_global:
                    local_global = False
                else:
                    if token.getType() == "NRO":
                        if '.' in token.getValue():
                            (self.printSemanticError(token.current_line, "An array index must be integer ",self.getExpression(values)))
                            return
                        else:
                            return
                    if token.getType() == "CAD":
                        (self.printSemanticError(token.current_line, "An array index must be integer ",self.getExpression(values)))
                        return

                    if token.getType() == 'ART':
                        if token.getValue() == '/':
                            (self.printSemanticError(token.current_line, "An array index must be integer ",self.getExpression(values)))
                            return
                    if token.getType() == 'PRE':
                        if token.getValue() == 'local':
                            is_local = True
                        elif token.getValue() == 'global':
                            is_global = True
                        else:
                             (self.printSemanticError(token.current_line, "Invalid token",self.getExpression(values)))
                    if token.getType() == 'IDE':
                        if is_local or is_global:
                            if is_local:
                                symbol = self.getSymbol('local', token.getValue(), current_context)
                                if symbol is None:
                                    (self.printSemanticError(token.current_line, "Local identifier not found",self.getExpression(values)))
                                else:
                                    if symbol.getAssignmentType() !='INT':
                                        (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                            elif is_global:
                                symbol = self.getSymbol('global', token.getValue())
                                if symbol is None:
                                    (self.printSemanticError(token.current_line, "Global identifier not found",self.getExpression(values)))
                                else:
                                    if symbol.getAssignmentType() !='INT':
                                        (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))                                    
                        else:
                            declared_token = self.getSymbol('local', token.getValue(), current_context)
                            if declared_token is not None:
                                if declared_token.getTokenType() in self.symbol_table['local'] and self.peekNextToken(tokens2).getValue() == '.':
                                    is_struct = True
                                    struct_type = declared_token.getTokenType()
                            if is_struct and got_del:
                                is_struct = False
                                got_del = False
                                symbol = self.getSymbol('local', token.getValue(), struct_type)
                                if not symbol:
                                    (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                                    return
                                else:
                                    if (symbol.getAssignmentType() != '' and symbol.getAssignmentType() != 'INT') or symbol.getTokenType() != 'int':
                                        (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                                        return
                            else:
                                if self.peekNextToken(tokens2).getValue() == ']':
                                    symbol = self.getSymbol('global', token.getValue())
                                    if not symbol:
                                        symbol = self.getSymbol('local', token.getValue(), current_context)
                                        if not symbol:
                                            symbol = self.functions_table[token.getValue()]
                                    if symbol is not None:
                                        if symbol.getAssignmentType() !='INT':
                                            if symbol.getIsArray():
                                                if symbol.getTokenType() != 'int':
                                                    (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                                            else:
                                                (self.printSemanticError(token.current_line, "An array index must be integer and must have a value",self.getExpression(values)))
                                                return
                    
        self.current_token_value = 0
        

    # 2 - Variável ou constante tem que ser inicializada antes de a utilizar.
    #TODO VERIFICAR ESCOPO GLOBAL
    def verifyIfIdentifierExists(self, tokens):
        tokens2 = tokens.copy()
        is_local = tokens2[0]
        found_local = False
        is_global = tokens2[1]
        found_global = False
        current_method = tokens2[2]
        identifier = tokens2[3]
        is_function = False
        encontrado = False
        if identifier.getValue() in self.functions_table:
            encontrado = True
            is_function = True
        elif identifier.getValue() not in self.symbol_table['local']:
            for global_symbol in self.symbol_table['global']:
                if identifier.getValue() == global_symbol.getIdentifier():
                    encontrado = True
                    if is_global:
                        found_global = True
            
            for simbolo in self.symbol_table['local'][current_method]:
                if identifier.getValue() == simbolo.getIdentifier():
                    encontrado = True
                    if is_local:
                        found_local = True
            if not encontrado:
                for tab in self.symbol_table['local']:
                    for simbolo in self.symbol_table['local'][tab]:
                        if identifier.getValue() == simbolo.getIdentifier():
                            encontrado = True
                            if is_local:
                                found_local = True
            
            if current_method in self.functions_table:
                for parametro in self.functions_table[current_method].getParameters():
                    if identifier.getValue() == parametro.getIdentifier():
                        encontrado = True
        else:
            encontrado = True

        if encontrado and is_function:
            return
        if is_local and not found_local:
            (self.printSemanticError(identifier.current_line, "Local identifier not found ",identifier.getValue()))

        elif is_global and not found_global:
            (self.printSemanticError(identifier.current_line, "Global identifier not found ",identifier.getValue()))



    # 3 - Uma function ou procedure tem que ser declarada antes de a utilizar.
    def methodDeclaredFirst(self, tokens):
        values = list(map(self.getTokenValue,tokens))

        if values[0] not in self.functions_table:
            (self.printSemanticError(tokens[0].current_line, "A function/procedure should be declared before call",tokens[0].getValue()+"()"))

    # 4 - Uma struct tem que herdar de outra struct existente.
    def structExtends(self, tokens):
        values = list(map(self.getTokenValue,tokens))
        if 'extends' in values:
            index = values.index('extends')
            index+=1
            if values[index] not in self.symbol_table["local"]:
                (self.printSemanticError(tokens[index].current_line, "A struct should only extends another struct if the second one exists", tokens[index].getValue()))


    
    # 6 - A função tem que ser chamada com a quantidade de parâmetros e tipos corretos
    def functionCallParameters(self, tokens):
        tokens2 = tokens.copy()
        current_context = tokens2.pop(0)
        declared_function = tokens2.pop(0)
        found = False
        quantity_parameters = 0
        same_type = True
        equal = False
        params = []
        got_params = False
        values = list(map(self.getTokenValue,tokens2))
        print(values)
        is_local_global = False
        is_local = False
        is_global = False
        is_del = False
        function_call_name = declared_function
        is_rel = False
        dot = False
        struct_value = ''
        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            if token.getType() == 'REL':
                if token.getValue() == '=':
                    is_rel = True
            if token.getType() == 'DEL':
                if token.getValue() == '(':
                    is_del = True
                if token.getValue() == '.' and tokens2[tokens2.index(token)-1].getType() != 'PRE':
                    dot = True
                    struct_value = tokens2[tokens2.index(token)-1].getValue()
                if self.hasNextToken(tokens2):
                    token = self.nextToken(tokens2)
            if is_rel or (self.peekNextToken(tokens2) is not None and self.peekNextToken(tokens2).getValue() == '(') :
                if token.getType() =='IDE':
                    function_call_name = token
                    is_rel = False

            if is_del:
                if token.getType() == 'PRE':
                    if token.getValue() == 'local' or token.getValue() == 'global':
                        is_local = True if token.getValue() == 'local' else False
                        is_global = True if token.getValue() == 'global' else False

                if token.getType() == 'IDE':
                    if self.peekNextToken(tokens2).getValue() != ".":
                        if dot:
                            dot = False
                            tkn = self.getSymbol('local', token.getValue(), current_context)
                            if not tkn:
                                (self.printSemanticError(token.current_line, f"{'Local' if is_local else 'Global'} Identifier not found",token.getValue()))
                                return
                            params.append(['struct', token, struct_value, 'local' if is_local else 'global' if is_global else ''])
                        elif is_local:
                            params.append(['local',token])
                        elif is_global:
                            params.append(['global',token])
                        else:
                            params.append(['',token])
                if token.getType() == 'NRO' or token.getType() =='CAD':
                    params.append(['',token])
        self.current_token_value = 0
        all_functions = self.getAllFunctionsWithSimilarName(function_call_name.getValue())
        quantity, types = self.getQuantityOfParametersAndTypes3(params, current_context)
        for function_name in all_functions:
            params = self.functions_table[function_name].getParameters()
            equal = True
            if quantity == len(params):
                for tipo_parametro, tipo_funcao in zip(types, params):
                    if type(tipo_parametro) == str:
                        if tipo_parametro != tipo_funcao.getTokenType():
                            equal = False
                    else:
                        if tipo_parametro.getTokenType() == tipo_funcao.getTokenType():
                            if tipo_parametro.getIsArray() != tipo_funcao.getIsArray():
                                equal = False
                        else:
                            equal = False
                if equal:
                    found = True
                    same_type = True
                    quantity_parameters = 0
                    return
                else: 
                    same_type = False
            elif quantity < len(params):
                quantity_parameters = -1
            elif quantity > len(params):
                quantity_parameters = 1

        if found:
            if self.functions_table[function_call_name].getIsProcedure():
                (self.printSemanticError(function_call_name.current_line, "Procedures doesn't return a value ",function_call_name.getValue()))


        if not found:
            if not same_type:
                (self.printSemanticError(function_call_name.current_line, "Function/procedure call with the wrong parameter type",function_call_name.getValue()))
            else:
                if quantity_parameters == 1:
                    (self.printSemanticError(function_call_name.current_line, "You passed more arguments than the function needs",function_call_name.getValue()))
                elif quantity_parameters == -1:
                    (self.printSemanticError(function_call_name.current_line, "You passed less arguments than the function needs",function_call_name.getValue()))
            
                
    # TODO: 7 - Expressões tem que ser realizadas entre valores de tipos coerentes (int + string = erro). 
    def verifyIfArithmeticExpressionIsCorrect(self, tokens):
        local_var = tokens[0]
        global_var = tokens[1]
        first_local = False
        first = False
        local_global = False
        current_context = tokens[2]
        tokens = tokens[3:]
        values = list(map(self.getTokenValue,tokens))
        previous_symbol = ''
        has_arithmetic = False
        is_local = False
        is_global = False
        dot = False
        struct_val = ''
        symbol = None
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
            if token.getValue() == '.':
                if tokens[tokens.index(token)-1].getValue() != 'local' and tokens[tokens.index(token)-1].getValue() != 'global':
                    dot = True
                    struct_val = tokens[tokens.index(token)-1]
                if not first_local:
                    first_local = True
                    local_global = True
            else:
                if local_global:
                    local_global = False
                if token.getType() == 'PRE':
                    if token.getValue() == 'local':
                        is_local = True
                    elif token.getValue() == 'global':
                        is_global = True
                if token.getType() == 'IDE':
                    if first:
                        first = False
                        is_local = local_var
                        is_global = global_var
                    if is_local or is_global:
                        if is_local:
                            symbol = self.getSymbol('local', token.getValue(), current_context)
                            if not symbol:
                                (self.printSemanticError(token.current_line, "Local identifier not found  ",token.getValue()))
                        elif is_global:
                            symbol = self.getSymbol('global', token.getValue())
                            if not symbol:
                                (self.printSemanticError(token.current_line, "Global identifier not found  ",token.getValue()))
                        is_local = is_global = False
                    else:
                        if dot:
                            dot = False
                            struct_variable = self.getSymbol('local', struct_val.getValue(), current_context)
                            if not struct_variable:
                                struct_variable = self.getSymbol('global', struct_val.getValue())
                                if not struct_variable:
                                    (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                    return
                            symbol = self.getSymbol('local', token.getValue(), struct_variable.getTokenType())
                        else:
                            if self.peekNextToken(tokens)!= None and self.peekNextToken(tokens).getValue() != '.':
                                symbol = self.getSymbol('local', token.getValue(), current_context)
                            if not symbol:
                                symbol = self.getSymbol('global', token.getValue())
                        if not symbol:
                            if token.getValue() in self.functions_table:
                                symbol = self.functions_table[token.getValue()]
                    if has_arithmetic:
                        if  previous_symbol != '' and symbol is not None and previous_symbol.getTokenType() != symbol.getTokenType():
                            (self.printSemanticError(token.current_line, "Expressions must be performed between values of coherent types",self.getExpression(values)))
                        has_arithmetic = False


                    if (symbol is not None and previous_symbol!= '' and previous_symbol.getIdentifier() != symbol.getIdentifier()) or (symbol is not None and previous_symbol == ''):
                            previous_symbol = symbol
                    
                    

                elif token.getType() == 'ART':
                    if self.isArithmetic(token.getValue()):
                        if token.getValue() == '/':
                            is_division = True
                            
                        has_arithmetic = True
                        is_local = is_global = False
                
        self.current_token_value = 0


        

    # 8 - Itens de condição em if e while tem que ser booleanos.
    def verifyIfBooleanExpressionIsCorrect(self, tokens):
        tokens2 = tokens.copy()
        if type(tokens2[0]) == str:
            current_context = tokens2[0]
        values = list(map(self.getTokenValue,tokens2[1:]))
        tokens2 = tokens2[1:]
        expressao_valida = False
        has_boolean = False
        last_token = tokens2[1]
        expressions_list = []
        dot = False
        struct_name = ''
        symbol = ''
        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            
            last_token = token
            if token.getType() == 'IDE' or token.getType() == 'PRE':
                if dot:
                    if struct_name!= '':
                        struct_symbol = self.getSymbol('local', struct_name, current_context)
                        if not struct_symbol:
                            struct_symbol = self.getSymbol('global', struct_name)
                            if not struct_symbol:
                                (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                return                        
                        symbol = self.getSymbol('local', token.getValue(), struct_symbol.getTokenType())
                else:
                    if self.peekNextToken(tokens2).getValue() != '.':
                        symbol = self.getSymbol('local', token.getValue(), current_context)

                if symbol == '' or symbol == None:
                    symbol = self.getSymbol('global', token.getValue())
                    if not symbol:
                        if (token.getType() == 'PRE' and (token.getValue() == 'true' or token.getValue() == 'false')):
                            has_boolean = True
                else:
                    if (symbol.getValue() == 'true' or symbol.getValue() == 'false' or symbol.getTokenType() == 'boolean'):
                        has_boolean = True
            elif token.getType() == 'REL':
                if self.isRelational(token.getValue()):
                    expressao_valida = True
            elif token.getType() == 'LOG':
                if self.isLogical(token.getValue()):
                    has_boolean = False
                    expressao_valida = False
            elif token.getType() == 'DEL':
                if token.getValue() == ')':
                    if self.peekNextToken(tokens2) is not None:
                        if (self.peekNextToken(tokens2).getValue() != ')' and not self.isRelational(self.peekNextToken(tokens2).getValue()) and not self.isArithmetic(self.peekNextToken(tokens2).getValue())):
                            expressions_list.append(has_boolean or expressao_valida)
                            has_boolean = False
                            expressao_valida = False
                    else:
                        expressions_list.append(has_boolean or expressao_valida)
                        has_boolean = False
                        expressao_valida = False    
                elif token.getValue() == '.':
                    dot = True
                    if tokens2[tokens2.index(token)-1].getValue() != 'local' and tokens2[tokens2.index(token)-1].getValue() != 'global':
                        struct_name = tokens2[tokens2.index(token)-1].getValue()

        self.current_token_value = 0
        if len(expressions_list) == 0:
            expressions_list.append(False)
        if(False in expressions_list ):
            (self.printSemanticError(last_token.current_line, "An condition must have a boolean value ",self.getExpression(values)))
    
    
    # 13 - Não é possível atribuir um valor a uma constante, após a sua declaração.
    def notAllowAConstraintToReceiveValue(self,tokens):
        tokens2 = tokens.copy()
        current_context = tokens2.pop(0)
        values = list(map(self.getTokenValue,tokens2))
        is_local_global = False
        is_local = False
        is_global = False
        if len(tokens2) > 1:
            if tokens2[0].getValue() == 'local' or tokens2[0].getValue() == 'global':
                is_local_global = True
                globloc = tokens2.pop(0)
                values.pop(0)
                tokens2.pop(0)
                values.pop(0)
                if globloc.getValue() == 'local':
                    is_local = True
                else:
                    is_global = True
            variable_name = values.pop(0)
            variable_token = tokens2.pop(0)
            if is_local_global:
                if is_local:
                    variable_symbol = self.getSymbol('local',variable_name,current_context)
                else:
                    variable_symbol = self.getSymbol('global',variable_name)
            else:
                variable_symbol = self.getSymbol('local',variable_name,current_context)
            if variable_symbol!= None:
                if variable_symbol.isAConstSymbol():
                    (self.printSemanticError(variable_token.current_line, "You cannot assign values to const variables after its declaration ",variable_token.getValue()))



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
        struct_value = ''
        dot = False
        symbol = ''
        while self.hasNextToken(tokens):
            token = self.nextToken(tokens)
            last_token = token

            if token.getValue() == '.' and tokens[tokens.index(token)-1].getValue()!= 'local' and tokens[tokens.index(token)-1].getValue()!= 'global':
                struct_value = tokens[tokens.index(token)-1].getValue()
                dot = True

            if token.getType() == 'IDE' or token.getType() == 'PRE':
                if dot:
                    dot = False
                    pre_symbol = self.getSymbol('local', struct_value, current_context)
                    if not pre_symbol:
                        pre_symbol = self.getSymbol('global', struct_value)
                        if not pre_symbol:
                            (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                            return            
                    symbol = self.getSymbol('local', token.getValue(), pre_symbol.getTokenType())
                else:
                    if self.peekNextToken(tokens).getValue()!='.':
                        symbol = self.getSymbol('local', token.getValue(), current_context)
                if relational_value and current_type != '':
                    if type(current_type)  == str:
                        if symbol and symbol.getTokenType() != current_type.getTokenType():
                            valor_verdadeiro = False
                            relational_value = False
                    elif symbol and symbol.getTokenType() != current_type.getTokenType():
                        valor_verdadeiro = False
                        relational_value = False
                if type(current_type)  == str:
                    if (symbol and symbol!= '' and current_type!= '' and current_type!= symbol.getIdentifier()) or (symbol and symbol!= '' and current_type == ''):
                        current_type = symbol
                elif (symbol and current_type!= '' and current_type.getIdentifier()!= symbol.getIdentifier()) or (symbol and current_type == ''):
                    current_type = symbol
                if not symbol:
                    symbol = self.getSymbol('global', token.getValue())
                    if type(symbol)!= str and type(current_type)!= str:
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
        self.current_token_value = 0
        if False in expressions_list:
            (self.printSemanticError(last_token.current_line, "You can't compare two different kinds of variables",self.getExpression(values)))


    def notAllowAssignNotInitializedVariable(self, tokens):
        tokens2 = tokens.copy()
        is_local = False
        is_global = False
        has_local_global = False
        function_name = tokens2.pop(0)
        values = list(map(self.getTokenValue, tokens2))
        if type(tokens2[0])!= str and type(tokens2[1])!=str and tokens2[0].getValue() == tokens2[1].getValue():
            tokens2.pop(0)
            values.pop(0)
        has_rel = False
        token_left = True
        first_token = ''
        isFunction = False
        dot = False
        struct_value = ''

        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)

            if token.getValue() == '.' and tokens2[tokens2.index(token)-1].getValue() != 'local' and tokens2[tokens2.index(token)-1].getValue() != 'global':
                dot = True
                struct_value = tokens2[tokens2.index(token)-1].getValue()

            if token.getType() == 'PRE':
                if token.getValue() == 'local' or 'global':
                    is_local = True if token.getValue() == 'local' else False
                    is_global = True if token.getValue() == 'global' else False
                    has_local_global = True
            
            if token.getType() == 'REL':
                has_rel = True
                

            if token.getType() != 'IDE':
                if token_left and self.peekNextToken(tokens2).getValue()!= '.' and token.getValue()!= '.':
                    (self.printSemanticError(token.current_line, "Invalid variable", token.getValue()))
                    return

            if token.getType() == 'IDE':
                if has_rel:
                    has_rel = False
                    if token.getValue() in self.functions_table:
                        isFunction = True
                if token_left:
                    if self.peekNextToken(tokens2).getValue() != '.':
                        token_left = False
                    if dot:
                        dot = False
                        struct_symbol = self.getSymbol('local', struct_value, function_name)
                        if not struct_symbol:
                            struct_symbol = self.getSymbol('global', struct_value)
                            if not struct_symbol:
                                (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                return            
                        symblocal = self.getSymbol('local', token.getValue(), struct_symbol.getTokenType())
                    else:
                        symblocal = self.getSymbol('local', token.getValue(), function_name)
                        symbglobal = self.getSymbol('global', token.getValue())
                    if has_local_global:
                        has_local_global = False
                        if is_local:
                            symbol1 = symblocal
                        else:
                            symbol1 = symbglobal
                    else:
                        symbol1 = symblocal if symblocal is not None else symbglobal
                    first_token = symbol1
                    if first_token is None:
                        (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                        return
                    
                else:
                    if dot:
                        dot = False
                        struct_symbol = self.getSymbol('local', struct_value, function_name)
                        if not struct_symbol:
                            struct_symbol = self.getSymbol('global', struct_value)
                            if not struct_symbol:
                                (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                return                   
                        else:
                            (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                            return
                        symblocal = self.getSymbol('local', token.getValue(), struct_symbol.getTokenType())
                    else:                       
                        symblocal = self.getSymbol('local', token.getValue(), function_name)
                        symbglobal = self.getSymbol('global', token.getValue())
                    if has_local_global:
                        has_local_global = False
                        if is_local:
                            symbol1 = symblocal
                        else:
                            symbol1 = symbglobal
                    else:
                        symbol1 = symblocal if symblocal is not None else symbglobal
                        if not symbol1:
                            if token.getValue() in self.functions_table:
                                symbol1 = self.functions_table[token.getValue()]
                    if symbol1 is None:
                        if function_name in self.functions_table:
                            function_symb = self.functions_table[function_name]
                            found = False
                            for param in function_symb.getParameters():
                                if param.getIdentifier() == token.getValue():
                                    found = True
                            if not found:
                                if token.getType()!= 'NRO' or token.getType()!= 'CAD':
                                    (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                    return
                    else:
                        
                        if(symbol1.getTokenType()!= first_token.getTokenType() or (symbol1.getIsArray() != first_token.getIsArray() and ('[' not in values))):
                            if not (symbol1 is not None and symbol1.getIsProcedure()) and not isFunction and self.peekNextToken(tokens2).getValue()!= ".":
                                (self.printSemanticError(token.current_line, "Variables must have the same type", token.getValue()))
            elif token.getType() == 'NRO' or token.getType() == 'CAD':
                token_type = ('real' if '.' in token.getValue() else 'int') if token.getType() == 'NRO' else 'string'
                if token_type != first_token.getTokenType():
                    if not (symbol1 is not None and symbol1.getIsProcedure()):
                        (self.printSemanticError(token.current_line, "Variables must have the same type", token.getValue()))
        self.current_token_value = 0
    
    def notAllowBooleanAndStringIncrements(self, tokens):
        tokens2 = tokens.copy()
        function_name = tokens2.pop(0)
        values = list(map(self.getTokenValue, tokens2))
        is_local = is_global = False
        is_art = False
        struct_value = ''
        dot = False
        symbol = ''

        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            if token.getValue() == '.' and tokens2[tokens2.index(token)-1].getValue() != 'local' and tokens2[tokens2.index(token)-1].getValue() != 'global':
                dot = True
                struct_value = tokens2[tokens2.index(token)-1].getValue()

            if token.getType() == 'PRE':
                is_local = True if token.getValue() == 'local' else False
                is_global = True if token.getValue() == 'global' else False

            if token.getType() == 'ART':
                if token.getValue() == '++' or token.getValue() == '--':
                    is_art = True

            if token.getType() == 'IDE':
                if dot:
                    struct_symbol = self.getSymbol('local', struct_value, function_name)
                    if not struct_symbol:
                        struct_symbol = self.getSymbol('global', struct_value)
                        if not struct_symbol:
                            (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                            return            
                    symbol = self.getSymbol('local', token.getValue(), struct_symbol.getTokenType())
                else:
                    if is_local:
                        symbol = self.getSymbol('local', token.getValue(), function_name)
                    elif is_global:
                        symbol = self.getSymbol('global', token.getValue())
                    else:
                        symbol = self.getSymbol('local', token.getValue(), function_name)
                        if symbol is None:
                            symbol = self.getSymbol('global', token.getValue())
                        if(not symbol): return
        if is_art:
            is_art = False
            if symbol:
                if(symbol.getTokenType()=='boolean' or symbol.getTokenType()=='string'):
                    (self.printSemanticError(token.current_line, "You cannot increment/decrement boolean or string variables ", token.getValue()))
        self.current_token_value = 0

            
        
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
            (self.printSemanticError(identifier.current_line, f'{ "Local" if inside_method or inside_struct else "Global"} Variable already declared ',identifier.getValue()))
        

    def typedefMustRedefineAllowedTypes(self, tokens):
        typedef_type, inside_method = tokens[0], tokens[1]
        struct_names = self.getDeclaredStructNames()
        if typedef_type.getValue() not in list(chain(['int', 'real', 'boolean', 'string'], struct_names)):
             (self.printSemanticError(typedef_type.current_line, "A typedef must redefine allowed types",typedef_type.getValue()))

    def typedefWithSameIdentifierAndDifferentScopes(self, tokens):
        typedef_type, typedef_new_type, inside_method = tokens[0], tokens[1], tokens[2]
        struct_names = self.getDeclaredStructNames()
        if inside_method:
            if typedef_type.getValue() in list(chain(['int', 'real', 'boolean', 'string'], struct_names)):
                if (typedef_new_type.getValue() in list(self.getTypedefValues())):
                    (self.printSemanticError(typedef_type.current_line, "You can't redefine a type with the same identifier within different scopes",typedef_type.getValue()))

    def methodOverloading(self, tokens):
        method_name, method_token, parameters = tokens[0], tokens[1], tokens[2]
        for fkey in self.functions_table:
            if ((fkey in method_name) or (fkey.translate(str.maketrans('','',digits))) == method_name.translate(str.maketrans('','',digits))) and fkey!= method_name:
                existing_method = self.functions_table[fkey]
                if existing_method :
                    if len(parameters) == len(existing_method.getParameters()):
                        if parameters == self.getFunctionParamsOrder(existing_method.getParameters()):
                            (self.printSemanticError(method_token.current_line, "This is not a valid method override",method_token.getValue()))
                    
    def startOverloading(self, tokens):
        token = tokens[0]
        if 'start' in self.symbol_table['local']:
            (self.printSemanticError(token.current_line, "You cannot override the start procedure ",token.getValue()))

    def verifyIfCallingAProcedureInsteadOfAFunction(self, tokens):
        tokens2 = tokens.copy()
        
        current_context = tokens2.pop(0)
        declared_function = tokens2.pop(0)
        values = list(map(self.getTokenValue, tokens2))
        has_rel = False
        got_func_name = False
        function_call_name = ''
        function_params = []
        dot = False
        struct_value = ''
        is_local = False
        is_global = False
        is_del = False

        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)

            if token.getValue() == '.' and tokens2[tokens2.index(token)-1].getValue() != 'local' and tokens2[tokens2.index(token)-1].getValue() != 'global':
                dot = True
                struct_value = tokens2[tokens2.index(token)-1].getValue()
            
            if token.getType() == 'DEL':
                if token.getValue() == '(':
                    is_del = True

            if token.getType() == 'REL':
                has_rel = True

            if token.getType() == 'PRE':
                if token.getValue() == 'local' or token.getValue() == 'global':
                    is_local = True if token.getValue() == 'local' else False
                    is_global = True if token.getValue() == 'global' else False

            if token.getType() == 'IDE':
                if self.peekNextToken(tokens2).getValue() == '(' and not got_func_name:
                    got_func_name = True
                    function_call_name = token
                if is_del:
                    if self.peekNextToken(tokens2).getValue() != ".":
                        if dot:
                            dot = False
                            function_params.append(['struct', token, struct_value])
                        elif is_local:
                            function_params.append(['local',token])
                        elif is_global:
                            function_params.append(['global',token])
                        else:
                            function_params.append(['',token])
                            
                    
            if token.getType() == 'NRO' or token.getType() =='CAD':
                function_params.append(['',token])
        self.current_token_value = 0
        quantity, types = self.getQuantityOfParametersAndTypes2(function_params, current_context)
        found = False
        for func in self.functions_table:
            function_parameter = self.functions_table[func].getParameters()
            func_param_size = len(function_parameter)
            if function_call_name.getValue() in func:
                if quantity == func_param_size:
                    found = True
                    if self.functions_table[func].getIsProcedure():
                        self.printSemanticError(function_call_name.current_line, "Procedures doesn't return a value ",function_call_name.getValue())
                        return
            if not found:
                self.printSemanticError(function_call_name.current_line, "Function not found ",function_call_name.getValue())
                return

    def verifyIfFunctionReturnIsEquivalent(self, tokens):
        tokens2 = tokens.copy()
        is_local = False
        is_global = False
        current_context = tokens2.pop(0)

        declared_function = tokens2.pop(0)
        is_first_variable = True
        is_relational = False
        time_for_params = False
        pre_variable = ''
        function_call_name = ''
        function_params = []
        dot = False
        struct_value = ''
        

        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            if token.getType() == "PRE":
                if token.getValue() == 'local' or token.getValue() == 'global':
                    if token.getValue() == 'local':
                        is_local = True
                    else:
                        is_global = True

            if token.getValue() == '.' and tokens2[tokens2.index(token)-1].getValue() != 'local' and tokens2[tokens2.index(token)-1].getValue() != 'global':
                dot = True
                struct_value = tokens2[tokens2.index(token)-1].getValue()

            if token.getType() == "REL":
                is_relational = True
                
            if token.getType() == "IDE":
                
                if is_local or is_global:
                    if is_first_variable and self.peekNextToken(tokens2).getValue() != '.':
                        is_first_variable = False
                        pre_variable = token
                        if is_local:

                            symbol = self.getSymbol('local', pre_variable.getValue(), current_context)
                            if not symbol:
                                (self.printSemanticError(pre_variable.current_line, "Symbol not found ",pre_variable.getValue()))
                                return
                        else:
                            symbol = self.getSymbol('global', pre_variable.getValue())
                            if not symbol:
                                (self.printSemanticError(pre_variable.current_line, "Symbol not found ",pre_variable.getValue()))
                                return
                else:
                    if is_first_variable and self.peekNextToken(tokens2).getValue() != '.':
                        is_first_variable = False
                        if dot:
                            dot = False
                            struct_symbol = self.getSymbol('local', struct_value, current_context)
                            if not struct_symbol:
                                struct_symbol = self.getSymbol('global', struct_value)
                                if not struct_symbol:
                                    (self.printSemanticError(token.current_line, "An identifier must be valid before assign to a variable", token.getValue()))
                                    return            
                            symbol = self.getSymbol('local', token.getValue(), struct_symbol.getTokenType())
                        else:
                            pre_variable = token
                            symbol = self.getSymbol('local', pre_variable.getValue(), current_context)
                            if not symbol:
                                symbol = self.getSymbol('global', pre_variable.getValue())
                                if not symbol:
                                    (self.printSemanticError(pre_variable.current_line, "Symbol not found ",pre_variable.getValue()))
                                    return
                if time_for_params:
                    if self.peekNextToken(tokens2).getValue()!= '.':
                        if dot:
                            dot = False
                            function_params.append(['struct', token, struct_value])
                        elif is_local:
                            function_params.append(['local', token])
                        elif is_global:
                            function_params.append(['', token])
                    if token.getType() == 'NRO' or token.getType() == 'CAD':
                        function_params.append(['', token])
                if is_relational:
                    is_relational = False
                    function_call_name = token
                    time_for_params = True
        
        self.current_token_value = 0

        quantity, types = self.getQuantityOfParametersAndTypes2(function_params, current_context)
        for func in self.functions_table:
            function_parameter = self.functions_table[func].getParameters()
            func_param_size = len(function_parameter)
            if function_call_name.getValue() in func :
                if quantity == func_param_size:
                    if self.functions_table[func].getAssignmentType().lower() != symbol.getTokenType():
                        (self.printSemanticError(function_call_name.current_line, "Function return's type doesn't match with variable type ",function_call_name.getValue()))
    
    def verifyFuncionReturnType(self, tokens):
        function_name = tokens.pop(0)
        tokens2 = tokens[0:-1]
        symbol = None
        values = list(map(self.getTokenValue, tokens2))
        if(len(tokens2)==0): return

        if(len(tokens2)==1):
            token = tokens2[0]
            if(token.getType()=='IDE'):
                parameters = self.functions_table[function_name].getParameters()
                if(token.getValue() in [param.getIdentifier() for param in parameters]):
                    get_symbol = lambda param: (token.getValue()==param.getIdentifier())
                    symbol = list(filter(get_symbol, parameters))[0]

                elif(self.getSymbol('local', token.getValue(), function_name)):
                    symbol = self.getSymbol('local', token.getValue(), function_name)
                
                if(not symbol): return

                if(self.functions_table.get(function_name).getAssignmentType() == symbol.getTokenType().upper()): 
                    return

            elif(self.functions_table.get(function_name).getAssignmentType() == self.getDataType(token)): return
            (self.printSemanticError(token.current_line, "Function's return must be the same declared type", token.getValue()))

        elif(tokens2[0].getType()=='IDE'):
            token = tokens2[0]
            if(not self.functions_table.get(token.getValue())):
                symbol = self.getSymbol('local', token.getValue(), function_name)
                if not symbol:
                    symbol = self.getSymbol('global', token.getValue())
                    if not symbol:
                        (self.printSemanticError(token.current_line, "A function should be declared before call", token.getValue()+"()"))
                return
        
            function_identifier = self.functions_table.get(tokens2[0].getValue())
            if(self.functions_table.get(function_name).getAssignmentType() == function_identifier.getAssignmentType()): return
            (self.printSemanticError(token.current_line, "Function's return must be the same declared type", token.getValue()+"()"))
        

    def verifyIfVetorAssignmentTypeIsValid(self, tokens):
        tokens2 = tokens.copy()
        function_name = tokens2.pop(0)
        current_symbol = tokens2.pop(0)
        values = list(map(self.getTokenValue, tokens2))
        tipo = ''
        is_local = is_global = False
        symbol = ''
        while self.hasNextToken(tokens2):
            token = self.nextToken(tokens2)
            if token.getValue() == ']':
                return
            if token.getType() == 'PRE':
                is_local = True if token.getValue() == 'local' else False
                is_global = True if token.getValue() == 'global' else False

            if token.getType() == 'IDE':
                if is_local:
                    is_local = False
                    symbol = self.getSymbol('local', token.getValue(), function_name)
                elif is_global:
                    is_global = False
                    symbol = self.getSymbol('global', token.getValue())
                else:
                    symbol = self.getSymbol('local', token.getValue(), function_name)
                    if symbol is None:
                        symbol = self.getSymbol('global', token.getValue())

                if symbol is None or symbol == '':
                    (self.printSemanticError(token.current_line, "Identifier not found", token.getValue()))
                else:
                    tipo =  symbol.getTokenType()
            


            if token.getType() == 'NRO':
                tipo = 'real' if '.' in token.getValue() else 'int'
            elif token.getType() == 'CAD':
                tipo = 'string'
            elif token.getType() == 'BOOLEAN':
                tipo = 'boolean'
            if tipo!= '' and tipo != current_symbol.getTokenType():
                (self.printSemanticError(tokens2[0].current_line, f"Array declared as {current_symbol.getTokenType()} and you are adding a(n) {tipo} value ", current_symbol.getIdentifier()))
                return

        self.current_token_value = 0

