import re
import os


class AnalizadorLexico:
    def __init__(self):
        # Rutas para el escáner interno (Consola)
        self.archivos_proyecto = ['main.py', 'Logica/Arboles.py', 'Logica/Analizador.py', 'Logica/Generador.py',
                                  'Logica/Nodo.py']

        # Diccionarios para analizar la expresión que el usuario pone en la INTERFAZ
        self.palabras_control = {'if', 'else', 'while', 'for', 'switch', 'return', 'break', 'continue'}
        self.funciones_conocidas = {'print', 'leer', 'input', 'write', 'read', 'main'}
        self.operadores_conocidos = {'+', '-', '*', '/', '^', '√', '<', '>', '==', '!=', '<=', '>='}

    def generar_reporte_texto(self, ecuacion):
        """Este es el que se muestra en la INTERFAZ VISUAL en cada módulo"""
        if not ecuacion: return ""

        conteos = {
            "Variables": 0,
            "Constantes": 0,
            "Expresiones (Operadores)": 0,
            "Inst. de Asignación (=)": 0,
            "Inst. de Control": 0,
            "Funciones": 0
        }

        # 1. Asignación simple
        if '=' in ecuacion and '==' not in ecuacion:
            conteos["Inst. de Asignación (=)"] += 1

        # 2. Extraer todos los tokens de la expresión del usuario
        tokens = re.findall(r"([a-zA-Z_]\w*|\d+(?:\.\d+)?|[+*/^√=<>!-]+)", ecuacion)

        # 3. Clasificar cada token
        for token in tokens:
            if token in self.palabras_control:
                conteos["Inst. de Control"] += 1
            elif token in self.funciones_conocidas:
                conteos["Funciones"] += 1
            elif token in self.operadores_conocidos:
                conteos["Expresiones (Operadores)"] += 1
            elif token.replace('.', '', 1).isdigit():
                conteos["Constantes"] += 1
            elif token.isalpha() or token.replace('_', '').isalpha():
                conteos["Variables"] += 1

        # 4. Construir el texto final sin usar barras invertidas en el f-string (Solución Python 3.11)
        texto_final = "\n\n📊 REPORTE LÉXICO DE LA EXPRESIÓN:\n"
        for categoria, cantidad in conteos.items():
            texto_final += f" ├─ {categoria}: {cantidad}\n"

        return texto_final

    def analizar_codigo_interno(self):
        """Lógica para el escáner interno de los archivos .py"""
        conteos = {
            "Variables (Identificadores)": 0, "Constantes (Números/Textos)": 0, "Expresiones (Op)": 0,
            "Instrucciones de Asignación (=)": 0, "Instrucciones de Control": 0, "Funciones": 0
        }
        for ruta in self.archivos_proyecto:
            if not os.path.exists(ruta): continue
            with open(ruta, 'r', encoding='utf-8') as archivo:
                codigo = archivo.read()
                codigo_limpio = re.sub(r'\"[^\"]*\"|\'[^\']*\'', '""', codigo)

                cadenas = re.findall(r'\"[^\"]*\"|\'[^\']*\'', codigo)
                numeros = re.findall(r'\b\d+(?:\.\d+)?\b', codigo)
                conteos["Constantes (Números/Textos)"] += len(cadenas) + len(numeros)
                conteos["Instrucciones de Asignación (=)"] += len(re.findall(r'(?<![=<>!])=(?![=])', codigo_limpio))

                funciones = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', codigo_limpio)
                conteos["Funciones"] += len(funciones)

                for op in ['+', '-', '*', '/', '%', '^', '<', '>', '==', '!=', '<=', '>=']:
                    conteos["Expresiones (Op)"] += codigo_limpio.count(op)

                palabras = re.findall(r'\b[a-zA-Z_]\w*\b', codigo_limpio)
                for p in palabras:
                    if p in self.palabras_control:
                        conteos["Instrucciones de Control"] += 1
                    elif p not in funciones:
                        conteos["Variables (Identificadores)"] += 1
        return conteos

    def imprimir_reporte_consola(self):
        """Imprime el análisis del código fuente en la terminal negra"""
        conteos = self.analizar_codigo_interno()
        print("\n" + "█" * 60 + "\n 🔍 REPORTE GLOBAL: ANALIZADOR LÉXICO INTERNO DEL PROYECTO\n" + "█" * 60)
        for categoria, total in conteos.items(): print(f" [ ✔ ] {categoria}: {total}")
        print("-" * 60 + "\n Análisis completado con éxito.\n")