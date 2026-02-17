import re#Manejo de expresiones regulares

from Logica.Nodo import Nodo#conecta con otro archivo

class CalculadoraArbol:
    def __init__(self):
        self.preferencia = {
            '^': 3, '√': 3,
            '*': 2, '/': 2,
            '+': 1, '-': 1,
            '(': 0
        }

    def infija_a_posfija(self, ecuacion):
        # 1. Obtener tokens
        tokens_originales = re.findall(r"(\d+|[/√+*^()-])", ecuacion)
        tokens_nuevos = []

        # --- VALIDACIÓN 1: NO EMPEZAR CON OPERADOR BINARIO ---
        # Si lo primero es un *, /, ^, etc. (Excepto √ o - que pueden ser unarios)
        if tokens_originales and tokens_originales[0] in ['*', '/', '^', ')']:
            raise ValueError(f"La ecuación no puede iniciar con '{tokens_originales[0]}'")

        # Definimos quiénes son operadores peligrosos si se juntan
        operadores = ['+', '-', '*', '/', '^', '√']

        for i, token in enumerate(tokens_originales):
            # --- VALIDACIÓN 2: CHOQUE DE OPERADORES (El error de 3+*2) ---
            if i > 0:
                previo = tokens_originales[i - 1]

                # Si el actual es operador Y el anterior también fue operador
                # Ejemplo: "3 + *" -> previo='+', token='*' -> ¡ERROR!
                if token in ['+', '*', '/', '^'] and previo in operadores:
                    raise ValueError(
                        f"Error de sintaxis: No puede haber dos operadores seguidos ('{previo}' y '{token}')")

                # Validación extra: Paréntesis vacío "()"
                if token == ')' and previo == '(':
                    raise ValueError("Error: Paréntesis vacíos '()'")

            # --- Lógica de inyección del 2 (Tu código anterior) ---
            if token == '√':
                if i == 0 or tokens_originales[i - 1] in ['+', '-', '*', '/', '^', '(', '√']:
                    tokens_nuevos.append('2')

            tokens_nuevos.append(token)

        # --- VALIDACIÓN 3: NO TERMINAR CON OPERADOR ---
        if tokens_nuevos and tokens_nuevos[-1] in operadores:
            raise ValueError("La ecuación no puede terminar en operador.")

        # 3. Algoritmo Shunting-yard (Esto sigue igual)
        salida = []
        pila = []

        for tocken in tokens_nuevos:
            if tocken.isdigit():
                salida.append(tocken)
            elif tocken == '(':
                pila.append(tocken)
            elif tocken == ')':
                # Validación de paréntesis balanceados
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                if not pila: raise ValueError("Error: Paréntesis de cierre ')' sin apertura.")
                pila.pop()
            else:
                while pila and pila[-1] != '(' and self.preferencia.get(pila[-1], 0) >= self.preferencia.get(tocken, 0):
                    salida.append(pila.pop())
                pila.append(tocken)

        while pila:
            op = pila.pop()
            if op == '(': raise ValueError("Error: Paréntesis de apertura '(' sin cierre.")
            salida.append(op)

        return salida

    def construir_arbol(self, lista_posfija):
        pila_arbol = []

        for token in lista_posfija:
            if token.isdigit():
                nodo = Nodo(token)
                pila_arbol.append(nodo)
            else:
                nuevo_nodo = Nodo(token)

                # --- VALIDACIÓN NUEVA ---
                if len(pila_arbol) < 2:
                    raise ValueError(f"Expresión mal formada: Falta un número para el operador '{token}'")
                # ------------------------

                nuevo_nodo.derecha = pila_arbol.pop()
                nuevo_nodo.izquierda = pila_arbol.pop()

                pila_arbol.append(nuevo_nodo)

        if len(pila_arbol) != 1:
             raise ValueError("Expresión incompleta (sobran números o faltan operadores)")

        return pila_arbol.pop() if pila_arbol else None

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
                raise ValueError("No se puede dividir entre cero")
            else:
                return valor_izq / valor_der
        if op == '^': return pow(valor_izq, valor_der)

        if op == '√' or op == '^':
            if valor_der < 0 and (valor_izq % 2 == 0 or (0 < valor_izq < 1)):
                raise ValueError("Resultado imaginario: No se puede raíz par de negativo")

        if op == '√':
            if valor_izq == 0: return 0
            else:
                return pow(valor_der, 1/valor_izq)

        return 0