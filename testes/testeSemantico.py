import unittest

from src.verificarTipos import verificarTipos

def terminal(simbolo, valor, linha=1):
    return {
        "tipo_no": "terminal",
        "simbolo": simbolo,
        "producao": [],
        "token": {"tipo": simbolo, "valor": valor, "linha": linha},
        "filhos": [],
    }

def nao_terminal(simbolo, producao, filhos):
    return {
        "tipo_no": "nao_terminal",
        "simbolo": simbolo,
        "producao": producao,
        "token": None,
        "filhos": filhos,
    }

def operando(no):
    return nao_terminal("operando", [no["simbolo"]], [no])

def operador_arit(simbolo):
    return nao_terminal("operador_arit", [simbolo], [terminal(simbolo, simbolo)])

def corpo_operacao(esq, operador, direita):
    return nao_terminal(
        "corpo",
        [esq["simbolo"], "resto_corpo"],
        [
            esq,
            nao_terminal(
                "resto_corpo",
                ["operando", "operador_arit"],
                [operando(direita), operador_arit(operador)],
            ),
        ],
    )

def condicao(esq, operador, direita):
    return nao_terminal(
        "condicao",
        ["LPAREN", "operando", "operando", "op_rel", "RPAREN"],
        [
            terminal("LPAREN", "("),
            operando(esq),
            operando(direita),
            nao_terminal("op_rel", [operador], [terminal(operador, operador)]),
            terminal("RPAREN", ")"),
        ],
    )

class TesteVerificarTipos(unittest.TestCase):
    def test_soma_int_com_real_resulta_real(self):
        arvore = corpo_operacao(terminal("INT", "2"), "OP_SUM", terminal("REAL", "3.5"))
        resultado = verificarTipos(arvore, {})
        self.assertEqual(resultado["arvore"]["tipo_inferido"], "REAL")
        self.assertEqual(resultado["erros"], [])

    def test_divisao_inteira_rejeita_real(self):
        arvore = corpo_operacao(terminal("REAL", "2.0"), "OP_DIVI", terminal("INT", "3"))
        resultado = verificarTipos(arvore, {})
        self.assertEqual(resultado["arvore"]["tipo_inferido"], "ERRO")
        self.assertEqual(resultado["erros"][0]["codigo"], "OPERANDOS_EXIGE_INT")

    def test_variavel_usa_tipo_da_tabela(self):
        arvore = corpo_operacao(terminal("MEM_ID", "VALOR"), "OP_MUL", terminal("INT", "2"))
        tabela = {"simbolos": {"VALOR": {"tipo": "REAL", "linha_definicao": 1}}}
        resultado = verificarTipos(arvore, tabela)
        self.assertEqual(resultado["arvore"]["tipo_inferido"], "REAL")
        self.assertEqual(resultado["erros"], [])

    def test_variavel_sem_declaracao_gera_erro(self):
        arvore = corpo_operacao(terminal("MEM_ID", "X"), "OP_SUM", terminal("INT", "2"))
        resultado = verificarTipos(arvore, {})
        codigos = [erro["codigo"] for erro in resultado["erros"]]
        self.assertIn("VARIAVEL_NAO_DECLARADA", codigos)

    def test_condicao_relacional_resulta_bool(self):
        arvore = condicao(terminal("INT", "1"), "OP_LT", terminal("REAL", "2.0"))
        resultado = verificarTipos(arvore, {})
        self.assertEqual(resultado["arvore"]["tipo_inferido"], "BOOL")
        self.assertEqual(resultado["erros"], [])

    def test_condicao_relacional_rejeita_bool(self):
        arvore = condicao(terminal("BOOL", "true"), "OP_GT", terminal("INT", "2"))
        resultado = verificarTipos(arvore, {})
        self.assertEqual(resultado["arvore"]["tipo_inferido"], "ERRO")
        self.assertEqual(resultado["erros"][0]["codigo"], "TIPO_INCOMPATIVEIS_RELACIONAL")


if __name__ == "__main__":
    unittest.main()
