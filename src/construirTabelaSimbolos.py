# Paulo Henrique Eidi Mino - Aluno 2
# Constrói a tabela de símbolos a partir da árvore sintática simplificada
# da Fase 2 e detecta erros semânticos de declaração (uso sem declaração,
# redefinição incompatível). Saída é consumida por verificarTipos() (Aluno 3)
# e gerarArvoreAtribuida() (Aluno 4).

# Tipos em MAIÚSCULAS para alinhar com os nomes dos terminais da gramática
# LL(1) da Fase 2 (INT, REAL, BOOL).
TIPO_INT = "INT"
TIPO_REAL = "REAL"
TIPO_BOOL = "BOOL"
TIPO_INDEFINIDO = "INDEFINIDO"

ESCOPO_GLOBAL = "global"

# Erros são dicts estruturados (não strings, como nas Fases 1 e 2) para
# permitir acúmulo sem interromper a análise — o usuário vê todos os erros
# de uma vez. O Aluno 3 estende com mais códigos em verificarTipos().
COD_VARIAVEL_NAO_DECLARADA = "VARIAVEL_NAO_DECLARADA"
COD_REDEFINICAO_INCOMPATIVEL = "REDEFINICAO_INCOMPATIVEL"


def _criar_simbolo(nome, tipo, linha):
    return {
        "nome": nome,
        "tipo": tipo,
        "linha_definicao": linha,
        "linhas_uso": [],
        "inicializada": True,
        "escopo": ESCOPO_GLOBAL,
    }


def _criar_erro(codigo, linha, simbolo, mensagem):
    return {
        "codigo": codigo,
        "linha": linha,
        "simbolo": simbolo,
        "mensagem": mensagem,
    }


def _inferir_tipo_valor(no_valor, simbolos):
    if not isinstance(no_valor, dict):
        return TIPO_INDEFINIDO

    tipo_no = no_valor.get("tipo")

    if tipo_no == "terminal":
        simbolo = no_valor.get("simbolo")
        if simbolo == "INT":
            return TIPO_INT
        if simbolo == "REAL":
            return TIPO_REAL
        return TIPO_INDEFINIDO

    if tipo_no == "leitura_memoria":
        nome = no_valor.get("nome")
        if nome in simbolos:
            return simbolos[nome]["tipo"]
        return TIPO_INDEFINIDO

    # expressao_aritmetica, res, condicao: propagação de tipos em expressões
    # é responsabilidade do Aluno 3 (Seção 7.3 do enunciado). Aqui retornamos
    # INDEFINIDO; verificarTipos() atualiza a tabela depois.
    return TIPO_INDEFINIDO


def _tratar_atribuicao_memoria(no, simbolos, erros):
    nome = no.get("nome")
    linha = no.get("linha")
    no_valor = no.get("valor")

    # Visita o lado direito ANTES de registrar o símbolo. Garante que, em
    # (Y MEM X), a leitura de Y seja contabilizada (e possível erro de Y
    # não declarado seja reportado) antes de inferirmos o tipo de X.
    _percorrer(no_valor, simbolos, erros)

    tipo_inferido = _inferir_tipo_valor(no_valor, simbolos)

    if nome not in simbolos:
        simbolos[nome] = _criar_simbolo(nome, tipo_inferido, linha)
        return

    tipo_anterior = simbolos[nome]["tipo"]

    if tipo_anterior == TIPO_INDEFINIDO:
        simbolos[nome]["tipo"] = tipo_inferido
        return

    if tipo_inferido == TIPO_INDEFINIDO:
        return

    if tipo_anterior != tipo_inferido:
        erros.append(_criar_erro(
            COD_REDEFINICAO_INCOMPATIVEL,
            linha,
            nome,
            f"Erro semântico na linha {linha}: variável '{nome}' foi "
            f"declarada como {tipo_anterior} na linha "
            f"{simbolos[nome]['linha_definicao']} e está sendo redefinida "
            f"como {tipo_inferido}."
        ))
        # Mantemos o tipo original. Sobrescrever propagaria erros em cascata
        # para todos os usos posteriores da variável.


def _tratar_leitura_memoria(no, simbolos, erros):
    nome = no.get("nome")
    linha = no.get("linha")

    if nome not in simbolos:
        erros.append(_criar_erro(
            COD_VARIAVEL_NAO_DECLARADA,
            linha,
            nome,
            f"Erro semântico na linha {linha}: variável '{nome}' usada "
            f"sem ter sido declarada."
        ))
        return

    if linha not in simbolos[nome]["linhas_uso"]:
        simbolos[nome]["linhas_uso"].append(linha)


def _percorrer(no, simbolos, erros):
    if not isinstance(no, dict):
        return

    tipo_no = no.get("tipo")

    if tipo_no == "sequencia":
        _percorrer(no.get("atual"), simbolos, erros)
        _percorrer(no.get("proximo"), simbolos, erros)
        return

    if tipo_no == "fim_programa":
        return

    if tipo_no == "atribuicao_memoria":
        _tratar_atribuicao_memoria(no, simbolos, erros)
        return

    if tipo_no == "leitura_memoria":
        _tratar_leitura_memoria(no, simbolos, erros)
        return

    if tipo_no == "terminal":
        return


def construirTabelaSimbolos(arvore):
    simbolos = {}
    erros = []
    _percorrer(arvore, simbolos, erros)
    return {
        "simbolos": simbolos,
        "erros": erros,
    }