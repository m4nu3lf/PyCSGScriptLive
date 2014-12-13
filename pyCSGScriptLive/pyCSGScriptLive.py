#!/usr/bin/env python
import sys
from PyQt4.QtGui import QApplication
from mainwindow import MainWindow


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
