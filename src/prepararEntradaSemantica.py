# Aluno 1 - Lucas Balint Vilar

import os

from lerTokens import lerTokens
from construirGramatica import construirGramatica
from parsear import parsear
from gerarArvore import gerarArvore, simplificarArvore

def prepararEntradaSemantica(arquivo):
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    caminhoArquivo = os.path.join(raiz, "testes", arquivo)

    if not os.path.isfile(caminhoArquivo):
        raise FileNotFoundError(f'Arquivo "{arquivo}" não encontrado na pasta testes.')
    
    # Análise Léxica
    tokens = lerTokens(caminhoArquivo)

    # Contrução da gramática LL(1)
    info = construirGramatica()

    # Análise Sintática
    derivacao, arvoreSintaticaJson = parsear(
        tokens, 
        info["tabela__LL1"],
        info["inicio"]
    )

    # Geração da árvore sintática em objetos
    arvoreSintatica = gerarArvore(arvoreSintaticaJson)

    # Geração da árvore simplificada
    arvoreSimplificada = simplificarArvore(arvoreSintatica)

    return {
        "arquivo": caminhoArquivo,
        "tokens": tokens,
        "derivacao": derivacao,
        "arvore_sintatica": arvoreSintatica,
        "arvore_sintatica_json": arvoreSintaticaJson,
        "arvore_simplificada": arvoreSimplificada
    }