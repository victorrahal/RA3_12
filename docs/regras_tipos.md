# Sistema de regras de tipos

Este documento descreve as regras usadas por `verificarTipos(arvore, tabelaSimbolos)`.

## Tipos

A linguagem usa tres tipos semanticos:

- `int`: literais inteiros e variaveis inteiras.
- `real`: literais reais e variaveis reais.
- `bool`: resultado de condicoes relacionais e literais logicos, quando existirem.

O ambiente de tipos e representado por `Gamma`. A notacao `Gamma |- e : T` significa: no ambiente `Gamma`, a expressao `e` possui tipo `T`.

## Literais e variaveis

```text
------------------ [T-Int]
Gamma |- INT : int

-------------------- [T-Real]
Gamma |- REAL : real

-------------------- [T-Bool]
Gamma |- BOOL : bool

Gamma(x) = T
-------------------- [T-Var]
Gamma |- x : T
```

Se `x` nao existir na tabela de simbolos, o verificador registra erro semantico.

## Operadores aritmeticos

Soma, subtracao, multiplicacao e potenciacao aceitam operandos numericos compativeis:

```text
Gamma |- e1 : int    Gamma |- e2 : int
----------------------------------------- [T-Arit-Int]
Gamma |- (e1 e2 op) : int

Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {int, real} e algum operando e real
--------------------------------------------- [T-Arit-Real]
Gamma |- (e1 e2 op) : real
```

Onde `op` pertence a `{OP_SUM, OP_SUB, OP_MUL, OP_POW}`.

Divisao real aceita operandos numericos e sempre produz `real`:

```text
Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {int, real}
-------------------------------------- [T-DivR]
Gamma |- (e1 e2 OP_DIVR) : real
```

Divisao inteira e resto aceitam apenas inteiros:

```text
Gamma |- e1 : int    Gamma |- e2 : int
----------------------------------------- [T-DivI]
Gamma |- (e1 e2 OP_DIVI) : int

Gamma |- e1 : int    Gamma |- e2 : int
---------------------------------------- [T-Mod]
Gamma |- (e1 e2 OP_MOD) : int
```

## Operadores relacionais

Os operadores relacionais comparam valores numericos e produzem `bool`:

```text
Gamma |- e1 : T1     Gamma |- e2 : T2
T1,T2 em {int, real}
-------------------------------------- [T-Rel]
Gamma |- (e1 e2 OP_LT) : bool
Gamma |- (e1 e2 OP_GT) : bool
```

## Operadores logicos

Quando a gramatica possuir operadores logicos, eles devem receber operandos booleanos:

```text
Gamma |- e1 : bool   Gamma |- e2 : bool
---------------------------------------- [T-Log]
Gamma |- (e1 e2 OP_AND) : bool
Gamma |- (e1 e2 OP_OR)  : bool

Gamma |- e : bool
--------------------------- [T-Not]
Gamma |- (e OP_NOT) : bool
```

## Comandos especiais

O comando `(V MEM x)` registra o tipo de `V` na variavel `x`. A consistencia da declaracao e controlada pela tabela de simbolos. O verificador de tipos usa essa tabela para consultar `Gamma(x)`.

```text
Gamma |- V : T
-------------------------------- [T-Mem]
Gamma, x:T |- (V MEM x) : T
```

O comando `(N RES)` referencia resultado anterior. O tipo inferido e o tipo de `N`, desde que a referencia seja valida pela fase de tabela de simbolos.

```text
Gamma |- N : T
------------------------- [T-Res]
Gamma |- (N RES) : T
```

O uso simples de memoria `(x)` possui o tipo registrado para `x`:

```text
Gamma(x) = T
---------------------- [T-Mem-Use]
Gamma |- (x) : T
```

## Decisoes e lacos

Condicoes de `if` e `while` devem possuir tipo `bool`:

```text
Gamma |- c : bool
Gamma |- l1 : T1
Gamma |- l2 : T2
----------------------------- [T-If]
Gamma |- if c l1 l2 : vazio

Gamma |- c : bool
Gamma |- l : T
----------------------------- [T-While]
Gamma |- while c l : vazio
```

O `for` usa limites inteiros pela propria gramatica e exige variavel de controle inteira:

```text
Gamma(i) = int
-------------------------------- [T-For]
Gamma |- for INT INT i linha : vazio
```

## Erros

O verificador gera uma lista de erros semanticos com codigo, linha, simbolo e mensagem. Os principais erros sao:

- `VARIAVEL_NAO_DECLARADA`
- `VARIAVEL_SEM_TIPO`
- `OPERANDOS_INVALIDOS`
- `RELACIONAL_INVALIDO`
- `LOGICO_INVALIDO`
- `CONDICAO_NAO_BOOL`
- `FOR_VARIAVEL_NAO_INT`
