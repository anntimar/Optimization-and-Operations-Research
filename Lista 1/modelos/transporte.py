from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/transporte.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    oferta = [float(valor) for valor in linhas[0].split()]
    demanda = [float(valor) for valor in linhas[1].split()]
    custos = [[float(valor) for valor in linha.split()] for linha in linhas[2:]]

    return oferta, demanda, custos


def resolver():
    oferta, demanda, custos = carregar_instancia()

    fabricas = range(len(oferta))
    depositos = range(len(demanda))

    modelo = pulp.LpProblem("Problema_do_Transporte", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        (fabricas, depositos),
        lowBound=0,
        cat="Continuous"
    )

    modelo += pulp.lpSum(
        custos[i][j] * x[i][j]
        for i in fabricas
        for j in depositos
    )

    for i in fabricas:
        modelo += pulp.lpSum(
            x[i][j]
            for j in depositos
        ) <= oferta[i]

    for j in depositos:
        modelo += pulp.lpSum(
            x[i][j]
            for i in fabricas
        ) == demanda[j]

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== PROBLEMA DO TRANSPORTE ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Custo minimo:", pulp.value(modelo.objective))

    for i in fabricas:
        for j in depositos:
            valor = pulp.value(x[i][j])
            if valor > 0:
                print(f"Fabrica {i + 1} -> Deposito {j + 1}: {valor}")

    return modelo


if __name__ == "__main__":
    resolver()