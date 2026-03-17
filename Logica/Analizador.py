import re


class AnalizadorLexico:
    def __init__(self):
        # Diccionarios de palabras clave (Puedes agregar más si la ingeniera lo pide)
        self.palabras_control = {'if', 'else', 'while', 'for', 'switch', 'return', 'break', 'continue'}
        self.funciones_conocidas = {'print', 'leer', 'input', 'write', 'read', 'main'}
        self.operadores_conocidos = {'+', '-', '*', '/', '^', '√', '<', '>', '==', '!=', '<=', '>='}

    def analizar_conteo(self, texto_codigo):
        """
        Recibe todo el texto del usuario y devuelve un diccionario con los conteos.
        """
        # Resultados inicializados en 0
        conteos = {
            "Variables": 0,
            "Constantes": 0,
            "Operadores": 0,
            "Inst. de Asignación": 0,
            "Inst. de Control": 0,
            "Funciones": 0
        }

        # Separar el texto por líneas para analizar línea por línea
        lineas = texto_codigo.split('\n')

        for linea in lineas:
            # 1. Contar Instrucciones de Asignación (Si hay un '=' que no sea '==')
            if '=' in linea and '==' not in linea:
                conteos["Inst. de Asignación"] += 1

            # Extraer todas las palabras (letras), números y símbolos usando Regex
            # Esta regla separa letras agrupadas, números y operadores individuales
            tokens = re.findall(r"([a-zA-Z_]\w*|\d+(?:\.\d+)?|[+*/^√=<>!-]+)", linea)

            for token in tokens:
                if token in self.palabras_control:
                    conteos["Inst. de Control"] += 1

                elif token in self.funciones_conocidas:
                    conteos["Inst. de Funciones"] += 1

                elif token in self.operadores_conocidos:
                    conteos["Operadores"] += 1

                elif token.replace('.', '', 1).isdigit():
                    conteos["Constantes"] += 1

                elif token.isalpha() or token.replace('_', '').isalpha():
                    # Si es texto y no fue ni control ni función, es una Variable
                    conteos["Variables"] += 1

        return conteos