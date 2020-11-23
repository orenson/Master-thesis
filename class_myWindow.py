from PyQt5.QtWidgets import QRadioButton, QSlider, QLabel, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton
from func import f64_2_u8, aryth_avg, update_plt_param, graph
from skimage.morphology import disk, closing
from matplotlib import cm, pyplot as plt
from class_groupParam import Group_param
from skimage.filters.rank import median
from PyQt5 import QtCore, QtWidgets
from class_hLayout import HLayout
from class_groupImg import GroupImg
from skimage.draw import ellipse
from scipy import ndimage
import numpy as np
import os


class MyWindow(QMainWindow):
    def __init__(self, path_ant=None, path_post=None):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Hepatobiliary scintigraphy image processing")
        self.setFixedSize(1393, 796)
        centralwidget = QWidget(self)
        self.computed = False
        self.mask_l = None
        self.mask_b = None
        self.shift_list = None
        self.ell = np.zeros((128, 128), dtype=np.bool)
        self.ell[ellipse(45, 66, 20, 25, rotation=np.deg2rad(0))] = 1
        plt.ion()

        self.s = HLayout(centralwidget, [QSlider(), QLabel()], [None,'0'])
        self.s.setGeometry(150, 520, 451, 61)
        self.s.wid_list[0].setMaximum(35)
        self.s.wid_list[0].setOrientation(QtCore.Qt.Horizontal)
        self.s.wid_list[0].valueChanged['int'].connect(self.s.wid_list[1].setNum)
        self.s.wid_list[1].setMinimumSize(30, 0)

        self.group_ant = GroupImg(centralwidget, "Anterior projection", 5, 10, 370, 419, self.s.wid_list[0])
        self.group_ant.add_widget(QPushButton(), 'Select')
        self.group_post = GroupImg(centralwidget, "Posterior projection", 380, 10, 370, 419, self.s.wid_list[0], True)
        self.group_post.add_widget(QPushButton(), 'Select')
        self.group_mean = GroupImg(centralwidget, "Gmean dataset", 755, 10, 632, 780, self.s.wid_list[0])
        filters = HLayout(self.group_mean,[QRadioButton() for i in range(3)],['Raw','Median filter','Negative'],(90,0,0,0))
        filters.setMaximumHeight(33)
        filters.wid_list[0].setChecked(True)
        self.group_mean.add_widget(filters)
        self.group_mean.wid_list[-1].wid_list[0].clicked.connect(self.transfo_raw)
        self.group_mean.wid_list[-1].wid_list[1].clicked.connect(self.transfo_med)
        self.group_mean.wid_list[-1].wid_list[2].clicked.connect(self.transfo_inv)
        self.group_mean.add_widget(QPushButton(), 'Compute geometric mean')
        self.group_mean.wid_list[-1].clicked.connect(self.compute_mean)
        self.group_mean.add_widget(QPushButton(), 'Show time-activity curve')
        self.group_mean.add_widget(QPushButton(), 'Save parameters')
        self.s.wid_list[0].valueChanged['int'].connect(self.call_update_display)

        self.group_liver = Group_param(centralwidget, 'Liver detection', 5, 620, 370, 170)
        self.group_liver.clicked.connect(self.liver_check)
        self.group_blood = Group_param(centralwidget, 'Blood pool detection', 380, 620, 370, 170)
        self.group_blood.clicked.connect(self.blood_check)

        self.setCentralWidget(centralwidget)
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(0, 0, 928, 22)
        self.setMenuBar(menubar)
        update_plt_param()

        if path_ant and path_post:
            self.group_ant.load_dicom(path_ant)
            self.group_post.load_dicom(path_post)
            self.compute_mean()
            self.group_liver.setChecked(True)
            self.group_blood.setChecked(True)
            self.group_liver.l1.wid_list[1].setValue(self.group_liver.l1.wid_list[1].value()+1)
            self.group_liver.l1.wid_list[1].setValue(self.group_liver.l1.wid_list[1].value()-1)
            self.respi()


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
                self.mean_u8 = f64_2_u8(self.mean_f64)
                avg_last10_f64 = aryth_avg(self.mean_f64[-10:])
                self.avg_last10_u8 = f64_2_u8(avg_last10_f64)
                avg_first5_f64 = aryth_avg(self.mean_f64[2:6])
                self.avg_first5_u8 = f64_2_u8(avg_first5_f64)

                self.group_liver.mask_init(self.avg_last10_u8)
                self.group_blood.mask_init(self.avg_first5_u8, 50)

                if self.group_mean.wid_list[2].wid_list[1].isChecked():
                    self.transfo_med()
                elif self.group_mean.wid_list[2].wid_list[2].isChecked():
                    self.transfo_inv()
                else:
                    self.transfo_raw()

                if not self.computed:
                    self.group_liver.l1.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_liver.l2.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_liver.l3.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_blood.l1.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_blood.l2.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_blood.l3.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_mean.wid_list[-1].clicked.connect(self.save)
                    self.group_mean.wid_list[-2].clicked.connect(self.show_curve)
                    self.computed = True
                    self.group_liver.l1.wid_list[1].sliderReleased.connect(self.respi)
                    self.group_liver.l2.wid_list[1].sliderReleased.connect(self.respi)
                    #self.group_liver.clicked.connect(self.respi)

                scinty_id = self.group_ant.getPath().split('/')[-1].split('_')[-1].split('.')[0]
                directory = '/'.join(self.group_ant.getPath().split('/')[:-1])+'/'
                found = False
                if os.path.exists(directory+'.hbs_presets.txt'):
                    with open(directory+'.hbs_presets.txt', "r") as f:
                        for line in f.readlines():
                            if line.strip().split(',')[0]==scinty_id:
                                found = True
                                print('presets found')
                                self.group_liver.l1.wid_list[1].setValue(int(line.strip().split(',')[1]))
                                self.group_liver.l2.wid_list[1].setValue(int(line.strip().split(',')[2]))
                                self.group_blood.l1.wid_list[1].setValue(int(line.strip().split(',')[3]))
                                self.group_blood.l2.wid_list[1].setValue(int(line.strip().split(',')[4]))
                                self.group_ant.setW(float(line.strip().split(',')[5]))
                                self.group_ant.setH(float(line.strip().split(',')[6]))
                self.respi()

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
            else: self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l,
            None, self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)

        elif self.computed and not self.group_liver.isChecked():
            self.mask_l = None
            self.blood_check()
            self.call_update_display(self.s.wid_list[0].value())

    def blood_check(self):
        thresh = self.group_blood.l1.wid_list[1].value()
        morpho = self.group_blood.l2.wid_list[1].value()

        if self.computed and self.group_blood.isChecked():
            if self.mask_l is not None: self.mask_b = self.group_blood.build_mask(thresh, morpho, self.mask_l, self.ell)
            else: self.mask_b = self.group_blood.build_mask(thresh, morpho, None, self.ell)
            i = self.s.wid_list[0].value()
            if not self.group_liver.isChecked():
                self.group_mean.update_display(i, None , self.mask_b,
                self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)
            else:
                self.group_mean.update_display(i, self.mask_l, self.mask_b,
                self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)
        elif self.computed and not self.group_blood.isChecked():
            self.mask_b = None
            self.call_update_display(self.s.wid_list[0].value())

    def respi(self):
        print('released')
        if self.mask_l is not None and self.group_liver.isChecked():
            self.shift_list = [0 for i in range(len(self.mean_f64))]
            for im in range(len(self.mean_f64)):
                tot = np.sum(self.mask_l*self.mean_f64[im])
                for i in range(1,6):
                    shifted_liv = ndimage.shift(self.mask_l, [i,0])
                    shifted_liv = closing(shifted_liv,disk(3))
                    shifted_liv = np.ma.masked_where(shifted_liv==0, shifted_liv)
                    if np.sum(shifted_liv*self.mean_f64[im])>tot:
                        tot=np.sum(shifted_liv*self.mean_f64[im])
                        print('{} shifted to {}'.format(im, i))
                        self.shift_list[im]=i


    def call_update_display(self, i):
        if self.group_ant.getImg() is not None:
            self.group_ant.update_display(i, None, None, None, None, None)
        if self.group_post.getImg() is not None:
            self.group_post.update_display(i, None, None, None, None, None)
        if self.computed:
            self.group_mean.update_display(i, self.mask_l, self.mask_b,
            self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)

    def transfo_med(self):
        to_display = self.mean_u8.copy()
        for i in range(len(self.mean_u8)):
            to_display[i] = median(self.mean_u8[i], disk(1))
        self.group_mean.setImg(to_display)
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, self.mask_b,
        self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)

    def transfo_inv(self):
        self.group_mean.setImg(np.invert(self.mean_u8))
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, self.mask_b,
        self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)

    def transfo_raw(self):
        self.group_mean.setImg(self.mean_u8)
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, self.mask_b,
        self.group_liver.get_trans(), self.group_blood.get_trans(), self.shift_list)

    def show_curve(self):
        if self.mask_l is not None and self.mask_b is not None:
            graph(self.group_ant.getTimeStep(), self.mean_f64, self.mask_l,
            self.mask_b, self.group_ant.getH(), self.group_ant.getW(), self.shift_list)
        else:
            graph(self.group_ant.getTimeStep(), self.mean_f64, self.mask_l,
            self.mask_b, None, None, None)

    def save(self):
        scinty_id = self.group_ant.getPath().split('/')[-1].split('_')[-1].split('.')[0]
        directory = '/'.join(self.group_ant.getPath().split('/')[:-1])+'/'
        lines = []

        if os.path.exists(directory+'.hbs_presets.txt'):
            with open(directory+'.hbs_presets.txt', "r") as f:
                lines = f.readlines()
        with open(directory+'.hbs_presets.txt', "w") as f:
            f.write('#Patient_id,liver_thresh,liver_morpho,blood_thresh,blood_morpho,weight,size'+'\n')
            for line in lines[1:]:
                if line.strip().split(',')[0] != scinty_id:
                    f.write(line)
            t1=str(self.group_liver.l1.wid_list[1].value())
            m1=str(self.group_liver.l2.wid_list[1].value())
            t2=str(self.group_blood.l1.wid_list[1].value())
            m2=str(self.group_blood.l2.wid_list[1].value())
            w=str(self.group_ant.getW())
            h=str(self.group_ant.getH())
            f.write(','.join([scinty_id, t1, m1, t2, m2, w, h])+'\n')
        print('saved')
