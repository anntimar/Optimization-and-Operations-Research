from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/caminho_minimo.txt"):
    linhas = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    origem, destino = linhas[0].split()
    arcos = []
    vertices = {origem, destino}
    for linha in linhas[1:]:
        i, j, custo = linha.split()
        arcos.append((i, j, float(custo)))
        vertices.update([i, j])
    return origem, destino, sorted(vertices), arcos


def resolver():
    origem, destino, vertices, arcos = carregar_instancia()

    modelo = pulp.LpProblem("Caminho_Minimo_PLI", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", [(i, j) for i, j, _ in arcos], cat="Binary")

    modelo += pulp.lpSum(custo * x[(i, j)] for i, j, custo in arcos), "Custo_total"

    for v in vertices:
        saida = pulp.lpSum(x[(i, j)] for i, j, _ in arcos if i == v)
        entrada = pulp.lpSum(x[(i, j)] for i, j, _ in arcos if j == v)

        if v == origem:
            modelo += saida - entrada == 1, f"Fluxo_origem_{v}"
        elif v == destino:
            modelo += saida - entrada == -1, f"Fluxo_destino_{v}"
        else:
            modelo += saida - entrada == 0, f"Conservacao_{v}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    caminho_arcos = [(i, j) for i, j, _ in arcos if pulp.value(x[(i, j)]) > 0.5]

    print("\n=== CAMINHO MINIMO PLI ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Origem:", origem)
    print("Destino:", destino)
    print("Arcos usados:", caminho_arcos)
    print("Custo total:", pulp.value(modelo.objective))
    return modelo


if __name__ == "__main__":
    resolver()
