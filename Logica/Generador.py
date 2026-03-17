class GeneradorCodigo:
    def __init__(self):
        self.contador_temporales = 1

    def es_operando(self, token):
        """Reutilizamos la lógica para detectar si es letra o número"""
        if token.isalpha():
            return True
        if token.replace('.', '', 1).isdigit():
            return True
        return False

    def generar_todo(self, lista_posfija):
        """
        Recibe la lista postfija y genera las 3 salidas a la vez.
        Retorna: (lista_codigo_p, lista_triplos, lista_cuadruplos)
        """
        codigo_p = []
        triplos = []
        cuadruplos = []
        pila = []

        # Reiniciamos el contador cada vez que se evalúa una nueva ecuación
        self.contador_temporales = 1

        # Diccionario para traducir operadores a instrucciones de ensamblador (Código P)
        map_op = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '^': 'POW', '√': 'SQRT'}

        for token in lista_posfija:
            if self.es_operando(token):
                # Si es un número o variable, entra a la pila temporal
                pila.append(token)

                # Para Código P: La instrucción de cargar a la pila es LOD (Load)
                codigo_p.append(f"LOD {token}")
            else:
                # Es un operador. Sacamos los dos últimos elementos de la pila
                if len(pila) < 2:
                    continue  # Defensa por si hay un error en la ecuación

                # ¡Recuerda la regla de oro que expusiste! Sale primero el derecho (b)
                arg2 = pila.pop()
                arg1 = pila.pop()

                # Creamos la variable temporal (T1, T2, etc.)
                temporal = f"T{self.contador_temporales}"
                self.contador_temporales += 1

                # 1. Generar Cuádruplo: (Operador, Arg1, Arg2, Resultado)
                cuadruplos.append((token, arg1, arg2, temporal))

                # 2. Generar Triplo: (Operador, Arg1, Arg2)
                # Nota: En triplos formales se usa el número de línea, pero usar T1, T2
                # es mucho más fácil de leer para la revisión de la ingeniera.
                triplos.append((token, arg1, arg2))

                # 3. Generar Código P: Solo se llama a la operación (ej. ADD, MUL)
                codigo_p.append(map_op.get(token, token))

                # Guardamos el resultado temporal de vuelta en la pila
                # para que la siguiente operación pueda usar este resultado
                pila.append(temporal)

        return codigo_p, triplos, cuadruplos