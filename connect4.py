import numpy as np
import random
import pygame 
import sys
import math

MORADO = (133,11,193)
NEGRO = (0,0,0)
ROJO = (255,0,0)
AMARILLO = (255,255,0)

CONTADOR_FILA = 6
CONTADOR_COLUMNA = 7

JUGADOR = 0
IA = 1

PIEZA_JUGADOR = 1
PIEZA_IA = 2

LARGO_PANTALLA = 4

VACIO = 0

def crear_tablero():
    tablero = np.zeros((CONTADOR_FILA, CONTADOR_COLUMNA))
    return tablero

def soltar_ficha(tablero, fila, columna, pieza):
    tablero[fila][columna] = pieza

def ubicacion_valida(tablero, columna):
    return tablero[5][columna] == 0

def obtener_siguiente_fila(tablero, columna):
    for fila in range(CONTADOR_FILA):
        if tablero[fila][columna] == 0:
            return fila

def imprimir_tablero(tablero):
    print(np.flip(tablero, 0))
    
def jugada_ganadora(tablero, pieza):
    # Revisar todas las ubicaciones horizontales por una victoria
    for c in range(CONTADOR_COLUMNA-3):
        for f in range (CONTADOR_FILA):
            if tablero[f][c] == pieza and tablero [f][c+1] == pieza and tablero [f][c+2] == pieza and tablero [f][c+3] == pieza:
                return True
            
    # Revisar todas las ubicaciones verticables por una victoria
    for c in range(CONTADOR_COLUMNA):
        for f in range (CONTADOR_FILA-3):
            if tablero[f][c] == pieza and tablero [f+1][c] == pieza and tablero [f+2][c] == pieza and tablero [f+3][c] == pieza:
                return True
            
    # Revisar diagonales con pendiente positiva
    for c in range(CONTADOR_COLUMNA-3):
        for f in range (CONTADOR_FILA-3):
            if tablero[f][c] == pieza and tablero [f+1][c+1] == pieza and tablero [f+2][c+2] == pieza and tablero [f+3][c+3] == pieza:
                return True
    
    # Revisar diagonales con pendiente negativa
    for c in range(CONTADOR_COLUMNA-3):
        for f in range (3, CONTADOR_FILA):
            if tablero[f][c] == pieza and tablero [f-1][c+1] == pieza and tablero [f-2][c+2] == pieza and tablero [f-3][c+3] == pieza:
                return True
            
def evaluar_pantalla(pantalla, pieza):
    puntuacion = 0
    pieza_enemiga = PIEZA_JUGADOR
    if pieza == PIEZA_JUGADOR:
        pieza_enemiga = PIEZA_IA
    
    if pantalla.count(pieza) == 4:
        puntuacion += 1000
    elif pantalla.count(pieza) == 3 and pantalla.count(VACIO) == 1:
        puntuacion += 5
    elif pantalla.count(pieza) == 2 and pantalla.count(VACIO) == 2:
        puntuacion += 2
        
    if pantalla.count(pieza_enemiga) == 3 and pantalla.count(VACIO) == 1:
        puntuacion -= 4
        
    return puntuacion
        
def posicion_puntuacion(tablero, pieza):
    puntuacion = 0
    
    # Puntuacion central
    centro_array = [int(i) for i in list(tablero[:,CONTADOR_COLUMNA//2])]
    centro_contador = centro_array.count(pieza)
    puntuacion += centro_contador * 3
    
    # Puntuacion horizontal
    for f in range(CONTADOR_FILA):
        fila_array = [int(i) for i in list(tablero[f,:])]
        for c in range(CONTADOR_COLUMNA-3):
            pantalla = fila_array[c:c+LARGO_PANTALLA]
            puntuacion += evaluar_pantalla(pantalla, pieza)
                
    # Puntuacion vertical        
    for c in range(CONTADOR_COLUMNA):
        col_array = [int(i) for i in list(tablero[:,c])]
        for r in range(CONTADOR_FILA-3):
            pantalla = col_array[r:r+LARGO_PANTALLA]
            puntuacion += evaluar_pantalla(pantalla, pieza)  
                
    # Diagonales lado positivo
    for f in range(CONTADOR_FILA-3):
        for c in range(CONTADOR_COLUMNA-3):
            pantalla = [tablero[f+i][c+i] for i in range(LARGO_PANTALLA)]
            puntuacion += evaluar_pantalla(pantalla, pieza)
                
    # Diagonales lado negativo            
    for f in range(CONTADOR_FILA-3):
        for c in range(CONTADOR_COLUMNA-3):
            pantalla = [tablero[f+3-i][c+i]for i in range(LARGO_PANTALLA)]
            puntuacion += evaluar_pantalla(pantalla, pieza)             

    return puntuacion

def nodo_terminal(tablero):
    return jugada_ganadora(tablero, PIEZA_JUGADOR) or jugada_ganadora(tablero, PIEZA_IA) or len(obtener_ubicaciones_permitidas(tablero)) == 0
        
def minimax(tablero, profundidad, alpha, beta, maximizingJugador):
    ubicaciones_permitidas = obtener_ubicaciones_permitidas(tablero)
    terminal = nodo_terminal(tablero)
    if profundidad == 0 or terminal:
        if terminal:
            if jugada_ganadora(tablero, PIEZA_IA):
                return (None, 10000000000000000000)
            elif jugada_ganadora(tablero, PIEZA_JUGADOR):
                return (None, -10000000000000000000)
            else: # Juego terminado, no hay movimientos validos
                return (None, 0)
        else: # Profundidad es cero
            return (None, posicion_puntuacion(tablero, PIEZA_IA))
    if maximizingJugador:
        valor = -math.inf
        columna = random.choice(ubicaciones_permitidas)
        for col in ubicaciones_permitidas:
            fila = obtener_siguiente_fila(tablero, col)
            t_copiar = tablero.copy()
            soltar_ficha(t_copiar, fila, col, PIEZA_IA)
            nueva_puntuacion = minimax(t_copiar, profundidad-1, alpha, beta, False)[1]
            if nueva_puntuacion > valor:
                valor = nueva_puntuacion
                columna = col
            alpha = max(alpha, valor)
            if alpha >= beta:
                break
        return columna, valor
        
    else: # Minimizando jugador
        valor = math.inf
        columna = random.choice(ubicaciones_permitidas)
        for col in ubicaciones_permitidas:
            fila = obtener_siguiente_fila(tablero, col)
            t_copiar = tablero.copy()
            soltar_ficha(t_copiar, fila, col, PIEZA_JUGADOR)
            nueva_puntuacion = minimax(t_copiar, profundidad-1, alpha, beta, True)[1]
            if nueva_puntuacion < valor:
                valor = nueva_puntuacion
                columna = col
            beta = min(beta, valor)
            if alpha >= beta:
                break
        return columna, valor

def obtener_ubicaciones_permitidas(tablero):
    ubicaciones_permitidas = []
    for col in range(CONTADOR_COLUMNA):
        if ubicacion_valida(tablero, col):
            ubicaciones_permitidas.append(col)
    return ubicaciones_permitidas

def escoger_mejor_movimiento(tablero, pieza):
    ubicaciones_permitidas = obtener_ubicaciones_permitidas(tablero)
    mejor_puntuacion = -10000
    mejor_columna = random.choice(ubicaciones_permitidas)
    for col in ubicaciones_permitidas:
        fil = obtener_siguiente_fila(tablero, col)
        tablero_temporal = tablero.copy()
        soltar_ficha(tablero_temporal, fil, col, pieza)
        puntuacion = posicion_puntuacion(tablero_temporal, pieza)
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_columna = col
            
    return mejor_columna

def dibujar_tablero(tablero):
    for c in range(CONTADOR_COLUMNA):
        for f in range(CONTADOR_FILA):
            pygame.draw.rect(pantalla, MORADO, (c*TAMAÑOCUADROS, f*TAMAÑOCUADROS+TAMAÑOCUADROS, TAMAÑOCUADROS, TAMAÑOCUADROS))
            pygame.draw.circle(pantalla, NEGRO, (int(c*TAMAÑOCUADROS+TAMAÑOCUADROS/2), int(f*TAMAÑOCUADROS+TAMAÑOCUADROS+TAMAÑOCUADROS/2)), RADIO)
    
    for c in range(CONTADOR_COLUMNA):
        for f in range(CONTADOR_FILA):        
            if tablero[f][c] == PIEZA_JUGADOR:
                pygame.draw.circle(pantalla, ROJO, (int(c*TAMAÑOCUADROS+TAMAÑOCUADROS/2), alto-int(f*TAMAÑOCUADROS+TAMAÑOCUADROS/2)), RADIO)    
            elif tablero[f][c] == PIEZA_IA:
                pygame.draw.circle(pantalla, AMARILLO, (int(c*TAMAÑOCUADROS+TAMAÑOCUADROS/2), alto-int(f*TAMAÑOCUADROS+TAMAÑOCUADROS/2)), RADIO)        
    pygame.display.update()
            
tablero = crear_tablero()
imprimir_tablero(tablero)
juego_terminado = False

pygame.init()

TAMAÑOCUADROS = 100

ancho = CONTADOR_COLUMNA * TAMAÑOCUADROS
alto = (CONTADOR_FILA+1) * TAMAÑOCUADROS

RADIO = int(TAMAÑOCUADROS/2 - 5)

tamaño = (ancho, alto)

pantalla = pygame.display.set_mode(tamaño)
dibujar_tablero(tablero)
pygame.display.update()

mensaje = pygame.font.SysFont("monospace", 60)

turno = random.randint(JUGADOR, IA)

while not juego_terminado:
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            sys.exit()
            
        if evento.type == pygame.MOUSEMOTION:
            pygame.draw.rect(pantalla, NEGRO, (0, 0, ancho, TAMAÑOCUADROS))
            posx = evento.pos[0]
            if turno == JUGADOR:
                pygame.draw.circle(pantalla, ROJO, (posx, int(TAMAÑOCUADROS/2)), RADIO)
            
        pygame.display.update()
            
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(pantalla, NEGRO, (0, 0, ancho, TAMAÑOCUADROS))

            # Pedirle al jugador 1 una jugada
            if turno == JUGADOR:
                posx = evento.pos[0]
                columna = int(math.floor(posx/TAMAÑOCUADROS))
                
                if ubicacion_valida(tablero, columna):
                    fila = obtener_siguiente_fila(tablero, columna)
                    soltar_ficha(tablero, fila, columna, PIEZA_JUGADOR)
                    
                    if jugada_ganadora(tablero, PIEZA_JUGADOR):
                        label = mensaje.render("El jugador 1 gana!", 1, ROJO)
                        pantalla.blit(label, (40,10))
                        juego_terminado = True
                
                    turno += 1
                    turno = turno % 2
                    
                    imprimir_tablero(tablero)
                    dibujar_tablero(tablero)                   
            
    # Pedirle al jugador 2 una jugada
    if turno == IA and not juego_terminado:

        columna, minimax_puntuacion = minimax(tablero, 6, -math.inf, math.inf, True)

        if ubicacion_valida(tablero, columna):
            #pygame.time.wait(500)
            fila = obtener_siguiente_fila(tablero, columna)
            soltar_ficha(tablero, fila, columna,PIEZA_IA)
            
            if jugada_ganadora(tablero, PIEZA_IA):
                label = mensaje.render("El jugador 2 gana!", 1, AMARILLO)
                pantalla.blit(label, (40,10))
                juego_terminado = True 
                
            imprimir_tablero(tablero)
            dibujar_tablero(tablero)

            turno += 1
            turno = turno % 2
            
    if juego_terminado:
        pygame.time.wait(3000)