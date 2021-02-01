from PyQt5.QtWidgets import QHBoxLayout, QDialog, QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QCheckBox, QFileDialog
from matplotlib import cm, pyplot as plt
from matplotlib import image as mpimg
from PyQt5 import QtCore, QtWidgets
from class_groupImg import GroupImg
from class_hLayout import HLayout
from func import gird_shape, graph
from skimage.feature import canny
import numpy as np
import os


class ScreenshotWindow(QDialog):
    def __init__(self, max):
        super().__init__()
        self.max = max
        self.setWindowTitle("Sceenshot settings")
        mainLayout = QVBoxLayout(self)
        hWidget = QWidget()
        hLayout = QHBoxLayout(hWidget)

        text = QLabel("Select frame(s) between 1 and {} :".format(self.max))
        self.input = QLineEdit()
        self.input.setPlaceholderText("ex : 3-6,9,10")
        self.res = QCheckBox('Include curves and results')
        self.prev = QCheckBox('Show after generation')
        ok = QPushButton('ok')
        ok.clicked.connect(self.ok_pressed)
        cancel = QPushButton('cancel')
        cancel.clicked.connect(self.cancel_pressed)

        mainLayout.addWidget(text)
        mainLayout.addWidget(self.input)
        mainLayout.addWidget(self.res)
        mainLayout.addWidget(self.prev)
        hLayout.addWidget(cancel)
        hLayout.addWidget(ok)
        hLayout.setContentsMargins(0,0,0,0)
        mainLayout.addWidget(hWidget)
        self.setLayout(mainLayout)

    def ok_pressed(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if self.input.text() == '' and not self.res.isChecked():
            QMessageBox(QMessageBox.Warning, "Error","Invalid selection").exec_()
        elif self.input.text() == '' and self.res.isChecked():
            self.lst=[]
            self.fileName, _ = QFileDialog.getSaveFileName(self,"Save as","TimeSeries.png","Pictures (.png)", options=options)
            if self.fileName: self.accept()

        elif len([i for i in 'abcdefghijklmnopqrstuvABCDEFGHIJKLMNOPQRSTUVWXYZ@\'\#&éàè$€*`ù%=+_?.;/:"' if i in self.input.text()])>0:
            QMessageBox(QMessageBox.Warning, "Error","Invalid selection").exec_()
        else:
            lst_it = [i for i in self.input.text().split(',') if i != ""]
            self.lst = [i for i in self.input.text().split(',') if i != ""]
            for i in range(len(lst_it))[::-1]:
                if '-' in lst_it[i]:
                    if len(lst_it[i].split('-'))==2 and '' not in lst_it[i].split('-') and\
                    int(lst_it[i].split('-')[1])<=self.max and int(lst_it[i].split('-')[0])>0 and\
                    int(lst_it[i].split('-')[0])<int(lst_it[i].split('-')[1]):
                        start, end = lst_it[i].split('-')
                        self.lst = self.lst[:i]+list(range(int(start),int(end)+1))+self.lst[i+1:]
                    else:
                        QMessageBox(QMessageBox.Warning, "Error","Invalid selection").exec_()
                        break
                elif int(lst_it[i])>self.max or int(lst_it[i])<1:
                    QMessageBox(QMessageBox.Warning, "Error","Invalid selection").exec_()
                    break
                else: self.lst[i]=int(lst_it[i])
                if i==0:
                    if self.res.isChecked():
                        self.fileName, _ = QFileDialog.getSaveFileName(self,"Save as","Prefix.png","Pictures (.png)", options=options)
                    elif not self.res.isChecked():
                        self.fileName, _ = QFileDialog.getSaveFileName(self,"Save as","Slices.png","Pictures (.png)", options=options)
                    if self.fileName: self.accept()

    def cancel_pressed(self):
        self.reject()

    def get_info(self):
        print(self.lst,self.res.isChecked(), self.prev.isChecked(), self.fileName)
        return((self.lst, self.res.isChecked(), self.prev.isChecked(), self.fileName))

    '''def generate_img(self, mean_f64, mask_l, mask_b, shift, h, w, ts):
        if len(self.lst)>0 and self.res.isChecked():
            prefix = self.fileName.split('.png')[0]
            fname1 = prefix+'_slices.png'
            fname2 = prefix+'_timeSeries.png'
        else: fname1 = fname2 = self.fileName
        gird_y, gird_x = gird_shape(len(self.lst))
        #plt.figure(figsize=[12,7])
        for i in range(len(self.lst)):
            plt.subplot(gird_y,gird_x,i+1)
            plt.axis('off')
            plt.title("Mean {}".format(self.lst[i]), fontdict={'fontsize': 8})
            plt.imshow(mean_f64[self.lst[i]-1],cmap=plt.cm.gray)

            if shift and shift[i]:
                mask_l = ndimage.shift(mask_l, [shift[i],0])
                mask_l = closing(mask_l,disk(3))
            if mask_l is not None:
                mask_l = canny(mask_l)
                mask_l = np.ma.masked_where(mask_l==0, mask_l)
                plt.imshow(mask_l, cmap='coolwarm', interpolation="nearest")
            if mask_b is not None:
                mask_b = canny(mask_b)
                mask_b = np.ma.masked_where(mask_b==0, mask_b)
                plt.imshow(mask_b, cmap='RdYlBu', interpolation="nearest")
            if i==len(self.lst)-1:
                plt.tight_layout()
                plt.savefig(fname1, bbox_inches='tight')
                plt.close()
                if self.prev.isChecked():
                    plt.figure(1,figsize=[8,5])
                    plt.axis('off')
                    plt.tight_layout()
                    plt.imshow(mpimg.imread(fname1))
        if self.res.isChecked():
            if mask_l is not None and mask_b is not None:
                plot = graph(ts, mean_f64, mask_l, mask_b, h, w, shift)
                plot.savefig(fname2, bbox_inches='tight')
                plt.close()
                if self.prev.isChecked():
                    plt.figure(2,figsize=[8,5])
                    plt.axis('off')
                    plt.tight_layout()
                    plt.imshow(mpimg.imread(fname2))
            else: QMessageBox(QMessageBox.Warning, "Error",
            "Plot failed, both masks sould be selected to generate results").exec_()
        if self.prev.isChecked(): plt.show()'''
