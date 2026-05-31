import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'src')
    )
)

from prepararEntradaSemantica import prepararEntradaSemantica

if len(sys.argv) != 2:
    print(f"Uso: python testePrepararEntradaSemantica.py <arquivo.txt>")
    sys.exit(1)

arquivo = sys.argv[1]

try:
    resultado = prepararEntradaSemantica(arquivo)

    print("Arquivo processado: ", resultado["arquivo"])
    print("Quantidade de tokens: ", len(resultado["tokens"]))
    print("Árvore sintática inicial gerada com sucesso.")

except Exception as erro:
    print("Erro encontrado: ", erro)