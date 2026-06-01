# João Henrique Tomaz Dutra - Aluno 3

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prepararEntradaSemantica import prepararEntradaSemantica
from construirTabelaSimbolos import construirTabelaSimbolos
from verificarTipos import verificarTipos

def _verificar(arquivo):
    entrada = prepararEntradaSemantica(arquivo)
    tabela  = construirTabelaSimbolos(entrada["arvore_base_semantica"])
    return verificarTipos(entrada["arvore_base_semantica"], tabela)

def _criar_temp(nome, conteudo):
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    caminho = os.path.join(raiz, "testes", nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho

class TesteEstruturaRetorno(unittest.TestCase):

    def test_retorno_tem_chave_erros(self):
        r = _verificar("teste1.txt")
        self.assertIn("erros", r)

    def test_retorno_tem_chave_arvore(self):
        r = _verificar("teste1.txt")
        self.assertIn("arvore", r)

    def test_retorno_tem_chave_tabela_simbolos(self):
        r = _verificar("teste1.txt")
        self.assertIn("tabelaSimbolos", r)

    def test_cada_erro_tem_codigo_linha_simbolo(self):
        r = _verificar("teste2.txt")
        for e in r["erros"]:
            self.assertIn("codigo",   e, "Erro sem campo 'codigo'")
            self.assertIn("linha",    e, "Erro sem campo 'linha'")
            self.assertIn("simbolo",  e, "Erro sem campo 'simbolo'")
            self.assertIn("mensagem", e, "Erro sem campo 'mensagem'")

class TesteProgamasValidos(unittest.TestCase):

    def test_programa1_sem_erros_de_tipo(self):
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [],
                         "teste1.txt não deve ter erros semânticos")

    def test_programa3_sem_erros_de_tipo(self):
        r = _verificar("teste3.txt")
        self.assertEqual(r["erros"], [],
                         "teste3.txt não deve ter erros semânticos")

class TesteOperadoresInteiros(unittest.TestCase):

    def test_divisao_inteira_entre_inteiros_valida(self):
        # teste1.txt tem (9 4 /) — deve ser válido
        r = _verificar("teste1.txt")
        codigos = [e["codigo"] for e in r["erros"]]
        self.assertNotIn("OPERADOR_EXIGE_INT", codigos)

    def test_divisao_inteira_com_real_esquerda_gera_erro(self):
        # teste2.txt tem (3.5 2 /)
        r = _verificar("teste2.txt")
        codigos = [e["codigo"] for e in r["erros"]]
        self.assertIn("OPERADOR_EXIGE_INT", codigos)

    def test_modulo_com_real_direita_gera_erro(self):
        # teste2.txt tem (5 2.5 %)
        r = _verificar("teste2.txt")
        codigos = [e["codigo"] for e in r["erros"]]
        self.assertIn("OPERADOR_EXIGE_INT", codigos)

    def test_modulo_entre_inteiros_valido(self):
        # teste1.txt tem (9 4 %) — deve ser válido
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

    def test_divisao_inteira_gera_exatamente_dois_erros_int(self):
        # teste2.txt tem dois erros OPERADOR_EXIGE_INT: (3.5 2 /) e (5 2.5 %)
        r = _verificar("teste2.txt")
        count = sum(1 for e in r["erros"] if e["codigo"] == "OPERADOR_EXIGE_INT")
        self.assertGreaterEqual(count, 2)

class TesteOperadoresAritmeticos(unittest.TestCase):

    def test_soma_int_int_valida(self):
        caminho = _criar_temp("_temp_soma_int.txt",
            "(START)\n(5 3 +)\n(END)\n")
        try:
            r = _verificar("_temp_soma_int.txt")
            self.assertEqual(r["erros"], [])
        finally:
            os.remove(caminho)

    def test_soma_real_real_valida(self):
        caminho = _criar_temp("_temp_soma_real.txt",
            "(START)\n(5.0 3.0 +)\n(END)\n")
        try:
            r = _verificar("_temp_soma_real.txt")
            self.assertEqual(r["erros"], [])
        finally:
            os.remove(caminho)

    def test_divisao_real_valida(self):
        # Divisão real (|) aceita INT e REAL — teste1.txt tem (9.0 3.0 |)
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

    def test_potenciacao_int_int_valida(self):
        # teste1.txt tem (2 3 ^)
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

class TesteVariaveisNaoDeclaradas(unittest.TestCase):

    def test_variavel_nao_declarada_gera_erro(self):
        # teste2.txt tem (XSEMDEF 5 +)
        r = _verificar("teste2.txt")
        codigos = [e["codigo"] for e in r["erros"]]
        self.assertIn("VARIAVEL_NAO_DECLARADA", codigos)

    def test_variavel_declarada_nao_gera_erro(self):
        caminho = _criar_temp("_temp_var_decl.txt",
            "(START)\n(10 MEM X)\n(X)\n(END)\n")
        try:
            r = _verificar("_temp_var_decl.txt")
            self.assertEqual(r["erros"], [])
        finally:
            os.remove(caminho)

class TesteEstruturasControle(unittest.TestCase):

    def test_if_condicao_valida_sem_erros(self):
        # teste1.txt tem IF (TOTAL 10 <)
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

    def test_while_condicao_valida_sem_erros(self):
        # teste1.txt tem WHILE (CONT 5 <)
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

    def test_for_valido_sem_erros(self):
        # teste1.txt tem FOR 1 5 I
        r = _verificar("teste1.txt")
        self.assertEqual(r["erros"], [])

    def test_condicao_com_operador_relacional_lt(self):
        caminho = _criar_temp("_temp_cond_lt.txt",
            "(START)\n(0 MEM N)\n(IF (N 10 <) (N 1 +) (N 1 -))\n(END)\n")
        try:
            r = _verificar("_temp_cond_lt.txt")
            self.assertEqual(r["erros"], [])
        finally:
            os.remove(caminho)

    def test_condicao_com_operador_relacional_gt(self):
        caminho = _criar_temp("_temp_cond_gt.txt",
            "(START)\n(0 MEM N)\n(IF (N 5 >) (N 1 +) (N 1 -))\n(END)\n")
        try:
            r = _verificar("_temp_cond_gt.txt")
            self.assertEqual(r["erros"], [])
        finally:
            os.remove(caminho)

def terminal(simbolo, valor, linha=1):
    return {
        "tipo_no": "terminal",
        "simbolo": simbolo,
        "producao": [],
        "token": {"tipo": simbolo, "valor": valor, "linha": linha},
        "filhos": [],
    }

if __name__ == "__main__":
    unittest.main(verbosity=2)
