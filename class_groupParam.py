from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QSlider, QCheckBox
from skimage.morphology import erosion, dilation, closing
from skimage.filters import threshold_otsu
from skimage.filters.rank import median
from matplotlib import pyplot as plt
from skimage.morphology import disk
from PyQt5 import QtCore, QtWidgets
from class_hLayout import HLayout
from skimage.feature import canny
from skimage.draw import ellipse
import numpy as np


class Group_param(QGroupBox):
    def __init__(self, parent, title, x, y, w, h):
        super(Group_param, self).__init__(parent)
        self.papa = parent
        #self.pos = (x,y,w,h)
        self.setGeometry(x,y,w,h)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setTitle(title)
        self.setCheckable(True)
        self.setChecked(False)

        vLayout = QVBoxLayout(self)
        self.l1=HLayout(self, [QLabel(),QSlider(),QLabel()], ['Threshold :',None,'0'], (0,0,0,0))
        self.l1.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l1.wid_list[1].valueChanged['int'].connect(self.l1.wid_list[2].setNum)
        self.l1.wid_list[0].setMinimumSize(90, 0)
        self.l1.wid_list[2].setMinimumSize(30, 0)
        vLayout.addWidget(self.l1)
        self.l2=HLayout(self, [QLabel(),QSlider(),QLabel()], ['Ero / Dilat :',None,'0'], (0,0,0,0))
        self.l2.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l2.wid_list[1].valueChanged['int'].connect(self.l2.wid_list[2].setNum)
        self.l2.wid_list[1].setMaximum(5)
        self.l2.wid_list[1].setMinimum(-5)
        self.l2.wid_list[0].setMinimumSize(90, 0)
        self.l2.wid_list[2].setMinimumSize(30, 0)
        vLayout.addWidget(self.l2)
        self.l3=HLayout(self, [QLabel(),QSlider(),QLabel()], ['Transparency :',None,'0'], (0,0,0,0))
        self.l3.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l3.wid_list[1].valueChanged['int'].connect(self.l3.wid_list[2].setNum)
        self.l3.wid_list[1].setMaximum(10)
        self.l3.wid_list[1].setValue(5)
        self.l3.wid_list[0].setMinimumSize(90, 0)
        self.l3.wid_list[2].setMinimumSize(30, 0)
        vLayout.addWidget(self.l3)
        self.l4=HLayout(self, [QCheckBox(),QPushButton(),QPushButton(),QPushButton(),
        QPushButton()],['All','Left','Up','Down','Right'], (0,0,0,0))
        #self.l4.wid_list[1].valueChanged['int'].connect(self.l3.wid_list[2].setNum)
        vLayout.addWidget(self.l4)
        process = QPushButton('Show build process')
        process.clicked.connect(self.show_process)
        vLayout.addWidget(process)
        self.setLayout(vLayout)


    def mask_init(self, avg, thresh_shift=0):
        self.avg = avg
        self.med = median(self.avg, disk(2))
        self.thresh = threshold_otsu(self.med)+thresh_shift
        self.l1.wid_list[1].setMaximum(255)
        self.l1.wid_list[1].setMinimum(0)
        self.l1.wid_list[1].setValue(self.thresh)
        self.l2.wid_list[1].setValue(0)


    def build_mask(self, thresh, morpho, priority=None, region=None):
        self.thresh = thresh
        self.mask = self.med > self.thresh
        self.mask = closing(self.mask, disk(3))
        if morpho>0: self.mask = dilation(self.mask, disk(morpho))
        elif morpho<0: self.mask = erosion(self.mask, disk(-morpho))

        if region is not None:
            self.mask*=region

        if priority is not None:
            for i in range(len(priority)):
                for j in range(len(priority[i])):
                    if priority[i,j]: self.mask[i,j]=0

        return(self.mask)


    def get_trans(self):
        return(self.l3.wid_list[1].value()/10)


    def show_process(self):
        masked = np.ma.masked_where(self.mask==0, self.mask)
        img_list = [self.avg, self.med, masked]
        title_list = ['Avg', 'Median', 'Mask']
        plt.figure(figsize=[12,4])
        for i,t,im in zip(range(len(img_list)), title_list, img_list):
            plt.subplot(1,len(img_list),i+1)
            plt.axis('off')
            plt.title(t)
            if i!=2: plt.imshow(im, cmap=plt.cm.gray)
            else :plt.imshow(im, cmap='Reds')
        plt.show()
