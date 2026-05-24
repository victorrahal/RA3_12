# verificarTipos.py

TIPO_INT = "INT"
TIPO_REAL = "REAL"
TIPO_BOOL = "BOOL"
TIPO_ERRO = "ERRO"


def verificarTipos(arvore, tabelaSimbolos):
    """
    Entrada:
        arvore: árvore sintática em formato dict
        tabelaSimbolos: tabela com variáveis, tipos, linhas de uso etc.

    Saída:
        {
            "arvore": arvore com atributo "tipo_inferido",
            "tabelaSimbolos": tabela atualizada,
            "erros": lista de erros semânticos
        }
    """

    erros = []
    simbolos = tabelaSimbolos.get("simbolos", {})

    operadores_aritmeticos = {"+", "-", "*", "^"}
    operadores_int = {"/", "%"}       # divisão inteira e resto
    operadores_real = {"|"}           # divisão real
    operadores_relacionais = {">", "<", ">=", "<=", "==", "!="}
    operadores_logicos = {"&&", "||", "AND", "OR"}
    operadores_unarios_logicos = {"!", "NOT"}

    def linha_do_no(no):
        token = no.get("token")
        if token:
            return token.get("linha", "?")
        for filho in no.get("filhos", []):
            linha = linha_do_no(filho)
            if linha != "?":
                return linha
        return "?"

    def adicionar_erro(no, mensagem):
        erros.append(f"Linha {linha_do_no(no)}: {mensagem}")

    def tipo_numero_compativel(t1, t2):
        return t1 in [TIPO_INT, TIPO_REAL] and t2 in [TIPO_INT, TIPO_REAL]

    def promover_tipo(t1, t2):
        if TIPO_ERRO in [t1, t2]:
            return TIPO_ERRO
        if t1 == TIPO_REAL or t2 == TIPO_REAL:
            return TIPO_REAL
        return TIPO_INT

    def inferir_terminal(no):
        token = no.get("token") or {}
        tipo_token = token.get("tipo")
        valor = token.get("valor")

        if tipo_token == "INT":
            return TIPO_INT

        if tipo_token == "REAL":
            return TIPO_REAL

        if tipo_token == "BOOL":
            return TIPO_BOOL

        if valor in ["true", "false", "TRUE", "FALSE"]:
            return TIPO_BOOL

        if tipo_token in ["MEM", "ID", "IDENTIFICADOR"]:
            nome = valor

            if nome not in simbolos:
                adicionar_erro(no, f"variável '{nome}' usada, mas não declarada")
                return TIPO_ERRO

            info = simbolos[nome]

            if not info.get("inicializada", False):
                adicionar_erro(no, f"variável '{nome}' usada antes de ser inicializada")

            return info.get("tipo", TIPO_ERRO)

        return None

    def inferir_operacao(no, tipos_filhos):
        simbolo = no.get("simbolo")
        token = no.get("token") or {}
        valor = token.get("valor")

        operador = valor if valor else simbolo

        tipos_validos = [t for t in tipos_filhos if t is not None]

        if operador in operadores_aritmeticos:
            if len(tipos_validos) < 2:
                adicionar_erro(no, f"operador '{operador}' precisa de dois operandos")
                return TIPO_ERRO

            t1, t2 = tipos_validos[-2], tipos_validos[-1]

            if not tipo_numero_compativel(t1, t2):
                adicionar_erro(
                    no,
                    f"operador '{operador}' espera INT ou REAL, mas recebeu {t1} e {t2}"
                )
                return TIPO_ERRO

            return promover_tipo(t1, t2)

        if operador in operadores_int:
            if len(tipos_validos) < 2:
                adicionar_erro(no, f"operador '{operador}' precisa de dois operandos")
                return TIPO_ERRO

            t1, t2 = tipos_validos[-2], tipos_validos[-1]

            if t1 != TIPO_INT or t2 != TIPO_INT:
                adicionar_erro(
                    no,
                    f"operador '{operador}' só aceita INT, mas recebeu {t1} e {t2}"
                )
                return TIPO_ERRO

            return TIPO_INT

        if operador in operadores_real:
            if len(tipos_validos) < 2:
                adicionar_erro(no, f"operador '{operador}' precisa de dois operandos")
                return TIPO_ERRO

            t1, t2 = tipos_validos[-2], tipos_validos[-1]

            if not tipo_numero_compativel(t1, t2):
                adicionar_erro(
                    no,
                    f"divisão real '{operador}' espera INT ou REAL, mas recebeu {t1} e {t2}"
                )
                return TIPO_ERRO

            return TIPO_REAL

        if operador in operadores_relacionais:
            if len(tipos_validos) < 2:
                adicionar_erro(no, f"operador relacional '{operador}' precisa de dois operandos")
                return TIPO_ERRO

            t1, t2 = tipos_validos[-2], tipos_validos[-1]

            if not tipo_numero_compativel(t1, t2):
                adicionar_erro(
                    no,
                    f"operador relacional '{operador}' espera tipos numéricos, mas recebeu {t1} e {t2}"
                )
                return TIPO_ERRO

            return TIPO_BOOL

        if operador in operadores_logicos:
            if len(tipos_validos) < 2:
                adicionar_erro(no, f"operador lógico '{operador}' precisa de dois operandos")
                return TIPO_ERRO

            t1, t2 = tipos_validos[-2], tipos_validos[-1]

            if t1 != TIPO_BOOL or t2 != TIPO_BOOL:
                adicionar_erro(
                    no,
                    f"operador lógico '{operador}' espera BOOL e BOOL, mas recebeu {t1} e {t2}"
                )
                return TIPO_ERRO

            return TIPO_BOOL

        if operador in operadores_unarios_logicos:
            if len(tipos_validos) < 1:
                adicionar_erro(no, f"operador lógico '{operador}' precisa de um operando")
                return TIPO_ERRO

            t1 = tipos_validos[-1]

            if t1 != TIPO_BOOL:
                adicionar_erro(
                    no,
                    f"operador lógico '{operador}' espera BOOL, mas recebeu {t1}"
                )
                return TIPO_ERRO

            return TIPO_BOOL

        return None

    def verificar_condicao(no, tipo):
        simbolo = no.get("simbolo", "").lower()

        if simbolo in ["if", "while", "decisao", "laco", "condicao"]:
            if tipo != TIPO_BOOL and tipo != TIPO_ERRO:
                adicionar_erro(
                    no,
                    f"condição de decisão/laço deve ser BOOL, mas recebeu {tipo}"
                )

    def percorrer(no):
        if not isinstance(no, dict):
            return None

        if no.get("tipo_no") == "terminal":
            tipo = inferir_terminal(no)
            no["tipo_inferido"] = tipo
            return tipo

        tipos_filhos = []

        for filho in no.get("filhos", []):
            tipo_filho = percorrer(filho)
            if tipo_filho is not None:
                tipos_filhos.append(tipo_filho)

        tipo_operacao = inferir_operacao(no, tipos_filhos)

        if tipo_operacao is not None:
            no["tipo_inferido"] = tipo_operacao
            verificar_condicao(no, tipo_operacao)
            return tipo_operacao

        if len(tipos_filhos) == 1:
            tipo = tipos_filhos[0]
        elif len(tipos_filhos) > 1:
            tipo = tipos_filhos[-1]
        else:
            tipo = None

        no["tipo_inferido"] = tipo
        verificar_condicao(no, tipo)

        return tipo

    percorrer(arvore)

    return {
        "arvore": arvore,
        "tabelaSimbolos": tabelaSimbolos,
        "erros": erros
    }