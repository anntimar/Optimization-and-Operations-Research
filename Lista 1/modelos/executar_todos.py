from mochila_01 import resolver as resolver_mochila
from bin_packing_pli import resolver as resolver_bin_packing
from caminho_minimo_pli import resolver as resolver_caminho_minimo
from clique_maxima_pli import resolver as resolver_clique_maxima
from tsp_pli import resolver as resolver_tsp
from cvrp_pli import resolver as resolver_cvrp


if __name__ == "__main__":
    resolver_mochila()
    resolver_bin_packing()
    resolver_caminho_minimo()
    resolver_clique_maxima()
    resolver_tsp()
    resolver_cvrp()
