import sys
from PyQt6.QtWidgets import QApplication
from curto_circuito.gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Curto-Circuito MT/BT")
    app.setOrganizationName("IEC60909")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
