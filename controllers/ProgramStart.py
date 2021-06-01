from controllers.Semantic import Semantic
from controllers.Lexical import Lexical
from controllers.Syntactic import Syntactic

import glob
import json

class ProgramStart:
    '''
        ProgramStart: módulo que a depender dos arquivos de entrada irá instanciar
        um objeto de analizador sintático.
    '''
    def __init__(self):
        self.txtfiles = []
        for file in glob.glob("entradas/entrada*.txt"):
            self.txtfiles.append(file)
        self.firstSet  = ''
        self.followSet = ''
        self.getFirstFile()
        self.getFollowFile()
        


    def analyze(self):
        for file in self.txtfiles:
            print("----------- Analisando o arquivo {} -----------".format(file))
            lexical = Lexical(file)
            semantic = Semantic()
            syntactic = Syntactic(lexical, semantic, self.firstSet, self.followSet)
            syntactic.run()


    def getFirstFile(self):
        with open('./util/first.json', 'r') as json_file:
            self.firstSet = json.load(json_file)

    def getFollowFile(self):
        with open('./util/follow.json', 'r') as json_file:
            self.followSet = json.load(json_file)


        
