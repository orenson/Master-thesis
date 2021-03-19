from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QCheckBox, QLineEdit
from skimage.morphology import erosion, dilation, closing, opening
from skimage.filters import threshold_otsu, gaussian, unsharp_mask
from skimage.measure import label, regionprops
from PyQt5 import QtCore, QtWidgets, QtGui
from skimage.filters.rank import median
from func import f64_2_u8, aryth_avg
from matplotlib import pyplot as plt
from skimage.morphology import disk
from class_mySlider import MySlider
from class_hLayout import HLayout
from skimage.feature import canny
from skimage.draw import ellipse
import numpy as np


class Group_param(QGroupBox):
    def __init__(self, parent, title, x, y, w, h):
        super(Group_param, self).__init__(parent)
        self.papa = parent
        self.shift_list = None
        self.setGeometry(x,y,w,h)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setTitle(title)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFont(QtGui.QFont('Arial', 20))

        vLayout = QVBoxLayout(self)
        self.l1=HLayout(self, [QLabel(),MySlider(),QLabel()], ['Threshold :',None,'0'], (0,0,0,0))
        self.l1.wid_list[0].setFont(QtGui.QFont('Arial', 14))
        self.l1.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l1.wid_list[1].valueChanged['int'].connect(self.l1.wid_list[2].setNum)
        self.l1.wid_list[0].setMinimumSize(90, 0)
        self.l1.wid_list[2].setMinimumSize(30, 0)
        self.l1.wid_list[2].setFont(QtGui.QFont('Arial', 14))
        vLayout.addWidget(self.l1)
        self.l2=HLayout(self, [QLabel(),MySlider(),QLabel()], ['Ero / Dilat :',None,'0'], (0,0,0,0))
        self.l2.wid_list[0].setFont(QtGui.QFont('Arial', 14))
        self.l2.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l2.wid_list[1].valueChanged['int'].connect(self.l2.wid_list[2].setNum)
        self.l2.wid_list[1].setMaximum(5)
        self.l2.wid_list[1].setMinimum(-5)
        self.l2.wid_list[0].setMinimumSize(90, 0)
        self.l2.wid_list[2].setMinimumSize(30, 0)
        self.l2.wid_list[2].setFont(QtGui.QFont('Arial', 14))
        vLayout.addWidget(self.l2)
        self.l3=HLayout(self, [QLabel(),MySlider(),QLabel()], ['Transparency :',None,'0'], (0,0,0,0))
        self.l3.wid_list[0].setFont(QtGui.QFont('Arial', 14))
        self.l3.wid_list[1].setOrientation(QtCore.Qt.Horizontal)
        self.l3.wid_list[1].valueChanged['int'].connect(self.l3.wid_list[2].setNum)
        self.l3.wid_list[1].setMaximum(10)
        self.l3.wid_list[1].setValue(0)
        self.l3.wid_list[0].setMinimumSize(90, 0)
        self.l3.wid_list[2].setMinimumSize(30, 0)
        self.l3.wid_list[2].setFont(QtGui.QFont('Arial', 14))
        vLayout.addWidget(self.l3)
        self.l4=HLayout(self, [QCheckBox(),QPushButton(),QPushButton(),QPushButton(),
        QPushButton()],['All','Left','Up','Down','Right'], (0,0,0,0))
        self.l4.wid_list[1].setAutoRepeat(True)
        self.l4.wid_list[2].setAutoRepeat(True)
        self.l4.wid_list[3].setAutoRepeat(True)
        self.l4.wid_list[4].setAutoRepeat(True)
        self.l4.wid_list[0].setFont(QtGui.QFont('Arial', 14))
        self.l4.wid_list[1].setFont(QtGui.QFont('Arial', 14))
        self.l4.wid_list[2].setFont(QtGui.QFont('Arial', 14))
        self.l4.wid_list[3].setFont(QtGui.QFont('Arial', 14))
        self.l4.wid_list[4].setFont(QtGui.QFont('Arial', 14))
        #self.l4.wid_list[1].valueChanged['int'].connect(self.l3.wid_list[2].setNum)
        vLayout.addWidget(self.l4)
        #process = QPushButton('Show build process')
        #process.clicked.connect(self.show_process)
        self.l5=HLayout(self, [QLineEdit(),QPushButton()], ['','Show build process'], (0,0,0,0))
        self.l5.wid_list[0].setMaximumWidth(116)
        self.l5.wid_list[1].clicked.connect(self.show_process)
        self.l5.wid_list[1].setFont(QtGui.QFont('Arial', 14))
        vLayout.addWidget(self.l5)
        self.setLayout(vLayout)

    def mask_init(self, mean_f64, start, end, offset=0):
        self.shift_list = [[0,0] for i in range(len(mean_f64))]
        self.avg = f64_2_u8(aryth_avg(mean_f64[start:end]))

        if offset != 0: #blood
            self.med = gaussian(median(self.avg, disk(3)),1)
            self.med *= 255
            #self.l1.wid_list[1].setMaximum(50)
            #self.l1.wid_list[1].setMinimum(0)
            #self.l1.wid_list[1].setValue(5)
            #self.l2.wid_list[1].setMaximum(50)
            #self.l2.wid_list[1].setMinimum(0)
            #self.l2.wid_list[1].setValue(5)
            #self.un = self.med.copy()
            self.thresh = threshold_otsu(self.med)+offset
            self.l1.wid_list[1].setMaximum(255)
            self.l1.wid_list[1].setMinimum(0)
            self.l1.wid_list[1].setValue(self.thresh)
            self.l2.wid_list[1].setValue(0)

        elif offset == 0: #liver
            self.med = median(self.avg, disk(3))
            #self.un = self.med.copy()
            self.thresh = threshold_otsu(self.med)
            self.l1.wid_list[1].setMaximum(255)
            self.l1.wid_list[1].setMinimum(0)
            self.l1.wid_list[1].setValue(self.thresh)
            self.l2.wid_list[1].setValue(0)


    def build_mask(self, thresh, morpho, priority=None, region=None):

        if region is not None: #blood
            #self.un = unsharp_mask(self.med, radius=thresh, amount=morpho)
            #self.mask = self.un*region > 0.9
            self.thresh = thresh
            self.mask = self.med*region > self.thresh
            #labels = label(self.mask)
            #try:
            #    self.mask = labels==np.argmax(np.bincount(labels.flat)[1:])+1
            #except: pass

            if morpho>0: self.mask = dilation(self.mask, disk(morpho))
            elif morpho<0: self.mask = erosion(self.mask, disk(-morpho))
            self.mask = closing(opening(self.mask, disk(3)), disk(3))
            if priority is not None:
                for i in range(len(priority)):
                    for j in range(len(priority[i])):
                        if priority[i,j]: self.mask[i,j]=0

        elif region is None: #liver
            self.thresh = thresh
            self.mask = self.med > self.thresh
            self.mask = closing(opening(self.mask, disk(2)), disk(2))
            if morpho>0: self.mask = dilation(self.mask, disk(morpho))
            elif morpho<0: self.mask = erosion(self.mask, disk(-morpho))

        return(self.mask)


    def update_shift(self,l,r,u,d,i):
        if not self.l4.wid_list[0].isChecked():
            self.shift_list[i][0] += (-l+r)
            self.shift_list[i][1] += (-u+d)
        elif self.l4.wid_list[0].isChecked():
            for j in range(len(self.shift_list)):
                self.shift_list[j][0] += (-l+r)
                self.shift_list[j][1] += (-u+d)


    def get_trans(self):
        return(self.l3.wid_list[1].value()/10)


    def get_shift(self):
        return(self.shift_list)


    def set_shift(self, l):
        self.shift_list = l


    def show_process(self):
        #masked = np.ma.masked_where(self.mask==0, self.mask)
        masked = canny(self.mask)
        img_list = [self.avg, self.med, self.med]
        title_list = ['Avg', 'Median', 'Masked']
        plt.figure(figsize=[12,4])
        for i,t,im in zip(range(len(img_list)), title_list, img_list):
            plt.subplot(1,len(img_list),i+1)
            plt.axis('off')
            plt.title(t)
            #if i!=2: plt.imshow(im, cmap=plt.cm.gray)
            #else :plt.imshow(im, cmap='Reds')
            plt.imshow(im, cmap=plt.cm.gray)
            if i==2: plt.imshow(np.ma.masked_where(masked==0, masked), cmap='RdYlBu')
        plt.show()
