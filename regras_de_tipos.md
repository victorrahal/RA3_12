# Sistema de Tipos — Analisador Semântico

**Disciplina:** Linguagens Formais e Compiladores  
**Aluno 3:** João Henrique Tomaz Dutra  
**Referência:** Frank Coelho de Alcantara — _Artefatos e Tipos_

---

## 1. Introdução

Um **tipo** é uma coleção de informações representadas por um identificador para:

- um conjunto de valores (inteiros, reais, lógicos);
- uma estrutura de memória;
- um conjunto de regras para tratar esses valores.

O sistema de tipos desta linguagem é definido pelo **Cálculo de Sequentes**, onde um julgamento de tipo tem a forma:

```
Γ ⊢ t : T
```

Lê-se: _"no contexto Γ, a expressão `t` tem o tipo `T`"_.  
Se o contexto Γ indicar que um símbolo tem o tipo errado, a expressão é considerada mal tipada e um erro semântico é emitido.

---

## 2. Tipos Primitivos da Linguagem

A linguagem possui três tipos primitivos:

| Tipo   | Descrição                                       | Constante no código  |
| ------ | ----------------------------------------------- | -------------------- |
| `INT`  | Número inteiro                                  | `TIPO_INT = "INT"`   |
| `REAL` | Número de ponto flutuante                       | `TIPO_REAL = "REAL"` |
| `BOOL` | Valor lógico (resultado de condição relacional) | `TIPO_BOOL = "BOOL"` |

Dois estados especiais são usados internamente durante a análise:

| Estado       | Descrição                                        |
| ------------ | ------------------------------------------------ |
| `INDEFINIDO` | Variável declarada mas ainda sem tipo inferido   |
| `ERRO`       | Expressão mal tipada; propaga o erro sem cascata |

---

## 3. Axiomas — Regras para Literais

Os axiomas não possuem premissas: valem por si só.

```
──────────────────
  int-literal : INT
```

```
──────────────────
  real-literal : REAL
```

```
──────────────────
  true : BOOL

──────────────────
  false : BOOL
```

**Em código (`tipo_terminal`):**

- Token `INT` → tipo `INT`
- Token `REAL` → tipo `REAL`
- Token `MEM_ID` → consulta a tabela de símbolos; se ausente, erro `VARIAVEL_NAO_DECLARADA`

---

## 4. Regras de Inferência para Operadores Aritméticos

### 4.1 Operadores Gerais: `OP_SUM`, `OP_SUB`, `OP_MUL`, `OP_POW`

Aceitam `INT` ou `REAL`. O resultado é promovido ao tipo mais abrangente (`REAL` prevalece sobre `INT`).

```
  E1 : τ₁    E2 : τ₂
  τ₁ ∈ {INT, REAL}    τ₂ ∈ {INT, REAL}
──────────────────────────────────────────────
  E1 op E2 : promover(τ₁, τ₂)

  onde op ∈ {OP_SUM, OP_SUB, OP_MUL, OP_POW}
  e    promover(INT,  INT)  = INT
       promover(REAL, _)    = REAL
       promover(_,    REAL) = REAL
```

### 4.2 Divisão Inteira e Módulo: `OP_DIVI`, `OP_MOD`

Ambos os operandos **devem** ser `INT`. Qualquer outro tipo gera erro `OPERADOR_EXIGE_INT`.

```
  E1 : INT    E2 : INT
──────────────────────────────────────────────
  E1 op E2 : INT

  onde op ∈ {OP_DIVI, OP_MOD}
```

### 4.3 Divisão Real: `OP_DIVR`

Aceita `INT` ou `REAL`, mas o resultado é sempre `REAL`.

```
  E1 : τ₁    E2 : τ₂
  τ₁ ∈ {INT, REAL}    τ₂ ∈ {INT, REAL}
──────────────────────────────────────────────
  E1 OP_DIVR E2 : REAL
```

---

## 5. Regras de Inferência para Operadores Relacionais

Os operadores `OP_LT` e `OP_GT` exigem operandos numéricos e produzem um valor lógico (`BOOL`).

```
  E1 : τ₁    E2 : τ₂
  τ₁ ∈ {INT, REAL}    τ₂ ∈ {INT, REAL}
──────────────────────────────────────────────
  E1 rop E2 : BOOL

  onde rop ∈ {OP_LT, OP_GT}
```

Caso os operandos não sejam numéricos, é gerado o erro `TIPOS_INCOMPATIVEIS_RELACIONAL`.

---

## 6. Regra de Atribuição — `KW_MEM`

A instrução `(valor MEM VARIAVEL)` atribui o tipo de `valor` à variável.

```
  E1 : τ    x ∈ Γ    Γ(x) = τ
──────────────────────────────────────────────
  (E1 MEM x) : τ
```

**Inferência de tipo para variáveis indefinidas:** se `Γ(x) = INDEFINIDO` e `τ ≠ ERRO`, a tabela de símbolos é atualizada com `Γ(x) := τ`.

**Incompatibilidade:** se `Γ(x) = τ'` e `τ' ≠ τ`, gera erro `ATRIBUICAO_TIPO_INCOMPATIVEL`.

---

## 7. Regras para Estruturas de Controle

### 7.1 Condicional — `KW_IF`

A condição deve ter tipo `BOOL`. Os dois ramos são analisados independentemente.

```
  E_cond : BOOL    E_then : τ    E_else : τ
──────────────────────────────────────────────
  (KW_IF E_cond E_then E_else) : τ
```

Se `E_cond` não for `BOOL`, gera erro `CONDICAO_NAO_BOOL`.

### 7.2 Laço — `KW_WHILE`

```
  E_cond : BOOL    E_corpo : τ
──────────────────────────────────────────────
  (KW_WHILE E_cond E_corpo) : τ
```

Se `E_cond` não for `BOOL`, gera erro `CONDICAO_NAO_BOOL`.

### 7.3 Laço com Contador — `KW_FOR`

A variável de controle deve ser `INT` (ou `INDEFINIDO`, com inferência aplicada).

```
  E_inicio : INT    E_fim : INT    x ∈ Γ    Γ(x) ∈ {INT, INDEFINIDO}    E_corpo : τ
──────────────────────────────────────────────────────────────────────────────────────
  (KW_FOR E_inicio E_fim x E_corpo) : τ
```

Se `Γ(x)` não for `INT` ou `INDEFINIDO`, gera erro `FOR_VARIAVEL_NAO_INT`.

---

## 8. Promoção de Tipos

A função `promover(τ₁, τ₂)` define a hierarquia de tipos para operações mistas:

```
promover(ERRO,  _)    = ERRO
promover(_,    ERRO)  = ERRO
promover(REAL,  _)    = REAL
promover(_,    REAL)  = REAL
promover(INT,  INT)   = INT
```

`REAL` é mais abrangente que `INT`. `ERRO` propaga e não é promovido.

---

## 9. Catálogo de Erros Semânticos

| Código                           | Situação                                               | Exemplo                          |
| -------------------------------- | ------------------------------------------------------ | -------------------------------- |
| `VARIAVEL_NAO_DECLARADA`         | `MEM_ID` usado sem declaração prévia via `KW_MEM`      | `(X)` sem `(42 MEM X)` antes     |
| `ATRIBUICAO_TIPO_INCOMPATIVEL`   | Valor atribuído tem tipo diferente do tipo da variável | `(42 MEM X)` após `(3.14 MEM X)` |
| `TIPOS_INCOMPATIVEIS_OPERADOR`   | Operador aritmético recebeu tipo não numérico          | `(BOOL_VAR OP_SUM 1)`            |
| `OPERADOR_EXIGE_INT`             | `OP_DIVI` ou `OP_MOD` recebeu `REAL`                   | `(3.5 OP_DIVI 2)`                |
| `TIPOS_INCOMPATIVEIS_RELACIONAL` | Operador relacional recebeu tipo não numérico          | `(true OP_LT 1)`                 |
| `CONDICAO_NAO_BOOL`              | Condição de `IF` ou `WHILE` não é `BOOL`               | `(IF 42 ...)`                    |
| `FOR_VARIAVEL_NAO_INT`           | Variável de controle do `FOR` não é `INT`              | `(FOR 1 10 REAL_VAR ...)`        |
| `CONDICAO_MAL_FORMADA`           | Nó `condicao` está incompleto na árvore                | Falha estrutural no parser       |
| `OPERADOR_AUSENTE`               | `resto_corpo` com `operando` mas sem operador          | Falha estrutural no parser       |

---

## 10. Exemplo de Julgamento de Tipos

### Programa de entrada

```
(START)
(42.5 MEM VALOR)
(VALOR)
(END)
```

### Derivação passo a passo

```
──────────────────          (axioma: real-literal)
  42.5 : REAL

  VALOR ∉ Γ  →  Γ := Γ ∪ {VALOR : REAL}   (inferência por atribuição)
──────────────────────────────────────────────
  (42.5 MEM VALOR) : REAL

  Γ(VALOR) = REAL           (consulta à tabela de símbolos)
──────────────────────────────────────────────
  (VALOR) : REAL
```

### Resultado na árvore anotada

| Nó                                  | `tipo_inferido` |
| ----------------------------------- | --------------- |
| Terminal `REAL` "42.5"              | `REAL`          |
| Terminal `MEM_ID` "VALOR" (linha 2) | `REAL`          |
| `resto_corpo` → KW_MEM MEM_ID       | `REAL`          |
| `corpo` → REAL resto_corpo          | `REAL`          |
| Terminal `MEM_ID` "VALOR" (linha 3) | `REAL`          |
| `corpo` → MEM_ID cauda_mem          | `REAL`          |
| `programa`                          | `REAL`          |

**Tabela de símbolos resultante:**

```json
{
  "VALOR": {
    "tipo": "REAL",
    "linha_definicao": 2,
    "linhas_uso": [3],
    "inicializada": true,
    "escopo": "global"
  }
}
```

**Erros:** nenhum.

---

## 11. Casos de Teste

### Válidos

| Programa                                              | Resultado esperado        |
| ----------------------------------------------------- | ------------------------- |
| `(START)(42 MEM X)(3 OP_DIVI X)(END)`                 | X: INT; operação OK       |
| `(START)(1.5 MEM A)(2.5 MEM B)(A OP_SUM B)(END)`      | A,B: REAL; resultado REAL |
| `(START)(5 MEM I)(10 MEM J)(I OP_LT J MEM COND)(END)` | I,J: INT; COND: BOOL      |
| `(START)(IF (1 OP_LT 2) (3 MEM X) (4 MEM X))(END)`    | Condição BOOL; ramos INT  |
| `(START)(FOR 1 10 C (C OP_SUM 1))(END)`               | C inferido como INT       |

### Inválidos

| Programa                                           | Erro esperado                                          |
| -------------------------------------------------- | ------------------------------------------------------ |
| `(START)(X)(END)`                                  | `VARIAVEL_NAO_DECLARADA` — X não foi declarada         |
| `(START)(3.14 MEM Y)(10 MEM Y)(END)`               | `ATRIBUICAO_TIPO_INCOMPATIVEL` — Y é REAL, recebeu INT |
| `(START)(3.5 MEM A)(A OP_DIVI 2)(END)`             | `OPERADOR_EXIGE_INT` — OP_DIVI exige INT e INT         |
| `(START)(3.5 MEM A)(2 OP_MOD A)(END)`              | `OPERADOR_EXIGE_INT` — OP_MOD exige INT e INT          |
| `(START)(10 MEM N)(IF N (1 MEM X) (2 MEM X))(END)` | `CONDICAO_NAO_BOOL` — condição do IF é INT             |
| `(START)(WHILE (5 MEM X) (X OP_SUM 1))(END)`       | `CONDICAO_NAO_BOOL` — condição do WHILE é INT          |
| `(START)(3.14 MEM F)(FOR 1 10 F (1 MEM X))(END)`   | `FOR_VARIAVEL_NAO_INT` — variável de controle é REAL   |

---

## 12. Interface da Função

```python
def verificarTipos(arvore, tabelaSimbolos):
    """
    Entrada:
        arvore         — árvore sintática em formato dict (saída do parser)
        tabelaSimbolos — saída de construirTabelaSimbolos(arvore)

    Saída:
        {
            "arvore":         árvore com atributo "tipo_inferido" em cada nó,
            "tabelaSimbolos": tabela atualizada com tipos inferidos,
            "erros":          lista de erros semânticos estruturados
        }
    """
```

Cada erro na lista tem o formato:

```json
{
  "codigo": "VARIAVEL_NAO_DECLARADA",
  "linha": 3,
  "simbolo": "X",
  "mensagem": "Erro semântico na linha 3: variável 'X' usada sem ter sido declarada."
}
```

---

_Documento gerado como artefato da etapa de análise semântica — verificação de tipos._
