from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/cvrp.txt"):
    linhas = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    capacidade, numero_veiculos, deposito = map(int, linhas[0].split())
    demandas = [float(x) for x in linhas[1].split()]
    matriz = [[float(x) for x in linha.split()] for linha in linhas[2:]]
    return capacidade, numero_veiculos, deposito, demandas, matriz


def resolver():
    capacidade, numero_veiculos, deposito, demandas, custo = carregar_instancia()

    n = len(demandas)
    nos = range(n)
    clientes = [i for i in nos if i != deposito]

    modelo = pulp.LpProblem("CVRP_PLI_MTZ", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        [(i, j) for i in nos for j in nos if i != j],
        cat="Binary"
    )

    # u[i] representa a carga acumulada ao chegar ao cliente i
    u = pulp.LpVariable.dicts(
        "u",
        clientes,
        lowBound=0,
        upBound=capacidade,
        cat="Continuous"
    )

    modelo += pulp.lpSum(custo[i][j] * x[(i, j)] for i in nos for j in nos if i != j), "Custo_total"

    # Cada cliente deve ter exatamente uma entrada e uma saída
    for i in clientes:
        modelo += pulp.lpSum(x[(i, j)] for j in nos if j != i) == 1, f"Sai_cliente_{i}"
        modelo += pulp.lpSum(x[(j, i)] for j in nos if j != i) == 1, f"Entra_cliente_{i}"

    # No máximo K veículos saem e retornam ao depósito
    modelo += pulp.lpSum(x[(deposito, j)] for j in clientes) <= numero_veiculos, "Limite_saida_deposito"
    modelo += pulp.lpSum(x[(i, deposito)] for i in clientes) <= numero_veiculos, "Limite_retorno_deposito"
    modelo += pulp.lpSum(x[(deposito, j)] for j in clientes) == pulp.lpSum(x[(i, deposito)] for i in clientes), "Balanceia_deposito"

    # Limites de carga ao atender cada cliente
    for i in clientes:
        modelo += u[i] >= demandas[i], f"Carga_minima_{i}"
        modelo += u[i] <= capacidade, f"Carga_maxima_{i}"

    # Restrições MTZ para eliminar subciclos e respeitar capacidade
    for i in clientes:
        for j in clientes:
            if i != j:
                modelo += (
                    u[i] - u[j] + capacidade * x[(i, j)]
                    <= capacidade - demandas[j]
                ), f"MTZ_CVRP_{i}_{j}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== CVRP PLI ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Custo total:", pulp.value(modelo.objective))

    arcos = [(i, j) for i in nos for j in nos if i != j and pulp.value(x[(i, j)]) > 0.5]
    print("Arcos usados:", arcos)

    # Reconstrói as rotas a partir dos arcos que saem do depósito
    rotas = []
    for _, inicio in [a for a in arcos if a[0] == deposito]:
        rota = [deposito, inicio]
        atual = inicio
        while atual != deposito:
            proximos = [j for i, j in arcos if i == atual]
            if not proximos:
                break
            atual = proximos[0]
            rota.append(atual)
        rotas.append(rota)

    for idx, rota in enumerate(rotas, start=1):
        carga = sum(demandas[i] for i in rota if i != deposito)
        print(f"Rota {idx}: {rota}, carga {carga}/{capacidade}")

    return modelo


if __name__ == "__main__":
    resolver()
