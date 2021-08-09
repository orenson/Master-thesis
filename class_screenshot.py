from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QCheckBox, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QLabel, QLineEdit, QMessageBox
from PyQt5 import QtCore, QtWidgets
from matplotlib import cm, pyplot as plt
from matplotlib import image as mpimg
from class_groupImg import GroupImg
from class_hLayout import HLayout
from func import gird_shape, graph
from skimage.feature import canny
import numpy as np
import os


class ScreenshotWindow(QDialog):
    def __init__(self, max, prefix):
        super().__init__()
        self.prefix = prefix
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
                        self.fileName, _ = QFileDialog.getSaveFileName(self,"Save as",self.prefix+".png","Pictures (.png)", options=options)
                    elif not self.res.isChecked():
                        self.fileName, _ = QFileDialog.getSaveFileName(self,"Save as","Slices.png","Pictures (.png)", options=options)
                    if self.fileName: self.accept()

    def cancel_pressed(self):
        self.reject()

    def get_info(self):
        print(self.lst,self.res.isChecked(), self.prev.isChecked(), self.fileName)
        return((self.lst, self.res.isChecked(), self.prev.isChecked(), self.fileName))
