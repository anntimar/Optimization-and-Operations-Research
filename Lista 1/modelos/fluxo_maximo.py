from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/fluxo_maximo.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    origem, destino = linhas[0].split()

    arcos = []
    vertices = set()

    for linha in linhas[1:]:
        i, j, capacidade = linha.split()
        arcos.append((i, j, float(capacidade)))
        vertices.add(i)
        vertices.add(j)

    return origem, destino, sorted(vertices), arcos


def resolver():
    origem, destino, vertices, arcos = carregar_instancia()

    modelo = pulp.LpProblem("Problema_do_Fluxo_Maximo", pulp.LpMaximize)

    f = pulp.LpVariable.dicts(
        "f",
        [(i, j) for i, j, _ in arcos],
        lowBound=0,
        cat="Continuous"
    )

    F = pulp.LpVariable("F", lowBound=0, cat="Continuous")

    modelo += F

    for i, j, capacidade in arcos:
        modelo += f[(i, j)] <= capacidade

    for v in vertices:
        entrada = pulp.lpSum(
            f[(i, j)]
            for i, j, _ in arcos
            if j == v
        )

        saida = pulp.lpSum(
            f[(i, j)]
            for i, j, _ in arcos
            if i == v
        )

        if v == origem:
            modelo += saida - entrada == F
        elif v == destino:
            modelo += entrada - saida == F
        else:
            modelo += entrada == saida

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== PROBLEMA DO FLUXO MAXIMO ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Fluxo maximo:", pulp.value(F))

    for i, j, _ in arcos:
        valor = pulp.value(f[(i, j)])
        if valor > 0:
            print(f"{i} -> {j}: {valor}")

    return modelo


if __name__ == "__main__":
    resolver()