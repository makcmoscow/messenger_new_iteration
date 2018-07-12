from PyQt5 import QtWidgets, uic
import sys
import PyQt5

class Wlogin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('Wlogin.ui', self)

    def register(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Wlogin()
    window.show()
    app.exec_()