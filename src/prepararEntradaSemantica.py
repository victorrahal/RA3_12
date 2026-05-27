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

def removerComentarios(conteudo):
    resultado = ''
    i = 0
    dentroComentario = False

    while i < len(conteudo):
        if not dentroComentario and i + 1 < len(conteudo) and conteudo[i] == "*" and conteudo[i + 1] == "{":
            dentroComentario = True
            i += 2
            continue
        if dentroComentario and i + 1 < len(conteudo) and conteudo[i] == "}" and conteudo[i + 1] == "*":
            dentroComentario = False
            i += 2
            continue
        if not dentroComentario:
            resultado += conteudo[i]

        i += 1

    if dentroComentario:
        raise ValueError("Erro léxico: comentário iniciado com '*{' não foi fechado com '}*'.")
    
    return resultado