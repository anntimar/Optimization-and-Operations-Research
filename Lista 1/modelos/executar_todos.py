from mochila_01 import resolver as resolver_mochila
from bin_packing_pli import resolver as resolver_bin_packing
from caminho_minimo_pli import resolver as resolver_caminho_minimo
from clique_maxima_pli import resolver as resolver_clique_maxima
from tsp_pli import resolver as resolver_tsp
from cvrp_pli import resolver as resolver_cvrp
from racao import resolver as resolver_racao
from dieta import resolver as resolver_dieta
from transporte import resolver as resolver_transporte

if __name__ == "__main__":
    resolver_mochila()
    resolver_bin_packing()
    resolver_caminho_minimo()
    resolver_clique_maxima()
    resolver_tsp()
    resolver_cvrp()
    resolver_racao()
    resolver_dieta()
    resolver_transporte()
