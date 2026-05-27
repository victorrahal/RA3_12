# Paulo Henrique Eidi Mino - Aluno 3

from tokensConfig import criarToken, OPERADORES_SIMPLES
from estadosLexicos import estadoNumero, estadoPalavra
 
def lerTokens(arquivo):
    tokens = []
 
    try:
        with open(arquivo, 'r') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo '{arquivo}' não encontrado.")
 
    for num_linha, linha in enumerate(linhas, start=1):
        linha = linha.strip()
        if not linha:
            continue
 
        i = 0
        while i < len(linha):
            ch = linha[i]
 
            # Espaços em branco
            if ch in (' ', '\t'):
                i += 1
                continue
 
            # Parênteses
            if ch == '(':
                tokens.append(criarToken("LPAREN", "(", num_linha))
                i += 1
                continue
 
            if ch == ')':
                tokens.append(criarToken("RPAREN", ")", num_linha))
                i += 1
                continue
 
            # Números (INT ou REAL)
            if ch.isdigit():
                tok, i = estadoNumero(linha, i, num_linha)
                tokens.append(tok)
                continue

            # Operadores simples (aritméticos e relacionais < >)
            if ch in OPERADORES_SIMPLES:
                tokens.append(criarToken(OPERADORES_SIMPLES[ch], ch, num_linha))
                i += 1
                continue
 
            # Palavras: keywords ou MEM_ID
            if ch.isalpha():
                tok, i = estadoPalavra(linha, i, num_linha)
                tokens.append(tok)
                continue
 
            # Erro de caractere não reconhecido
            raise ValueError(
                f"Erro léxico na linha {num_linha}: "
                f"caractere inesperado '{ch}'"
            )
 
    # Token de fim de entrada (necessário para o parser)
    tokens.append(criarToken("$", "$", -1))
    return tokens