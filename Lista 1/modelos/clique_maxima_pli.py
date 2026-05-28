from pathlib import Path
import itertools
import pulp


def carregar_instancia(caminho="instancias/clique_maxima.txt"):
    linhas = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    vertices = linhas[0].split()
    arestas = set()
    for linha in linhas[1:]:
        i, j = linha.split()
        arestas.add(tuple(sorted((i, j))))
    return vertices, arestas


def resolver():
    vertices, arestas = carregar_instancia()

    modelo = pulp.LpProblem("Clique_Maxima_PLI", pulp.LpMaximize)

    x = pulp.LpVariable.dicts("x", vertices, cat="Binary")

    modelo += pulp.lpSum(x[v] for v in vertices), "Tamanho_da_clique"

    for i, j in itertools.combinations(vertices, 2):
        if tuple(sorted((i, j))) not in arestas:
            modelo += x[i] + x[j] <= 1, f"Nao_adjacentes_{i}_{j}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    clique = [v for v in vertices if pulp.value(x[v]) > 0.5]

    print("\n=== CLIQUE MAXIMA PLI ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Clique encontrada:", clique)
    print("Tamanho:", int(round(pulp.value(modelo.objective))))
    return modelo


if __name__ == "__main__":
    resolver()
