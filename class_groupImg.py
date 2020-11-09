from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtWidgets import QGroupBox, QMessageBox, QWidget, QVBoxLayout, QLabel, QInputDialog
from func import load_file, process_date
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtWidgets
from class_hLayout import HLayout
import pydicom as pd
import numpy as np


class GroupImg(QGroupBox):
    def __init__(self, parent, title, x, y, w, h, slider, flip=False):
        super(GroupImg, self).__init__(parent)
        self.papa = parent
        self.slider = slider
        self.pos = (x,y,w,h)
        self.flip = flip
        self.img_f64 = None
        self.setGeometry(*self.pos)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setTitle(title)

        self.wid_list = []
        fig = Figure(figsize=(3, 3))
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        self.wid_list.append(canvas)
        self.wid_list.append(ax)

        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.addWidget(canvas)
        self.setLayout(self.vLayout)


    def add_widget(self, wid, text=None):
        self.vLayout.addWidget(wid)
        self.wid_list.append(wid)
        if callable(getattr(wid, "setText", None)):
            wid.setText(text)
        if text == "Select":
            self.wid_list[-1].clicked.connect(self.load_dicom)


    def load_dicom(self):
        path = load_file()
        if path:
            try:
                scinty = pd.dcmread(path)
                print(path, "opened")
            except:
                QMessageBox(QMessageBox.Warning, "Error", "Can't open file").exec_()
            else:
                self.read_file(scinty, path.split('/')[-1])


    def read_file(self, scinty, fname):
        try:
            if self.flip : self.img_f64 = scinty.pixel_array[:,:,::-1]
            else: self.img_f64 = scinty.pixel_array
            patient = str(scinty['PatientName'].value)
            date = str(scinty[0x0008, 0x0022].value)
            instit = str(scinty[0x0008, 0x0080].value)
            exam = str(scinty[0x0008, 0x103E].value)
            genre = str(scinty[0x0010, 0x0040].value)
            age = str(scinty[0x0010, 0x1010].value)
            self.size = str(scinty[0x0010, 0x1020].value)
            self.weight = str(scinty[0x0010, 0x1030].value)
            self.tot = str(scinty[0x0018, 0x0070].value)
            rows = str(scinty[0x0028, 0x0010].value)
            col = str(scinty[0x0028, 0x0011].value)
            frames = str(scinty[0x0028, 0x0008].value)
            self.time = str(scinty[0x0054, 0x0032][0].ActualFrameDuration/1000)
        except:
            QMessageBox(QMessageBox.Warning, "Error", "Error while reading file").exec_()
        else:
            self.slider.setValue(0)
            self.slider.setMaximum(len(self.img_f64)-1)

            info_widget = QWidget(self.papa)
            info_widget.setGeometry(self.pos[0]+7, 434, self.pos[2]-14, 70)
            info_widget.setContentsMargins(0,0,0,0)
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0,0,0,0)
            alignment = (QtCore.Qt.AlignLeft, QtCore.Qt.AlignRight)
            l1 = HLayout(info_widget, [QLabel(), QLabel()], [fname, instit], (0,0,0,0), alignment)
            l2 = HLayout(info_widget, [QLabel(), QLabel()], [patient, exam+' ({}s)'.format(self.time)], (0,0,0,0), alignment)
            l3 = HLayout(info_widget, [QLabel(), QLabel()], [genre+'   '+age+'   '+self.weight, frames+' x '+col+' x '+rows], (0,0,0,0), alignment)
            self.l4 = HLayout(info_widget, [QLabel(), QLabel()], [process_date(date), self.tot], (0,0,0,0), alignment)
            info_layout.addWidget(l1)
            info_layout.addWidget(l2)
            info_layout.addWidget(l3)
            info_layout.addWidget(self.l4)
            info_widget.show()
            self.update_display(0, None, None)


    def update_display(self, i, mask_l, mask_b):
        self.wid_list[1].clear()
        self.wid_list[1].axis('off')
        self.wid_list[1].imshow(self.img_f64[i], cmap=plt.cm.gray)
        if mask_l is not None:
            self.wid_list[1].imshow(mask_l, cmap='coolwarm', alpha = 0.5)
        if mask_b is not None:
            self.wid_list[1].imshow(mask_b, cmap='RdYlBu', alpha = 0.5)
        self.wid_list[0].draw()
        if hasattr(self, 'l4'):
            self.l4.wid_list[1].setText(str(np.sum(self.img_f64[i]))+' / '+self.tot)

    def getImg(self):
        return(self.img_f64)

    def setImg(self, img_stack):
        self.img_f64 = img_stack

    def getTimeStep(self):
        return(self.time)

    def getW(self):
        if float(self.weight) == 0:
            self.weight, okPressed = QInputDialog.getDouble(self,"Weight input",
            "Weight not specified in dicom file,\nplease enter manually",
            50.0, 0.0, 500.0, 0.1)
        return(float(self.weight))

    def getH(self):
        if float(self.size) == 0:
            self.size, okPressed = QInputDialog.getInt(self,"Size input",
            "Height not specified in dicom file,\nplease enter manually",
            160, 50, 250, 1)
        return(float(self.size))
