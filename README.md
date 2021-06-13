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

## Listas de Regras Semânticas:

### Variáveis

```

[x] Variável ou constante tem que ser inicializada antes de a utilizar.
[ ] Index de vetor/matriz tem que ser um número inteiro
[x] Se declarar uma variável como um tipo, não pode atribuir um valor de outro tipo nela.
[ ] Não é possível declarar uma variável global se outra com o mesmo nome já foi declarada anteriormente.
[ ] Não é possível declarar uma variável local se outra com o mesmo nome já foi declara anteriormente.
[ ] É possível declarar uma variável local com o mesmo nome de uma variável global.
[x] Não é possível atribuir uma variável sem valor a outra.
[x] Não é possível atribuir um valor a uma constante, após a sua declaração.
[ ] Não é possível declarar tipos diferentes de valores em um array (e.g. int a[] = {1,2,3,"abc",4})
[ ] É possível fazer a concatenação de duas strings a partir do operador '+'

```

### Typedef

```

[ ] Typedef tem que redefinir tipos permitidos
[ ] Não é permitido fazer typedefs com o mesmo identificador em escopos diferentes

```

### Funções

```

[x] Função ou procedure tem que ser declarada antes de a utilizar.
[x] A função tem que ser chamada com a quantidade de parâmetros e tipos corretos.
[ ] O retorno da função tem que ser igual ao valor retornado
[ ] Não é possível fazer overloading do procedure start
[ ] Para ter a sobrecarga de métodos em geral, é avaliado a quantidade e tipo de parâmetros além do tipo de retorno
[ ] É possível ter uma função com o mesmo nome de um procedimento.

```

### Structs

```

[x] Struct tem que herdar de outra Struct existente

```

### Operações / Expressões / Comparações

```

[ ] Operações com valores de tipos diferentes não podem ser realizadas, pois a linguagem não permite a conversão de tipos.
[ ] Expressões tem que ser realizadas entre valores de tipos coerentes (int + string = erro).
[x] Não é possível realizar a comparação de valores de tipos diferentes.
[x] Não é possível fazer incremento em string e em booleano
[x] Itens de condição em if e while tem que ser booleanos.
[ ] Dentro do print pode ser passado como parâmetro tudo que retorna valor, incluindo expressões no geral.


