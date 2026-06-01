# Sistema de regras de tipos

Este documento descreve as regras usadas por `verificarTipos(arvore, tabelaSimbolos)`.
A função recebe a árvore sintática no formato `{tipo_no, simbolo, producao, token, filhos}` e a tabela gerada por `construirTabelaSimbolos(arvore)`. A saída contém a árvore anotada com `tipo_inferido`, a tabela atualizada e a lista de erros semânticos.

## Tipos

A implementação usa os seguintes tipos semânticos, iguais às constantes do código:

- `INT`: literais inteiros e variáveis inteiras.
- `REAL`: literais reais e variáveis reais.
- `BOOL`: resultado de condições relacionais.
- `INDEFINIDO`: variável declarada, mas ainda sem tipo inferido.
- `ERRO`: marcação interna usada para propagar falhas de tipo pela árvore.

O ambiente de tipos é representado por `Gamma`. A notação `Gamma |- e : T` significa: no ambiente `Gamma`, a expressão `e` possui tipo `T`.

## Literais e variáveis

```text
------------------ [T-Int]
Gamma |- INT : INT

-------------------- [T-Real]
Gamma |- REAL : REAL

Gamma(x) = T
-------------------- [T-Var]
Gamma |- x : T
```

Na gramática atual, `BOOL` não aparece como literal direto; ele é produzido por operadores relacionais. Se `x` não existir na tabela de símbolos, o verificador registra `VARIAVEL_NAO_DECLARADA` e anota o nó como `ERRO`.

## Operadores aritméticos

Soma, subtração, multiplicação e potenciação aceitam operandos numéricos:

```text
Gamma |- e1 : INT    Gamma |- e2 : INT
----------------------------------------- [T-Arit-Int]
Gamma |- (e1 e2 op) : INT

Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {INT, REAL} e algum operando é REAL
--------------------------------------------- [T-Arit-Real]
Gamma |- (e1 e2 op) : REAL
```

Onde `op` pertence a `{OP_SUM, OP_SUB, OP_MUL, OP_POW}`. Caso algum operando não seja numérico, o erro gerado é `TIPOS_INCOMPATIVEIS_OPERADOR`.

## Divisão real, divisão inteira e resto

Divisão real aceita operandos numéricos e sempre produz `REAL`:

```text
Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {INT, REAL}
-------------------------------------- [T-DivR]
Gamma |- (e1 e2 OP_DIVR) : REAL
```

Divisão inteira e resto aceitam apenas inteiros:

```text
Gamma |- e1 : INT    Gamma |- e2 : INT
----------------------------------------- [T-DivI]
Gamma |- (e1 e2 OP_DIVI) : INT

Gamma |- e1 : INT    Gamma |- e2 : INT
---------------------------------------- [T-Mod]
Gamma |- (e1 e2 OP_MOD) : INT
```

Se `OP_DIVI` ou `OP_MOD` receber `REAL`, o erro gerado é `OPERADOR_EXIGE_INT`.

## Operadores relacionais

Os operadores relacionais comparam valores numéricos e produzem `BOOL`:

```text
Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {INT, REAL}
-------------------------------------- [T-Rel]
Gamma |- (e1 e2 OP_LT) : BOOL
Gamma |- (e1 e2 OP_GT) : BOOL
```

Se algum operando não for numérico, o erro gerado é `TIPOS_INCOMPATIVEIS_RELACIONAL`.

## Comandos especiais

O comando `(V MEM x)` armazena em `x` o tipo inferido para `V`. Se `x` estiver como `INDEFINIDO`, o verificador atualiza seu tipo; se `x` já tiver outro tipo, registra incompatibilidade.

```text
Gamma |- V : T
Gamma(x) = INDEFINIDO ou Gamma(x) = T
-------------------------------------- [T-Mem]
Gamma |- (V MEM x) : T
```

O uso simples de memória `(x)` possui o tipo registrado para `x`:

```text
Gamma(x) = T
---------------------- [T-Mem-Use]
Gamma |- (x) : T
```

O comando `(N RES)` tem sua validade conferida na etapa de tabela de símbolos. No verificador de tipos, a regra apenas propaga o tipo do valor usado na referência.

```text
Gamma |- N : T
------------------------- [T-Res]
Gamma |- (N RES) : T
```

## Decisões e laços

Condições de `IF` e `WHILE` devem possuir tipo `BOOL`:

```text
Gamma |- c : BOOL
Gamma |- l1 : T1
Gamma |- l2 : T2
----------------------------- [T-If]
Gamma |- IF c l1 l2 : vazio

Gamma |- c : BOOL
Gamma |- l : T
----------------------------- [T-While]
Gamma |- WHILE c l : vazio
```

Se a condição não for `BOOL`, o erro gerado é `CONDICAO_NAO_BOOL`. Se a estrutura da condição estiver incompleta, o erro gerado é `CONDICAO_MAL_FORMADA`.

O `FOR` usa limites inteiros pela própria gramática e exige variável de controle inteira:

```text
Gamma(i) = INT ou Gamma(i) = INDEFINIDO
--------------------------------------- [T-For]
Gamma |- FOR INT INT i linha : vazio
```

Se a variável de controle tiver outro tipo, o erro gerado é `FOR_VARIAVEL_NAO_INT`.

## Propagação de erro na árvore

Quando um nó recebe `tipo_inferido = ERRO`, esse tipo pode subir para nós pais como `corpo`, `linhas_rest`, `linhas` e `programa`. Isso é esperado e serve para impedir que uma expressão inválida seja tratada como válida. A lista de erros, porém, registra apenas o erro semântico de origem, evitando repetição desnecessária.

## Erros gerados

O verificador gera uma lista de erros semânticos com `codigo`, `linha`, `simbolo` e `mensagem`. Os principais códigos usados são:

- `VARIAVEL_NAO_DECLARADA`
- `TIPOS_INCOMPATIVEIS_OPERADOR`
- `OPERADOR_EXIGE_INT`
- `TIPOS_INCOMPATIVEIS_RELACIONAL`
- `CONDICAO_MAL_FORMADA`
- `CONDICAO_NAO_BOOL`
- `FOR_VARIAVEL_NAO_INT`
- `ATRIBUICAO_TIPO_INCOMPATIVEL`
- `OPERADOR_AUSENTE`

A saída final junta os erros já encontrados pela tabela de símbolos com os erros encontrados por `verificarTipos`.
