import sys
import os
import json

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'src')
    )
)

from prepararEntradaSemantica import prepararEntradaSemantica

if len(sys.argv) != 2:
    print("Uso: python testePrepararEntradaSemantica.py <arquivo.txt>")
    sys.exit(1)

arquivo = sys.argv[1]

try:
    resultado = prepararEntradaSemantica(arquivo)

    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pastaSaida = os.path.join(raiz, 'saida')
    os.makedirs(pastaSaida, exist_ok=True)

    caminhoJson = os.path.join(pastaSaida, 'arvore_sintatica_inicial.json')

    with open(caminhoJson, 'w', encoding='utf-8') as f:
        json.dump(resultado["arvore_base_semantica"], f, indent=2, ensure_ascii=False)

    print("Arquivo processado:", resultado["arquivo"])
    print("Quantidade de tokens:", len(resultado["tokens"]))
    print("Árvore sintática inicial gerada com sucesso.")
    print("Árvore salva em:", caminhoJson)

except Exception as erro:
    print("Erro encontrado:", erro)