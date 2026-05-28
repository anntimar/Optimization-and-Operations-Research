from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/mochila.txt"):
    linhas = []
    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    capacidade = int(linhas[0])
    itens = []
    for linha in linhas[1:]:
        item, peso, valor = linha.split()
        itens.append((item, float(peso), float(valor)))
    return capacidade, itens


def resolver():
    capacidade, itens = carregar_instancia()
    n = len(itens)

    modelo = pulp.LpProblem("Mochila_0_1", pulp.LpMaximize)

    x = pulp.LpVariable.dicts("x", range(n), cat="Binary")

    modelo += pulp.lpSum(itens[i][2] * x[i] for i in range(n)), "Valor_total"
    modelo += pulp.lpSum(itens[i][1] * x[i] for i in range(n)) <= capacidade, "Capacidade"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    escolhidos = [itens[i][0] for i in range(n) if pulp.value(x[i]) > 0.5]
    peso_total = sum(itens[i][1] for i in range(n) if pulp.value(x[i]) > 0.5)
    valor_total = pulp.value(modelo.objective)

    print("\n=== MOCHILA 0-1 ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Itens escolhidos:", escolhidos)
    print("Peso total:", peso_total)
    print("Valor total:", valor_total)
    return modelo


if __name__ == "__main__":
    resolver()
