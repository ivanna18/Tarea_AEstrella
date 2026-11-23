# Búsqueda A* sobre una cuadrícula

Implementación del algoritmo **A\*** en Python con visualización paso a paso en pygame.
Tarea "Elige tu Algoritmo" — Opción A.

video: https://drive.google.com/drive/folders/1VV-RNx9cyixzawRvxRyAzeR-MJ4LxdKi?usp=share_link

## Estructura

```
.
├── main.py           # interfaz pygame: cuadrícula, obstáculos, animación y panel de resultados
├── astar.py          # algoritmo A* (generador), heurísticas y reconstrucción del camino
├── nodo.py           # clase Nodo: posición, padre, g, h, f
├── requirements.txt
└── README.md
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python main.py
```

## Controles

| Tecla / acción | Efecto |
|---|---|
| Clic izquierdo (o arrastrar) | Poner / quitar obstáculos |
| `ESPACIO` | Ejecutar A* (heurística Manhattan) |
| `D` | Ejecutar Dijkstra (h = 0), búsqueda no informada para comparar |
| `V` | Mostrar g, h y f en cada celda |
| `P` | Pausar / reanudar |
| `→` | Avanzar un solo paso |
| `C` | Limpiar la búsqueda (conserva obstáculos) |
| `R` | Reiniciar todo |
| `+` / `-` | Cambiar la velocidad de la animación |

**Colores:** verde = inicio, rojo = meta, negro = obstáculo, azul = frontera (descubiertos sin expandir),
naranja = nodos expandidos (con su número de turno), morado = nodo actual, amarillo = camino final.

## Cómo funciona

A* mantiene una cola de prioridad (`heapq`) de nodos por explorar y siempre expande el de menor

```
f(n) = g(n) + h(n)
```

- **g(n):** costo real desde el inicio hasta `n` (1 por cada paso).
- **h(n):** estimación del costo restante hasta la meta.

En cada iteración se saca el nodo con menor f, se marca como expandido y se agregan (o se mejoran) sus
vecinos libres en 4 direcciones. Si dos nodos empatan en f, se prefiere el de menor h (el más cercano a la meta).
Al llegar a la meta, el camino se reconstruye siguiendo el `padre` de cada nodo.

`astar.buscar` es un **generador**: hace un `yield` después de cada nodo expandido con la frontera,
los nodos cerrados y el nodo actual. Así `main.py` puede mostrar el proceso interno y no solo el resultado final.

## Heurística: distancia Manhattan

```
h(n) = |fila_n - fila_meta| + |columna_n - columna_meta|
```

**¿Por qué es admisible?** Con movimientos solo en 4 direcciones y costo 1 por paso, cualquier camino
hasta la meta necesita al menos |Δfila| + |Δcolumna| pasos. Los obstáculos solo pueden alargar el camino, nunca acortarlo, así que h nunca sobreestima el costo real. Por eso A* garantiza encontrar el camino más corto.
Además es **consistente** (h(n) ≤ 1 + h(vecino)), por lo que un nodo expandido ya tiene su mejor g.

## Comparación contra búsqueda no informada

Con `h = 0`, A* se convierte en Dijkstra: no sabe dónde está la meta y se expande en todas direcciones.
Ambos encuentran un camino óptimo, pero A* explora muchos menos nodos.

| Mapa | Algoritmo | Nodos expandidos | Largo del camino |
|---|---|---|---|
| Cuadrícula vacía 10x10 | A* (Manhattan) | 19 | 18 |
| Cuadrícula vacía 10x10 | Dijkstra (h = 0) | 100 | 18 |
| Pared vertical en la columna 4 (filas 0-3 y 5-9), hueco en la fila 4 | A* (Manhattan) | 39 | 18 |
| Pared vertical en la columna 4 (filas 0-3 y 5-9), hueco en la fila 4 | Dijkstra (h = 0) | 91 | 18 |


## Validación

Se comprobó contra BFS en 2,000 cuadrículas aleatorias de 10x10 (30 % de obstáculos): A* y Dijkstra
siempre devolvieron la longitud óptima del camino, y A* nunca expandió más nodos que Dijkstra.

## Autora

Ivanna Rodríguez Rosales - 2111651