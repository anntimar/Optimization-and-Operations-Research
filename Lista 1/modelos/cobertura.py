from pathlib import Path
import pulp

def carregar_instancia(caminho="instancias/cobertura.txt"):
    linhas = []

    with open(Path(__file__).parent / caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    bairros = linhas[0].split()

    cobertura = {}

    for linha in linhas[1:]:
        partes = linha.split()
        candidato = partes[0]
        cobertos = partes[1:]
        cobertura[candidato] = cobertos

    return bairros, cobertura


def resolver():
    bairros, cobertura = carregar_instancia()

    modelo = pulp.LpProblem("Problema_de_Cobertura", pulp.LpMinimize)

    y = pulp.LpVariable.dicts(
        "y",
        bairros,
        cat="Binary"
    )

    modelo += pulp.lpSum(
        y[j]
        for j in bairros
    )

    for bairro in bairros:
        modelo += pulp.lpSum(
            y[candidato]
            for candidato in bairros
            if bairro in cobertura[candidato]
        ) >= 1

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    print("\n=== PROBLEMA DE COBERTURA ===")
    print("Status:", pulp.LpStatus[modelo.status])
    print("Numero minimo de escolas:", pulp.value(modelo.objective))

    escolhidos = [
        bairro
        for bairro in bairros
        if pulp.value(y[bairro]) > 0.5
    ]

    print("Construir escolas nos bairros:", escolhidos)

    return modelo


if __name__ == "__main__":
    resolver()