class Nodo:
    """Un nodo de la búsqueda: una celda de la cuadrícula más su 'historial'.

    posicion : (fila, columna) de la celda
    padre    : nodo desde el que llegamos (sirve para reconstruir el camino)
    g        : costo real recorrido desde el inicio hasta este nodo
    h        : estimación heurística del costo restante hasta la meta
    f        : g + h, la prioridad con la que A* elige qué nodo expandir
    """

    def __init__(self, posicion, padre=None, g=0, h=0):
        self.posicion = posicion
        self.padre = padre
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, otro):
        # heapq saca el nodo "menor": primero el de menor f.
        # Desempate: el de menor h (el que está más cerca de la meta),
        # así A* no se dispersa entre caminos con el mismo f.
        if self.f != otro.f:
            return self.f < otro.f
        return self.h < otro.h

    def __repr__(self):
        return f"Nodo({self.posicion}, g={self.g}, h={self.h}, f={self.f})"