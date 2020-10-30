from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QSlider
from skimage.filters import threshold_otsu
from skimage.filters.rank import median
from matplotlib import pyplot as plt
from skimage.morphology import disk
from PyQt5 import QtCore, QtWidgets
from class_hLayout import HLayout
import numpy as np


class Group_param(QGroupBox):
    def __init__(self, parent, title, x, y, w, h):
        super(Group_param, self).__init__(parent)
        self.papa = parent
        self.pos = (x,y,w,h)
        self.setGeometry(*self.pos)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setTitle(title)
        self.setCheckable(True)
        self.setChecked(False)

        vLayout = QVBoxLayout(self)
        self.l1=HLayout(self, [QLabel(),QSlider(),QLabel()], ['Threshold :',None,'0'], (0,0,0,0))
        self.l1.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l1.wid_list[1].valueChanged['int'].connect(self.l1.wid_list[2].setNum)
        self.l1.wid_list[2].setMinimumSize(30, 0)
        vLayout.addWidget(self.l1)
        self.l2=HLayout(self, [QLabel(),QSlider(),QLabel()], ['Ero / Dilat :',None,'0'], (0,0,0,0))
        self.l2.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l2.wid_list[1].valueChanged['int'].connect(self.l2.wid_list[2].setNum)
        self.l2.wid_list[1].setMaximum(5)
        self.l2.wid_list[1].setMinimum(-5)
        self.l2.wid_list[2].setMinimumSize(30, 0)
        vLayout.addWidget(self.l2)
        process = QPushButton('Show build process')
        process.clicked.connect(self.show_process)
        vLayout.addWidget(process)
        self.setLayout(vLayout)


    def mask_init(self, avg, thresh_shift=0):
        self.avg = avg
        self.med = median(self.avg, disk(2))
        self.thresh = threshold_otsu(self.med)+thresh_shift
        self.l1.wid_list[1].setMaximum(self.thresh+75)
        self.l1.wid_list[1].setMinimum(self.thresh-75)
        self.l1.wid_list[1].setValue(self.thresh)
        self.backup = self.med > self.thresh


    def build_mask(self, priority = None):
        mask = self.med > self.thresh
        if priority is not None:
            for i in range(len(priority)):
                for j in range(len(priority[i])):
                    if priority[i,j]: mask[i,j]=0
        self.masked_array = np.ma.masked_where(mask==0, mask)
        return(self.masked_array)


    def setThresh(self, i):
        self.thresh = i


    def show_process(self):
        img_list = [self.avg, self.med, self.masked_array]
        title_list = ['Avg', 'Median', 'Mask']
        plt.figure(figsize=[12,4])
        for i,t,im in zip(range(len(img_list)), title_list, img_list):
            plt.subplot(1,len(img_list),i+1)
            plt.axis('off')
            plt.title(t)
            plt.imshow(im, cmap=plt.cm.gray)
        plt.show()
