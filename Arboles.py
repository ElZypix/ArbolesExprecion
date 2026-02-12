import re#Manejo de expresiones regulares
#Sirve para dibujar el grafico
import networkx as nx
import matplotlib.pyplot as plt

import time

import math#Funciones matematicas

from Nodo import Nodo#conecta con otro archivo

class CalculadoraArbol:
    def __init__(self):
        self.preferencia = {
            '^': 3, '√': 3,
            '*': 2, '/': 2,
            '+': 1, '-': 1,
            '(': 0
        }

    def infija_a_posfija(self, ecuacion):
        tockens = re.findall(r"(\d+|[/√+*^()-])", ecuacion)
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
                while pila and pila[-1] != '(' and self.preferencia.get(pila[-1], 0) >= self.preferencia.get(tocken, 0):
                    salida.append(pila.pop())

                pila.append(tocken)

        while pila:
            salida.append(pila.pop())

        return salida

    def construir_arbol(self, lista_posfija):
        pila_arbol = []

        for tocken in lista_posfija:
            if tocken.isdigit():
                nodo = Nodo(tocken)
                pila_arbol.append(nodo)
            else:
                nuevo_nodo = Nodo(tocken)

                if tocken == '√':
                    if pila_arbol:
                        nuevo_nodo.derecha = pila_arbol.pop()
                else:
                    if len(pila_arbol) >= 2:
                        nuevo_nodo.derecha = pila_arbol.pop()
                        nuevo_nodo.izquierda = pila_arbol.pop()

                pila_arbol.append(nuevo_nodo)


        return pila_arbol.pop() if pila_arbol else None

    def graficar(self, raiz, ecuacion_texto):
        """Dibuja el árbol usando NetworkX"""
        if not raiz:
            print("No hay árbol para dibujar.")
            return

        G = nx.DiGraph()
        labels = {}
        pos = {}
        contador_x = [0]

        def procesar_nodo(nodo, nivel):
            if not nodo: return

            # Izquierda
            if nodo.izquierda:
                G.add_edge(id(nodo), id(nodo.izquierda))
                procesar_nodo(nodo.izquierda, nivel + 1)

            # Centro (Nodo actual)
            nodo_id = id(nodo)
            labels[nodo_id] = nodo.valor
            pos[nodo_id] = (contador_x[0], -nivel)
            contador_x[0] += 1

            # Derecha
            if nodo.derecha:
                G.add_edge(id(nodo), id(nodo.derecha))
                procesar_nodo(nodo.derecha, nivel + 1)

        procesar_nodo(raiz, 0)

        plt.figure(figsize=(10, 6))
        plt.title(f"Árbol: {ecuacion_texto}")
        nx.draw(G, pos, labels=labels, with_labels=True,
                node_size=2500, node_color="lightgreen",
                edge_color="black", font_size=12, font_weight="bold", arrows=False)

        plt.axis("off")
        plt.show()

    def evaluar(self, nodo):
        if not nodo:
            return 0

        if nodo.izquierda is None and nodo.derecha is None:
            return float(nodo.valor)

        valor_izq = self.evaluar(nodo.izquierda) if nodo.izquierda else 0
        valor_der = self.evaluar(nodo.derecha) if nodo.derecha else 0

        op = nodo.valor

        if op == '+': return valor_izq + valor_der
        if op == '-': return valor_izq - valor_der
        if op == '*': return valor_izq * valor_der
        if op == '/':
            if valor_der == 0:
                return ValueError("No se puede dividir entre cero")
            else:
                return valor_izq / valor_der
        if op == '^': return pow(valor_izq, valor_der)

        if op == '√':
            return math.sqrt(valor_der)

        return 0


def main():
    calc = CalculadoraArbol()  # Instanciamos la clase una sola vez

    MENU = """
    === ARBOLES DE EXPRESION ===
    1.- Ingresar expresión y Graficar
    2.- Salir
    Seleccione una opción: """

    while True:
        opcion = input(MENU)

        if opcion == "1":
            print("Ingrese la ecuación (ej: (6/3)*5 ):")
            ecuacion = input(">> ")

            try:
                # 1. Obtener Posfija
                postfix = calc.infija_a_posfija(ecuacion)
                print(f"Postfija: {postfix}")

                # 2. Construir Árbol
                raiz = calc.construir_arbol(postfix)

                # --- CALCULAR RESULTADO ---
                resultado = calc.evaluar(raiz)
                print(f"El resultado es: {resultado}")

                # 3. Graficar
                print("Generando gráfico...")
                time.sleep(1)
                calc.graficar(raiz, ecuacion)

            except Exception as e:
                print(f"Error al procesar la ecuación: {e}")

        elif opcion == "2":
            print("Saliendo...")
            time.sleep(1)
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()