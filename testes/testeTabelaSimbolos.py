# Paulo Henrique Eidi Mino - Aluno 2
#
# Testes unitários para construirTabelaSimbolos (iteração 1).
#
# Esta iteração cobre apenas os nós:
#   - sequencia
#   - fim_programa
#   - atribuicao_memoria
#   - leitura_memoria
#
# Testes para res, for, if, while, expressao_aritmetica serão adicionados
# na iteração 2.

import os
import sys
import unittest

# Permite rodar com "python3 testes/testeTabelaSimbolos.py"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from construirTabelaSimbolos import (  # noqa: E402
    construirTabelaSimbolos,
    TIPO_INT,
    TIPO_REAL,
    TIPO_INDEFINIDO,
    COD_VARIAVEL_NAO_DECLARADA,
    COD_REDEFINICAO_INCOMPATIVEL,
)


# ---------------------------------------------------------------------------
# Helpers para montar árvores simplificadas (formato da Fase 2)
# ---------------------------------------------------------------------------
# Em vez de copiar e colar dicionários gigantes em cada teste, usamos
# pequenas funções construtoras que produzem nós no MESMO formato gerado
# pela função simplificarArvore() do gerarArvore.py (Fase 2). Isso mantém
# os testes legíveis e protege contra divergências futuras do formato.


def terminal_int(valor, linha):
    """Nó terminal representando um literal inteiro."""
    return {
        "tipo": "terminal",
        "simbolo": "INT",
        "valor": str(valor),
        "linha": linha,
    }


def terminal_real(valor, linha):
    """Nó terminal representando um literal real."""
    return {
        "tipo": "terminal",
        "simbolo": "REAL",
        "valor": str(valor),
        "linha": linha,
    }


def atribuicao(nome, no_valor, linha):
    """Nó atribuicao_memoria: (V MEM X)."""
    return {
        "tipo": "atribuicao_memoria",
        "nome": nome,
        "valor": no_valor,
        "linha": linha,
    }


def leitura(nome, linha):
    """Nó leitura_memoria: (X)."""
    return {
        "tipo": "leitura_memoria",
        "nome": nome,
        "linha": linha,
    }


def fim(linha):
    """Nó fim_programa: (END)."""
    return {"tipo": "fim_programa", "linha": linha}


def programa(*comandos):
    """
    Encadeia uma lista de comandos em nós 'sequencia', terminando em
    'fim_programa'. Replica o jeito que simplificarArvore() encadeia.

    Exemplo:
        programa(decl_a, decl_b, leit_a)
    produz:
        sequencia(decl_a, sequencia(decl_b, sequencia(leit_a, fim_programa)))
    """
    if not comandos:
        return fim(linha=1)

    # Constrói de trás para frente.
    no_atual = fim(linha=comandos[-1].get("linha", 1) + 1)
    for cmd in reversed(comandos):
        no_atual = {
            "tipo": "sequencia",
            "atual": cmd,
            "proximo": no_atual,
        }
    return no_atual


# ---------------------------------------------------------------------------
# Testes — declaração e leitura básica
# ---------------------------------------------------------------------------

class TestDeclaracaoBasica(unittest.TestCase):
    """Casos simples: declarar uma variável e consultar a tabela."""

    def test_declaracao_real_simples(self):
        # (3.0 MEM A) na linha 2
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertIn("A", resultado["simbolos"])
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["A"]["linha_definicao"], 2)
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [])
        self.assertTrue(resultado["simbolos"]["A"]["inicializada"])
        self.assertEqual(resultado["erros"], [])

    def test_declaracao_int_simples(self):
        # (5 MEM B) na linha 2
        arvore = programa(
            atribuicao("B", terminal_int("5", 2), linha=2),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertIn("B", resultado["simbolos"])
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["erros"], [])

    def test_multiplas_declaracoes(self):
        # (3.0 MEM A) linha 2
        # (5 MEM B)   linha 3
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("B", terminal_int("5", 3), linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["simbolos"]["A"]["linha_definicao"], 2)
        self.assertEqual(resultado["simbolos"]["B"]["linha_definicao"], 3)
        self.assertEqual(resultado["erros"], [])


class TestLeituraBasica(unittest.TestCase):
    """Casos simples: ler uma variável e registrar a linha de uso."""

    def test_leitura_de_variavel_declarada(self):
        # (3.0 MEM A)   linha 2
        # (A)           linha 3
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("A", linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3])
        self.assertEqual(resultado["erros"], [])

    def test_leitura_em_multiplas_linhas(self):
        # (3.0 MEM A)   linha 2
        # (A)           linha 3
        # (A)           linha 5
        # (A)           linha 7
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("A", linha=3),
            leitura("A", linha=5),
            leitura("A", linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3, 5, 7])

    def test_leitura_mesma_linha_nao_duplica(self):
        # Caso patológico de teste — não acontece com simplificarArvore real,
        # mas garante a invariante "não duplicamos linhas".
        # Simulamos duas leituras da mesma variável na MESMA linha.
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("A", linha=3),
            leitura("A", linha=3),  # mesma linha 3
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3])


# ---------------------------------------------------------------------------
# Testes — erros de declaração
# ---------------------------------------------------------------------------

class TestVariavelNaoDeclarada(unittest.TestCase):
    """Detectar uso de variável antes da declaração."""

    def test_leitura_sem_declaracao_gera_erro(self):
        # (X)   linha 2 — X nunca foi declarada
        arvore = programa(
            leitura("X", linha=2),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertNotIn("X", resultado["simbolos"])
        self.assertEqual(len(resultado["erros"]), 1)

        erro = resultado["erros"][0]
        self.assertEqual(erro["codigo"], COD_VARIAVEL_NAO_DECLARADA)
        self.assertEqual(erro["linha"], 2)
        self.assertEqual(erro["simbolo"], "X")
        self.assertIn("X", erro["mensagem"])

    def test_leitura_depois_de_declaracao_de_outra_variavel(self):
        # (3.0 MEM A)   linha 2
        # (B)           linha 3 — B não foi declarada
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            leitura("B", linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertIn("A", resultado["simbolos"])
        self.assertNotIn("B", resultado["simbolos"])
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_VARIAVEL_NAO_DECLARADA)
        self.assertEqual(resultado["erros"][0]["simbolo"], "B")

    def test_uso_em_atribuicao_sem_declaracao(self):
        # ((Y) MEM X)   linha 2 — Y nunca foi declarada
        # Espera-se erro VARIAVEL_NAO_DECLARADA para Y, e X registrada como
        # INDEFINIDO (pois o tipo de Y é desconhecido).
        arvore = programa(
            atribuicao("X", leitura("Y", linha=2), linha=2),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertIn("X", resultado["simbolos"])
        self.assertEqual(resultado["simbolos"]["X"]["tipo"], TIPO_INDEFINIDO)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_VARIAVEL_NAO_DECLARADA)
        self.assertEqual(resultado["erros"][0]["simbolo"], "Y")


class TestRedefinicao(unittest.TestCase):
    """Redefinições compatíveis e incompatíveis."""

    def test_redefinicao_compativel_nao_gera_erro(self):
        # (3.0 MEM A)   linha 2
        # (4.0 MEM A)   linha 5 — ambos REAL, ok
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("A", terminal_real("4.0", 5), linha=5),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        # A primeira linha de definição permanece como referência principal.
        self.assertEqual(resultado["simbolos"]["A"]["linha_definicao"], 2)
        self.assertEqual(resultado["erros"], [])

    def test_redefinicao_incompativel_real_para_int(self):
        # (3.0 MEM A)   linha 2  -> REAL
        # (5 MEM A)     linha 7  -> tenta INT
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("A", terminal_int("5", 7), linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)

        # Tipo original preservado (decisão de design — ver comentários no
        # próprio construirTabelaSimbolos.py).
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(len(resultado["erros"]), 1)

        erro = resultado["erros"][0]
        self.assertEqual(erro["codigo"], COD_REDEFINICAO_INCOMPATIVEL)
        self.assertEqual(erro["linha"], 7)
        self.assertEqual(erro["simbolo"], "A")

    def test_redefinicao_incompativel_int_para_real(self):
        # (5 MEM A)     linha 2  -> INT
        # (3.0 MEM A)   linha 7  -> tenta REAL
        arvore = programa(
            atribuicao("A", terminal_int("5", 2), linha=2),
            atribuicao("A", terminal_real("3.0", 7), linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_INT)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertEqual(resultado["erros"][0]["codigo"], COD_REDEFINICAO_INCOMPATIVEL)


# ---------------------------------------------------------------------------
# Testes — atribuição via leitura de outra variável (caso (Y MEM X))
# ---------------------------------------------------------------------------

class TestAtribuicaoViaLeitura(unittest.TestCase):
    """
    Casos onde a atribuição usa uma leitura de outra variável como valor.
    Verifica que o tipo é propagado E que a linha de uso da fonte é
    registrada.
    """

    def test_copia_tipo_de_variavel_existente(self):
        # (3.0 MEM A)     linha 2
        # ((A) MEM B)     linha 3 — copia A para B
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("B", leitura("A", linha=3), linha=3),
        )
        resultado = construirTabelaSimbolos(arvore)

        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_REAL)
        # A leitura de A na linha 3 deve estar registrada como uso.
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [3])
        self.assertEqual(resultado["erros"], [])


# ---------------------------------------------------------------------------
# Testes — programas vazios / triviais
# ---------------------------------------------------------------------------

class TestProgramasTriviais(unittest.TestCase):
    """Bordas: programa só com (START)(END), só com fim_programa, etc."""

    def test_apenas_fim_de_programa(self):
        arvore = fim(linha=1)
        resultado = construirTabelaSimbolos(arvore)
        self.assertEqual(resultado["simbolos"], {})
        self.assertEqual(resultado["erros"], [])

    def test_arvore_none(self):
        resultado = construirTabelaSimbolos(None)
        self.assertEqual(resultado["simbolos"], {})
        self.assertEqual(resultado["erros"], [])


# ---------------------------------------------------------------------------
# Teste integrado — programa parecido com o teste1.txt da Fase 2
# ---------------------------------------------------------------------------

class TestProgramaCompleto(unittest.TestCase):
    """Simula um programa que combina vários comandos suportados."""

    def test_programa_com_declaracoes_e_leituras(self):
        # (START)
        # (3.0 MEM A)     linha 2
        # (5 MEM B)       linha 3
        # ((A) MEM C)     linha 4 — copia A em C
        # (A)             linha 5
        # (B)             linha 6
        # (C)             linha 7
        # (END)
        arvore = programa(
            atribuicao("A", terminal_real("3.0", 2), linha=2),
            atribuicao("B", terminal_int("5", 3), linha=3),
            atribuicao("C", leitura("A", linha=4), linha=4),
            leitura("A", linha=5),
            leitura("B", linha=6),
            leitura("C", linha=7),
        )
        resultado = construirTabelaSimbolos(arvore)

        # Tipos
        self.assertEqual(resultado["simbolos"]["A"]["tipo"], TIPO_REAL)
        self.assertEqual(resultado["simbolos"]["B"]["tipo"], TIPO_INT)
        self.assertEqual(resultado["simbolos"]["C"]["tipo"], TIPO_REAL)

        # Linhas de uso
        # A é usada na linha 4 (dentro da atribuicao de C) e na linha 5.
        self.assertEqual(resultado["simbolos"]["A"]["linhas_uso"], [4, 5])
        self.assertEqual(resultado["simbolos"]["B"]["linhas_uso"], [6])
        self.assertEqual(resultado["simbolos"]["C"]["linhas_uso"], [7])

        # Sem erros
        self.assertEqual(resultado["erros"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)