import pygame
import sys
import random
import time
import heapq

# Inicialización de Pygame
pygame.init()

# Dimensiones del tablero
ANCHO_TABLERO = 5
ALTO_TABLERO = 20
TAMANO_CELDA = 30
ANCHO_PANTALLA = ANCHO_TABLERO * TAMANO_CELDA
ALTO_PANTALLA = ALTO_TABLERO * TAMANO_CELDA

# Colores
COLOR_FONDO = (0, 0, 0)
COLOR_CELDA = (0, 255, 0)
COLOR_REJILLA = (50, 50, 50)

# Definir la pantalla
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption('Tetris AI con A*')

# Definir las piezas y sus rotaciones
PIEZAS = {
    'Tipo1': [  # Forma T, centrada en el elemento central
        [[1, 1, 1],
         [0, 1, 0]],
        [[0, 1],
         [1, 1],
         [0, 1]],
        [[0, 1, 0],
         [1, 1, 1]],
        [[1, 0],
         [1, 1],
         [1, 0]]
    ],
    'Tipo2': [  # Forma Cuadrado, centrada en la esquina inferior izquierda
        [[1, 1],
         [1, 1]]
    ],
    'Tipo3': [  # Forma L, centrada en el medio del elemento largo
        [[1, 0],
         [1, 0],
         [1, 1]],
        [[1, 1, 1],
         [1, 0, 0]],
        [[1, 1],
         [0, 1],
         [0, 1]],
        [[0, 0, 1],
         [1, 1, 1]]
    ],
    'Tipo4': [  # Forma L invertida, centrada en el medio del elemento largo
        [[0, 1],
         [0, 1],
         [1, 1]],
        [[1, 1, 1],
         [0, 0, 1]],
        [[1, 1],
         [1, 0],
         [1, 0]],
        [[1, 0, 0],
         [1, 1, 1]]
    ],
    'Tipo5': [  # Forma Subida (Z)
        [[1, 1, 0],
         [0, 1, 1]],
        [[0, 1],
         [1, 1],
         [1, 0]]
    ],
    'Tipo6': [  # Forma Bajada (S)
        [[0, 1, 1],
         [1, 1, 0]],
        [[1, 0],
         [1, 1],
         [0, 1]]
    ],
    'Tipo7': [  # Forma Palo
        [[1],
         [1],
         [1],
         [1]],
        [[1, 1, 1, 1]]
    ]
}

# Pesos heurísticos
PESO_ALTURA = 0.5
PESO_HUECOS = 1
PESO_IRREGULARIDAD = 0.5
PESO_LINEAS_ELIMINADAS = 10

def copiar_tablero(tablero):
    # Realizar una copia del tablero
    return [fila[:] for fila in tablero]

def puede_colocar_pieza(tablero, pieza, x, y):
    # Verificar si una pieza se puede colocar en la posición especificada
    for i in range(len(pieza)):
        for j in range(len(pieza[0])):
            if pieza[i][j]:
                tablero_x = x + j
                tablero_y = y + i
                if tablero_x < 0 or tablero_x >= ANCHO_TABLERO or tablero_y >= ALTO_TABLERO:
                    return False
                if tablero_y >= 0 and tablero[tablero_y][tablero_x]:
                    return False
    return True

def colocar_pieza(tablero, pieza, x, y):
    # Colocar una pieza en el tablero y devolver un nuevo tablero
    tablero_nuevo = copiar_tablero(tablero)
    for i in range(len(pieza)):
        for j in range(len(pieza[0])):
            if pieza[i][j]:
                tablero_x = x + j
                tablero_y = y + i
                if tablero_y >= 0:
                    tablero_nuevo[tablero_y][tablero_x] = 1
    return tablero_nuevo

def bloquear_pieza(tablero, pieza, x):
    # Simular la caída de una pieza hasta que no se pueda mover más
    y = -len(pieza)
    while puede_colocar_pieza(tablero, pieza, x, y + 1):
        y += 1
    if y < -len(pieza) + 1:
        return None  # No se puede colocar la pieza en esta columna y rotación
    return colocar_pieza(tablero, pieza, x, y)

def limpiar_lineas(tablero):
    # Eliminar líneas completas del tablero
    tablero_nuevo = [fila for fila in tablero if not all(fila)]
    lineas_eliminadas = ALTO_TABLERO - len(tablero_nuevo)
    tablero_nuevo = [[0]*ANCHO_TABLERO for _ in range(lineas_eliminadas)] + tablero_nuevo
    return tablero_nuevo, lineas_eliminadas

def calcular_altura(tablero):
    # Calcular la altura total del tablero
    for y in range(ALTO_TABLERO):
        if any(tablero[y]):
            return ALTO_TABLERO - y
    return 0

def calcular_huecos(tablero):
    # Contar el número de huecos en el tablero
    huecos = 0
    for x in range(ANCHO_TABLERO):
        bloque_encontrado = False
        for y in range(ALTO_TABLERO):
            if tablero[y][x]:
                bloque_encontrado = True
            elif bloque_encontrado:
                huecos += 1
    return huecos

def calcular_irregularidad(tablero):
    # Calcular la irregularidad del tablero (diferencias de altura entre columnas)
    alturas = []
    for x in range(ANCHO_TABLERO):
        altura_columna = 0
        for y in range(ALTO_TABLERO):
            if tablero[y][x]:
                altura_columna = ALTO_TABLERO - y
                break
        alturas.append(altura_columna)
    irregularidad = sum(abs(alturas[i] - alturas[i+1]) for i in range(len(alturas)-1))
    return irregularidad

def heuristica(tablero):
    # Calcular la heurística del tablero
    altura = calcular_altura(tablero)
    huecos = calcular_huecos(tablero)
    irregularidad = calcular_irregularidad(tablero)
    return (PESO_ALTURA * altura) + (PESO_HUECOS * huecos) + (PESO_IRREGULARIDAD * irregularidad)

def calcular_costo(tablero_anterior, tablero_nuevo, lineas_eliminadas):
    # Aplicar la función de costo para el tablero actualizado
    altura = calcular_altura(tablero_nuevo)
    huecos = calcular_huecos(tablero_nuevo)
    return (PESO_ALTURA * altura) + (PESO_HUECOS * huecos) - (lineas_eliminadas * PESO_LINEAS_ELIMINADAS)

class Nodo:
    def __init__(self, tablero, pieza_actual, siguiente_pieza, indice_pieza, costo_g, costo_h, padre=None, accion=None):
        self.tablero = tablero                      # Estado actual del tablero
        self.pieza_actual = pieza_actual            # Pieza actual a colocar
        self.siguiente_pieza = siguiente_pieza      # Siguiente pieza a colocar
        self.indice_pieza = indice_pieza            # Índice de la pieza actual en la secuencia
        self.costo_g = costo_g                      # Costo acumulado
        self.costo_h = costo_h                      # Estimación heurística
        self.costo_f = costo_g + costo_h            # Costo total estimado
        self.padre = padre                          # Nodo padre
        self.accion = accion                        # Acción tomada para llegar a este nodo

    def __lt__(self, otro):
        return self.costo_f < otro.costo_f

def generar_sucesores(nodo_actual, piezas_por_colocar, look_ahead=1):
    # Generar nodos sucesores considerando todas las posiciones y rotaciones posibles
    sucesores = []
    pieza_actual = nodo_actual.pieza_actual
    siguiente_pieza = nodo_actual.siguiente_pieza
    indice_pieza_actual = nodo_actual.indice_pieza

    if pieza_actual is None:
        return sucesores  # No hay más piezas para colocar

    for indice_rotacion, rotacion in enumerate(PIEZAS[pieza_actual]):
        pieza_rotada = rotacion
        ancho_pieza = len(pieza_rotada[0])
        for x in range(-ancho_pieza + 1, ANCHO_TABLERO):
            tablero_nuevo = bloquear_pieza(nodo_actual.tablero, pieza_rotada, x)
            if tablero_nuevo:
                tablero_limpio, lineas_eliminadas = limpiar_lineas(tablero_nuevo)
                costo_g_nuevo = nodo_actual.costo_g + calcular_costo(nodo_actual.tablero, tablero_limpio, lineas_eliminadas)
                costo_h_nuevo = heuristica(tablero_limpio)
                accion = (x, indice_rotacion, pieza_rotada)
                indice_pieza_nueva = indice_pieza_actual + 1
                if (indice_pieza_nueva + 1) < len(piezas_por_colocar):
                    nueva_siguiente_pieza = piezas_por_colocar[indice_pieza_nueva + 1]
                else:
                    nueva_siguiente_pieza = None
                nuevo_nodo = Nodo(
                    tablero=tablero_limpio,
                    pieza_actual=siguiente_pieza,
                    siguiente_pieza=nueva_siguiente_pieza,
                    indice_pieza=indice_pieza_nueva,
                    costo_g=costo_g_nuevo,
                    costo_h=costo_h_nuevo,
                    padre=nodo_actual,
                    accion=accion
                )
                sucesores.append(nuevo_nodo)
    return sucesores

def ejecutar_movimientos(tablero_inicial, camino, piezas_por_colocar):
    # Ejecutar los movimientos siguiendo el camino encontrado
    tablero = copiar_tablero(tablero_inicial)
    for idx, accion in enumerate(camino):
        x, indice_rotacion, pieza_rotada = accion
        y_actual = -len(pieza_rotada)
        while puede_colocar_pieza(tablero, pieza_rotada, x, y_actual + 1):
            y_actual += 1
            dibujar_tablero(tablero)
            for i in range(len(pieza_rotada)):
                for j in range(len(pieza_rotada[0])):
                    if pieza_rotada[i][j]:
                        tablero_x = x + j
                        tablero_y = y_actual + i
                        if 0 <= tablero_x < ANCHO_TABLERO and 0 <= tablero_y < ALTO_TABLERO:
                            pygame.draw.rect(pantalla, (255, 0, 0), (tablero_x*TAMANO_CELDA, tablero_y*TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA))
            pygame.display.flip()
            time.sleep(0.05)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        tablero = colocar_pieza(tablero, pieza_rotada, x, y_actual)
        tablero, lineas_eliminadas = limpiar_lineas(tablero)
        dibujar_tablero(tablero)
        time.sleep(0.5)

def dibujar_tablero(tablero):
    # Dibujar el tablero y la rejilla
    pantalla.fill(COLOR_FONDO)
    for y in range(ALTO_TABLERO):
        for x in range(ANCHO_TABLERO):
            if tablero[y][x]:
                pygame.draw.rect(pantalla, COLOR_CELDA, (x*TAMANO_CELDA, y*TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA))
    for x in range(ANCHO_TABLERO + 1):
        pygame.draw.line(pantalla, COLOR_REJILLA, (x*TAMANO_CELDA, 0), (x*TAMANO_CELDA, ALTO_PANTALLA))
    for y in range(ALTO_TABLERO + 1):
        pygame.draw.line(pantalla, COLOR_REJILLA, (0, y*TAMANO_CELDA), (ANCHO_PANTALLA, y*TAMANO_CELDA))
    pygame.display.flip()

def main():
    # Tablero inicial vacío
    tablero_inicial = [[0]*ANCHO_TABLERO for _ in range(ALTO_TABLERO)]

    # Generar una secuencia de 50 piezas aleatorias
    piezas_por_colocar = [random.choice(list(PIEZAS.keys())) for _ in range(50)]

    # Inicializar piezas actual y siguiente
    pieza_actual = piezas_por_colocar[0]
    siguiente_pieza = piezas_por_colocar[1] if len(piezas_por_colocar) > 1 else None

    # Crear nodo inicial
    nodo_inicial = Nodo(
        tablero=tablero_inicial,
        pieza_actual=pieza_actual,
        siguiente_pieza=siguiente_pieza,
        indice_pieza=0,
        costo_g=0,
        costo_h=heuristica(tablero_inicial)
    )

    lista_abierta = []
    heapq.heappush(lista_abierta, nodo_inicial)
    conjunto_cerrado = set()
    PROFUNDIDAD_MAXIMA = 50

    camino = None

    while lista_abierta:
        nodo_actual = heapq.heappop(lista_abierta)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if nodo_actual.padre and nodo_actual.indice_pieza >= len(piezas_por_colocar) - 1:
            camino = []
            nodo = nodo_actual
            while nodo.padre is not None:
                camino.append(nodo.accion)
                nodo = nodo.padre
            camino.reverse()
            break

        clave_estado = (tuple(tuple(fila) for fila in nodo_actual.tablero), nodo_actual.pieza_actual, nodo_actual.indice_pieza)
        if clave_estado in conjunto_cerrado:
            continue
        conjunto_cerrado.add(clave_estado)

        sucesores = generar_sucesores(nodo_actual, piezas_por_colocar, look_ahead=1)
        for sucesor in sucesores:
            if sucesor.indice_pieza - nodo_inicial.indice_pieza > PROFUNDIDAD_MAXIMA:
                continue
            clave_sucesor = (tuple(tuple(fila) for fila in sucesor.tablero), sucesor.pieza_actual, sucesor.indice_pieza)
            if clave_sucesor in conjunto_cerrado:
                continue
            heapq.heappush(lista_abierta, sucesor)

    if camino:
        print("Camino encontrado con A* considerando las siguientes piezas:")
        for idx, accion in enumerate(camino):
            x, indice_rotacion, _ = accion
            print(f"Pieza {idx+1}: Colocar en X={x}, Rotación={indice_rotacion}")
        ejecutar_movimientos(tablero_inicial, camino, piezas_por_colocar)
    else:
        print("No se encontró un camino válido para colocar todas las piezas.")

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
