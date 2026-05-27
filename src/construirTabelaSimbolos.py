# Paulo Henrique Eidi Mino - Aluno 2
# Constrói a tabela de símbolos a partir da árvore sintática simplificada
# da Fase 2 e detecta erros semânticos de declaração (uso sem declaração,
# redefinição incompatível, índice RES inválido, variável de FOR conflitante).
# Saída é consumida por verificarTipos() (Aluno 3) e gerarArvoreAtribuida()
# (Aluno 4).

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
COD_RES_INDICE_INVALIDO = "RES_INDICE_INVALIDO"
COD_FOR_VARIAVEL_REDEFINIDA = "FOR_VARIAVEL_REDEFINIDA"


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


def _tratar_atribuicao_memoria(no, simbolos, erros, contexto):
    nome = no.get("nome")
    linha = no.get("linha")
    no_valor = no.get("valor")

    # Visita o lado direito ANTES de registrar o símbolo. Garante que, em
    # (Y MEM X), a leitura de Y seja contabilizada (e possível erro de Y
    # não declarado seja reportado) antes de inferirmos o tipo de X.
    _percorrer(no_valor, simbolos, erros, contexto)

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


def _tratar_leitura_memoria(no, simbolos, erros, contexto):
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


def _tratar_res(no, simbolos, erros, contexto):
    indice = no.get("indice")
    linha = no.get("linha")
    linha_logica = contexto["linha_logica"]

    # Convenção do enunciado (Seção 2.2): (N RES) retorna o resultado da
    # expressão N linhas anteriores. N deve ser inteiro não-negativo e
    # apontar para uma linha que já foi executada.
    if not isinstance(indice, int) or indice < 0:
        erros.append(_criar_erro(
            COD_RES_INDICE_INVALIDO,
            linha,
            "RES",
            f"Erro semântico na linha {linha}: índice de RES deve ser "
            f"inteiro não-negativo, recebido '{indice}'."
        ))
        return

    if indice >= linha_logica:
        erros.append(_criar_erro(
            COD_RES_INDICE_INVALIDO,
            linha,
            "RES",
            f"Erro semântico na linha {linha}: (RES {indice}) faz "
            f"referência a uma linha inexistente (só existem "
            f"{linha_logica} linha(s) anterior(es)."
        ))


def _tratar_for(no, simbolos, erros, contexto):
    nome_variavel = no.get("variavel")
    linha = no.get("linha")
    no_inicio = no.get("inicio")
    no_fim = no.get("fim")
    no_corpo = no.get("corpo")

    # Visita os limites antes da variável de controle, para contabilizar
    # leituras que possam aparecer em (inicio) ou (fim).
    _percorrer(no_inicio, simbolos, erros, contexto)
    _percorrer(no_fim, simbolos, erros, contexto)

    # A gramática força (FOR INT INT MEM_ID ...), então a variável de
    # controle é sempre INT por construção.
    if nome_variavel not in simbolos:
        simbolos[nome_variavel] = _criar_simbolo(nome_variavel, TIPO_INT, linha)
    else:
        tipo_anterior = simbolos[nome_variavel]["tipo"]
        if tipo_anterior not in (TIPO_INT, TIPO_INDEFINIDO):
            erros.append(_criar_erro(
                COD_FOR_VARIAVEL_REDEFINIDA,
                linha,
                nome_variavel,
                f"Erro semântico na linha {linha}: variável '{nome_variavel}' "
                f"foi declarada como {tipo_anterior} na linha "
                f"{simbolos[nome_variavel]['linha_definicao']} e está sendo "
                f"usada como variável de controle de FOR (que exige INT)."
            ))
        elif tipo_anterior == TIPO_INDEFINIDO:
            simbolos[nome_variavel]["tipo"] = TIPO_INT

    _percorrer(no_corpo, simbolos, erros, contexto)


def _tratar_expressao_aritmetica(no, simbolos, erros, contexto):
    for operando in no.get("operandos", []):
        _percorrer(operando, simbolos, erros, contexto)


def _tratar_condicao(no, simbolos, erros, contexto):
    _percorrer(no.get("esquerdo"), simbolos, erros, contexto)
    _percorrer(no.get("direito"), simbolos, erros, contexto)


def _tratar_if(no, simbolos, erros, contexto):
    _percorrer(no.get("condicao"), simbolos, erros, contexto)
    _percorrer(no.get("entao"), simbolos, erros, contexto)
    _percorrer(no.get("senao"), simbolos, erros, contexto)


def _tratar_while(no, simbolos, erros, contexto):
    _percorrer(no.get("condicao"), simbolos, erros, contexto)
    _percorrer(no.get("corpo"), simbolos, erros, contexto)


def _percorrer(no, simbolos, erros, contexto):
    if not isinstance(no, dict):
        return

    tipo_no = no.get("tipo")

    if tipo_no == "sequencia":
        # Linha lógica só incrementa para nós no NÍVEL SUPERIOR do programa
        # (filhos diretos de uma 'sequencia'). Sub-expressões aninhadas não
        # contam para o histórico de RES — mesma semântica usada pelo
        # gerarAssembly.py da Fase 2.
        _percorrer(no.get("atual"), simbolos, erros, contexto)
        contexto["linha_logica"] += 1
        _percorrer(no.get("proximo"), simbolos, erros, contexto)
        return

    if tipo_no == "fim_programa":
        return

    if tipo_no == "terminal":
        return

    despachadores = {
        "atribuicao_memoria": _tratar_atribuicao_memoria,
        "leitura_memoria": _tratar_leitura_memoria,
        "res": _tratar_res,
        "for": _tratar_for,
        "expressao_aritmetica": _tratar_expressao_aritmetica,
        "condicao": _tratar_condicao,
        "if": _tratar_if,
        "while": _tratar_while,
    }

    handler = despachadores.get(tipo_no)
    if handler:
        handler(no, simbolos, erros, contexto)


def construirTabelaSimbolos(arvore):
    simbolos = {}
    erros = []
    # contexto mutável é mais simples que passar linha_logica por valor e
    # devolver via tupla em cada handler — todos os handlers ficam com a
    # mesma assinatura.
    contexto = {"linha_logica": 0}
    _percorrer(arvore, simbolos, erros, contexto)
    return {
        "simbolos": simbolos,
        "erros": erros,
    }