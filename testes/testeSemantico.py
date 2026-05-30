import json
import os 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.verificarTipos import verificarTipos


caminho_arvore = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "arvore.json")
)

with open(caminho_arvore, "r", encoding="utf-8") as f:
    arvore = json.load(f)
    
tabelaSimbolos = {
    "simbolos": {
        "VALOR": {
            "nome": "VALOR",
            "tipo": "REAL",
            "linha_definicao": 2,
            "linhas_uso": [3],
            "inicializada": True,
            "escopo": "global"
        }
    },
    "erros": []
}


resultado = verificarTipos(arvore, tabelaSimbolos)


os.makedirs("saida", exist_ok=True)

with open("saida/arvore_aumentada.json", "w", encoding="utf-8") as f:
    json.dump(
        resultado,
        f,
        indent=2,
        ensure_ascii=False
    )
