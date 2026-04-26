import sys
import time
import random
import copy


CAPACIDADE = 1.0
EPS = 1e-9


# ============================================================
# LEITURA DA INSTÂNCIA
# ============================================================

def ler_instancia(nome_arquivo):
    """
    Lê uma instância do problema Bin Packing.

    Formato esperado:
    Primeira linha: quantidade de itens n
    Linhas seguintes: tamanho de cada item, entre 0 e 1
    """
    with open(nome_arquivo, "r") as arquivo:
        linhas = [linha.strip() for linha in arquivo if linha.strip()]

    n = int(linhas[0])
    itens = [float(valor) for valor in linhas[1:]]

    if len(itens) != n:
        raise ValueError("A quantidade de itens no arquivo não corresponde ao valor informado na primeira linha.")

    for item in itens:
        if item <= 0 or item > CAPACIDADE:
            raise ValueError(f"Item inválido encontrado: {item}")

    return itens


# ============================================================
# FUNÇÕES BÁSICAS DA SOLUÇÃO
# ============================================================

def carga_bin(bin_atual):
    return sum(bin_atual)


def folga_bin(bin_atual):
    return CAPACIDADE - carga_bin(bin_atual)


def avaliar(solucao):
    """
    Função de avaliação principal.

    Como o objetivo do Bin Packing é minimizar o número de bins,
    o custo principal é a quantidade de recipientes utilizados.

    Também usamos um segundo critério para desempate:
    quanto menor a soma das folgas quadráticas, melhor a compactação.
    """
    qtd_bins = len(solucao)

    desperdicio_quadratico = sum(folga_bin(b) ** 2 for b in solucao)

    return qtd_bins, desperdicio_quadratico


def solucao_valida(solucao):
    """
    Verifica se nenhuma capacidade foi violada.
    """
    for b in solucao:
        if carga_bin(b) > CAPACIDADE + EPS:
            return False
    return True


def limpar_solucao(solucao):
    """
    Remove bins vazios e ordena os bins por carga decrescente.
    Isso ajuda a manter a solução mais organizada.
    """
    solucao = [b for b in solucao if len(b) > 0]
    solucao.sort(key=lambda b: carga_bin(b), reverse=True)
    return solucao


def copiar_solucao(solucao):
    return [b[:] for b in solucao]


# ============================================================
# CONSTRUÇÃO INICIAL
# ============================================================

def first_fit_decreasing(itens):
    """
    Heurística construtiva First Fit Decreasing.

    Os itens são ordenados do maior para o menor.
    Cada item é colocado no primeiro bin em que couber.
    """
    itens_ordenados = sorted(itens, reverse=True)
    solucao = []

    for item in itens_ordenados:
        inserido = False

        for b in solucao:
            if carga_bin(b) + item <= CAPACIDADE + EPS:
                b.append(item)
                inserido = True
                break

        if not inserido:
            solucao.append([item])

    return limpar_solucao(solucao)


def best_fit_decreasing(itens):
    """
    Heurística construtiva Best Fit Decreasing.

    Os itens são ordenados do maior para o menor.
    Cada item é colocado no bin em que deixar a menor folga possível.
    """
    itens_ordenados = sorted(itens, reverse=True)
    solucao = []

    for item in itens_ordenados:
        melhor_indice = None
        menor_folga = float("inf")

        for i, b in enumerate(solucao):
            nova_carga = carga_bin(b) + item

            if nova_carga <= CAPACIDADE + EPS:
                folga = CAPACIDADE - nova_carga

                if folga < menor_folga:
                    menor_folga = folga
                    melhor_indice = i

        if melhor_indice is None:
            solucao.append([item])
        else:
            solucao[melhor_indice].append(item)

    return limpar_solucao(solucao)


def construir_solucao_inicial(itens):
    """
    Gera mais de uma solução inicial e escolhe a melhor.
    """
    s1 = first_fit_decreasing(itens)
    s2 = best_fit_decreasing(itens)

    if avaliar(s1) <= avaliar(s2):
        return s1

    return s2


# ============================================================
# VIZINHANÇA 1: MOVER UM ITEM
# ============================================================

def vizinhanca_mover_item(solucao):
    """
    Tenta mover um item de um bin para outro.

    Exemplo:
    Bin A: [0.6, 0.3]
    Bin B: [0.4]

    Move 0.3 para o Bin B:
    Bin A: [0.6]
    Bin B: [0.4, 0.3]
    """
    melhor = copiar_solucao(solucao)
    melhor_avaliacao = avaliar(melhor)

    for i in range(len(solucao)):
        for j in range(len(solucao)):
            if i == j:
                continue

            for pos_item in range(len(solucao[i])):
                item = solucao[i][pos_item]

                if carga_bin(solucao[j]) + item <= CAPACIDADE + EPS:
                    vizinho = copiar_solucao(solucao)

                    item_movido = vizinho[i].pop(pos_item)
                    vizinho[j].append(item_movido)

                    vizinho = limpar_solucao(vizinho)

                    if avaliar(vizinho) < melhor_avaliacao:
                        melhor = vizinho
                        melhor_avaliacao = avaliar(vizinho)

    return melhor


# ============================================================
# VIZINHANÇA 2: TROCAR DOIS ITENS ENTRE BINS
# ============================================================

def vizinhanca_trocar_itens(solucao):
    """
    Tenta trocar um item de um bin com um item de outro bin.

    Essa vizinhança é útil quando mover um único item não melhora,
    mas uma troca pode liberar espaço e compactar melhor a solução.
    """
    melhor = copiar_solucao(solucao)
    melhor_avaliacao = avaliar(melhor)

    for i in range(len(solucao)):
        for j in range(i + 1, len(solucao)):
            for pos_i in range(len(solucao[i])):
                for pos_j in range(len(solucao[j])):
                    item_i = solucao[i][pos_i]
                    item_j = solucao[j][pos_j]

                    carga_i = carga_bin(solucao[i])
                    carga_j = carga_bin(solucao[j])

                    nova_carga_i = carga_i - item_i + item_j
                    nova_carga_j = carga_j - item_j + item_i

                    if nova_carga_i <= CAPACIDADE + EPS and nova_carga_j <= CAPACIDADE + EPS:
                        vizinho = copiar_solucao(solucao)

                        vizinho[i][pos_i] = item_j
                        vizinho[j][pos_j] = item_i

                        vizinho = limpar_solucao(vizinho)

                        if avaliar(vizinho) < melhor_avaliacao:
                            melhor = vizinho
                            melhor_avaliacao = avaliar(vizinho)

    return melhor


# ============================================================
# VIZINHANÇA 3: TENTAR ESVAZIAR UM BIN
# ============================================================

def tentar_esvaziar_bin(solucao):
    """
    Escolhe bins menos carregados e tenta redistribuir todos os seus itens
    nos outros bins.

    Se conseguir, aquele bin é removido da solução.
    """
    melhor = copiar_solucao(solucao)
    melhor_avaliacao = avaliar(melhor)

    indices_ordenados = sorted(
        range(len(solucao)),
        key=lambda i: carga_bin(solucao[i])
    )

    for indice_bin in indices_ordenados:
        vizinho = copiar_solucao(solucao)

        itens_para_realocar = sorted(vizinho[indice_bin], reverse=True)
        vizinho[indice_bin] = []

        sucesso = True

        for item in itens_para_realocar:
            melhor_destino = None
            menor_folga = float("inf")

            for j in range(len(vizinho)):
                if j == indice_bin:
                    continue

                nova_carga = carga_bin(vizinho[j]) + item

                if nova_carga <= CAPACIDADE + EPS:
                    folga = CAPACIDADE - nova_carga

                    if folga < menor_folga:
                        menor_folga = folga
                        melhor_destino = j

            if melhor_destino is None:
                sucesso = False
                break
            else:
                vizinho[melhor_destino].append(item)

        if sucesso:
            vizinho = limpar_solucao(vizinho)

            if avaliar(vizinho) < melhor_avaliacao:
                melhor = vizinho
                melhor_avaliacao = avaliar(vizinho)

    return melhor


# ============================================================
# VIZINHANÇA 4: COMPACTAÇÃO
# ============================================================

def compactar_solucao(solucao):
    """
    Reinsere todos os itens usando Best Fit Decreasing.

    Essa etapa serve como uma compactação da solução atual.
    """
    todos_itens = []

    for b in solucao:
        todos_itens.extend(b)

    return best_fit_decreasing(todos_itens)


# ============================================================
# BUSCA LOCAL COM MÚLTIPLAS VIZINHANÇAS
# ============================================================

def busca_local_vnd(solucao):
    """
    Variable Neighborhood Descent.

    A busca local percorre diferentes vizinhanças.
    Sempre que uma delas melhora a solução, o processo volta para
    a primeira vizinhança.
    """
    atual = copiar_solucao(solucao)

    melhorou = True

    while melhorou:
        melhorou = False

        vizinhancas = [
            vizinhanca_mover_item,
            vizinhanca_trocar_itens,
            tentar_esvaziar_bin,
            compactar_solucao
        ]

        for vizinhanca in vizinhancas:
            vizinho = vizinhanca(atual)

            if avaliar(vizinho) < avaliar(atual):
                atual = vizinho
                melhorou = True
                break

    return atual


# ============================================================
# PERTURBAÇÃO
# ============================================================

def perturbar_solucao(solucao, intensidade=0.15):
    """
    Faz uma perturbação na solução para escapar de ótimos locais.

    A ideia é remover alguns bins da solução e reinserir seus itens.
    """
    nova = copiar_solucao(solucao)

    qtd_bins = len(nova)

    if qtd_bins <= 2:
        return nova

    qtd_remover = max(1, int(qtd_bins * intensidade))

    indices = list(range(qtd_bins))
    random.shuffle(indices)

    bins_removidos = sorted(indices[:qtd_remover], reverse=True)

    itens_removidos = []

    for indice in bins_removidos:
        itens_removidos.extend(nova[indice])
        del nova[indice]

    random.shuffle(itens_removidos)

    for item in itens_removidos:
        melhor_destino = None
        menor_folga = float("inf")

        for i, b in enumerate(nova):
            nova_carga = carga_bin(b) + item

            if nova_carga <= CAPACIDADE + EPS:
                folga = CAPACIDADE - nova_carga

                if folga < menor_folga:
                    menor_folga = folga
                    melhor_destino = i

        if melhor_destino is None:
            nova.append([item])
        else:
            nova[melhor_destino].append(item)

    return limpar_solucao(nova)


# ============================================================
# META-HEURÍSTICA PRINCIPAL
# ============================================================

def iterated_local_search(itens, tempo_limite):
    """
    Meta-heurística principal.

    Combina:
    - solução inicial;
    - busca local;
    - perturbação;
    - aceitação de soluções melhores;
    - critério de parada por tempo.
    """
    inicio = time.time()

    solucao_atual = construir_solucao_inicial(itens)
    solucao_atual = busca_local_vnd(solucao_atual)

    melhor_solucao = copiar_solucao(solucao_atual)

    iteracao = 0
    sem_melhora = 0

    while time.time() - inicio < tempo_limite:
        iteracao += 1

        if sem_melhora < 20:
            intensidade = 0.10
        elif sem_melhora < 50:
            intensidade = 0.20
        else:
            intensidade = 0.35

        candidata = perturbar_solucao(solucao_atual, intensidade)
        candidata = busca_local_vnd(candidata)

        if avaliar(candidata) < avaliar(melhor_solucao):
            melhor_solucao = copiar_solucao(candidata)
            solucao_atual = copiar_solucao(candidata)
            sem_melhora = 0
        else:
            sem_melhora += 1

            # Aceitação ocasional para diversificação
            if random.random() < 0.05:
                solucao_atual = copiar_solucao(candidata)

        if sem_melhora > 100:
            solucao_atual = construir_solucao_inicial(itens)
            random.shuffle(itens)
            solucao_atual = busca_local_vnd(solucao_atual)
            sem_melhora = 0

    return melhor_solucao, iteracao


# ============================================================
# IMPRESSÃO DA SOLUÇÃO
# ============================================================

def imprimir_solucao(solucao, tempo_execucao, iteracoes):
    print("=" * 60)
    print("RESULTADO FINAL - BIN PACKING")
    print("=" * 60)

    print(f"Quantidade de bins utilizados: {len(solucao)}")
    print(f"Tempo de execução: {tempo_execucao:.4f} segundos")
    print(f"Iterações realizadas: {iteracoes}")
    print()

    desperdicio_total = sum(folga_bin(b) for b in solucao)
    ocupacao_media = sum(carga_bin(b) for b in solucao) / len(solucao)

    print(f"Desperdício total: {desperdicio_total:.4f}")
    print(f"Ocupação média dos bins: {ocupacao_media:.4f}")
    print()

    print("Distribuição dos itens:")
    print("-" * 60)

    for i, b in enumerate(solucao, start=1):
        carga = carga_bin(b)
        folga = folga_bin(b)

        itens_formatados = ", ".join(f"{item:.2f}" for item in b)

        print(f"Bin {i:03d} | carga = {carga:.4f} | folga = {folga:.4f} | itens: [{itens_formatados}]")

    print("=" * 60)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    if len(sys.argv) < 3:
        print("Uso correto:")
        print("python bin_packing_metaheuristica.py instancia.txt tempo_limite")
        print()
        print("Exemplo:")
        print("python bin_packing_metaheuristica.py instancia_grande.txt 30")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    tempo_limite = float(sys.argv[2])

    random.seed()

    itens = ler_instancia(nome_arquivo)

    inicio = time.time()

    melhor_solucao, iteracoes = iterated_local_search(itens, tempo_limite)

    fim = time.time()

    if not solucao_valida(melhor_solucao):
        print("Erro: a solução encontrada é inválida.")
        sys.exit(1)

    imprimir_solucao(melhor_solucao, fim - inicio, iteracoes)


if __name__ == "__main__":
    main()