import re


class AnalizadorLexico:
    def __init__(self):
        self.palabras_control = {'if', 'else', 'while', 'for', 'switch', 'return', 'break', 'continue'}
        self.funciones_conocidas = {'print', 'leer', 'input', 'write', 'read', 'main'}
        self.operadores_conocidos = {'+', '-', '*', '/', '^', '√', '<', '>', '==', '!=', '<=', '>='}

    def analizar_conteo(self, texto_codigo):
        conteos = {
            "Variables": 0,
            "Constantes": 0,
            "Expresiones": 0,  # <-- Cambiado para coincidir con el pizarrón
            "Inst. de Asignación": 0,
            "Inst. de Control": 0,
            "Funciones": 0
        }

        lineas = texto_codigo.split('\n')
        for linea in lineas:
            if '=' in linea and '==' not in linea:
                conteos["Inst. de Asignación"] += 1

            tokens = re.findall(r"([a-zA-Z_]\w*|\d+(?:\.\d+)?|[+*/^√=<>!-]+)", linea)
            for token in tokens:
                if token in self.palabras_control:
                    conteos["Inst. de Control"] += 1
                elif token in self.funciones_conocidas:
                    conteos["Funciones"] += 1
                elif token in self.operadores_conocidos:
                    conteos["Expresiones"] += 1
                elif token.replace('.', '', 1).isdigit():
                    conteos["Constantes"] += 1
                elif token.isalpha() or token.replace('_', '').isalpha():
                    conteos["Variables"] += 1

        return conteos

    def generar_reporte_texto(self, ecuacion):
        """Genera un texto bonito con el conteo para pegarlo al final de los procedimientos"""
        conteos = self.analizar_conteo(ecuacion)
        texto_final = "\n\n📊 REPORTE DE CONTEO LÉXICO:\n"
        for categoria, cantidad in conteos.items():
            texto_final += f" ├─ {categoria}: {cantidad}\n"
        return texto_final