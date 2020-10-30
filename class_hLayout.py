from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5 import QtCore, QtWidgets


class HLayout(QWidget):
    def __init__(self, parent, wid, text, margins=None, alignment=None):
        super(HLayout, self).__init__(parent)
        layout = QHBoxLayout(self)
        self.wid_list = []
        for w, t in zip(wid, text):
            layout.addWidget(w)
            self.wid_list.append(w)
            if callable(getattr(w, "setText", None)):
                w.setText(t)

        if margins is not None:
            layout.setContentsMargins(*margins)
            for i in range(len(self.wid_list)):
                self.wid_list[i].setContentsMargins(*margins)
        if alignment is not None:
            for i, al in zip (range(len(self.wid_list)), alignment):
                self.wid_list[i].setAlignment(al)
