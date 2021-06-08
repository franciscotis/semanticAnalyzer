# Analisador Semântico - MI - PROC. DE LINGUAGEM DE PROGRAMAÇÃO(TP04) - 2020.1
## Feito por: Esaú Mascarenhas e Francisco Pereira

## Como Utilizar:
### Arquivos de Entrada
    Os arquivos de entrada devem estar armazenados dentro da pasta "entradas".
    Cada arquivo deve conter o seguinte padrão: "entradaX.txt" Onde X é um número
    inteiro que irá ser utilizado para diferenciar cada arquivo.

### Programa Principal

 Dentro do diretório principal, existe um arquivo chamado "main.py". 
    Execute no terminal:

```bash
    python3 main.py 
```

ou

```bash
    python main.py 
```

### Arquivos de Saída
    A partir disso o programa irá ler os arquivos de entrada e as saídas estarão presentes dentro da pasta "saída". 
    Cada arquivo de entrada terá o seu respectivo arquivo de saída.
    Os arquivos terão o seguinte padrão: "saidaX.txt". Onde X é um número inteiro igual ao arquivo de entrada.
    

### Formatação dos tokens .
O arquivo de saída irá conter os seguintes tokens formatados como mostra a seguir:

```
PRE  - Palavra Reservada
IDE  - Identificador
NRO  - Número
DEL  - Delimitador
REL  - Operador Relacional
LOG  - Operador Lógico
ART  - Operador Aritmético
SIB  - Simbolo Inválido
CMF  - Cadeia Mal Formada
NMF  - Número Mal Formado
CoMF - Comentário Mal Formado
OpMF - Operador Mal Formado
CAD  - Cadeia de Caracteres

```

### Lista de Regras Semânticas:
```
[ ] Index de vetor/matriz tem que ser um número inteiro
[x] Variável ou constante tem que ser inicializada antes de a utilizar.
[x] Função ou procedure tem que ser declarada antes de a utilizar.
[x] Struct tem que herdar de outra Struct existente
[ ] Sobrecarga realmente tem que ser sobrecarga (e não sobrescrita).
[x] A função tem que ser chamada com a quantidade de parâmetros e tipos corretos.
[ ] Expressões tem que ser realizadas entre valores de tipos coerentes (int + string = erro).
[x] Itens de condição em if e while tem que ser booleanos.
[ ] Operações com valores de tipos diferentes não podem ser realizadas, pois a linguagem não permite a conversão de tipos.
[ ] Se declarar uma variável como um tipo, não pode atribuir um valor de outro tipo nela.
[x] Não é possível realizar a comparação de valores de tipos diferentes.
[x] Não é possível atribuir uma variável sem valor a outra.
[x] Não é possível atribuir um valor a uma constante, após a sua declaração.
[x] Não é possível fazer incremento em string e em booleano
[ ] Não é possível declarar tipos diferentes de valores em um array (e.g. int a[] = {1,2,3,"abc",4})
```