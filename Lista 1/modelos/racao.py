from pathlib import Path
import pulp


def carregar_instancia(caminho="instancias/racao.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    produtos = []

    for i in range(2):
        nome, cereais, carne, preco = linhas[i].split()
        produtos.append({
            "nome": nome,
            "cereais": float(cereais),
            "carne": float(carne),
            "preco": float(preco),
        })

    custo_cereal = float(linhas[2].split()[1])
    custo_carne = float(linhas[3].split()[1])

    disponibilidade_cereais = float(linhas[4].split()[1])
    disponibilidade_carne = float(linhas[5].split()[1])

    return produtos, custo_cereal, custo_carne, disponibilidade_cereais, disponibilidade_carne


def resolver():
    produtos, custo_cereal, custo_carne, disponibilidade_cereais, disponibilidade_carne = carregar_instancia()

    modelo = pulp.LpProblem("Problema_da_Racao", pulp.LpMaximize)

    nomes_produtos = [produto["nome"] for produto in produtos]

    x = pulp.LpVariable.dicts(
        "x",
        nomes_produtos,
        lowBound=0,
        cat="Integer"
    )

    lucro_unitario = {}

    for produto in produtos:
        nome = produto["nome"]
        custo_insumos = (
            produto["cereais"] * custo_cereal
            + produto["carne"] * custo_carne
        )
        lucro_unitario[nome] = produto["preco"] - custo_insumos

    modelo += pulp.lpSum(
        lucro_unitario[produto["nome"]] * x[produto["nome"]]
        for produto in produtos
    ), "Lucro_total"

    modelo += pulp.lpSum(
        produto["cereais"] * x[produto["nome"]]
        for produto in produtos
    ) <= disponibilidade_cereais, "Disponibilidade_cereais"

    modelo += pulp.lpSum(
        produto["carne"] * x[produto["nome"]]
        for produto in produtos
    ) <= disponibilidade_carne, "Disponibilidade_carne"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== PROBLEMA DA RACAO ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Lucro total:", pulp.value(modelo.objective))

    for produto in produtos:
        nome = produto["nome"]
        print(f"{nome}: {pulp.value(x[nome])}")

    return modelo


if __name__ == "__main__":
    resolver()