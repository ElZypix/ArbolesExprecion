import re
from Logica.Nodo import Nodo


class CalculadoraArbol:
    def __init__(self):
        self.preferencia = {'^': 3, '√': 3, '*': 2, '/': 2, '+': 1, '-': 1, '(': 0}

    def es_operando(self, token):
        if token.isalpha(): return True
        if token.replace('.', '', 1).isdigit(): return True
        return False

    def infija_a_posfija(self, ecuacion):
        tokens_originales = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
        tokens_nuevos = []
        if not tokens_originales: return []
        if tokens_originales[0] in ['*', '/', '^', ')']: raise ValueError(f"Inicio inválido")

        operadores = ['+', '-', '*', '/', '^', '√']
        for i, token in enumerate(tokens_originales):
            if token == '√':
                if i == 0 or tokens_originales[i - 1] in operadores or tokens_originales[i - 1] == '(':
                    tokens_nuevos.append('2')
            tokens_nuevos.append(token)

        salida = []
        pila = []
        for token in tokens_nuevos:
            if self.es_operando(token):
                salida.append(token)
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(': salida.append(pila.pop())
                if not pila: raise ValueError("Paréntesis desbalanceados")
                pila.pop()
            else:
                while pila and pila[-1] != '(' and self.preferencia.get(pila[-1], 0) >= self.preferencia.get(token, 0):
                    salida.append(pila.pop())
                pila.append(token)
        while pila: salida.append(pila.pop())
        return salida

    def construir_arbol(self, lista_posfija):
        pila_arbol = []
        for token in lista_posfija:
            if self.es_operando(token):
                pila_arbol.append(Nodo(token))
            else:
                if len(pila_arbol) < 2: raise ValueError("Faltan operandos")
                nodo = Nodo(token)
                nodo.derecha = pila_arbol.pop()
                nodo.izquierda = pila_arbol.pop()
                pila_arbol.append(nodo)
        return pila_arbol.pop() if pila_arbol else None

    def obtener_prefija(self, nodo):
        if nodo is None: return []
        return [nodo.valor] + self.obtener_prefija(nodo.izquierda) + self.obtener_prefija(nodo.derecha)

    def obtener_infija(self, nodo):
        if nodo is None: return []
        return self.obtener_infija(nodo.izquierda) + [nodo.valor] + self.obtener_infija(nodo.derecha)

    def obtener_postfija(self, nodo):
        if nodo is None: return []
        return self.obtener_postfija(nodo.izquierda) + self.obtener_postfija(nodo.derecha) + [nodo.valor]

    def evaluar(self, nodo):
        res, _ = self.evaluar_con_pasos(nodo)
        return res

    def evaluar_con_pasos(self, nodo):
        if not nodo: return "", []
        if nodo.izquierda is None and nodo.derecha is None:
            try:
                num = float(nodo.valor)
                return int(num) if num.is_integer() else num, []
            except ValueError:
                return str(nodo.valor), []

        val_izq, pasos_izq = self.evaluar_con_pasos(nodo.izquierda) if nodo.izquierda else ("", [])
        val_der, pasos_der = self.evaluar_con_pasos(nodo.derecha) if nodo.derecha else ("", [])

        op = nodo.valor
        paso_texto = ""
        res = ""
        son_numeros = isinstance(val_izq, (int, float)) and isinstance(val_der, (int, float))

        try:
            if son_numeros:
                if op == '+':
                    res = val_izq + val_der
                elif op == '-':
                    res = val_izq - val_der
                elif op == '*':
                    res = val_izq * val_der
                elif op == '/':
                    if val_der == 0: raise ValueError("División por cero")
                    res = val_izq / val_der
                elif op == '^':
                    res = pow(val_izq, val_der)
                elif op == '√':
                    res = pow(val_der, 1 / val_izq) if val_izq != 0 else 0

                if isinstance(res, float) and res.is_integer(): res = int(res)
                paso_texto = f"✔ Operación: {val_izq} {op} {val_der} = {res}"
            else:
                if op == '√':
                    res = f"√{val_der}" if val_izq in [2, "2"] else f"{val_izq}√{val_der}"
                else:
                    if op == '+' and val_izq == 0:
                        res = val_der
                    elif op == '+' and val_der == 0:
                        res = val_izq
                    elif op == '*' and val_izq == 1:
                        res = val_der
                    elif op == '*' and val_der == 1:
                        res = val_izq
                    elif op == '*' and (val_izq == 0 or val_der == 0):
                        res = 0
                    else:
                        res = f"({val_izq} {op} {val_der})"
                paso_texto = f"📌 Agrupando: {val_izq} y {val_der} con '{op}' ➔ {res}"
        except Exception as e:
            raise ValueError(f"Error en '{op}': {str(e)}")

        return res, pasos_izq + pasos_der + [paso_texto]