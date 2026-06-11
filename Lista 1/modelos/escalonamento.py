from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/escalonamento.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    demanda = [int(valor) for valor in linhas[0].split()]

    return demanda


def resolver():
    demanda = carregar_instancia()

    dias = range(7)

    modelo = pulp.LpProblem("Escalonamento_de_Horarios", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        dias,
        lowBound=0,
        cat="Integer"
    )

    modelo += pulp.lpSum(
        x[i]
        for i in dias
    )

    for d in dias:
        modelo += pulp.lpSum(
            x[i]
            for i in dias
            if (d - i) % 7 in [0, 1, 2, 3]
        ) >= demanda[d]

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== ESCALONAMENTO DE HORARIOS ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Numero minimo de funcionarios:", pulp.value(modelo.objective))

    for i in dias:
        print(f"Comecam no dia {i + 1}: {pulp.value(x[i])}")

    return modelo


if __name__ == "__main__":
    resolver()