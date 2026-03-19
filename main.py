import sys
import re
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QLabel, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QMessageBox, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QTimer

from Logica.Arboles import CalculadoraArbol
from Logica.Generador import GeneradorCodigo
from Logica.Analizador import AnalizadorLexico
from Logica.Nodo import Nodo


class CompiladorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Gui/interfaz.ui", self)

        self.calc = CalculadoraArbol()
        self.gen = GeneradorCodigo()
        self.lexico = AnalizadorLexico()

        # Variables Globales para el Árbol Manual (Anti-Crasheos)
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.mapa_items = {}

        # Variables para Animación
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.paso_animacion)
        self.lista_animacion = []
        self.pila_animacion = []
        self.indice_animacion = 0
        self.tipo_animacion = ""
        self.arbol_animacion = None
        self.modo_animacion = "expresion"

        self.aplicar_estilos_figma()

        # NAVEGACIÓN
        self.btn_EArbol.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_AExpresion.clicked.connect(lambda: self.cambiar_pestana_manual(1))
        self.btn_ENotacion.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn_ANotacion.clicked.connect(lambda: self.cambiar_pestana_manual(3))
        self.btn_Ecodigo.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
        self.btn_ACodigo.clicked.connect(lambda: self.cambiar_pestana_manual(5))

        # ==========================================
        # CONEXIONES DE EVENTOS
        # ==========================================
        # MODULO 1: Expresión a Árbol
        self.inp_Exp.textChanged.connect(self.procesar_expresion_arbol_tiempo_real)

        # MÓDULOS MANUALES (2, 4 y 6) -> Comparten el mismo árbol
        # Pag 2
        self.btn_agregarAexp.clicked.connect(lambda: self.agregar_nodo_manual(self.inp_nod))
        self.btn_EliminarAexp.clicked.connect(self.eliminar_nodo_manual)
        self.btn_limpiarAexp.clicked.connect(self.limpiar_arbol_manual)
        self.inp_nod.returnPressed.connect(lambda: self.agregar_nodo_manual(self.inp_nod))
        # Pag 4
        self.btn_AgregarANota.clicked.connect(lambda: self.agregar_nodo_manual(self.int_NodoANota))
        self.btn_EliminarANota.clicked.connect(self.eliminar_nodo_manual)
        self.btn_LimpiarANota.clicked.connect(self.limpiar_arbol_manual)
        self.int_NodoANota.returnPressed.connect(lambda: self.agregar_nodo_manual(self.int_NodoANota))
        # Pag 6
        self.btn_AgregarACode.clicked.connect(lambda: self.agregar_nodo_manual(self.inp_ACode))
        self.btn_EliminarACode.clicked.connect(self.eliminar_nodo_manual)
        self.btn_LimpiarACode.clicked.connect(self.limpiar_arbol_manual)
        self.inp_ACode.returnPressed.connect(lambda: self.agregar_nodo_manual(self.inp_ACode))

        # MODULO 3: Expresión a Notación (Animación)
        self.pushButton_12.clicked.connect(lambda: self.iniciar_animacion_notacion("prefija"))
        self.pushButton_10.clicked.connect(lambda: self.iniciar_animacion_notacion("infija"))
        self.pushButton_11.clicked.connect(lambda: self.iniciar_animacion_notacion("postfija"))

        # MODULO 4: Árbol a Notación
        self.btn_PrefijaANota.clicked.connect(lambda: self.procesar_arbol_a_notacion("prefija"))
        self.btn_infijaANota.clicked.connect(lambda: self.procesar_arbol_a_notacion("infija"))
        self.btn_postfijaANota.clicked.connect(lambda: self.procesar_arbol_a_notacion("postfija"))

        # MODULO 5: Expresión a Código
        self.btn_CuadruplosECodigo.clicked.connect(
            lambda: self.procesar_codigo(self.inp_ExpCodigo.text(), "cuadruplos", self.area_res5, self.tab_1))
        self.btn_expTriplos.clicked.connect(
            lambda: self.procesar_codigo(self.inp_ExpCodigo.text(), "triplos", self.area_res5, self.tab_1))
        self.btn_CodpECod.clicked.connect(
            lambda: self.procesar_codigo(self.inp_ExpCodigo.text(), "codigop", self.area_res5, self.tab_1))

        # MODULO 6: Árbol a Código
        self.btn_CuadruplosACode.clicked.connect(lambda: self.procesar_arbol_a_codigo("cuadruplos"))
        self.btn_TriplosACode.clicked.connect(lambda: self.procesar_arbol_a_codigo("triplos"))
        self.btn_CodePACode.clicked.connect(lambda: self.procesar_arbol_a_codigo("codigop"))

    # ==========================================
    # LÓGICA DE PROCEDIMIENTOS (LOS 6 MÓDULOS)
    # ==========================================

    # Módulo 1: Expresión a Árbol (Tiempo real)
    def procesar_expresion_arbol_tiempo_real(self, ecuacion):
        if not ecuacion.strip():
            if self.grap_GenArbol1.scene(): self.grap_GenArbol1.scene().clear()
            self.mostrar_texto_en_scroll(self.area_Res1, "")
            return
        try:
            tokens = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
            posfija = self.calc.infija_a_posfija(ecuacion)
            arbol = self.calc.construir_arbol(posfija)

            # Dibujamos
            escena = QGraphicsScene()
            self.grap_GenArbol1.setScene(escena)
            self._dibujar_nodo_interactivo(arbol, escena, 0, 0, 100)

            # PROCEDIMIENTO DETALLADO
            proc = "⚙️ PROCEDIMIENTO:\n\n"
            proc += f"1. Análisis Léxico (Tokens):\n   {' '.join(tokens)}\n\n"
            proc += f"2. Algoritmo Shunting-yard (Postfija):\n   {' '.join(posfija)}\n\n"
            proc += "3. Construcción del Árbol (Regla):\n   - Variables/Números -> Hojas\n   - Operadores -> Nodos Raíz"
            self.mostrar_texto_en_scroll(self.area_Res1, proc)
        except Exception:
            pass

    # Módulos 2, 4 y 6: Árbol Manual y sus Procedimientos
    def cambiar_pestana_manual(self, indice):
        self.stackedWidget.setCurrentIndex(indice)
        self.actualizar_vistas_arbol_manual()

    def al_seleccionar_nodo(self):
        vista = None
        idx = self.stackedWidget.currentIndex()
        if idx == 1:
            vista = self.grap_Arbol2
        elif idx == 3:
            vista = self.grap_3
        elif idx == 5:
            vista = self.grap_Arbol4

        if vista and vista.scene():
            items = vista.scene().selectedItems()
            if items:
                self.nodo_seleccionado = self.mapa_items.get(items[0])
                QTimer.singleShot(0, self.actualizar_vistas_arbol_manual)

    def agregar_nodo_manual(self, input_widget):
        valor = input_widget.text().strip().upper()
        input_widget.clear()
        if not valor: return

        if self.arbol_manual is None:
            self.arbol_manual = Nodo(valor)
            self.nodo_seleccionado = self.arbol_manual
        elif self.nodo_seleccionado:
            if self.calc.es_operando(self.nodo_seleccionado.valor):
                QMessageBox.warning(self, "Inválido", "Los números y variables son 'hojas', no pueden tener hijos.")
                return
            if self.nodo_seleccionado.izquierda is None:
                self.nodo_seleccionado.izquierda = Nodo(valor)
            elif self.nodo_seleccionado.derecha is None:
                self.nodo_seleccionado.derecha = Nodo(valor)
            else:
                QMessageBox.information(self, "Lleno", "El nodo ya tiene sus dos hijos.")
                return
        else:
            QMessageBox.warning(self, "Selección", "Selecciona un nodo padre haciendo clic en él.")
            return
        self.actualizar_vistas_arbol_manual()

    def eliminar_nodo_manual(self):
        if self.nodo_seleccionado and self.arbol_manual:
            if self.nodo_seleccionado == self.arbol_manual:
                self.arbol_manual = None
            else:
                self.eliminar_referencia(self.arbol_manual, self.nodo_seleccionado)
            self.nodo_seleccionado = None
            self.actualizar_vistas_arbol_manual()

    def eliminar_referencia(self, nodo_actual, nodo_a_borrar):
        if not nodo_actual: return
        if nodo_actual.izquierda == nodo_a_borrar: nodo_actual.izquierda = None; return
        if nodo_actual.derecha == nodo_a_borrar: nodo_actual.derecha = None; return
        self.eliminar_referencia(nodo_actual.izquierda, nodo_a_borrar)
        self.eliminar_referencia(nodo_actual.derecha, nodo_a_borrar)

    def limpiar_arbol_manual(self):
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.actualizar_vistas_arbol_manual()

    def actualizar_vistas_arbol_manual(self):
        for v in [self.grap_Arbol2, self.grap_3, self.grap_Arbol4]:
            if v.scene():
                try:
                    v.scene().selectionChanged.disconnect()
                except:
                    pass
                v.scene().clear()
        self.mapa_items = {}

        msg_mod2 = "Empieza agregando la Raíz del árbol."
        msg_mod4 = "1. Construye el árbol.\n2. Haz clic en los botones de Notación."
        msg_mod6 = "1. Construye el árbol.\n2. Haz clic en Cuádruplos/Triplos."

        if self.arbol_manual:
            idx = self.stackedWidget.currentIndex()
            vista_activa = None
            if idx == 1:
                vista_activa = self.grap_Arbol2
            elif idx == 3:
                self.stackedWidget_3.setCurrentIndex(0)
                vista_activa = self.grap_3
            elif idx == 5:
                self.stackedWidget_2.setCurrentIndex(0)
                vista_activa = self.grap_Arbol4

            if vista_activa: self.dibujar_arbol_interactivo(self.arbol_manual, vista_activa)

            try:
                infija = " ".join(self.calc.obtener_infija(self.arbol_manual))
                msg_mod2 = f"✅ Expresión (Recorrido Inorden):\n{infija}\n\n"

                res, pasos = self.calc.evaluar_con_pasos(self.arbol_manual)
                msg_mod2 += "⚙️ PROCEDIMIENTO DE EVALUACIÓN:\n" + "\n".join(pasos) + f"\n\n🎯 RESULTADO FINAL: {res}"
            except Exception:
                msg_mod2 += "⚙️ PROCEDIMIENTO:\n(Expresión con variables, solo se muestra la fórmula, no se puede calcular numéricamente)."

        self.mostrar_texto_en_scroll(self.area_res2, msg_mod2)
        self.mostrar_texto_en_scroll(self.area_res4,
                                     msg_mod4 if not self.arbol_manual else "Árbol listo. Elige una notación.")
        self.mostrar_texto_en_scroll(self.area_res6,
                                     msg_mod6 if not self.arbol_manual else "Árbol listo. Elige generación de código.")

    # Módulo 4: Árbol a Notación (¡AHORA CON ANIMACIÓN EN QGRAPHICSVIEW!)
    def procesar_arbol_a_notacion(self, tipo):
        if not self.arbol_manual:
            QMessageBox.warning(self, "Aviso", "Primero construye un árbol.")
            return

        # Cambiamos a la vista donde está grap_ANotacion2
        self.stackedWidget_3.setCurrentIndex(1)

        if tipo == "prefija":
            self.lista_animacion = self.calc.obtener_prefija(self.arbol_manual)
        elif tipo == "infija":
            self.lista_animacion = self.calc.obtener_infija(self.arbol_manual)
        elif tipo == "postfija":
            self.lista_animacion = self.calc.obtener_postfija(self.arbol_manual)

        self.pila_animacion = []
        self.indice_animacion = 0
        self.tipo_animacion = tipo
        self.modo_animacion = "arbol"  # Le decimos al timer que es la animación del Módulo 4

        # Limpiamos el GraphicsView de platos antes de empezar
        if self.grap_ANotacion2.scene():
            self.grap_ANotacion2.scene().clear()

        self.mostrar_texto_en_scroll(self.area_res4,
                                     f"⚙️ PROCEDIMIENTO:\n\nIniciando recorrido {tipo.capitalize()}...\nGenerando animación de Platos.")

        # Iniciamos animación
        self.timer_animacion.start(800)

    # Módulo 6: Árbol a Código (Funcionalidad y Procedimiento)
    def procesar_arbol_a_codigo(self, tipo):
        if not self.arbol_manual:
            QMessageBox.warning(self, "Aviso", "Primero construye un árbol.")
            return

        postfija = self.calc.obtener_postfija(self.arbol_manual)
        ecuacion_falsa = " ".join(postfija)
        self.stackedWidget_2.setCurrentIndex(1)
        self.procesar_codigo(ecuacion_falsa, tipo, self.area_res6, self.tab_2, es_desde_arbol=True)

    # Módulos 5 y 6: Expresión/Árbol a Código (Generación)
    def procesar_codigo(self, ecuacion, tipo, area_res, tabla, es_desde_arbol=False):
        if not ecuacion: return
        try:
            posfija = ecuacion.split() if es_desde_arbol else self.calc.infija_a_posfija(ecuacion)
            cod_p, triplos, cuadruplos = self.gen.generar_todo(posfija)

            proc = "⚙️ PROCEDIMIENTO:\n\n"
            proc += f"1. Extracción de Postfija:\n   {' '.join(posfija)}\n\n"
            proc += "2. Asignación de variables temporales (T1, T2...) mediante pila.\n\n"

            if tipo == "codigop":
                self.mostrar_texto_en_scroll(area_res,
                                             proc + "3. Traducción a Nemónicos (LOD, ADD, MUL)\n\n🎯 RESULTADO (CÓDIGO P):\n" + "\n".join(
                                                 cod_p))
                tabla.setRowCount(0)
            elif tipo == "triplos":
                datos = [[i, op, a1, a2] for i, (op, a1, a2) in enumerate(triplos)]
                self.llenar_tabla(tabla, ["Índice", "Operador", "Arg 1", "Arg 2"], datos)
                self.mostrar_texto_en_scroll(area_res, proc + "3. Mapeo a tabla de 3 Direcciones (Sin resultado).")
            elif tipo == "cuadruplos":
                datos = [[i, op, a1, a2, res] for i, (op, a1, a2, res) in enumerate(cuadruplos)]
                self.llenar_tabla(tabla, ["Índice", "Operador", "Arg 1", "Arg 2", "Resultado"], datos)
                self.mostrar_texto_en_scroll(area_res, proc + "3. Mapeo a tabla de 4 Direcciones (Con variables T).")
        except Exception as e:
            self.mostrar_texto_en_scroll(area_res, f"❌ Error:\n{str(e)}")

    # Módulo 3: Expresión a Notación (Animación)
    def iniciar_animacion_notacion(self, tipo):
        ecuacion = self.lineEdit_3.text()
        if not ecuacion: return
        try:
            posfija = self.calc.infija_a_posfija(ecuacion)
            self.arbol_animacion = self.calc.construir_arbol(posfija)

            if tipo == "prefija":
                self.lista_animacion = self.calc.obtener_prefija(self.arbol_animacion)
            elif tipo == "infija":
                self.lista_animacion = self.calc.obtener_infija(self.arbol_animacion)
            elif tipo == "postfija":
                self.lista_animacion = self.calc.obtener_postfija(self.arbol_animacion)

            self.pila_animacion = []
            self.indice_animacion = 0
            self.tipo_animacion = tipo
            self.modo_animacion = "expresion"  # Le decimos al timer que es la animación del Módulo 3

            self.mostrar_texto_en_scroll(self.area_res3,
                                         f"⚙️ PROCEDIMIENTO:\n\nIniciando recorrido {tipo.capitalize()}...\nGenerando animación de Platos y Árbol.")
            self.timer_animacion.start(800)
        except Exception as e:
            pass

    # ==========================================
    # LÓGICA DEL TEMPORIZADOR DE ANIMACIONES
    # ==========================================
    def paso_animacion(self):
        if self.indice_animacion >= len(self.lista_animacion):
            self.timer_animacion.stop()
            msg = f"✅ PROCEDIMIENTO FINALIZADO\n\n🎯 RESULTADO:\n{' '.join(self.pila_animacion)}"

            if self.modo_animacion == "expresion":
                self.mostrar_texto_en_scroll(self.area_res3, msg)
                self.dibujar_escena_dividida(None)
            else:
                self.mostrar_texto_en_scroll(self.area_res4, msg)
                self.dibujar_platos_solos(self.grap_ANotacion2)
            return

        token_actual = self.lista_animacion[self.indice_animacion]
        self.pila_animacion.append(token_actual)

        if self.modo_animacion == "expresion":
            # Animación original del Módulo 3 (Árbol y Platos)
            nodo_a_resaltar = self.buscar_nodo_por_valor(self.arbol_animacion, token_actual)
            self.dibujar_escena_dividida(nodo_a_resaltar)
            self.mostrar_texto_en_scroll(self.area_res3,
                                         f"⚙️ PROCEDIMIENTO:\n\nProcesando nodo: {token_actual}\n\nPila actual:\n{' '.join(self.pila_animacion)}")
        else:
            # Nueva animación Módulo 4 (Solo Platos)
            self.dibujar_platos_solos(self.grap_ANotacion2)
            self.mostrar_texto_en_scroll(self.area_res4,
                                         f"⚙️ PROCEDIMIENTO:\n\nProcesando nodo: {token_actual}\n\nAgregando al tope de la Pila.")

        self.indice_animacion += 1

    def buscar_nodo_por_valor(self, nodo, valor):
        if not nodo: return None
        if nodo.valor == valor: return nodo
        izq = self.buscar_nodo_por_valor(nodo.izquierda, valor)
        if izq: return izq
        return self.buscar_nodo_por_valor(nodo.derecha, valor)

    # ==========================================
    # UTILIDADES GRAFICAS
    # ==========================================
    def dibujar_arbol_interactivo(self, nodo_raiz, vista_grafica):
        escena = QGraphicsScene()
        vista_grafica.setScene(escena)
        if nodo_raiz:
            self._dibujar_nodo_interactivo(nodo_raiz, escena, 0, 0, 100)
        escena.selectionChanged.connect(self.al_seleccionar_nodo)

    def _dibujar_nodo_interactivo(self, nodo, escena, x, y, dx):
        radio = 20
        pen_linea = QPen(QColor("#6C5CE7"), 2)
        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 60, pen_linea)
            self._dibujar_nodo_interactivo(nodo.izquierda, escena, x - dx, y + 60, dx / 1.5)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 60, pen_linea)
            self._dibujar_nodo_interactivo(nodo.derecha, escena, x + dx, y + 60, dx / 1.5)

        elipse = QGraphicsEllipseItem(x - radio, y - radio, radio * 2, radio * 2)
        color = "#00E676" if nodo == self.nodo_seleccionado else "#2D2D2D"
        elipse.setBrush(QBrush(QColor(color)))
        elipse.setPen(QPen(QColor("#FFFFFF"), 2))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        escena.addItem(elipse)
        self.mapa_items[elipse] = nodo

        texto = QGraphicsTextItem(str(nodo.valor))
        texto.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        texto.setDefaultTextColor(QColor("#000000" if nodo == self.nodo_seleccionado else "#FFFFFF"))
        texto.setPos(x - texto.boundingRect().width() / 2, y - texto.boundingRect().height() / 2)
        texto.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        escena.addItem(texto)

    def dibujar_escena_dividida(self, nodo_resaltado):
        escena = QGraphicsScene()
        self.graphicsView_3.setScene(escena)
        if self.arbol_animacion:
            self._dibujar_nodo_animado(self.arbol_animacion, escena, -100, 0, 60, nodo_resaltado)

        ancho_plato = 60
        alto_plato = 25
        x_base = 150
        y_base = 150
        escena.addLine(x_base - 40, y_base + 30, x_base + 40, y_base + 30, QPen(QColor("#00E676"), 4))
        for i, token in enumerate(self.pila_animacion):
            y_actual = y_base - (i * (alto_plato + 5))
            escena.addRect(x_base - ancho_plato / 2, y_actual, ancho_plato, alto_plato, QPen(QColor("#FFFFFF"), 2),
                           QBrush(QColor("#6C5CE7")))
            texto = escena.addText(token, QFont("Arial", 11, QFont.Weight.Bold))
            texto.setDefaultTextColor(QColor("#FFFFFF"))
            texto.setPos(x_base - texto.boundingRect().width() / 2, y_actual + 1)

    # NUEVA FUNCIÓN: Dibuja solo los platos centrados para el Módulo 4
    def dibujar_platos_solos(self, vista):
        escena = QGraphicsScene()
        vista.setScene(escena)

        ancho_plato = 80
        alto_plato = 30
        x_base = 0  # Lo centramos en la vista
        y_base = 120  # Lo bajamos un poco para que la pila suba

        # Base de la pila (Línea verde)
        escena.addLine(x_base - 60, y_base + 35, x_base + 60, y_base + 35, QPen(QColor("#00E676"), 4))

        # Dibujamos cada plato desde la base hacia arriba
        for i, token in enumerate(self.pila_animacion):
            y_actual = y_base - (i * (alto_plato + 5))
            escena.addRect(x_base - ancho_plato / 2, y_actual, ancho_plato, alto_plato, QPen(QColor("#FFFFFF"), 2),
                           QBrush(QColor("#6C5CE7")))
            texto = escena.addText(token, QFont("Arial", 12, QFont.Weight.Bold))
            texto.setDefaultTextColor(QColor("#FFFFFF"))
            texto.setPos(x_base - texto.boundingRect().width() / 2, y_actual + 2)

    def _dibujar_nodo_animado(self, nodo, escena, x, y, dx, nodo_resaltado):
        radio = 18
        pen_linea = QPen(QColor("#444444"), 2)
        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 50, pen_linea)
            self._dibujar_nodo_animado(nodo.izquierda, escena, x - dx, y + 50, dx / 1.5, nodo_resaltado)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 50, pen_linea)
            self._dibujar_nodo_animado(nodo.derecha, escena, x + dx, y + 50, dx / 1.5, nodo_resaltado)
        color = "#00E676" if nodo == nodo_resaltado else "#2D2D2D"
        escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(QColor("#FFFFFF"), 2), QBrush(QColor(color)))
        texto = escena.addText(str(nodo.valor), QFont("Arial", 11, QFont.Weight.Bold))
        texto.setDefaultTextColor(QColor("#000000" if nodo == nodo_resaltado else "#FFFFFF"))
        texto.setPos(x - texto.boundingRect().width() / 2, y - texto.boundingRect().height() / 2)

    def llenar_tabla(self, tabla, cabeceras, datos):
        tabla.clear()
        tabla.setColumnCount(len(cabeceras))
        tabla.setHorizontalHeaderLabels(cabeceras)
        tabla.setRowCount(len(datos))
        for fila, fila_datos in enumerate(datos):
            for col, val in enumerate(fila_datos):
                item = QtWidgets.QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla.setItem(fila, col, item)
        tabla.resizeColumnsToContents()

    def aplicar_estilos_figma(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QFrame { background-color: #1E1E1E; border: none; border-radius: 8px; }
            QPushButton { background-color: #6C5CE7; color: white; border-radius: 6px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #5A48D2; }
            QLineEdit { background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444; border-radius: 5px; padding: 8px; font-size: 14px; }
            QLabel { color: #E0E0E0; font-size: 14px; font-weight: bold; }
            QTableWidget { background-color: #1E1E1E; color: white; gridline-color: #333333; border: none; }
            QHeaderView::section { background-color: #2D2D2D; color: white; padding: 5px; border: 1px solid #333333; font-weight: bold; }
            QGraphicsView { background-color: #151515; border: 1px solid #333; border-radius: 5px; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollArea > QWidget > QWidget { background-color: transparent; }
        """)

    def mostrar_texto_en_scroll(self, scroll_area, texto):
        label = QLabel(texto)
        label.setStyleSheet("color: #00E676; font-size: 14px; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll_area.setWidget(label)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())