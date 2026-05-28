from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/tsp.txt"):
    matriz = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                matriz.append([float(x) for x in linha.split()])
    return matriz


def resolver():
    custo = carregar_instancia()
    n = len(custo)
    cidades = range(n)

    modelo = pulp.LpProblem("TSP_PLI_MTZ", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        [(i, j) for i in cidades for j in cidades if i != j],
        cat="Binary"
    )

    # Variaveis auxiliares MTZ para eliminar subciclos
    u = pulp.LpVariable.dicts("u", cidades, lowBound=0, upBound=n - 1, cat="Continuous")

    modelo += pulp.lpSum(custo[i][j] * x[(i, j)] for i in cidades for j in cidades if i != j), "Custo_total"

    for i in cidades:
        modelo += pulp.lpSum(x[(i, j)] for j in cidades if i != j) == 1, f"Sai_da_cidade_{i}"

    for j in cidades:
        modelo += pulp.lpSum(x[(i, j)] for i in cidades if i != j) == 1, f"Entra_na_cidade_{j}"

    modelo += u[0] == 0, "Fixa_cidade_inicial"

    for i in cidades:
        for j in cidades:
            if i != j and i != 0 and j != 0:
                modelo += u[i] - u[j] + n * x[(i, j)] <= n - 1, f"MTZ_{i}_{j}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    arcos = [(i, j) for i in cidades for j in cidades if i != j and pulp.value(x[(i, j)]) > 0.5]

    print("\n=== TSP PLI ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Arcos da rota:", arcos)
    print("Custo total:", pulp.value(modelo.objective))
    return modelo


if __name__ == "__main__":
    resolver()
