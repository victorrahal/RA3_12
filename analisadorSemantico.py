# Integrantes do grupo:
# João Henrique Tomaz Dutra - Jhtomaz
# Lucas Balint Vilar - lucasdxl
# Paulo Henrique Eidi Mino - phmino
# Victor Rahal Basseto - victorrahal
# Professor: FRANK COELHO DE ALCANTARA
# Nome do grupo no Canvas: RA3_12

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from prepararEntradaSemantica import prepararEntradaSemantica
from construirTabelaSimbolos import (
    construirTabelaSimbolos,
    salvarTabelaSimbolos,
    salvarTabelaSimbolosMarkdown,
    salvarErrosDeclaracao,
)
from verificarTipos import verificarTipos
from gerarArvoreAtribuida import (
    gerarArvoreAtribuida,
    salvarArvoreAtribuida,
    salvarArvoreAtribuidaMarkdown,
)
from gerarAssembly import gerarAssembly

def _garantir_saida():
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida")
    os.makedirs(pasta, exist_ok=True)

def main():
    if len(sys.argv) < 2:
        print("Uso: python AnalisadorSemantico.py <arquivo_de_teste>")
        sys.exit(1)
    arquivo = sys.argv[1]
    _garantir_saida()
    try:
        entrada = prepararEntradaSemantica(arquivo)
    except FileNotFoundError as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO LÉXICO/SINTÁTICO] {e}")
        sys.exit(1)
    print(f"\n=== Analisando: {arquivo} ===")
    print(f"[Léxico]    OK — {len(entrada['tokens'])} tokens")
    print("[Sintático] OK")
    arvore_base  = entrada["arvore_base_semantica"]
    arvore_simpl = entrada["arvore_simplificada"]
    tabelaSimbolos = construirTabelaSimbolos(arvore_base)
    tipos = verificarTipos(arvore_base, tabelaSimbolos)
    todos_erros = tipos.get("erros", [])
    salvarTabelaSimbolos(tabelaSimbolos)
    salvarTabelaSimbolosMarkdown(tabelaSimbolos, arquivo_origem=arquivo)
    salvarErrosDeclaracao({"erros": todos_erros})
    if todos_erros:
        print(f"[Semântico] {len(todos_erros)} erro(s) encontrado(s):")
        for e in todos_erros:
            print(f"  [{e.get('codigo')}] linha {e.get('linha')}: {e.get('mensagem')}")
    else:
        print("[Semântico] OK — nenhum erro encontrado")
    arvoreAtribuida = gerarArvoreAtribuida(arvore_simpl, tabelaSimbolos, tipos)
    salvarArvoreAtribuida(arvoreAtribuida)
    salvarArvoreAtribuidaMarkdown(arvoreAtribuida, arquivo_origem=arquivo)
    if todos_erros:
        print("\n[Assembly]  IGNORADO — erros semânticos impedem a geração")
    else:
        gerarAssembly(arvoreAtribuida)
        print("[Assembly]  OK → saida/Assembly.s")
    print("\nArtefatos gerados em saida/:")
    print("  tabela_simbolos.json + tabela_simbolos.md")
    print("  arvore_atribuida.json + arvore_atribuida.md")
    print("  erros_declaracao.json")
    if not todos_erros:
        print("  Assembly.s")

if __name__ == "__main__":
    main()
