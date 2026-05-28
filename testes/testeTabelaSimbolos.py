# Paulo Henrique Eidi Mino - Aluno 2
# Testes unitários do construirTabelaSimbolos. Cobre as duas iterações:
# nós básicos (declaração e leitura) e nós de controle/expressão (if, while,
# for, res, expressao_aritmetica, condicao).

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from construirTabelaSimbolos import (  # noqa: E402
    construirTabelaSimbolos,
    TIPO_INT,
    TIPO_REAL,
    TIPO_INDEFINIDO,
    COD_VARIAVEL_NAO_DECLARADA,
    COD_REDEFINICAO_INCOMPATIVEL,
    COD_RES_INDICE_INVALIDO,
    COD_FOR_VARIAVEL_REDEFINIDA,
)

# Helpers — montam nós no mesmo formato produzido por simplificarArvore().

def terminal_int(valor, linha):
    return {"tipo": "terminal", "simbolo": "INT", "valor": str(valor), "linha": linha}


def terminal_real(valor, linha):
    return {"tipo": "terminal", "simbolo": "REAL", "valor": str(valor), "linha": linha}


def atribuicao(nome, no_valor, linha):
    return {"tipo": "atribuicao_memoria", "nome": nome, "valor": no_valor, "linha": linha}


def leitura(nome, linha):
    return {"tipo": "leitura_memoria", "nome": nome, "linha": linha}


def res(indice, linha):
    return {"tipo": "res", "indice": indice, "linha": linha}


def expr(operador, esq, dir_, linha):
    return {
        "tipo": "expressao_aritmetica",
        "operador": operador,
        "operandos": [esq, dir_],
        "linha": linha,
    }

def condicao(esq, dir_, operador, linha):
    return {
        "tipo": "condicao",
        "operador": operador,
        "esquerdo": esq,
        "direito": dir_,
        "linha": linha,
    }

def no_if(cond, entao, senao, linha):
    return {"tipo": "if", "condicao": cond, "entao": entao, "senao": senao, "linha": linha}

def no_while(cond, corpo, linha):
    return {"tipo": "while", "condicao": cond, "corpo": corpo, "linha": linha}

def no_for(variavel, inicio, fim, corpo, linha):
    return {
        "tipo": "for",
        "variavel": variavel,
        "inicio": inicio,
        "fim": fim,
        "corpo": corpo,
        "linha": linha,
    }

def fim(linha):
    return {"tipo": "fim_programa", "linha": linha}

def programa(*comandos):
    if not comandos:
        return fim(linha=1)
    no_atual = fim(linha=comandos[-1].get("linha", 1) + 1)
    for cmd in reversed(comandos):
        no_atual = {"tipo": "sequencia", "atual": cmd, "proximo": no_atual}
    return no_atual

# Iteração 1 (mantida) — declaração, leitura, redefinição.

class TestDeclaracaoBasica(unittest.TestCase):

    def test_declaracao_real_simples(self):
        arvore = programa(atribuicao("A", terminal_real("3.0", 2), linha=2))
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["A"]["linha_definicao"], 2)
        self.assertEqual(resultado["erros"], [])

    def test_declaracao_int_simples(self):
        arvore = programa(atribuicao("B", terminal_int("5", 2), linha=2))
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["erros"], [])

    def test_multiplas_declaracoes(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("B", terminal_int("5", 3), linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_INT)

class TestLeituraBasica(unittest.TestCase):

    def test_leitura_de_variavel_declarada(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("A", linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3])

    def test_leitura_em_multiplas_linhas(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("A", linha=3),
            leitura("A", linha=5),
            leitura("A", linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3, 5, 7])

class TestVariavelNaoDeclarada(unittest.TestCase):

    def test_leitura_sem_declaracao_gera_erro(self):
        arvore = programa(leitura("X", linha=2))
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_VARIAVEL_NAO_DECLARADA)
        self.assertEqual(resultado["erros"][0]["simbolo"], "X")

    def test_uso_em_atribuicao_sem_declaracao(self):
        arvore = programa(atribuicao("X", leitura("Y", linha=2), linha=2))
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["X"]["tipo"], TIPO_INDEFINIDO)
        self.assertEqual(resultado["erros"][0]["simbolo"], "Y")

class TestRedefinicao(unittest.TestCase):

    def test_redefinicao_compativel(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("A", terminal_real("4.0", 5), linha=5),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["erros"], [])

    def test_redefinicao_incompativel_real_para_int(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("A", terminal_int("5", 7), linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)
        # Tipo original preservado para evitar cascata de erros.
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_REDEFINICAO_INCOMPATIVEL)

# Iteração 2 — RES.

class TestRes(unittest.TestCase):

    def test_res_valido(self):
        # Programa com 3 linhas anteriores ao RES, RES referencia a linha 0.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),  # linha lógica 0
            atribuicao("B", terminal_int("5", 3), linha=3),     # linha lógica 1
            res(indice=1, linha=4),                              # linha lógica 2: pega linha 1 (B)
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["erros"], [])

    def test_res_indice_alem_do_historico(self):
        # Só uma linha anterior, mas RES pede a linha 5.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),  # linha lógica 0
            res(indice=5, linha=3),                              # linha lógica 1: índice 5 inválido
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_RES_INDICE_INVALIDO)
        self.assertEqual(resultado["erros"][0]["linha"], 3)

    def test_res_indice_negativo(self):
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            res(indice=-1, linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_RES_INDICE_INVALIDO)

    def test_res_na_primeira_linha_do_programa(self):
        # Primeiro comando é RES — sempre inválido, não existe nada antes.
        arvore = programa(res(indice=0, linha=2))
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_RES_INDICE_INVALIDO)

# Iteração 2 — FOR.

class TestFor(unittest.TestCase):

    def test_for_declara_variavel_nova_como_int(self):
        # (FOR 0 10 I (1 2 +))
        arvore = programa(
            no_for(
                variavel="I",
                inicio=terminal_int("0", 2),
                fim=terminal_int("10", 2),
                corpo=expr("+", terminal_int("1", 2), terminal_int("2", 2), linha=2),
                linha=2,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertIn("I", resultado["simbolos"])
        self.assertEqual(resultado["simbolos"]["I"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["erros"], [])

    def test_for_reaproveita_variavel_int_silenciosamente(self):
        # Variável já era INT — segue sem ruído.
        arvore = programa(
            atribuicao("I", terminal_int("0", 2), linha=2),
            no_for(
                variavel="I",
                inicio=terminal_int("0", 3),
                fim=terminal_int("10", 3),
                corpo=terminal_int("0", 3),
                linha=3,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["I"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["erros"], [])

    def test_for_conflita_com_variavel_real(self):
        # I já era REAL — FOR exige INT, gera FOR_VARIAVEL_REDEFINIDA.
        arvore = programa(
            atribuicao("I", terminal_real("3.0", 2), linha=2),
            no_for(
                variavel="I",
                inicio=terminal_int("0", 3),
                fim=terminal_int("10", 3),
                corpo=terminal_int("0", 3),
                linha=3,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        # Tipo original preservado.
        self.assertEqual(resultado["simbolos"]["I"]["tipo"], TIPO_REAL)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_FOR_VARIAVEL_REDEFINIDA)

# Iteração 2 — expressão aritmética.

class TestExpressaoAritmetica(unittest.TestCase):

    def test_expressao_simples_registra_uso(self):
        # (A 2 +) na linha 3 — A é lida na linha 3.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            expr("+", leitura("A", linha=3), terminal_int("2", 3), linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3])

    def test_expressao_aninhada_registra_todos_os_usos(self):
        # ((A 2 +) (B 3 *) -) na linha 4 — A e B são lidas na linha 4.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("B", terminal_int("5", 3), linha=3),
            expr(
                "-",
                expr("+", leitura("A", linha=4), terminal_int("2", 4), linha=4),
                expr("*", leitura("B", linha=4), terminal_int("3", 4), linha=4),
                linha=4,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [4])
        self.assertEqual(resultado["simbolos"]["B"]["linhas_uso"], [4])
        self.assertEqual(resultado["erros"], [])

# Iteração 2 — IF e WHILE com condicao.

class TestIfWhile(unittest.TestCase):

    def test_if_registra_uso_em_condicao_e_ramos(self):
        # (IF (A 5 <) (1 2 +) ((B) 3 -))
        # A usada na linha 3 (condição), B usada na linha 3 (ramo else).
        arvore = programa(
            atribuicao("A", terminal_int("0", 2), linha=2),
            atribuicao("B", terminal_int("0", 2), linha=2),  # B declarada também
            no_if(
                cond=condicao(leitura("A", linha=4), terminal_int("5", 4), "<", linha=4),
                entao=expr("+", terminal_int("1", 4), terminal_int("2", 4), linha=4),
                senao=expr("-", leitura("B", linha=4), terminal_int("3", 4), linha=4),
                linha=4,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [4])
        self.assertEqual(resultado["simbolos"]["B"]["linhas_uso"], [4])
        self.assertEqual(resultado["erros"], [])

    def test_while_detecta_uso_de_variavel_nao_declarada_na_condicao(self):
        # (WHILE (N 10 <) ((N) 1 +)) — N nunca declarada.
        arvore = programa(
            no_while(
                cond=condicao(leitura("N", linha=2), terminal_int("10", 2), "<", linha=2),
                corpo=expr("+", leitura("N", linha=2), terminal_int("1", 2), linha=2),
                linha=2,
            ),
        )
        resultado = construirTabelaSimbolos(arvore)
        # N é usada duas vezes na mesma linha — gera 2 erros, mas tabela vazia.
        self.assertNotIn("N", resultado["simbolos"])
        codigos = [e["codigo"] for e in resultado["erros"]]
        self.assertEqual(codigos.count(COD_VARIAVEL_NAO_DECLARADA), 2)

# Iteração 2 — contador de linha lógica não infla com aninhamento.

class TestContadorLinhaLogica(unittest.TestCase):

    def test_res_apos_expressao_aninhada(self):
        # Programa de 3 linhas lógicas. RES com índice 0 pega a primeira.
        # A expressão aninhada da linha 2 NÃO deve inflar o contador.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),       # linha lógica 0
            expr(                                                     # linha lógica 1
                "+",
                expr("*", terminal_int("2", 3), terminal_int("3", 3), linha=3),
                terminal_int("1", 3),
                linha=3,
            ),
            res(indice=1, linha=4),                                   # linha lógica 2 - válido
        )
        resultado = construirTabelaSimbolos(arvore)
        # Se o contador estivesse inflado, o índice 1 seria inválido.
        self.assertEqual(resultado["erros"], [])

# Programa completo combinando tudo.

class TestProgramaCompleto(unittest.TestCase):

    def test_programa_realista(self):
        # Simula um trecho do teste1.txt da Fase 2:
        # (VALOR := 42.5), (LEITURA), (IF), (FOR), (RES)
        arvore = programa(
            atribuicao("VALOR", terminal_real("42.5", 2), linha=2),
            leitura("VALOR", linha=3),
            no_if(
                cond=condicao(terminal_int("3", 4), terminal_int("5", 4), "<", linha=4),
                entao=expr("+", terminal_int("1", 4), terminal_int("2", 4), linha=4),
                senao=expr("*", terminal_int("3", 4), terminal_int("4", 4), linha=4),
                linha=4,
            ),
            no_for(
                variavel="I",
                inicio=terminal_int("0", 5),
                fim=terminal_int("3", 5),
                corpo=expr("+", leitura("I", linha=5), terminal_int("1", 5), linha=5),
                linha=5,
            ),
            res(indice=0, linha=6),  # pega a linha lógica 3 (FOR)
        )
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"]["VALOR"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["I"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["simbolos"]["VALOR"]["linhas_uso"], [3])
        self.assertEqual(resultado["simbolos"]["I"]["linhas_uso"], [5])
        self.assertEqual(resultado["erros"], [])

if __name__ == "__main__":
    unittest.main(verbosity=2)