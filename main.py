
import sys

import pygame

from astar import buscar, heuristica_cero, heuristica_manhattan

pygame.init()

# ------------------------------------------------------------- configuración
ANCHO = 800
ALTO_GRID = 800
ALTO_PANEL = 110
FILAS = 10
COLUMNAS = 10
TAM_CELDA = ANCHO // COLUMNAS

# Colores RGB
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 200, 0)          # inicio
ROJO = (220, 0, 0)           # meta
GRIS = (180, 180, 180)       # líneas de la cuadrícula
AZUL_FRONTERA = (150, 210, 255)   # descubiertos, aún sin expandir
NARANJA_CERRADO = (255, 205, 160)  # ya expandidos
MORADO_ACTUAL = (170, 100, 255)    # nodo que se acaba de expandir
AMARILLO_CAMINO = (255, 225, 0)    # camino final
LINEA_CAMINO = (150, 100, 0)
PANEL_FONDO = (30, 30, 40)
TEXTO_CLARO = (235, 235, 235)

ventana = pygame.display.set_mode((ANCHO, ALTO_GRID + ALTO_PANEL))
pygame.display.set_caption("Algoritmo A* - Busqueda de caminos")
reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("arial", 18)
fuente_chica = pygame.font.SysFont("arial", 14)
fuente_orden = pygame.font.SysFont("arial", 22, bold=True)

# ------------------------------------------------------------------- estado
cuadricula = [[0] * COLUMNAS for _ in range(FILAS)]
inicio = (0, 0)
meta = (9, 9)

busqueda = None            # generador de astar.buscar mientras corre
estado = None              # último estado devuelto por el generador
nombre_algoritmo = ""
resultados = {}            # {"A*": (expandidos, largo), "Dijkstra": (...)}
mostrar_valores = False    # mostrar g / h / f en cada celda
pausado = False
retraso_ms = 300           # tiempo entre pasos de la búsqueda
ultimo_paso = 0
modo_pincel = None         # "poner" o "quitar" mientras se arrastra el mouse


# ---------------------------------------------------------------- búsqueda
def limpiar_busqueda():
    global busqueda, estado, nombre_algoritmo
    busqueda = None
    estado = None
    nombre_algoritmo = ""


def iniciar_busqueda(heuristica, nombre):
    global busqueda, estado, nombre_algoritmo, ultimo_paso, pausado
    limpiar_busqueda()
    nombre_algoritmo = nombre
    busqueda = buscar(cuadricula, inicio, meta, heuristica)
    ultimo_paso = pygame.time.get_ticks()
    pausado = False


def avanzar_paso():
    """Pide al generador el siguiente paso de la búsqueda."""
    global busqueda, estado
    if busqueda is None:
        return
    try:
        estado = next(busqueda)
    except StopIteration:
        busqueda = None
        return

    if estado["terminado"]:
        largo = len(estado["camino"]) - 1 if estado["camino"] else None
        resultados[nombre_algoritmo] = (len(estado["cerrados"]), largo)
        busqueda = None


def reiniciar_todo():
    global cuadricula
    cuadricula = [[0] * COLUMNAS for _ in range(FILAS)]
    resultados.clear()
    limpiar_busqueda()


# ------------------------------------------------------------------ dibujo
def centro(posicion):
    fila, columna = posicion
    return (columna * TAM_CELDA + TAM_CELDA // 2, fila * TAM_CELDA + TAM_CELDA // 2)


def escribir(texto, fuente_usada, color, x, y, centrado=False):
    superficie = fuente_usada.render(texto, True, color)
    rect = superficie.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    ventana.blit(superficie, rect)


def dibujar_cuadricula():
    ventana.fill(BLANCO)

    cerrados = estado["cerrados"] if estado else {}
    frontera = estado["frontera"] if estado else {}
    actual = estado["actual"] if estado else None
    camino = estado["camino"] if estado and estado["camino"] else []
    en_camino = set(camino)
    orden = {pos: i + 1 for i, pos in enumerate(cerrados)}

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            pos = (fila, columna)
            x = columna * TAM_CELDA
            y = fila * TAM_CELDA

            color = BLANCO
            if cuadricula[fila][columna] == 1:
                color = NEGRO
            elif pos in en_camino:
                color = AMARILLO_CAMINO
            elif actual is not None and pos == actual.posicion:
                color = MORADO_ACTUAL
            elif pos in cerrados:
                color = NARANJA_CERRADO
            elif pos in frontera:
                color = AZUL_FRONTERA

            if pos == inicio:
                color = VERDE
            if pos == meta:
                color = ROJO

            pygame.draw.rect(ventana, color, (x, y, TAM_CELDA, TAM_CELDA))
            pygame.draw.rect(ventana, GRIS, (x, y, TAM_CELDA, TAM_CELDA), 1)

            # Números dentro de la celda
            nodo = cerrados.get(pos) or frontera.get(pos)
            if nodo is not None and cuadricula[fila][columna] == 0:
                if mostrar_valores:
                    escribir(f"g={nodo.g}", fuente_chica, NEGRO, x + 5, y + 4)
                    escribir(f"h={nodo.h}", fuente_chica, NEGRO, x + 5, y + 22)
                    escribir(f"f={nodo.f}", fuente_orden, NEGRO,
                             x + TAM_CELDA // 2, y + TAM_CELDA // 2 + 8, centrado=True)
                if pos in orden:
                    # Número de expansión: en qué turno se expandió esta celda
                    if mostrar_valores:
                        escribir(f"#{orden[pos]}", fuente_chica, (120, 0, 0),
                                 x + TAM_CELDA - 30, y + TAM_CELDA - 20)
                    else:
                        escribir(str(orden[pos]), fuente_orden, (120, 0, 0),
                                 x + TAM_CELDA // 2, y + TAM_CELDA // 2, centrado=True)

    # Línea que une el camino final
    if len(camino) > 1:
        pygame.draw.lines(ventana, LINEA_CAMINO, False,
                          [centro(p) for p in camino], 6)

    dibujar_panel()
    pygame.display.update()


def dibujar_panel():
    pygame.draw.rect(ventana, PANEL_FONDO, (0, ALTO_GRID, ANCHO, ALTO_PANEL))
    y = ALTO_GRID + 8

    # Línea 1: estado de la búsqueda actual
    if estado:
        expandidos = len(estado["cerrados"])
        en_frontera = len(estado["frontera"])
        texto = f"{nombre_algoritmo}  |  expandidos: {expandidos}  |  frontera: {en_frontera}"
        if estado["terminado"]:
            if estado["camino"]:
                texto += f"  |  camino: {len(estado['camino']) - 1} pasos"
            else:
                texto += "  |  SIN CAMINO"
    else:
        texto = "Dibuja obstaculos con el mouse y presiona ESPACIO"
    escribir(texto, fuente, TEXTO_CLARO, 10, y)

    # Línea 2: comparación entre algoritmos
    if resultados:
        partes = []
        for nombre, (expandidos, largo) in resultados.items():
            camino_txt = f"{largo} pasos" if largo is not None else "sin camino"
            partes.append(f"{nombre}: {expandidos} nodos expandidos, {camino_txt}")
        escribir("   ||   ".join(partes), fuente, (255, 225, 0), 10, y + 28)

    # Líneas 3-4: controles
    escribir("ESPACIO: A*   D: Dijkstra (h=0)   V: ver g/h/f   P: pausa   FLECHA DER: 1 paso",
             fuente_chica, (170, 170, 170), 10, y + 60)
    escribir("C: limpiar busqueda   R: reiniciar todo   +/-: velocidad   "
             "Azul=frontera  Naranja=expandido  Morado=actual  Amarillo=camino",
             fuente_chica, (170, 170, 170), 10, y + 80)


# ------------------------------------------------------------ eventos / mouse
def celda_bajo_mouse(posicion_mouse):
    x, y = posicion_mouse
    if y >= ALTO_GRID or x >= ANCHO:
        return None
    return (y // TAM_CELDA, x // TAM_CELDA)


def editar_celda(celda, modo):
    fila, columna = celda
    if celda == inicio or celda == meta:
        return
    nuevo = 1 if modo == "poner" else 0
    if cuadricula[fila][columna] != nuevo:
        cuadricula[fila][columna] = nuevo
        # Si el mapa cambia, la búsqueda anterior ya no es válida
        resultados.clear()
        limpiar_busqueda()


def manejar_evento(evento):
    global modo_pincel, mostrar_valores, pausado, retraso_ms

    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        celda = celda_bajo_mouse(evento.pos)
        if celda is not None:
            modo_pincel = "quitar" if cuadricula[celda[0]][celda[1]] == 1 else "poner"
            editar_celda(celda, modo_pincel)

    elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
        modo_pincel = None

    elif evento.type == pygame.MOUSEMOTION and modo_pincel is not None:
        celda = celda_bajo_mouse(evento.pos)
        if celda is not None:
            editar_celda(celda, modo_pincel)

    elif evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_SPACE:
            iniciar_busqueda(heuristica_manhattan, "A* (Manhattan)")
        elif evento.key == pygame.K_d:
            iniciar_busqueda(heuristica_cero, "Dijkstra (h=0)")
        elif evento.key == pygame.K_v:
            mostrar_valores = not mostrar_valores
        elif evento.key == pygame.K_p:
            pausado = not pausado
        elif evento.key == pygame.K_RIGHT:
            avanzar_paso()          # un paso manual (útil para explicar en el video)
        elif evento.key == pygame.K_c:
            limpiar_busqueda()
        elif evento.key == pygame.K_r:
            reiniciar_todo()
        elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            retraso_ms = max(20, int(retraso_ms * 0.7))
        elif evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            retraso_ms = min(2000, int(retraso_ms * 1.4))


# --------------------------------------------------------------- bucle principal
def main():
    global ultimo_paso
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            else:
                manejar_evento(evento)

        # Avanza la búsqueda automáticamente cada `retraso_ms`
        ahora = pygame.time.get_ticks()
        if busqueda is not None and not pausado and ahora - ultimo_paso >= retraso_ms:
            avanzar_paso()
            ultimo_paso = ahora

        dibujar_cuadricula()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()