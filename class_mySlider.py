from PyQt5.QtWidgets import QSlider
from PyQt5 import QtGui

class MySlider(QSlider):
    def __init__(self, *args, **kwargs):
        super(MySlider, self).__init__(*args, **kwargs)

    def focusInEvent(self, e):
        super(MySlider, self).focusInEvent(e)
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(200,200,200))
        self.setPalette(p)

    def focusOutEvent(self, e):
        super(MySlider, self).focusOutEvent(e)
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45,111,197))
        self.setPalette(p)
