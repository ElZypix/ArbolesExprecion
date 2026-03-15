import re
from Logica.Nodo import Nodo

class CalculadoraArbol:
    def __init__(self):
        # Preferencia de operadores (jerarquía)
        self.preferencia = {'^': 3, '√': 3, '*': 2, '/': 2, '+': 1, '-': 1, '(': 0}

    def es_operando(self, token):
        """Devuelve True si el token es una variable (letra) o un número"""
        if token.isalpha():  # Es una letra (ej. A, B, X)
            return True
        if token.replace('.', '', 1).isdigit():  # Es un número (ej. 10, 3.14)
            return True
        return False

    def infija_a_posfija(self, ecuacion):
        # 1. Limpieza y Tokenización (AHORA ACEPTA LETRAS)
        tokens_originales = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
        tokens_nuevos = []

        if not tokens_originales: return []

        # Validaciones iniciales
        if tokens_originales[0] in ['*', '/', '^', ')']:
            raise ValueError(f"Inicio inválido con '{tokens_originales[0]}'")

        operadores = ['+', '-', '*', '/', '^', '√']

        for i, token in enumerate(tokens_originales):
            # Inyección del '2' para raíces cuadradas implícitas (ej: √16 -> 2√16)
            if token == '√':
                if i == 0 or tokens_originales[i - 1] in operadores or tokens_originales[i - 1] == '(':
                    tokens_nuevos.append('2')

            tokens_nuevos.append(token)

        # 2. Algoritmo Shunting-yard
        salida = []
        pila = []

        for token in tokens_nuevos:
            if self.es_operando(token):  # Usamos nuestra nueva función para aceptar letras y números
                salida.append(token)
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                if not pila: raise ValueError("Paréntesis desbalanceados")
                pila.pop()
            else:
                while pila and pila[-1] != '(' and self.preferencia.get(pila[-1], 0) >= self.preferencia.get(token, 0):
                    salida.append(pila.pop())
                pila.append(token)

        while pila:
            salida.append(pila.pop())

        return salida

    def construir_arbol(self, lista_posfija):
        pila_arbol = []
        for token in lista_posfija:
            if self.es_operando(token): # Acepta letras y números como hojas del árbol
                pila_arbol.append(Nodo(token))
            else:
                if len(pila_arbol) < 2: raise ValueError("Faltan operandos")
                nodo = Nodo(token)
                nodo.derecha = pila_arbol.pop()
                nodo.izquierda = pila_arbol.pop()
                pila_arbol.append(nodo)

        return pila_arbol.pop() if pila_arbol else None

    # ==========================================
    # NUEVOS MÉTODOS: RECORRIDOS (NOTACIONES)
    # ==========================================

    def obtener_prefija(self, nodo):
        """Recorrido Preorden (Raíz, Izquierda, Derecha) - Notación Polaca"""
        if nodo is None:
            return []
        return [nodo.valor] + self.obtener_prefija(nodo.izquierda) + self.obtener_prefija(nodo.derecha)

    def obtener_infija(self, nodo):
        """Recorrido Inorden (Izquierda, Raíz, Derecha) - Notación Normal"""
        if nodo is None:
            return []
        return self.obtener_infija(nodo.izquierda) + [nodo.valor] + self.obtener_infija(nodo.derecha)

    def obtener_postfija(self, nodo):
        """Recorrido Postorden (Izquierda, Derecha, Raíz) - Notación Polaca Inversa"""
        if nodo is None:
            return []
        return self.obtener_postfija(nodo.izquierda) + self.obtener_postfija(nodo.derecha) + [nodo.valor]

    # ==========================================
    # EVALUACIÓN MATEMÁTICA (Solo para números)
    # ==========================================

    def evaluar(self, nodo):
        # Versión simple que solo devuelve el resultado
        res, _ = self.evaluar_con_pasos(nodo)
        return res

    def evaluar_con_pasos(self, nodo):
        """
        Devuelve una tupla: (resultado_numerico, lista_de_pasos_texto)
        Nota: Esto solo funcionará si la ecuación tiene puros números.
        """
        if not nodo: return 0, []

        # Caso Base: Es un número o variable (Hoja)
        if nodo.izquierda is None and nodo.derecha is None:
            try:
                return float(nodo.valor), []
            except ValueError:
                raise ValueError(f"No se puede calcular matemáticamente la variable '{nodo.valor}'")

        # Paso Recursivo: Evaluar hijos
        val_izq, pasos_izq = self.evaluar_con_pasos(nodo.izquierda) if nodo.izquierda else (0, [])
        val_der, pasos_der = self.evaluar_con_pasos(nodo.derecha) if nodo.derecha else (0, [])

        # Operación Actual
        op = nodo.valor
        res = 0
        paso_texto = ""

        try:
            if op == '+':
                res = val_izq + val_der
                paso_texto = f"{self._fmt(val_izq)} + {self._fmt(val_der)} = {self._fmt(res)}"
            elif op == '-':
                res = val_izq - val_der
                paso_texto = f"{self._fmt(val_izq)} - {self._fmt(val_der)} = {self._fmt(res)}"
            elif op == '*':
                res = val_izq * val_der
                paso_texto = f"{self._fmt(val_izq)} * {self._fmt(val_der)} = {self._fmt(res)}"
            elif op == '/':
                if val_der == 0: raise ValueError("División por cero")
                res = val_izq / val_der
                paso_texto = f"{self._fmt(val_izq)} / {self._fmt(val_der)} = {self._fmt(res)}"
            elif op == '^':
                res = pow(val_izq, val_der)
                paso_texto = f"{self._fmt(val_izq)} ^ {self._fmt(val_der)} = {self._fmt(res)}"
            elif op == '√':
                if val_izq == 0:
                    res = 0
                else:
                    res = pow(val_der, 1 / val_izq)
                paso_texto = f"Raíz {self._fmt(val_izq)} de {self._fmt(val_der)} = {self._fmt(res)}"
        except Exception as e:
            raise ValueError(f"Error matemático en {op}: {str(e)}")

        # Combinar pasos: pasos de los hijos + paso actual
        todos_los_pasos = pasos_izq + pasos_der + [paso_texto]
        return res, todos_los_pasos

    def _fmt(self, num):
        """Ayuda visual: Quita el .0 si es entero"""
        if num == int(num): return str(int(num))
        return f"{num:.2f}"