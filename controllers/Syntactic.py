from model.Symbol import Symbol
from itertools import chain
import re 
class Syntactic:
    def __init__(self, lexical, semantic, firstSet, followSet):
        self.lexical = lexical
        self.token = ''    
        self.firstSet  = firstSet
        self.followSet = followSet
        self.token_list = []
        self.symbol_table = {"global": [], "local": {}}
        self.functions_table = {}
        self.inside_method = False
        self.inside_struct = False
        self.inside_code = False
        self.is_const = False
        self.current_symbol = ''
        self.current_struct = ''
        self.declared_function = ''
        self.current_variable_type = ''
        self.current_context = ''
        self.current_var_value = ''
        self.token_value_list = []
        self.semantic = semantic

    def run(self):
        self.getNextToken()
        self.inicio()
        self.lexical.file.print_file(self.token_list)




    def getNextToken(self):
        self.token = self.lexical.obterToken()
        if self.token is not None:
            self.token_list.append(self.token.toString())
            self.token_value_list.append(self.token)
    
    def getError(self, sync_tokens:list):
        while(self.token is not None):
            for follow in sync_tokens:
                if(self.token.getValue()==follow): return
                if(self.token.getType()==follow):  return
            self.getNextToken()

    

    def printError(self, lineNumber, expected, got):
        esperado = ', '.join(expected)
        texto = f"ERROR on line {lineNumber}: Expecting [{esperado}]. Got: '{got}'"
        return texto

    def printSemanticError(self, lineNumber, errorType, got):
        texto = f"SEMANTIC ERROR on line {lineNumber}. {errorType} - {got}"
        return texto


    def inicio(self):
        if self.token is not None:
            if(self.token.getValue() in self.firstSet["TYPEDEFDECLARATION"]):
                self.typedefDeclaration()
                self.inicio()
            elif(self.token.getValue() in self.firstSet["STRUCTDECLARATION"]):
                self.inside_struct = True
                self.structDeclaration()
                self.inside_struct = False
                self.inicio()
            elif(self.token.getValue() in self.firstSet["VARDECLARATION"]):
                self.varDeclaration()
                self.header1()
            elif(self.token.getValue() in self.firstSet["CONSTDECLARATION"]):
                self.constDeclaration()
                self.header2()
            elif(self.token.getValue() in self.firstSet["METHODS"]):
                self.methods()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["INICIO"], self.token.getValue())) 
                self.getError(self.followSet["INICIO"])

    def header1(self):
        if self.token is not None:
            if self.token.getValue() in self.firstSet["TYPEDEFDECLARATION"]:
                self.typedefDeclaration()
                self.header1()
            elif self.token.getValue() in self.firstSet["STRUCTDECLARATION"]:
                self.inside_struct = True
                self.structDeclaration()
                self.inside_struct = False
                self.header1()
            elif self.token.getValue() in self.firstSet["CONSTDECLARATION"]:
                self.constDeclaration()
                self.header3()
            elif self.token.getValue() in self.firstSet["METHODS"]:
                self.methods()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["HEADER1"], self.token.getValue()))
                self.getError(self.followSet["HEADER1"])


    def header2(self):
        if self.token is not None:
            if self.token.getValue() in self.firstSet["TYPEDEFDECLARATION"]:
                self.typedefDeclaration()
                self.header2()  
            elif self.token.getValue() in self.firstSet["STRUCTDECLARATION"]:
                self.inside_struct = True
                self.structDeclaration()
                self.inside_struct = False
                self.header2()
            elif self.token.getValue() in self.firstSet["VARDECLARATION"]:
                self.varDeclaration()
                self.header3()
            elif self.token.getValue() in self.firstSet["METHODS"]:
                self.methods()
            else: 
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["HEADER2"], self.token.getValue()))
                self.getError(self.followSet["HEADER2"])

    def header3(self):
        if self.token.getValue() in self.firstSet["TYPEDEFDECLARATION"]:
            self.typedefDeclaration()
            self.header3()  
        elif self.token.getValue() in self.firstSet["STRUCTDECLARATION"]:
            self.inside_struct = True
            self.structDeclaration()
            self.inside_struct = False
            self.header3()
        elif self.token.getValue() in self.firstSet["METHODS"]:
            self.methods()
        else: 
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["HEADER3"], self.token.getValue()))
            self.getError(self.followSet["HEADER3"])

    def methods(self):
        if self.token is not None:
            if self.token.getValue() in self.firstSet["FUNCTION"]:
                self.inside_method = True
                self.function()
                self.inside_method = False
                self.methods()
            elif self.token.getValue() in self.firstSet["PROCEDURE"]:
                if self.token.getValue() == 'procedure':
                    self.inside_method = True
                    self.getNextToken()
                    self.procedure()
                    self.inside_method = False
                    self.methods()


    def value(self):
        if self.token.getValue() == 'true' or self.token.getValue()=='false':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["BOOLOPERATIONS2"] or self.token.getType() in self.firstSet["BOOLOPERATIONS2"]:
                self.boolOperations2()
        elif self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
            self.aritimeticOp()
            if self.token.getValue() in self.firstSet["BOOLOPERATIONS2"] or self.token.getType() in self.firstSet["BOOLOPERATIONS2"]:
                self.boolOperations2()
            if self.token.getValue() == '(':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["CONTFCALL"] or self.token.getType() in self.firstSet["CONTFCALL"]:
                    self.contFCall()
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTFCALL"], self.token.getValue()))
        elif self.token.getType() in self.firstSet["FUNCTIONCALL"]:
            self.functionCall()
        elif self.token.getValue() == '(':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["LOGICALOP"] or self.token.getType() in self.firstSet["LOGICALOP"]:
                self.logicalOp()
                if self.token.getValue() == ')':
                    self.getNextToken()
                else:
                    self.token_list.append(self.printError(self.token.current_line, [')'], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["LOGICALOP"], self.token.getValue()))
    
                
    
    def variavel(self):
        if self.token.getType() == "IDE":
            self.identificador()
        elif self.token.getValue() in self.firstSet["GLOBAL"]:
            self.globalFunction()
        elif self.token.getValue() in self.firstSet["LOCAL"]:
            self.local()

    def identificador(self):
        if self.token.getType()=="IDE":
            if self.inside_code:
                self.semantic.analyze(self.symbol_table, ['verifyIfIdentifierExists'],[self.token], self.functions_table)
            self.getNextToken()
            if self.token.getValue() in self.firstSet["CONTIDENTIFICADOR"]:
                self.contIdentificador()
        else:
            print(self.printError(self.token.current_line, ["Identifier Token"], self.token.getValue()))


    def contIdentificador(self):
        if self.token.getValue() in self.firstSet["CONTELEMENTO"]:
            self.contElemento()
    
    def globalFunction(self):
        if self.token.getValue() == 'global':
            self.getNextToken()
            if self.token.getValue() == '.':
                self.getNextToken()
                if self.token.getType() == "IDE":
                    self.identificador()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["IDENTIFICADOR"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line,["."], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["global"], self.token.getValue()))

    def local(self):
            if self.token.getValue() == 'local':
                self.getNextToken()
                if self.token.getValue() == '.':
                    self.getNextToken()
                    if self.token.getType() == "IDE":
                        self.identificador()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["IDENTIFICADOR"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["."], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, ["local"], self.token.getValue()))

    def aritmeticValue(self):
        if self.token.getType() =="IDE":
            self.identificador()
        elif self.token.getType() == "NRO":
            self.getNextToken()
        elif self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"] :
            self.variavel()
        elif self.token.getType() == "CAD":
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, ["Expression aritmetic value"], self.token.getValue()))

    def dataType(self):
        return True if (self.token.getValue() in self.firstSet["DATATYPE"] or self.token.getType()=="IDE") else False

    def contElemento(self):
        if self.token.getValue() in self.firstSet["STRUCTE1"]:
            self.structE1()
        elif self.token.getValue() in self.firstSet["VETORE1"]:
            self.vetorE1()
        elif self.token.getValue() in self.firstSet["MATRIZE1"]:
            self.matrizE1()
        else:
            self.printError(self.token.current_line, self.firstSet["CONTELEMENTO"], self.token.getValue())

    
    def structE1(self):
        if self.token.getValue() == '.':
            self.getNextToken()
            if self.token.getType() == "IDE":
                self.identificador()
                if self.token.getValue() in self.firstSet["CONTIDENTIFICADOR"]:
                    self.contIdentificador()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["Identifier Expected"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["."], self.token.getValue()))

    def vetorE1(self):
        if self.token.getValue() =='[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritimeticOp()
                if self.token.getValue() == ']':
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["VETORE2"]:
                        self.vetorE2()
                if self.token.getValue() == '[':
                    self.vetorE1()
                    self.matrizE2()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
        
    def vetorE2(self):
        if self.token.getValue() in self.firstSet["STRUCTE1"]:
            self.structE1()
        
    def matrizE1(self):
        if self.token.getValue() in self.firstSet["VETORE1"]:
            self.vetorE1()
            if self.token.getValue() in self.firstSet["VETORE1"]:
                self.vetorE1()
                if self.token.getValue() in self.firstSet["MATRIZE2"]:
                    self.matrizE2()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VETORE1"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VETORE1"], self.token.getValue()))

    def matrizE2(self):
        if self.token.getValue() in self.firstSet["STRUCTE1"]:
            self.structE1()

    def varDeclaration(self):
        if self.token.getValue() == "var":
            self.getNextToken()
            if self.token.getValue() =="{":
                self.getNextToken()
                if self.token.getValue() in self.firstSet["PRIMEIRAVAR"] or self.token.getType() in self.firstSet["PRIMEIRAVAR"]:
                    self.primeiraVar()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRIMEIRAVAR"], self.token.getValue())) 
                    self.getError(self.followSet["VARDECLARATION"])
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARDECLARATION"], self.token.getValue())) 
                self.getError(self.followSet["VARDECLARATION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARDECLARATION"], self.token.getValue()))           
            self.getError(self.followSet["VARDECLARATION"])

    def primeiraVar(self):
        if self.token.getValue() in self.firstSet["CONTINUESOS"] or self.token.getType() in self.firstSet["CONTINUESOS"]:
            self.continueSos()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTINUESOS"], self.token.getValue()))
            self.getError(self.followSet["VARDECLARATION"])

    def continueSos(self):
        if self.token.getValue() == 'struct':
            self.getNextToken()
            if self.dataType():
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["Datatype token"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        elif self.dataType():
            self.current_variable_type = self.token.getValue()
            self.getNextToken()
        else:
            self.printError(self.token.current_line, self.firstSet["CONTINUESOS"], self.token.getValue())
    
    def proxVar(self):
        if self.token.getValue() in self.firstSet["CONTINUESOS"] or self.token.getType() in self.firstSet["CONTINUESOS"]:
            self.continueSos()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        elif self.token.getValue() == '}':
            self.getNextToken()
        else:
            self.printError(self.token.current_line, self.firstSet["PROXVAR"], self.token.getValue())

    def varId(self):
        if self.token.getType() == "IDE":
            symbol = Symbol(self.token.getValue(), 'var', self.current_variable_type)
            if self.inside_method:
                self.symbol_table["local"][self.current_method].append(symbol)
                self.current_symbol = symbol
            else:
                if self.inside_struct:
                    self.symbol_table["local"][self.current_struct].append(symbol)
                    self.current_symbol = symbol
                else:
                    self.symbol_table["global"].append(symbol)
                    self.current_symbol = symbol
                
            self.identificador()
            if self.token.getValue() in self.firstSet["VAREXP"]:
                self.varExp()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VAREXP"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, ["Identifier"], self.token.getValue()))
            self.getError(self.followSet["VARDECLARATION"])

    def varExp(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))   
                self.getError(self.followSet["VARDECLARATION"])
        elif self.token.getValue() == '=':
            self.getNextToken()
            #TODO fazer para mais tipos
            if self.token.getType() == "NRO":
                self.current_symbol.addValue(self.token.getValue())
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                self.verifVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        elif self.token.getValue() == ';':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXVAR"] or self.token.getType() in self.firstSet["PROXVAR"]:
                self.proxVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVAR"], self.token.getValue()))
                self.getError(self.followSet["VARDECLARATION"])
        elif self.token.getValue() == '[':
            self.getNextToken()
            if(self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]):
                self.aritmeticOp()
                if self.token.getValue() == ']':
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["ESTRUTURA"]:
                        self.estrutura()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["ESTRUTURA"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VAREXP"], self.token.getValue()))

    
    def estrutura(self):
        if self.token.getValue()== '[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or  self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritmeticOp()
                if self.token.getValue() == ']':
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["CONTMATRIZ"]:
                        self.contMatriz()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTMATRIZ"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["INICIO"], self.token.getValue()))
        elif self.token.getValue() =='=':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["INITVETOR"]:
                self.initVetor()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["INITVETOR"], self.token.getValue()))
        elif self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))
        elif self.token.getValue() == ';':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXVAR"] or self.token.getType() in self.firstSet["PROXVAR"]:
                self.proxVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["ESTRUTURA"], self.token.getValue()))

    def initVetor(self):
        if self.token.getValue() == '[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXVETOR"]:
                    self.proxVetor()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVETOR"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["["], self.token.getValue()))

    
    def proxVetor(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXVETOR"]:
                    self.proxVetor()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVETOR"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        elif self.token.getValue() ==']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VERIFVAR"]:
                self.verifVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVETOR"], self.token.getValue()))

    def contMatriz(self):
        if self.token.getValue() == '=':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["INITMATRIZ"]:
                self.initMatriz()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["INITMATRIZ"], self.token.getValue()))
        elif self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))
        elif self.token.getValue() == ';':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXVAR"] or self.token.getType() in self.firstSet["PROXVAR"]:
                self.proxVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTMATRIZ"], self.token.getValue()))

    def initMatriz(self):
        if self.token.getValue() == '[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["MATRIZVALUE"]:
                self.matrizValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["MATRIZVALUE"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["INITMATRIZ"], self.token.getValue()))

    def matrizValue(self):
        if self.token.getValue() == '[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXMATRIZ"]:
                self.proxMatriz()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXMATRIZ"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["MATRIZVALUE"], self.token.getValue()))
    
    def proxMatriz(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXMATRIZ"]:
                    self.proxMatriz()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXMATRIZ"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        elif self.token.getValue() == ']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["NEXT"]:
                self.next()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXT"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXMATRIZ"], self.token.getValue()))

    def next(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["MATRIZVALUE"]:
                self.matrizValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["MATRIZVALUE"], self.token.getValue()))
        elif self.token.getValue() == ']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VERIFVAR"]:
                self.verifVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXT"], self.token.getValue()))

    def verifVar(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getType() in self.firstSet["VARID"]:
                self.varId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARID"], self.token.getValue()))
        elif self.token.getValue() ==';':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXVAR"] or self.token.getType() in self.firstSet["PROXVAR"]:
                self.proxVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFVAR"], self.token.getValue()))

    def constDeclaration(self):
        if self.token.getValue() =='const':
            self.is_const = True
            self.getNextToken()
            if self.token.getValue() =='{':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["PRIMEIRACONST"] or self.token.getType() in self.firstSet["PRIMEIRACONST"]:
                    self.primeiraConst()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRIMEIRACONST"], self.token.getValue()))
                    self.getError(self.followSet["PRIMEIRACONST"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTDECLARATION"], self.token.getValue()))
            self.getError(self.followSet["PRIMEIRACONST"])
        self.is_const = False


    def primeiraConst(self):
        if self.token.getValue() in self.firstSet["CONTINUECONSTSOS"] or self.token.getType() in self.firstSet["CONTINUECONSTSOS"]:
            self.continueConstSos()
            if self.token.getType() == "IDE":
                self.constId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTID"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTINUECONSTSOS"], self.token.getValue()))
            self.getError(self.followSet["PRIMEIRACONST"])
    
    def continueConstSos(self):
        if self.token.getValue() =='struct':
            self.getNextToken()
            if self.dataType():
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["Datatype token"], self.token.getValue()))
        elif self.dataType():
            self.current_variable_type = self.token.getValue()
            self.getNextToken()
        else:
            self.token_list.append("ERROR")

    def proxConst(self):
        if self.token.getValue() in self.firstSet["CONTINUECONSTSOS"] or self.token.getType() in self.firstSet["CONTINUECONSTSOS"]:
            self.continueConstSos()
            if self.token.getType() in self.firstSet["CONSTID"]:
                self.constId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTID"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])
        elif self.token.getValue() == '}':
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONST"], self.token.getValue()))
    
    def constId(self):
        if self.token.getType() == "IDE":
            symbol = Symbol(self.token.getValue(), 'var', self.current_variable_type)
            symbol.setIsConst(self.is_const)
            if self.inside_method:
                self.symbol_table["local"][self.current_method].append(symbol)
                self.current_symbol = symbol
            else:
                if self.inside_struct:
                    self.symbol_table["local"][self.current_struct].append(symbol)
                    self.current_symbol = symbol
                else:
                    self.symbol_table["global"].append(symbol)
                    self.current_symbol = symbol
            self.identificador()
            if self.token.getValue() in self.firstSet["CONSTEXP"]:
                self.constExp()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTEXP"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTID"], self.token.getValue()))
    

    def constExp(self):
        if self.token.getValue() =='=':
            self.getNextToken()
            if self.token.getType() in self.firstSet["VALUE"] or self.token.getValue() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["VERIFCONST"]:
                    self.verifConst()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFCONST"], self.token.getValue()))
                    self.getError(self.followSet["PRIMEIRACONST"])
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])
        elif self.token.getValue() =='[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritimeticOp()
                if self.token.getValue() == ']':
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["ESTRUTURACONST"]:
                        self.estruturaConst()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["ESTRUTURACONST"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTEXP"], self.token.getValue()))

    def estruturaConst(self):
        if self.token.getValue() == '[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritimeticOp()
                if self.token.getValue() ==']':
                    self.getNextToken()
                    if self.token.getValue() == '=':
                        self.getNextToken()
                        if self.token.getValue() in self.firstSet["INITCONSTMATRIZ"]:
                            self.initConstMatriz()
                        else:
                            self.token_list.append(self.printError(self.token.current_line, self.firstSet["INITCONSTMATRIZ"], self.token.getValue()))
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["="], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))
        elif self.token.getValue() == '=':
            self.getNextToken()
            if self.token.getValue() == '[':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                    self.value()
                    if self.token.getValue() in self.firstSet["PROXCONSTVETOR"]:
                        self.proxConstVetor()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTVETOR"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, ["["], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["ESTRUTURACONST"], self.token.getValue()))

    def proxConstVetor(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXCONSTVETOR"]:
                    self.proxConstVetor()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTVETOR"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        elif self.token.getValue() == ']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VERIFCONST"]:
                self.verifConst()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFCONST"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTVETOR"], self.token.getValue()))

    def initConstMatriz(self):
        if self.token.getValue() =='[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["MATRIZCONSTVALUE"]:
                self.matrizConstValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["MATRIZCONSTVALUE"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["["], self.token.getValue()))

    def matrizConstValue(self):
        if self.token.getValue() =='[':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXCONSTMATRIZ"]:
                    self.proxConstMatriz()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTMATRIZ"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line,["["], self.token.getValue()))
    
    def proxConstMatriz(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["PROXCONSTMATRIZ"]:
                    self.proxConstMatriz()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTMATRIZ"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        elif self.token.getValue() == ']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["NEXTCONST"]:
                self.nextConst()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXTCONST"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONSTMATRIZ"], self.token.getValue()))

    def nextConst(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["MATRIZCONSTVALUE"]:
                self.matrizConstValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["MATRIZCONSTVALUE"], self.token.getValue()))
        elif self.token.getValue() == ']':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VERIFCONST"]:
                self.verifConst()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFCONST"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXTCONST"], self.token.getValue()))

    def verifConst(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getType() in self.firstSet["CONSTID"]:
                self.constId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTID"], self.token.getValue()))
                self.getError(self.followSet["PRIMEIRACONST"])

        elif self.token.getValue() == ';':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXCONST"] or self.token.getType() in self.firstSet["PROXCONST"]:
                self.proxConst()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXCONST"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VERIFCONST"], self.token.getValue()))

    
    def function(self):
        if self.token.getValue() == 'function':
            self.getNextToken()
            if self.dataType():
                self.getNextToken()
                if self.token.getType() == 'IDE':
                    symbol = Symbol(self.token.getValue(),'function','IDE')
                    self.functions_table[self.token.getValue()] = symbol 
                    self.symbol_table["local"][self.token.getValue()] = []
                    self.current_method = self.token.getValue()
                    self.getNextToken()
                    if self.token.getValue() =='(':
                        self.getNextToken()
                        if self.token.getValue() in self.firstSet["CONTINUEFUNCTION"] or self.token.getType() in self.firstSet["CONTINUEFUNCTION"]:
                            self.continueFunction()
                        else:
                            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTINUEFUNCTION"], self.token.getValue()))
                            self.getError(self.followSet["FUNCTION"])
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["("], self.token.getValue()))
                        self.getError(self.followSet["FUNCTION"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["Identifier Token"], self.token.getValue()))
                    self.getError(self.followSet["FUNCTION"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["Datatype token"], self.token.getValue()))
                self.getError(self.followSet["FUNCTION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["FUNCTION"], self.token.getValue()))
            self.getError(self.followSet["FUNCTION"])

    def continueFunction(self):
        if self.token.getValue() in self.firstSet["PARAMETERS"] or self.token.getType() in self.firstSet["PARAMETERS"]:
            self.parameters()
            if self.token.getValue() in self.firstSet["BlockFunction"]:
                self.blockFunction()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["BlockFunction"], self.token.getValue()))
                self.getError(self.followSet["FUNCTION"])
        elif self.token.getValue() == ")":
            self.getNextToken()
            if self.token.getValue() in self.firstSet["BlockFunction"]:
                self.blockFunction()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["BlockFunction"], self.token.getValue()))
                self.getError(self.followSet["FUNCTION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTINUEFUNCTION"], self.token.getValue()))
            self.getError(self.followSet["FUNCTION"])

    def parameters(self):
        if self.dataType():
            self.current_variable_type = self.token.getValue()
            self.getNextToken()
            if self.token.getType() == "IDE":
                symbol = Symbol(self.token.getValue(), 'var', self.current_variable_type)
                self.functions_table[self.current_method].addParameters(symbol)
                self.identificador()
                
                if self.token.getValue() in self.firstSet["PARAMLOOP"]:
                    self.paramLoop()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PARAMLOOP"], self.token.getValue()))
                    self.getError(self.followSet["PARAMETERS"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["IDE token"], self.token.getValue()))
                self.getError(self.followSet["PARAMETERS"])
        else:
            self.token_list.append(self.printError(self.token.current_line, ["Datatype token"], self.token.getValue()))
            self.getError(self.followSet["PARAMETERS"])
    
    def paramLoop(self):
        if self.token.getValue() == ',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PARAMETERS"] or self.token.getType() in self.firstSet["PARAMETERS"]:
                self.parameters()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PARAMETERS"], self.token.getValue()))
                self.getError(self.followSet["PARAMETERS"])
        elif self.token.getValue() ==")":
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PARAMLOOP"], self.token.getValue()))
            self.getError(self.followSet["PARAMETERS"])

    def blockFunction(self):
        if self.token.getValue() =='{':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["BlockFuncContent"] or self.token.getType() in self.firstSet["BlockFuncContent"]:
                self.blockFuncContent()
                if self.token.getValue() == ';':
                    self.getNextToken()
                    if self.token.getValue() == '}':
                        self.getNextToken()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                        self.getError(self.followSet["FUNCTION"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
                    self.getError(self.followSet["FUNCTION"])
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["BlockFuncContent"], self.token.getValue()))
                self.getError(self.followSet["FUNCTION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["BlockFunction"], self.token.getValue()))
            self.getError(self.followSet["FUNCTION"])

    def blockFuncContent(self):
        if self.token.getValue() in self.firstSet["VARDECLARATION"]:
            self.varDeclaration()
            if self.token.getValue() in self.firstSet["CONTENT1"] or self.token.getType() in self.firstSet["CONTENT1"]:
                self.content1()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT1"], self.token.getValue()))
                self.getError(self.followSet["BlockFuncContent"])
        elif self.token.getValue() in self.firstSet["CONSTDECLARATION"]:
            self.constDeclaration()
            if self.token.getValue() in self.firstSet["CONTENT2"] or self.token.getType() in self.firstSet["CONTENT2"]:
                self.content2()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT2"], self.token.getValue()))
                self.getError(self.followSet["BlockFuncContent"])
        elif self.token.getValue() in self.firstSet["FUNCCONTENT"] or self.token.getType() in self.firstSet["FUNCCONTENT"]:
            self.funcContent()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["BlockFuncContent"], self.token.getValue()))
            self.getError(self.followSet["BlockFuncContent"])
                        
    def funcContent(self):
        if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"] :
            self.codigo()
            if self.token.getValue() == "return":
                self.getNextToken()
                if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                    self.value()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, ["return"], self.token.getValue()))
                self.getError(self.followSet["FUNCCONTENT"])
        elif self.token.getValue() == "return":
                self.getNextToken()
                if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                    self.value()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
                    self.getError(self.followSet["FUNCCONTENT"])
        else: 
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["FUNCCONTENT"], self.token.getValue()))
            self.getError(self.followSet["FUNCCONTENT"])

    def content1(self):
        if self.token.getValue() in self.firstSet["CONSTDECLARATION"]:
            self.constDeclaration()
            if self.token.getValue() in self.firstSet["CONTENT3"] or self.token.getType() in self.firstSet["CONTENT3"]:
                self.content3()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT3"], self.token.getValue()))
                self.getError(self.followSet["CONTENT1"])
        elif self.token.getValue() in self.firstSet["FUNCCONTENT"] or self.token.getType() in self.firstSet["FUNCCONTENT"]:
            self.funcContent()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT1"], self.token.getValue()))
            self.getError(self.followSet["CONTENT1"])

    def content2(self):
        if self.token.getValue() in self.firstSet["VARDECLARATION"]:
            self.varDeclaration()
            if self.token.getValue() in self.firstSet["CONTENT3"] or self.token.getType() in self.firstSet["CONTENT3"]:
                self.content3()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT3"], self.token.getValue()))
                self.getError(self.followSet["CONTENT2"])     
        elif self.token.getValue() in self.firstSet["FUNCCONTENT"] or self.token.getType() in self.firstSet["FUNCCONTENT"]:
            self.funcContent()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT2"], self.token.getValue()))
            self.getError(self.followSet["CONTENT2"])


    def content3(self):
        if self.token.getValue() in self.firstSet["FUNCCONTENT"] or self.token.getType() in self.firstSet["FUNCCONTENT"]:
            self.funcContent()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTENT3"], self.token.getValue()))

    

    def structDeclaration(self):
        if(self.token.getValue() == 'struct'):
            self.getNextToken()
            if(self.token.getType()=="IDE"):
                self.symbol_table["local"][self.token.getValue()] = []
                self.current_struct = self.token.getValue() 
                self.getNextToken()
                if self.token.getValue() in self.firstSet["STRUCTVARS"]:
                    self.structVars()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARS"], self.token.getValue()))
                    self.getError(self.firstSet["INICIO"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["IDE TOKEN"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTDECLARATION"], self.token.getValue()))
            self.getError(self.firstSet["INICIO"])
        self.semantic.analyze(self.symbol_table, ['structExtends'],self.token_value_list)
        self.token_value_list = []
        
    def structVars(self):
        if(self.token.getValue() =='{'):
            self.getNextToken()
            if(self.token.getValue() == 'var'):
                self.getNextToken()
                if(self.token.getValue() =='{'):
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["FIRSTSTRUCTVAR"] or self.token.getType() in self.firstSet["FIRSTSTRUCTVAR"]:
                        self.firstStructVar()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["FIRSTSTRUCTVAR"], self.token.getValue()))
                        self.getError(self.firstSet["INICIO"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                    self.getError(self.firstSet["INICIO"])
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARS"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])

        elif(self.token.getValue() == 'extends'):
            self.getNextToken()
            if(self.token.getType()=="IDE"):
                #if(self.token.getValue() not in self.symbol_table["local"]):
                    #print(self.printSemanticError(self.token.current_line, "A struct should only extends another struct if the second one exists", self.token.getValue()))
                self.getNextToken()
                if(self.token.getValue() == '{'):
                    self.getNextToken()
                    if(self.token.getValue() == 'var'):
                        self.getNextToken()
                        if(self.token.getValue() == '{'):
                            self.getNextToken()
                            if self.token.getValue() in self.firstSet["FIRSTSTRUCTVAR"] or self.token.getType() in self.firstSet["FIRSTSTRUCTVAR"]:
                                 self.firstStructVar()
                            else:
                                self.token_list.append(self.printError(self.token.current_line, self.firstSet["FIRSTSTRUCTVAR"], self.token.getValue()))
                                self.getError(self.firstSet["INICIO"])
                        else:
                            self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                            self.getError(self.firstSet["INICIO"])
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["var"], self.token.getValue()))
                        self.getError(self.firstSet["INICIO"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                    self.getError(self.firstSet["HEADER3"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["IDE token"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARS"], self.token.getValue()))
            self.getError(self.firstSet["INICIO"])

        
    def firstStructVar(self):
        if(self.dataType()):
            self.getNextToken()
            if self.token.getType() == 'IDE':
                self.structVarId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARID"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["FIRSTSTRUCTVAR"], self.token.getValue()))
            self.getError(self.firstSet["INICIO"])

    def structVarId(self):
        if(self.token.getType()=="IDE"):
            self.getNextToken()
            if self.token.getValue() in self.firstSet["STRUCTVAREXP"]:
                self.structVarExp()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVAREXP"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        else:
            self.token_list.append(self.printError(self.token.current_line, ["IDE token"], self.token.getValue()))
            self.getError(self.firstSet["INICIO"])
    
    def structVarExp(self):
        if(self.token.getValue() == ','):
            self.getNextToken()
            if self.token.getType() in self.firstSet["STRUCTVARID"]:
                self.structVarId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARID"], self.token.getValue()))
        elif(self.token.getValue() == ';'):
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXSTRUCTVAR"] or self.token.getType() in self.firstSet["PROXSTRUCTVAR"]:
                self.proxStructVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXSTRUCTVAR"], self.token.getValue()))
        elif(self.token.getValue() == '['):
            self.getNextToken()
            if(self.inteiro(self.token.getValue())):
                self.getNextToken()
                if(self.token.getValue() == ']'):
                    self.getNextToken()
                    self.structMatriz()
                else:
                    self.printError(self.token.current_line, ["["], self.token.getValue()) 
            else:
                 self.printError(self.token.current_line,["Integer token"], self.token.getValue())
        else:
            self.printError(self.token.current_line, self.firstSet["STRUCTVAREXP"], self.token.getValue())
    

    def structMatriz(self):
        if(self.token.getValue() == '['):
            self.getNextToken()
            if(self.inteiro(self.token.getValue())):
                self.getNextToken()
                if(self.token.getValue() == ']'):
                    self.getNextToken()
                    if self.token.getValue() in self.firstSet["CONTSTRUCTMATRIZ"]:
                        self.contStructMatriz()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONSTSTRUCTMATRIZ"], self.token.getValue()))
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["]"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, ["Integer Token"], self.token.getValue()))
        elif(self.token.getValue() ==','):
            self.getNextToken()
            if self.token.getType() in self.firstSet["STRUCTVARID"]:
                self.structVarId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARID"], self.token.getValue()))
        elif(self.token.getValue() == ';'):
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PROXSTRUCTVAR"] or self.token.getType() in self.firstSet["PROXSTRUCTVAR"]:
                self.proxStructVar()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXSTRUCTVAR"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTMATRIZ"], self.token.getValue()))


    def proxStructVar(self):
        if(self.dataType()):
            self.getNextToken()
            if self.token.getType() in self.firstSet["STRUCTVARID"]:
                self.structVarId()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["STRUCTVARID"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        elif(self.token.getValue() == "}"):
            self.getNextToken()
            if(self.token.getValue() == "}"):
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                self.getError(self.firstSet["INICIO"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROXSTRUCTVAR"], self.token.getValue()))
            self.getError(self.firstSet["INICIO"])
    
    def opNegate(self):
        if self.token.getValue() == '-':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICVALUE"] or self.token.getType() in self.firstSet["ARITMETICVALUE"]:
                self.aritmeticValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICVALUE"], self.token.getValue()))
        elif self.token.getValue() in self.firstSet["ARITMETICVALUE"] or self.token.getType() in self.firstSet["ARITMETICVALUE"]:
            self.aritmeticValue()
        elif self.token.getValue() == '(':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritimeticOp()
                if self.token.getValue() == ")":
                    self.getNextToken()
                else:
                    self.token_list.append(self.printError(self.token.current_line, [")"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["OpNegate"], self.token.getValue()))  

    def opMult(self):
        if self.token.getValue() in self.firstSet["OpNegate"] or self.token.getType() in self.firstSet["OpNegate"]:
            self.opNegate()
            if self.token.getValue() in self.firstSet["AUXSTATE2"]:
                self.auxState2()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["Opmult"], self.token.getValue()))
    
    def auxState2(self):
        if self.token.getValue() in self.firstSet["MULTSYMBOL"]:
            self.multSymbol()
            if self.token.getValue() in self.firstSet["Opmult"] or self.token.getType() in self.firstSet["Opmult"]:
                self.opMult()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["Opmult"], self.token.getValue()))
    
    def multSymbol(self):
        if self.token.getValue() == '*':
            self.getNextToken()
        elif self.token.getValue() == '/':
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["MULTSYMBOL"], self.token.getValue()))

    def aritimeticOp(self):
        if self.token.getValue() in self.firstSet["Opmult"] or self.token.getType() in self.firstSet["Opmult"]:
            self.opMult()
            if self.token.getValue() in self.firstSet["OPMULT2"]:
                self.opMult2()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))

    def opMult2(self):
        if self.token.getValue() in self.firstSet["ARITSYMBOL"]:
            self.aritSymbol()
            if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
                self.aritimeticOp()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITMETICOP"], self.token.getValue()))

    def aritSymbol(self):
        if self.token.getValue() =="+":
            self.getNextToken()
        elif self.token.getValue =='-':
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["ARITSYMBOL"], self.token.getValue()))
    
    def opBoolValue(self):
        if self.token.getValue() in self.firstSet["ARITMETICOP"] or self.token.getType() in self.firstSet["ARITMETICOP"]:
            self.aritimeticOp()
        elif self.token.getValue() == 'true' or self.token.getValue() =='false':
            self.getNextToken()
        elif self.token.getValue() =='(':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["LOGICALOP"] or self.token.getType() in self.firstSet["LOGICALOP"]:
                self.logicalOp()
                if self.token.getValue() ==')':
                    self.getNextToken()
                else:
                    self.token_list.append(self.printError(self.token.current_line, [")"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["LOGICALOP"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE"], self.token.getValue()))

    def relacionalOp(self):
        if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
            self.opBoolValue()
            if self.token.getValue() in self.firstSet["RELSYMBOL"]:
                self.relSymbol()
                if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
                    self.opBoolValue()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["RELSYMBOL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["RELACIONALOP"], self.token.getValue()))

    def relSymbol(self):
        if self.token.getValue() =='<':
            self.getNextToken()
        elif self.token.getValue() == '>':
            self.getNextToken()
        elif self.token.getValue() == '==':
            self.getNextToken()
        elif self.token.getValue() == '<=':
            self.getNextToken()
        elif self.token.getValue() == '>=':
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["RELSYMBOL"], self.token.getValue()))
    
    def opBoolValue2(self):
        if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
            self.opBoolValue()
            if self.token.getValue() in self.firstSet["OPBOOLVALUE3"]:
                self.opBoolValue3()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE2"], self.token.getValue()))
    
    def opBoolValue3(self):
        if self.token.getValue() in self.firstSet["RELSYMBOL"]:
            self.relSymbol()
            if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
                self.opBoolValue()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE"], self.token.getValue()))

    def logicSymbol(self):
        if self.token.getValue() =="!=":
            self.getNextToken()
        elif self.token.getValue() =="&&":
            self.getNextToken()
        elif self.token.getValue()=="||":
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["LOGICSYMBOL"], self.token.getValue()))

    def logicalOp(self):
        if self.token.getValue() in self.firstSet["OPBOOLVALUE2"] or self.token.getType() in self.firstSet["OPBOOLVALUE2"]:
            self.opBoolValue2()
            if self.token.getValue() in self.firstSet["LOGICSYMBOL"]:
                self.logicSymbol()
                if self.token.getValue() in self.firstSet["OPBOOLVALUE2"] or self.token.getType() in self.firstSet["OPBOOLVALUE2"]:
                    self.opBoolValue2()
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE2"], self.token.getValue()))
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["LOGICSYMBOL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["LOGICALOP"], self.token.getValue()))

    def negBoolValue(self):
        if self.token.getValue() == "!":
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"]:
                self.variavel()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARIAVEL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEGBOOLVALUE"], self.token.getValue()))

    def incrementOp(self, variavel=True):
        enter = False
        if not variavel:
            enter = True
        if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"] or enter:
            if variavel:
                self.variavel()
            if self.token.getValue() =="++":
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line,["++"], self.token.getValue()))
        elif self.token.getValue() =="++":
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"]:
                self.variavel()
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARIAVEL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["INCREMENTOP"], self.token.getValue()))

    def decrementOp(self, variavel = True):
        enter = False
        if not variavel:
            enter = True
        if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"] or enter:
            if variavel:
                self.variavel()
            if self.token.getValue() =="--":
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["--"], self.token.getValue()))
        elif self.token.getValue() =="--":
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"]:
                self.variavel()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["VARIAVEL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["DECREMENTOP"], self.token.getValue()))

    def boolOperations(self):
        if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
            self.opBoolValue()
            if self.token.getValue() in self.firstSet["BOOLOPERATIONS2"]:
                self.boolOperations2()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS2"], self.token.getValue()))
        elif self.token.getValue() in self.firstSet["NEGBOOLVALUE"]:
            self.negBoolValue()
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS"], self.token.getValue()))

    def boolOperations2(self):
        if self.token.getValue() in self.firstSet["BOOLOPERATIONS3"]:
            self.boolOperations3()
            if self.token.getValue() in self.firstSet["BOOLOPERATIONS4"]:
                self.boolOperations4()
        elif self.token.getValue() in self.firstSet["LOGICSYMBOL"]:
            self.logicSymbol()
            if self.token.getValue() in self.firstSet["OPBOOLVALUE2"] or self.token.getType() in self.firstSet["OPBOOLVALUE2"]:
                self.opBoolValue2()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE2"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS2"], self.token.getValue()))

    def boolOperations3(self):
        if self.token.getValue() in self.firstSet["RELSYMBOL"]:
            self.relSymbol()
            if self.token.getValue() in self.firstSet["OPBOOLVALUE"] or self.token.getType() in self.firstSet["OPBOOLVALUE"]:
                self.opBoolValue()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS3"], self.token.getValue()))
    
    def boolOperations4(self):
        if self.token.getValue() in self.firstSet["LOGICSYMBOL"]:
            self.logicSymbol()
            if self.token.getValue() in self.firstSet["OPBOOLVALUE2"] or self.token.getType() in self.firstSet["OPBOOLVALUE2"]:
                self.opBoolValue2()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["OPBOOLVALUE2"], self.token.getValue()))

    
    def typedefDeclaration(self):
        if self.token.getValue() == "typedef":
            self.getNextToken()
            if self.token.getValue() in self.firstSet["CONTTYPEDEFDEC"] or self.token.getType() in self.firstSet["CONTTYPEDEFDEC"]:
                self.contTypedefDeclaration()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTTYPEDEFDEC"], self.token.getValue()))
                self.getError(self.followSet["TYPEDEFDECLARATION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["TYPEDEFDECLARATION"], self.token.getValue()))
            self.getError(self.followSet["TYPEDEFDECLARATION"])

    def contTypedefDeclaration(self):
        if self.dataType():
            self.getNextToken()
            if self.token.getType()=="IDE":
                self.getNextToken()
                if self.token.getValue() == ';':
                    self.getNextToken()
                else:
                    self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
                    self.getError(self.followSet["TYPEDEFDECLARATION"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["IDE TOKEN"], self.token.getValue()))
                self.getError(self.followSet["TYPEDEFDECLARATION"])
        elif self.token.getValue() == 'struct':
            self.getNextToken()
            if self.token.getType()=="IDE":
                self.getNextToken()
                if self.token.getType()=="IDE":
                    self.getNextToken()
                    if self.token.getValue() == ';':
                        self.getNextToken()
                    else:
                        self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
                        self.getError(self.followSet["TYPEDEFDECLARATION"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, ["IDE TOKEN"], self.token.getValue()))
                    self.getError(self.followSet["TYPEDEFDECLARATION"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["IDE TOKEN"], self.token.getValue()))
                self.getError(self.followSet["TYPEDEFDECLARATION"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTTYPEDEFDEC"], self.token.getValue()))
            self.getError(self.followSet["TYPEDEFDECLARATION"])


    def procedure(self):
        if self.token.getType() == "IDE":
            symbol = Symbol(self.token.getValue(),'function','IDE')
            self.functions_table[self.token.getValue()] = symbol
            self.symbol_table["local"][self.token.getValue()] = []
            self.current_method = self.token.getValue() 
            self.identificador()
            if self.token.getValue() =="(":
                self.getNextToken()
                if self.token.getValue() in self.firstSet["PROCPARAM"] or self.token.getType() in self.firstSet["PROCPARAM"]:
                    self.procParam()
                    if self.token.getValue() == '{':
                        self.getNextToken()
                        if self.token.getValue() in self.firstSet["PROCCONTENT"] or self.token.getType() in self.firstSet["PROCCONTENT"]:
                            self.procContent()
                        else:
                            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT"], self.token.getValue()))
                            self.getError(self.followSet["PROCEDURE"])
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                        self.getError(self.followSet["PROCEDURE"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCPARAM"], self.token.getValue()))
                    self.getError(self.followSet["PROCEDURE"])
            else:
                self.token_list.append(self.printError(self.token.current_line,["("], self.token.getValue()))
                self.getError(self.followSet["PROCEDURE"])
        elif self.token.getValue() =='start':
            symbol = Symbol(self.token.getValue(),'function','IDE')
            self.functions_table[self.token.getValue()] = symbol
            self.symbol_table["local"][self.token.getValue()] = []
            self.current_method = self.token.getValue()
            self.getNextToken()
            if self.token.getValue() == '(':
                self.getNextToken()
                if self.token.getValue() ==')':
                    self.getNextToken()
                    if self.token.getValue() == '{':
                        self.getNextToken()
                        if self.token.getValue() in self.firstSet["PROCCONTENT"] or self.token.getType() in self.firstSet["PROCCONTENT"]:
                            self.procContent()
                        else:
                            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT"], self.token.getValue()))
                            self.getError(self.followSet["PROCEDURE"])
                    else:
                        self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                        self.getError(self.followSet["PROCEDURE"])
                else:
                    self.token_list.append(self.printError(self.token.current_line, [")"], self.token.getValue()))
                    self.getError(self.followSet["PROCEDURE"])
            else:
                self.token_list.append(self.printError(self.token.current_line, ["("], self.token.getValue()))
                self.getError(self.followSet["PROCEDURE"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCEDURE"], self.token.getValue()))
            self.getError(self.followSet["PROCEDURE"])
    
    def procParam(self):
        if self.token.getValue() in self.firstSet["PARAMETERS"] or self.token.getType() in self.firstSet["PARAMETERS"]:
            self.parameters()
        elif self.token.getValue() == ')':
            self.getNextToken()
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCPARAM"], self.token.getValue()))   
            self.getError(self.followSet["PROCPARAM"])

    def procContent(self):
        if self.token.getValue() in self.firstSet["VARDECLARATION"]:
            self.varDeclaration()
            if self.token.getValue() in self.firstSet["PROCCONTENT2"] or self.token.getType() in self.firstSet["PROCCONTENT2"]:
                self.procContent2()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT2"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT"])
        elif self.token.getValue() in self.firstSet["CONSTDECLARATION"]:
            self.constDeclaration()
            if self.token.getValue() in self.firstSet["PROCCONTENT3"] or self.token.getType() in self.firstSet["PROCCONTENT3"]:
                self.procContent3()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT3"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT"])
        elif self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
            self.codigo()
            if self.token.getValue() =='}':
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT"], self.token.getValue()))
            self.getError(self.followSet["PROCCONTENT"])

    def procContent2(self):
        if self.token.getValue() in self.firstSet["CONSTDECLARATION"]:
            self.constDeclaration()
            if self.token.getValue() in self.firstSet["PROCCONTENT4"] or self.token.getType() in self.firstSet["PROCCONTENT4"]:
                self.procContent4()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT4"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT2"])
        elif self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
            self.codigo()
            if self.token.getValue() == "}":
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT2"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT2"], self.token.getValue()))
            self.getError(self.followSet["PROCCONTENT2"])

    def procContent3(self):
        if self.token.getValue() in self.firstSet["VARDECLARATION"]:
            self.varDeclaration()
            if self.token.getValue() in self.firstSet["PROCCONTENT4"] or self.token.getType() in self.firstSet["PROCCONTENT4"]:
                self.procContent4()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT4"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT3"])
        elif self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
            self.codigo()
            if self.token.getValue() == '}':
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT3"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT3"], self.token.getValue()))
            self.getError(self.followSet["PROCCONTENT3"])

    def procContent4(self):
        if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
            self.codigo()
            if self.token.getValue() == '}':
                self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                self.getError(self.followSet["PROCCONTENT4"])
        else:
            self.token_list.append(self.printError(self.token.current_line, self.firstSet["PROCCONTENT4"], self.token.getValue()))
            self.getError(self.followSet["PROCCONTENT4"])

    def codigo(self):
        self.inside_code = True
        if self.token.getValue() in self.firstSet["COMANDO"] or self.token.getType() in self.firstSet["COMANDO"]:
            self.comando()
            if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
                self.codigo()
        self.inside_code = False

    def comando(self):
        if self.token.getValue() in self.firstSet["PRINT"]:
            self.printFunction()
        elif self.token.getType() in self.firstSet["FUNCTIONCALL"] and self.token.getType() in self.firstSet["ATRIBUICAO"]:
            self.preFuncionAtribuicao()
        elif self.token.getValue() in self.firstSet["ATRIBUICAO"]:
            self.atribuicao()
        elif self.token.getValue() in self.firstSet["READ"]:
            self.read()
        elif self.token.getValue() in self.firstSet["INCREMENTOP"]:
            self.incrementOp()
            if self.token.getValue() ==';':
                self.getNextToken()
            else:
                 self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
        elif self.token.getValue() in self.firstSet["DECREMENTOP"] :
            self.decrementOp()
            if self.token.getValue() ==';':
                self.getNextToken()
            else:
                 self.token_list.append(self.printError(self.token.current_line,[";"], self.token.getValue()))
        elif self.token.getValue() in self.firstSet["WHILE"]:
            self.whileFunction()
        elif self.token.getValue() in self.firstSet["CONDITIONAL"]:
            self.conditional()
        elif self.token.getValue() in self.firstSet["TYPEDEFDECLARATION"]:
            self.typedefDeclaration()
        elif self.token.getValue() in self.firstSet["STRUCTDECLARATION"]:
            self.inside_struct = True
            self.structDeclaration()
            self.inside_struct = False
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["COMANDO"], self.token.getValue()))

    def preFuncionAtribuicao(self):
        if self.token.getType() == "IDE":
            self.declared_function = self.token
            self.identificador()
            if self.token.getValue() == '(':
                self.semantic.analyze(self.symbol_table, ['methodDeclaredFirst'],[self.declared_function])
                self.token_value_list = []
                self.functionCall()
                self.semantic.analyze(self.symbol_table, ['functionCallParameters'],list(chain([self.current_method, self.declared_function], self.token_value_list)), self.functions_table)
                self.token_value_list = []
            elif self.token.getValue() == '=':
                self.token_value_list = []
                self.atribuicao(False)
                self.semantic.analyze(self.symbol_table, ['notAllowAConstraintToReceiveValue'],list(chain([self.current_method, self.declared_function], self.token_value_list)))
                self.token_value_list = []
            elif self.token.getValue() == '++':
                self.incrementOp(False)
                if self.token.getValue() ==';':
                    self.getNextToken()
            elif self.token.getValue() == '--':
                self.decrementOp(False)
                if self.token.getValue() ==';':
                    self.getNextToken()
            


    def printFunction(self):
        if self.token.getValue() == "print":
            self.getNextToken()
            if self.token.getValue() =="(":
                self.getNextToken()
                if self.token.getValue() in self.firstSet["PRINTABLELIST"] or self.token.getType() in self.firstSet["PRINTABLELIST"]:
                    self.printableList()
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRINTABLELIST"], self.token.getValue()))
            else:
                 self.token_list.append(self.printError(self.token.current_line,["("], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRINT"], self.token.getValue()))
        
    
    def printableList(self):
        if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
            self.value()
            if self.token.getValue() in self.firstSet["NEXTPRINTVALUE"]:
                self.nextPrintValue()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXTPRINTVALUE"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRINTABLELIST"], self.token.getValue()))

    def nextPrintValue(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["PRINTABLELIST"] or self.token.getType() in self.firstSet["PRINTABLELIST"]:
                self.printableList()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["PRINTABLELIST"], self.token.getValue()))
        elif self.token.getValue() ==')':
            self.getNextToken()
            if self.token.getValue() ==';':
                self.getNextToken()
            else:
                 self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["NEXTPRINTVALUE"], self.token.getValue()))

    
    def atribuicao(self, variavel=True):
        enter = False
        if not variavel:
            enter = True
        if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"] or enter:
            if variavel:
                self.variavel()
            if self.token.getValue() == '=':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                    self.value()
                    if self.token.getValue() == ';':
                        self.getNextToken()
                    else:
                         self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue())) 
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
            else: 
                self.token_list.append(self.printError(self.token.current_line, ["="], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["ATRIBUICAO"], self.token.getValue()))

    def functionCall(self):
        if self.token.getValue() == '(':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["CONTFCALL"] or self.token.getType() in self.firstSet["CONTFCALL"]:
                self.contFCall()
                if self.token.getValue() == ';':
                    self.getNextToken()
            else:
                self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTFCALL"], self.token.getValue()))
        else:
            self.token_list.append(self.printError(self.token.current_line, ["("], self.token.getValue()))

    def contFCall(self):
        if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
            self.value()
            if self.token.getValue() in self.firstSet["FCALLPARAMS"]:
                self.fCallParams()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["FCALLPARAMS"], self.token.getValue()))
        elif self.token.getValue() == ')':
            self.getNextToken()
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONTFCALL"], self.token.getValue()))

    def fCallParams(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["VALUE"] or self.token.getType() in self.firstSet["VALUE"]:
                self.value()
                if self.token.getValue() in self.firstSet["FCALLPARAMS"]:
                    self.fCallParams()
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["FCALLPARAMS"], self.token.getValue()))
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["VALUE"], self.token.getValue()))
        elif self.token.getValue() == ')':
            self.getNextToken()
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["FCALLPARAMS"], self.token.getValue()))

    def read(self):
        if self.token.getValue() == 'read':
            self.getNextToken()
            if self.token.getValue() == '(':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["READPARAMS"] or self.token.getType() in self.firstSet["READPARAMS"]:
                    self.readParams()
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["READPARAMS"], self.token.getValue()))
            else:
                 self.token_list.append(self.printError(self.token.current_line, ["("], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["READ"], self.token.getValue()))

    def readParams(self):
        if self.token.getValue() in self.firstSet["VARIAVEL"] or self.token.getType() in self.firstSet["VARIAVEL"]:
            self.variavel()
            if self.token.getValue() in self.firstSet["READLOOP"]:
                self.readLoop()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["READLOOP"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["READPARAMS"], self.token.getValue()))
    
    def readLoop(self):
        if self.token.getValue() ==',':
            self.getNextToken()
            if self.token.getValue() in self.firstSet["READPARAMS"] or self.token.getType() in self.firstSet["READPARAMS"]:
                self.readParams()
            else:
                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["READPARAMS"], self.token.getValue()))
        elif self.token.getValue() ==')':
            self.getNextToken()
            if self.token.getValue() ==';':
                self.getNextToken()
            else:
                 self.token_list.append(self.printError(self.token.current_line, [";"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["READLOOP"], self.token.getValue()))


    def whileFunction(self):
        if self.token.getValue() =='while':
            self.getNextToken()
            if self.token.getValue() =='(':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["BOOLOPERATIONS"] or self.token.getType() in self.firstSet["BOOLOPERATIONS"]:
                    self.boolOperations()
                    if self.token.getValue() == ')':
                        self.getNextToken()
                        if self.token.getValue() == '{':
                            self.getNextToken()
                            if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
                                self.codigo()
                                if self.token.getValue() == '}':
                                    self.getNextToken()
                                else:
                                     self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                            else:
                                 self.token_list.append(self.printError(self.token.current_line, self.firstSet["CODIGO"], self.token.getValue()))
                        else:
                             self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                    else:
                         self.token_list.append(self.printError(self.token.current_line, [")"], self.token.getValue()))
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS"], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["WHILE"], self.token.getValue()))
    
    def conditional(self):
        if self.token.getValue() =='if':
            self.getNextToken()
            if self.token.getValue() =='(':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["BOOLOPERATIONS"] or self.token.getType() in self.firstSet["BOOLOPERATIONS"]:
                    self.boolOperations()
                    if self.token.getValue() == ')':
                        self.getNextToken()
                        if self.token.getValue() == 'then':
                            self.getNextToken()
                            if self.token.getValue() == '{':
                                self.getNextToken()
                                if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
                                    self.codigo()
                                    if self.token.getValue() =='}':
                                        self.getNextToken()
                                    else:
                                        self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                                else:
                                    self.token_list.append(self.printError(self.token.current_line, self.firstSet["CODIGO"], self.token.getValue()))
                            else:
                                self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))
                        else:
                            self.token_list.append(self.printError(self.token.current_line, ["then"], self.token.getValue()))

                    else:
                         self.token_list.append(self.printError(self.token.current_line, [")"], self.token.getValue()))
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["BOOLOPERATIONS"], self.token.getValue()))
            else:
                 self.token_list.append(self.printError(self.token.current_line, ["("], self.token.getValue()))
        else:
             self.token_list.append(self.printError(self.token.current_line, self.firstSet["CONDITIONAL"], self.token.getValue()))


    def elsePart(self):
        if self.token.getValue() =='else':
            self.getNextToken()
            if self.token.getValue() =='{':
                self.getNextToken()
                if self.token.getValue() in self.firstSet["CODIGO"] or self.token.getType() in self.firstSet["CODIGO"]:
                    self.codigo()
                    if self.token.getValue() == '}':
                        self.getNextToken()
                    else:
                         self.token_list.append(self.printError(self.token.current_line, ["}"], self.token.getValue()))
                else:
                     self.token_list.append(self.printError(self.token.current_line, self.firstSet["CODIGO"], self.token.getValue()))
            else:
                 self.token_list.append(self.printError(self.token.current_line, ["{"], self.token.getValue()))


    def inteiro(self, token):
        p = re.compile('[0-9],')
        return True if p.match(token) is not None else False

        
   



