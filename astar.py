import heapq

from nodo import Nodo


# heurísticas
def heuristica_manhattan(a, b):
   
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica_cero(a, b):
    
    return 0


# utilidades
def vecinos(cuadricula, posicion):
    filas = len(cuadricula)
    columnas = len(cuadricula[0])
    fila, columna = posicion
    for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nf, nc = fila + df, columna + dc
        if 0 <= nf < filas and 0 <= nc < columnas and cuadricula[nf][nc] == 0:
            yield (nf, nc)


def reconstruir_camino(nodo):
    camino = []
    while nodo is not None:
        camino.append(nodo.posicion)
        nodo = nodo.padre
    return camino[::-1]


#  A*
def buscar(cuadricula, inicio, meta, heuristica=heuristica_manhattan):
    abiertos = [Nodo(inicio, None, 0, heuristica(inicio, meta))]  # heap por f
    mejor_g = {inicio: 0}   # menor g conocido para cada celda
    cerrados = {}           # el dict conserva el orden de expansión

    while abiertos:
        actual = heapq.heappop(abiertos)

        # Entradas viejas: una celda pudo entrar al heap varias veces
        if actual.posicion in cerrados:
            continue
        cerrados[actual.posicion] = actual

        if actual.posicion == meta:
            yield {
                "actual": actual,
                "frontera": _frontera(abiertos, cerrados, mejor_g),
                "cerrados": cerrados,
                "camino": reconstruir_camino(actual),
                "terminado": True,
            }
            return

        for vecino in vecinos(cuadricula, actual.posicion):
            if vecino in cerrados:
                continue
            g_nuevo = actual.g + 1
            if g_nuevo < mejor_g.get(vecino, float("inf")):
                mejor_g[vecino] = g_nuevo
                heapq.heappush(
                    abiertos, Nodo(vecino, actual, g_nuevo, heuristica(vecino, meta))
                )

        yield {
            "actual": actual,
            "frontera": _frontera(abiertos, cerrados, mejor_g),
            "cerrados": cerrados,
            "camino": None,
            "terminado": False,
        }

    # Se vació la frontera sin llegar a la meta: no hay camino
    yield {
        "actual": None,
        "frontera": {},
        "cerrados": cerrados,
        "camino": None,
        "terminado": True,
    }


def _frontera(abiertos, cerrados, mejor_g):
    return {
        n.posicion: n
        for n in abiertos
        if n.posicion not in cerrados and n.g == mejor_g[n.posicion]
    }