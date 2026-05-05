# Grupo: 02 | Técnica: Algoritmo del Panadero
# Integrantes: Calderón José Luis Alejandro, Berríos Boris Benjamín,
#              Paolini Matías Francisco Alejandro, Araya Ignacio Alberto
# Asignatura: Sistemas Operativos | Universidad La Serena

import threading
import random
import math
import time

# El algoritmo del panadero funciona como una fila con número:
# cada hilo toma un turno y espera a que los de menor número pasen primero.
# Si dos hilos sacan el mismo número, entra el que tenga menor índice.

N = 2
eligiendo = [False] * N  # True mientras el hilo está sacando su turno
turno     = [0] * N      # número de turno de cada hilo (0 = no está en fila)


def tomar_turno(id_hilo):
    # Avisa que va a elegir su número
    eligiendo[id_hilo] = True
    turno[id_hilo] = max(turno) + 1
    eligiendo[id_hilo] = False

    # Revisa si algún otro hilo tiene prioridad antes de entrar
    for j in range(N):
        if j == id_hilo:
            continue
        # Espera si el otro todavía está eligiendo su turno
        while eligiendo[j]:
            pass
        # Espera si el otro tiene un turno menor, o igual pero menor índice
        while turno[j] != 0 and (turno[j], j) < (turno[id_hilo], id_hilo):
            pass


def liberar_turno(id_hilo):
    # Devuelve el turno a 0, libera el paso para los demás
    turno[id_hilo] = 0


# Variables compartidas entre los dos hilos
buffer       = []
ARCHIVO      = "resultados.txt"
TOTAL_ITEMS  = 10

#Esto genera números aleatorios entre 1 y 10 y los escribe en el archivo
def productor(id_hilo):
    # sample garantiza que no se repite ningún número
    numeros = random.sample(range(1, 11), TOTAL_ITEMS)
    for numero in numeros:

        tomar_turno(id_hilo)
        # --- sección crítica: escribe en el buffer compartido ---
        buffer.append(numero)
        print(f"[Productor] agregó: {numero}")
        liberar_turno(id_hilo)

        time.sleep(1.0)

#esto lee los números del archivo, calcula su factorial y guarda los resultados
def consumidor(id_hilo):
    procesados = 0
    with open(ARCHIVO, "w") as archivo:
        while procesados < TOTAL_ITEMS:

            tomar_turno(id_hilo)
            #sección crítica: lee del buffer y calcula el factorial
            if buffer:
                n = buffer.pop(0)
                resultado = math.factorial(n)
                linea = f"El factorial de: {n} es {resultado}"
                archivo.write(linea + "\n")
                archivo.flush()
                print(f"[Consumidor] {linea}")
                procesados += 1
            liberar_turno(id_hilo)

            time.sleep(0.08)

    print(f"\nArchivo '{ARCHIVO}' generado con {procesados} líneas.")


if __name__ == "__main__":
    print("=== Grupo 02 — Algoritmo del Panadero ===\n")

    hilo_productor  = threading.Thread(target=productor,  args=(0,))
    hilo_consumidor = threading.Thread(target=consumidor, args=(1,))

    hilo_productor.start()
    hilo_consumidor.start()
    hilo_productor.join()
    hilo_consumidor.join()

    print("\nEjecución finalizada.")


# -----------------------------------------------------------
# Respuestas preguntas a) - f)
# -----------------------------------------------------------

"""
a) Que problema resuelve el Algoritmo del Panadero?
   El problema principal es la exclusión mutua: cuando dos hilos acceden
   al mismo recurso compartido al mismo tiempo (en este caso el buffer y
   el archivo), los datos se pueden corromper o sobrescribir. El algoritmo
   garantiza que solo un hilo entra a la sección crítica a la vez, y lo
   hace completamente en software, sin necesitar funciones especiales del
   sistema operativo como mutexes o semáforos.

b) Como funciona el mecanismo interno?
   Funciona en tres pasos. Primero, el hilo anuncia que va a elegir turno
   (eligiendo[i] = True) para que los demás no lean un valor incompleto.
   Segundo, toma el turno más alto disponible más uno. Tercero, antes de
   entrar revisa a todos los demás hilos: si alguno tiene un turno menor,
   o el mismo turno pero menor índice, espera. Cuando nadie tiene
   prioridad, entra a la sección crítica. Al salir, devuelve su turno a 0.

c) Por que el código no produce deadlock?
   Para que haya deadlock tendría que ocurrir que el hilo A espera al B
   y al mismo tiempo el hilo B espera al A. Eso significaría que el turno
   de B es menor que el de A, y también que el de A es menor que el de B,
   lo cual es una contradicción: dos números no pueden ser menores entre
   sí al mismo tiempo. Siempre hay uno con turno menor que puede avanzar,
   así que el deadlock es imposible por diseño.

d) Cuáles son las limitaciones del algoritmo?
   La más importante es el busy-waiting: mientras un hilo espera su turno,
   sigue ejecutándose en el procesador sin hacer nada útil, lo que consume
   CPU innecesariamente. Además, a medida que aumenta el número de hilos,
   cada uno tiene que revisar a todos los demás antes de entrar. Por último,
   requiere que todos los hilos compartan la misma memoria, por lo que no
   funciona para procesos en distintas máquinas.

e) Que pasa si dos hilos sacan el mismo número de turno?
   Puede ocurrir si ambos leen el máximo actual antes de que alguno haya
   escrito su nuevo turno. Se resuelve con el índice: el par (turno, índice)
   siempre tiene un ganador porque dos hilos no pueden tener el mismo índice.
   El de menor índice entra primero. La variable eligiendo[] existe para
   reducir las chances de que esto ocurra.

f) Cuando usarías Bakery en un proyecto real? Comparación con otras técnicas:

   vs Lock (Grupo 1):
     El Lock es más eficiente porque el hilo que no puede entrar se bloquea
     y deja de consumir CPU hasta que le toque. Bakery sigue girando.
     La ventaja de Bakery es que se implementa sin ninguna herramienta del
     SO, útil en hardware embebido donde esas primitivas no existen.

   vs Semáforos (Grupo 4):
     El semáforo permite que hasta N hilos accedan al recurso al mismo
     tiempo, lo que sirve cuando hay varios slots disponibles. Bakery
     garantiza acceso exclusivo a uno solo. Si el problema requiere
     limitar el acceso a más de uno, el semáforo es la opción correcta.

   vs Monitores (Grupo 3):
     El monitor encapsula los datos y la sincronización en un mismo objeto,
     lo que hace el código más ordenado. Bakery es más bajo nivel y requiere
     manejar todo manualmente. En proyectos grandes el monitor es preferible;
     Bakery sirve para entender qué hay por debajo de esas abstracciones.

   En resumen, usaríamos Bakery en sistemas donde no hay un SO que provea
   primitivas de sincronización, o para demostrar que la exclusión mutua
   se puede resolver solo con lógica de software.
"""