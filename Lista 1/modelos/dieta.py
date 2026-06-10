from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/dieta.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    n = int(linhas[0])
    custos = [float(valor) for valor in linhas[1].split()]

    vitaminas = []

    for linha in linhas[2:]:
        partes = linha.split()
        nome = partes[0]
        minimo = float(partes[1])
        coeficientes = [float(valor) for valor in partes[2:]]

        if len(coeficientes) != n:
            raise ValueError(f"A vitamina {nome} nao possui {n} coeficientes.")

        vitaminas.append({
            "nome": nome,
            "minimo": minimo,
            "coeficientes": coeficientes,
        })

    if len(custos) != n:
        raise ValueError("Quantidade de custos diferente do numero de ingredientes.")

    return n, custos, vitaminas


def resolver():
    n, custos, vitaminas = carregar_instancia()
    ingredientes = range(n)

    modelo = pulp.LpProblem("Problema_da_Dieta", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        ingredientes,
        lowBound=0,
        cat="Continuous"
    )

    modelo += pulp.lpSum(
        custos[i] * x[i]
        for i in ingredientes
    ), "Custo_total"

    for vitamina in vitaminas:
        modelo += pulp.lpSum(
            vitamina["coeficientes"][i] * x[i]
            for i in ingredientes
        ) >= vitamina["minimo"], f"Minimo_vitamina_{vitamina['nome']}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== PROBLEMA DA DIETA ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Custo minimo:", pulp.value(modelo.objective))

    for i in ingredientes:
        print(f"Ingrediente {i + 1}: {pulp.value(x[i]):.4f}")

    return modelo


if __name__ == "__main__":
    resolver()