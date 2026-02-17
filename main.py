import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
from Logica.Arboles import CalculadoraArbol


class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("Gui/interfaz.ui", self)

        operadores = [
            "btn_mas", "btn_men", "btn_multi", "btn_entre",
            "btn_elevar", "btn_raiz", "btn_pun",
            "btn_parentesis1", "btn_parentesis2"
        ]

        self.logica = CalculadoraArbol()

        for i in range(10):
            nombre_boton = f"btn_{i}"

            boton = getattr(self, nombre_boton)

            boton.clicked.connect(self.agregar_numero)

        for i in operadores:
            nombre_boton = f"{i}"

            boton = getattr(self, nombre_boton)

            boton.clicked.connect(self.agregar_numero)

        self.btn_borrar.clicked.connect(self.limpiar_pantalla)

        self.btn_del.clicked.connect(self.borrar)


    def agregar_numero(self):
        boton = self.sender()

        texto_boton = boton.text()

        texto_actual = self.lbl_pantalla.text()
        self.lbl_pantalla.setText(texto_actual+texto_boton)


    def limpiar_pantalla(self):
        self.lbl_pantalla.setText("")

    def borrar(self):
        texto_actual = self.lbl_pantalla.text()
        nuevo_texto = texto_actual[:-1]
        self.lbl_pantalla.setText(nuevo_texto)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())