import heapq

from nodo import Nodo


# heurísticas
def heuristica_manhattan(a, b):
    """Distancia Manhattan.

    Es admisible porque en una cuadrícula con movimientos solo en 4 direcciones
    (arriba, abajo, izquierda, derecha) y costo 1 por paso, el camino real
    nunca puede ser MÁS corto que |dfila| + |dcolumna|. Los obstáculos solo
    pueden alargar el camino, nunca acortarlo, así que h nunca sobreestima.
    También es consistente: h(n) <= 1 + h(vecino).
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica_cero(a, b):
    """h = 0 para todo: A* se vuelve Dijkstra (búsqueda no informada).
    Sirve de base de comparación sobre la misma instancia."""
    return 0


# utilidades
def vecinos(cuadricula, posicion):
    """Celdas libres adyacentes (4 direcciones)."""
    filas = len(cuadricula)
    columnas = len(cuadricula[0])
    fila, columna = posicion
    for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nf, nc = fila + df, columna + dc
        if 0 <= nf < filas and 0 <= nc < columnas and cuadricula[nf][nc] == 0:
            yield (nf, nc)


def reconstruir_camino(nodo):
    """Sigue los 'padre' desde la meta hasta el inicio."""
    camino = []
    while nodo is not None:
        camino.append(nodo.posicion)
        nodo = nodo.padre
    return camino[::-1]


#  A*
def buscar(cuadricula, inicio, meta, heuristica=heuristica_manhattan):
    """A* escrito como GENERADOR: después de expandir cada nodo hace un `yield`
    con una foto del estado de la búsqueda. Así main.py puede dibujar el
    proceso paso a paso en lugar de recibir solo el resultado final.

    Cada yield es un diccionario:
        actual    : Nodo que se acaba de expandir
        frontera  : {posicion: Nodo} nodos descubiertos, aún sin expandir
        cerrados  : {posicion: Nodo} nodos ya expandidos (en orden de expansión)
        camino    : lista de posiciones inicio->meta (solo al terminar con éxito)
        terminado : True en el último yield
    """
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
    """Nodos vigentes del heap (descarta entradas viejas o ya expandidas)."""
    return {
        n.posicion: n
        for n in abiertos
        if n.posicion not in cerrados and n.g == mejor_g[n.posicion]
    }