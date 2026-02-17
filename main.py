import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QLabel, \
    QGraphicsItem, QMessageBox, QTextEdit
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QMouseEvent
from PyQt6.QtCore import Qt, QPoint
from PyQt6 import uic
from Logica.Arboles import CalculadoraArbol
from Logica.Nodo import Nodo


class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Gui/interfaz.ui", self)

        # --- CONTROL DE VENTANA ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_minimizar.clicked.connect(self.showMinimized)
        self.bt_maximizar.clicked.connect(self.maximizar_restaurar)
        self.click_position = None

        # ==========================================================
        #                 PESTAÑA 1: CALCULADORA
        # ==========================================================
        self.scene = QGraphicsScene()
        self.visor_arbol.setScene(self.scene)
        self.visor_arbol.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Etiqueta de Resultado
        self.lbl_resultado = QLabel("Resultado: 0")
        self.lbl_resultado.setStyleSheet("font-size: 22px; color: #2e7d32; font-weight: bold; margin: 5px;")
        self.lbl_resultado.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.fra_calcu.layout().addWidget(self.lbl_resultado)

        # 2. Área de Procedimiento (PASO A PASO) - NUEVO
        self.txt_pasos = QTextEdit()
        self.txt_pasos.setReadOnly(True)
        self.txt_pasos.setMaximumHeight(100)  # Que no ocupe toda la pantalla
        self.txt_pasos.setPlaceholderText("Aquí aparecerá el procedimiento paso a paso...")
        self.txt_pasos.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                color: #555;
            }
        """)
        self.fra_calcu.layout().addWidget(self.txt_pasos)

        self.logica = CalculadoraArbol()

        # Conexiones
        for i in range(10): getattr(self, f"btn_{i}").clicked.connect(self.agregar_numero)

        operadores = ["btn_mas", "btn_men", "btn_multi", "btn_entre", "btn_elevar", "btn_raiz", "btn_pun",
                      "btn_parentesis1", "btn_parentesis2"]
        for op in operadores: getattr(self, op).clicked.connect(self.agregar_numero)

        self.btn_borrar.clicked.connect(self.limpiar_pantalla)
        self.btn_del.clicked.connect(self.borrar_uno)

        # ==========================================================
        #              PESTAÑA 2: EDITOR (ARBOL A EXPRESION)
        # ==========================================================
        self.scene_editor = QGraphicsScene()
        self.graphicsView.setScene(self.scene_editor)
        self.graphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.lbl_resultado_editor = QLabel("Resultado: 0")
        self.lbl_resultado_editor.setStyleSheet("font-size: 18px; color: #2e7d32; font-weight: bold; margin-top: 10px;")
        self.lbl_resultado_editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_controles.layout().addWidget(self.lbl_resultado_editor)

        # Área de Pasos para el Editor también
        self.txt_pasos_editor = QTextEdit()
        self.txt_pasos_editor.setReadOnly(True)
        self.txt_pasos_editor.setMaximumHeight(100)
        self.txt_pasos_editor.setStyleSheet(self.txt_pasos.styleSheet())  # Copiar estilo
        self.panel_controles.layout().addWidget(self.txt_pasos_editor)

        self.raiz_editor = None
        self.nodo_seleccionado = None
        self.mapa_items = {}

        self.btn_establecer.clicked.connect(self.agregar_nodo_manual)
        self.btn_eliminar.clicked.connect(self.eliminar_nodo_manual)
        self.btn_limpiar.clicked.connect(self.limpiar_editor)
        self.scene_editor.selectionChanged.connect(self.al_seleccionar_nodo)

    # --- CONTROL VENTANA ---
    def maximizar_restaurar(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.Barra_superior.geometry().contains(event.pos()):
            self.click_position = event.globalPosition().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.click_position:
            delta = event.globalPosition().toPoint() - self.click_position
            self.move(self.pos() + delta)
            self.click_position = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.click_position = None

    # --- PESTAÑA 1 ---
    def agregar_numero(self):
        boton = self.sender()
        self.lbl_pantalla.setText(self.lbl_pantalla.text() + boton.text())
        self.procesar_arbol()

    def limpiar_pantalla(self):
        self.lbl_pantalla.setText("")
        self.scene.clear()
        self.lbl_resultado.setText("Resultado: 0")
        self.txt_pasos.clear()

    def borrar_uno(self):
        self.lbl_pantalla.setText(self.lbl_pantalla.text()[:-1])
        self.procesar_arbol()

    def procesar_arbol(self):
        ecuacion = self.lbl_pantalla.text()
        self.scene.clear()
        self.txt_pasos.clear()  # Limpiar pasos anteriores

        if not ecuacion: return
        try:
            postfix = self.logica.infija_a_posfija(ecuacion)
            raiz = self.logica.construir_arbol(postfix)
            if raiz:
                # AQUÍ ESTÁ LA MAGIA: EVALUAR CON PASOS
                res, pasos = self.logica.evaluar_con_pasos(raiz)

                # Mostrar Resultado
                if res == int(res):
                    self.lbl_resultado.setText(f"Resultado: {int(res)}")
                else:
                    self.lbl_resultado.setText(f"Resultado: {res:.2f}")

                # Mostrar Pasos
                texto_pasos = "Procedimiento:\n"
                for i, paso in enumerate(pasos, 1):
                    texto_pasos += f"{i}. {paso}\n"
                self.txt_pasos.setText(texto_pasos)

                self.dibujar_nodo(self.scene, raiz, 0, 0, 150)
        except:
            pass  # Si la expresión está incompleta, simplemente no mostramos nada nuevo

    # --- PESTAÑA 2 ---
    def es_numero(self, texto):
        try:
            float(texto)
            return True
        except:
            return False

    def es_operador(self, texto):
        return texto in ['+', '-', '*', '/', '^', '√']

    def agregar_nodo_manual(self):
        valor = self.input_valor.text().strip()
        if not valor: return

        if not (self.es_numero(valor) or self.es_operador(valor)):
            QMessageBox.warning(self, "Valor Inválido", "Ingresa número u operador válido.")
            return

        if self.raiz_editor is None:
            self.raiz_editor = Nodo(valor)
            self.nodo_seleccionado = self.raiz_editor
        elif self.nodo_seleccionado:
            if self.es_numero(self.nodo_seleccionado.valor):
                QMessageBox.warning(self, "Acción Inválida", "Los números no pueden tener hijos.")
                return
            if self.nodo_seleccionado.izquierda is None:
                self.nodo_seleccionado.izquierda = Nodo(valor)
            elif self.nodo_seleccionado.derecha is None:
                self.nodo_seleccionado.derecha = Nodo(valor)
            else:
                QMessageBox.information(self, "Lleno", "Nodo lleno.")
                return
        else:
            QMessageBox.warning(self, "Selección", "Selecciona un nodo padre.")
            return

        self.input_valor.setText("")
        self.actualizar_editor()

    def eliminar_nodo_manual(self):
        if self.nodo_seleccionado and self.raiz_editor:
            if self.nodo_seleccionado == self.raiz_editor:
                self.raiz_editor = None
            else:
                self.eliminar_referencia(self.raiz_editor, self.nodo_seleccionado)
            self.nodo_seleccionado = None
            self.actualizar_editor()

    def eliminar_referencia(self, nodo_actual, nodo_a_borrar):
        if not nodo_actual: return
        if nodo_actual.izquierda == nodo_a_borrar:
            nodo_actual.izquierda = None;
            return
        if nodo_actual.derecha == nodo_a_borrar:
            nodo_actual.derecha = None;
            return
        self.eliminar_referencia(nodo_actual.izquierda, nodo_a_borrar)
        self.eliminar_referencia(nodo_actual.derecha, nodo_a_borrar)

    def limpiar_editor(self):
        self.raiz_editor = None
        self.nodo_seleccionado = None
        self.salida_expresion.setText("")
        self.scene_editor.clear()
        self.lbl_resultado_editor.setText("Resultado: 0")
        self.txt_pasos_editor.clear()

    def actualizar_editor(self):
        nodo_previo = self.nodo_seleccionado
        try:
            self.scene_editor.selectionChanged.disconnect()
        except:
            pass

        self.scene_editor.clear()
        self.mapa_items = {}

        self.nodo_seleccionado = nodo_previo
        self.scene_editor.selectionChanged.connect(self.al_seleccionar_nodo)

        if self.raiz_editor:
            self.dibujar_nodo_editor(self.raiz_editor, 0, 0, 150)
            try:
                # MAGIA TAMBIÉN AQUÍ
                res, pasos = self.logica.evaluar_con_pasos(self.raiz_editor)

                if res == int(res):
                    self.lbl_resultado_editor.setText(f"Resultado: {int(res)}")
                else:
                    self.lbl_resultado_editor.setText(f"Resultado: {res:.2f}")

                texto_pasos = "Procedimiento:\n"
                for i, paso in enumerate(pasos, 1):
                    texto_pasos += f"{i}. {paso}\n"
                self.txt_pasos_editor.setText(texto_pasos)

            except:
                self.lbl_resultado_editor.setText("Resultado: ...")
                self.txt_pasos_editor.clear()
        else:
            self.lbl_resultado_editor.setText("Resultado: 0")
            self.txt_pasos_editor.clear()

        self.salida_expresion.setText(self.generar_expresion(self.raiz_editor))

    def generar_expresion(self, nodo):
        if not nodo: return ""
        if not nodo.izquierda and not nodo.derecha: return str(nodo.valor)
        izq = self.generar_expresion(nodo.izquierda)
        der = self.generar_expresion(nodo.derecha)
        return f"({izq} {nodo.valor} {der})"

    def al_seleccionar_nodo(self):
        items = self.scene_editor.selectedItems()
        self.nodo_seleccionado = self.mapa_items.get(items[0]) if items else None

    # --- DIBUJADO ---
    def dibujar_nodo(self, escena, nodo, x, y, dx):
        if not nodo: return
        r = 25
        pen = QPen(Qt.GlobalColor.black, 2)
        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 80, pen)
            self.dibujar_nodo(escena, nodo.izquierda, x - dx, y + 80, dx / 1.6)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 80, pen)
            self.dibujar_nodo(escena, nodo.derecha, x + dx, y + 80, dx / 1.6)

        elipse = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
        elipse.setBrush(QBrush(QColor("#0078D7")))
        elipse.setPen(QPen(Qt.GlobalColor.white, 2))
        escena.addItem(elipse)

        txt = QGraphicsTextItem(str(nodo.valor))
        txt.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        txt.setDefaultTextColor(Qt.GlobalColor.white)
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)
        escena.addItem(txt)

    def dibujar_nodo_editor(self, nodo, x, y, dx):
        if not nodo: return
        r = 25
        pen = QPen(Qt.GlobalColor.black, 2)
        if nodo.izquierda:
            self.scene_editor.addLine(x, y, x - dx, y + 80, pen)
            self.dibujar_nodo_editor(nodo.izquierda, x - dx, y + 80, dx / 1.6)
        if nodo.derecha:
            self.scene_editor.addLine(x, y, x + dx, y + 80, pen)
            self.dibujar_nodo_editor(nodo.derecha, x + dx, y + 80, dx / 1.6)

        elipse = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
        color = "#ff9800" if nodo == self.nodo_seleccionado else "#0078D7"
        elipse.setBrush(QBrush(QColor(color)))
        elipse.setPen(QPen(Qt.GlobalColor.white, 2))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene_editor.addItem(elipse)

        self.mapa_items[elipse] = nodo

        txt = QGraphicsTextItem(str(nodo.valor))
        txt.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        txt.setDefaultTextColor(Qt.GlobalColor.white)
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)
        txt.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.scene_editor.addItem(txt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())