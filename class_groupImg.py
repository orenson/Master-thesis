from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtWidgets import QGroupBox, QMessageBox, QWidget, QVBoxLayout, QLabel, QInputDialog
from skimage.morphology import closing, disk
from func import load_file, process_date
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtWidgets
from skimage.feature import canny
from class_hLayout import HLayout
from skimage import transform
from scipy import ndimage
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

        self.info_widget = QWidget(self.papa)
        self.info_widget.setGeometry(self.pos[0]+7, 434, self.pos[2]-14, 70)
        self.info_widget.setContentsMargins(0,0,0,0)
        info_layout = QVBoxLayout(self.info_widget)
        info_layout.setContentsMargins(0,0,0,0)
        alignment = (QtCore.Qt.AlignLeft, QtCore.Qt.AlignRight)
        self.l1 = HLayout(self.info_widget, [QLabel(), QLabel()], ["", ""], (0,0,0,0), alignment)
        self.l2 = HLayout(self.info_widget, [QLabel(), QLabel()], ["", ""], (0,0,0,0), alignment)
        self.l3 = HLayout(self.info_widget, [QLabel(), QLabel()], ["", ""], (0,0,0,0), alignment)
        self.l4 = HLayout(self.info_widget, [QLabel(), QLabel()], ["", ""], (0,0,0,0), alignment)
        info_layout.addWidget(self.l1)
        info_layout.addWidget(self.l2)
        info_layout.addWidget(self.l3)
        info_layout.addWidget(self.l4)


    def add_widget(self, wid, text=None):
        self.vLayout.addWidget(wid)
        self.wid_list.append(wid)
        if callable(getattr(wid, "setText", None)):
            wid.setText(text)
        if text == "Select":
            self.wid_list[-1].clicked.connect(self.load_dicom)


    def load_dicom(self, path=None):
        if not path: path = load_file()
        self.path = path
        if self.path:
            try:
                scinty = pd.dcmread(self.path)
                print(self.path, "opened")
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
            self.l1.wid_list[0].setText(fname)
            self.l1.wid_list[1].setText(instit)
            self.l2.wid_list[0].setText(patient)
            self.l2.wid_list[1].setText(exam+' ({}s)'.format(self.time))
            self.l3.wid_list[0].setText(genre+'  '+age+'  '+self.weight+'  '+self.size)
            self.l3.wid_list[1].setText(frames+' x '+col+' x '+rows)
            self.l4.wid_list[0].setText(process_date(date))
            self.update_display(0, None, None, 0.5, 0.5, None)


    def update_display(self, i, mask_l, mask_b, transpa_l, transpa_b, shift, apply=True):
        if mask_l is not None and shift and shift[i]:
            matrix = transform.EuclideanTransform(translation=(0,shift[i]))
            mask_l = transform.warp(mask_l, matrix.inverse)
        if transpa_l == 0 and mask_l is not None:
            mask_l = canny(mask_l)
            transpa_l = 1
        if transpa_b == 0 and mask_b is not None:
            mask_b = canny(mask_b)
            transpa_b = 1
        if mask_l is not None: mask_l = np.ma.masked_where(mask_l==0, mask_l)
        if mask_b is not None: mask_b = np.ma.masked_where(mask_b==0, mask_b)

        if apply:
            self.wid_list[1].clear()
            self.wid_list[1].axis('off')
            self.wid_list[1].imshow(self.img_f64[i], cmap=plt.cm.gray)
            if mask_l is not None:
                self.wid_list[1].imshow(mask_l, cmap='coolwarm', alpha = transpa_l, interpolation="nearest")
            if mask_b is not None:
                self.wid_list[1].imshow(mask_b, cmap='RdYlBu', alpha = transpa_b, interpolation="nearest")
            self.wid_list[0].draw()
            if hasattr(self, 'tot'):
                self.l4.wid_list[1].setText(str(np.sum(self.img_f64[i]))+' / '+self.tot)
        else:
            return(mask_l, mask_b)


    def getImg(self):
        return(self.img_f64)

    def setImg(self, img_stack):
        self.img_f64 = img_stack

    def getTimeStep(self):
        return(self.time)

    def getPath(self):
        return(self.path)

    def getW(self):
        if float(self.weight) == 0:
            self.weight, okPressed = QInputDialog.getDouble(self,"Weight input",
            "Weight not specified in dicom file,\nplease enter manually",
            50.0, 0.0, 500.0, 0.1)
        return(float(self.weight))

    def setW(self, x):
        self.weight = x

    def getH(self):
        if float(self.size) == 0:
            self.size, okPressed = QInputDialog.getInt(self,"Size input",
            "Height not specified in dicom file,\nplease enter manually",
            160, 50, 250, 1)
        return(float(self.size))

    def setH(self, x):
        self.size = x
