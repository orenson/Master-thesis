from PyQt5.QtWidgets import QRadioButton, QSlider, QLabel, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton
from func import f64_2_u8, aryth_avg, update_plt_param, graph
from matplotlib import cm, pyplot as plt
from class_groupParam import Group_param
from skimage.filters.rank import median
from skimage.morphology import disk
from PyQt5 import QtCore, QtWidgets
from class_hLayout import HLayout
from class_groupImg import GroupImg
import numpy as np


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setFixedSize(1425, 796)
        centralwidget = QWidget(self)
        self.computed = False
        self.mask_l = None
        self.mask_b = None
        plt.ion()

        self.s = HLayout(centralwidget, [QSlider(), QLabel()], [None,'0'])
        self.s.setGeometry(150, 535, 451, 61)
        self.s.wid_list[0].setMaximum(35)
        self.s.wid_list[0].setOrientation(QtCore.Qt.Horizontal)
        self.s.wid_list[0].valueChanged['int'].connect(self.s.wid_list[1].setNum)
        self.s.wid_list[1].setMinimumSize(30, 0)

        self.group_ant = GroupImg(centralwidget, "Anterior projection", 5, 10, 370, 419, self.s.wid_list[0])
        self.group_ant.add_widget(QPushButton(), 'Select')
        self.group_post = GroupImg(centralwidget, "Posterior projection", 380, 10, 370, 419, self.s.wid_list[0], True)
        self.group_post.add_widget(QPushButton(), 'Select')
        self.group_mean = GroupImg(centralwidget, "Gmean dataset", 755, 10, 662, 780, self.s.wid_list[0])
        filters = HLayout(self.group_mean,[QRadioButton() for i in range(3)],['Raw','Median filter','Negative'],(70,0,0,0))
        filters.setMaximumHeight(33)
        filters.wid_list[0].setChecked(True)
        self.group_mean.add_widget(filters)
        self.group_mean.wid_list[-1].wid_list[0].clicked.connect(self.compute_mean)
        self.group_mean.wid_list[-1].wid_list[1].clicked.connect(self.compute_mean)
        self.group_mean.wid_list[-1].wid_list[2].clicked.connect(self.compute_mean)
        self.group_mean.add_widget(QPushButton(), 'Compute')
        self.group_mean.wid_list[-1].clicked.connect(self.compute_mean)
        self.group_mean.add_widget(QPushButton(), 'Show time-activity curve')
        self.s.wid_list[0].valueChanged['int'].connect(self.call_update_display)

        self.group_liver = Group_param(centralwidget, 'Liver detection', 5, 640, 370, 150)
        self.group_liver.clicked.connect(self.liver_check)
        self.group_blood = Group_param(centralwidget, 'Blood pool detection', 380, 640, 370, 150)
        self.group_blood.clicked.connect(self.blood_check)

        self.setCentralWidget(centralwidget)
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(0, 0, 928, 22)
        self.setMenuBar(menubar)
        update_plt_param()


    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Right:
            self.s.wid_list[0].setValue(self.s.wid_list[0].value() + 1)
        elif event.key()==QtCore.Qt.Key_Left:
            self.s.wid_list[0].setValue(self.s.wid_list[0].value() - 1)
        elif event.key()==QtCore.Qt.Key_Up:
            self.s.wid_list[0].setValue(self.s.wid_list[0].value() + 1)
        elif event.key()==QtCore.Qt.Key_Down:
            self.s.wid_list[0].setValue(self.s.wid_list[0].value() - 1)
        elif event.key()==QtCore.Qt.Key_R:
            self.group_mean.wid_list[2].wid_list[0].setChecked(True)
            self.compute_mean()
        elif event.key()==QtCore.Qt.Key_M:
            self.group_mean.wid_list[2].wid_list[1].setChecked(True)
            self.compute_mean()
        elif event.key()==QtCore.Qt.Key_N:
            self.group_mean.wid_list[2].wid_list[2].setChecked(True)
            self.compute_mean()
        elif event.key()==QtCore.Qt.Key_L:
            if self.group_liver.isChecked(): self.group_liver.setChecked(False)
            else: self.group_liver.setChecked(True)
            self.liver_check()
        elif event.key()==QtCore.Qt.Key_B:
            if self.group_blood.isChecked(): self.group_blood.setChecked(False)
            else: self.group_blood.setChecked(True)
            self.blood_check()
        else:
            super().keyPressEvent(event)


    def wheelEvent(self,event):
        delta = int(event.angleDelta().y()/8)/15
        self.s.wid_list[0].setValue(self.s.wid_list[0].value() + delta)


    def compute_mean(self):
        if hasattr(self.group_ant, 'img_f64') and hasattr(self.group_post, 'img_f64'):
            ant = self.group_ant.getImg()
            post = self.group_post.getImg()
            if ant.shape == post.shape:
                self.mean_f64 = (ant*post)**(1/2)
                mean_u8 = f64_2_u8(self.mean_f64)
                avg_last10_f64 = aryth_avg(self.mean_f64[-10:])
                self.avg_last10_u8 = f64_2_u8(avg_last10_f64)
                avg_first5_f64 = aryth_avg(self.mean_f64[2:6])
                self.avg_first5_u8 = f64_2_u8(avg_first5_f64)
                to_display = mean_u8.copy()

                if self.group_mean.wid_list[2].wid_list[1].isChecked():
                    for i in range(len(mean_u8)):
                        med = median(to_display[i], disk(1))
                        to_display[i] = med
                elif self.group_mean.wid_list[2].wid_list[2].isChecked():
                    to_display = np.invert(mean_u8)

                self.group_mean.setImg(to_display)
                self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, self.mask_b)

                if not self.computed:
                    self.group_liver.mask_init(self.avg_last10_u8)
                    self.group_liver.l1.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_liver.l2.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_blood.mask_init(self.avg_first5_u8, 50)
                    self.group_blood.l1.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_blood.l2.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_mean.wid_list[-1].clicked.connect(self.show_curve)
                    self.computed = True

            else:
                QMessageBox(QMessageBox.Warning, "Error",\
                "Projections must have same format :\
                \nAnterior " + str(self.ant_pix.shape) +\
                "\nPosteror" + str(self.post_pix.shape)).exec_()
        else:
            QMessageBox(QMessageBox.Warning, "Error",\
            "Posterior and/or anterior projection not selected").exec_()


    def liver_check(self):
        thresh = self.group_liver.l1.wid_list[1].value()
        morpho = self.group_liver.l2.wid_list[1].value()

        if self.computed and self.group_liver.isChecked():
            self.mask_l = self.group_liver.build_mask(thresh, morpho)
            if self.group_blood.isChecked(): self.blood_check()
            else: self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, None)

        elif self.computed and not self.group_liver.isChecked():
            self.mask_l = None
            self.blood_check()
            self.compute_mean()


    def blood_check(self):
        thresh = self.group_blood.l1.wid_list[1].value()
        morpho = self.group_blood.l2.wid_list[1].value()

        if self.computed and self.group_blood.isChecked():
            self.mask_b = self.group_blood.build_mask(thresh, morpho, self.mask_l)
            i = self.s.wid_list[0].value()
            if not self.group_liver.isChecked(): self.group_mean.update_display(i, None ,self.mask_b)
            else: self.group_mean.update_display(i, self.mask_l, self.mask_b)
        elif self.computed and not self.group_blood.isChecked():
            self.mask_b = None
            self.compute_mean()


    def call_update_display(self, i):
        if self.group_ant.getImg() is not None:
            self.group_ant.update_display(i, None, None)
        if self.group_post.getImg() is not None:
            self.group_post.update_display(i, None, None)
        if self.computed:
            self.group_mean.update_display(i, self.mask_l, self.mask_b)


    def show_curve(self):
        graph(self.group_ant.getTimeStep(), self.mean_f64, self.mask_l, self.mask_b)
