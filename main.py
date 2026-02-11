import math
import re
import networkx as nx
import matplotlib.pyplot as plt

ecuacion = "6/3^2*1^(3-2)√9"
print(6/pow(3,2)*pow(1,(3-2))*math.sqrt(9))

tockens = re.findall(r"(\d+|[/√+*^()-])", ecuacion)

preferencia = {
    '^': 3,
    '√': 3,
    '*': 2,
    '/': 2,
    '+': 1,
    '-': 1,
    '(': 0
}

salida = []

pila = []

for tocken in tockens:
    if tocken.isdigit():
        salida.append(tocken)

    elif tocken == '(':
        pila.append(tocken)

    elif tocken == ')':
        while pila[-1] != '(':
            salida.append(pila.pop())
        pila.pop()

    else:
        while pila and pila[-1] != '(' and preferencia.get(pila[-1], 0) >= preferencia.get(tocken, 0):
            salida.append(pila.pop())

        pila.append(tocken)

while pila:
    salida.append(pila.pop())

print(salida)

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

    def __str__(self):
        return str(self.valor)



pila_arbol = []

for token in salida:
    if token.isdigit():
        nuevo_nodo = Nodo(token)
        pila_arbol.append(nuevo_nodo)

    else:
        nuevo_nodo = Nodo(token)

        nodo_derecho = pila_arbol.pop()
        nodo_izquierdo = pila_arbol.pop()

        nuevo_nodo.derecha = nodo_derecho
        nuevo_nodo.izquierda = nodo_izquierdo

        pila_arbol.append(nuevo_nodo)

raiz = pila_arbol.pop()

print("Raiz del arbol:", raiz.valor)
print("Hijo Izquierdo:", raiz.izquierda.valor)
print("Hijo Derecho:", raiz.derecha.valor)


# --- VISUALIZACION MEJORADA ---
def dibujar_arbol(raiz):
    G = nx.DiGraph()
    labels = {}
    pos = {}  # Aquí guardaremos las coordenadas (X, Y) calculadas manualmente

    # Variable "nonlocal" para llevar la cuenta de la posición horizontal
    # Usamos una lista para poder modificarla dentro de la funcion recursiva
    contador_x = [0]

    # 1. Construir el Grafo y calcular posiciones al mismo tiempo
    def procesar_nodo(nodo, nivel):
        if not nodo:
            return

        # --- PASO A: Ir lo más a la izquierda posible ---
        if nodo.izquierda:
            # Conectamos en NetworkX
            G.add_edge(id(nodo), id(nodo.izquierda))
            # Recursividad bajando de nivel
            procesar_nodo(nodo.izquierda, nivel + 1)

        # --- PASO B: Procesar el nodo actual (Centro) ---
        nodo_id = id(nodo)
        labels[nodo_id] = nodo.valor

        # La magia: X aumenta secuencialmente, Y es negativo (hacia abajo)
        pos[nodo_id] = (contador_x[0], -nivel)
        contador_x[0] += 1  # Nos movemos a la derecha para el siguiente nodo

        # --- PASO C: Ir a la derecha ---
        if nodo.derecha:
            G.add_edge(id(nodo), id(nodo.derecha))
            procesar_nodo(nodo.derecha, nivel + 1)

    # Iniciamos el proceso desde la raíz (nivel 0)
    procesar_nodo(raiz, 0)

    # 2. Dibujar con las posiciones exactas
    plt.figure(figsize=(10, 6))

    # Dibujar nodos y aristas
    nx.draw(G, pos,
            labels=labels,  # Usamos labels aquí directo
            with_labels=True,  # Que sí muestre el texto
            node_size=2500,  # Bolitas más grandes
            node_color="lightgreen",  # Color más bonito
            edge_color="black",
            font_size=12,
            font_weight="bold",
            arrows=False)  # Sin flechas se ve más limpio a veces

    plt.title(f"Árbol de Expresión: {ecuacion}")
    plt.axis("off")  # Ocultar ejes X/Y feos
    plt.show()


# --- LLAMADA FINAL ---
dibujar_arbol(raiz)