from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/bin_packing.txt"):
    linhas = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    capacidade = float(linhas[0])
    itens = []
    for linha in linhas[1:]:
        item, tamanho = linha.split()
        itens.append((item, float(tamanho)))
    return capacidade, itens


def resolver():
    capacidade, itens = carregar_instancia()
    n = len(itens)
    bins = range(n)  # no pior caso, cada item usa um bin

    modelo = pulp.LpProblem("Bin_Packing_PLI", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", (range(n), bins), cat="Binary")
    y = pulp.LpVariable.dicts("y", bins, cat="Binary")

    modelo += pulp.lpSum(y[j] for j in bins), "Numero_de_bins"

    for i in range(n):
        modelo += pulp.lpSum(x[i][j] for j in bins) == 1, f"Item_{i}_em_um_bin"

    for j in bins:
        modelo += pulp.lpSum(itens[i][1] * x[i][j] for i in range(n)) <= capacidade * y[j], f"Capacidade_bin_{j}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== BIN PACKING PLI ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Bins usados:", int(round(pulp.value(modelo.objective))))

    for j in bins:
        if pulp.value(y[j]) > 0.5:
            itens_bin = [itens[i][0] for i in range(n) if pulp.value(x[i][j]) > 0.5]
            carga = sum(itens[i][1] for i in range(n) if pulp.value(x[i][j]) > 0.5)
            print(f"Bin {j}: itens {itens_bin}, carga {carga}/{capacidade}")
    return modelo


if __name__ == "__main__":
    resolver()
