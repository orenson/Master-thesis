from PyQt5.QtWidgets import QRadioButton, QSlider, QLabel, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QInputDialog
from func import f64_2_u8, aryth_avg, update_plt_param, graph, gird_shape, time_series, best_match, check_range_input
from class_screenshot import ScreenshotWindow
from skimage.morphology import disk, closing
from skimage.color import rgba2rgb,rgb2gray
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib import cm, pyplot as plt
from class_groupParam import Group_param
from skimage.filters.rank import median
from matplotlib import image as mpimg
from skimage.transform import resize
from class_groupImg import GroupImg
from class_mySlider import MySlider
from skimage import transform, io
from class_hLayout import HLayout
from skimage.draw import ellipse
from PyQt5.QtCore import Qt
from datetime import date
import pydicom as pd
import numpy as np
import os

class MyWindow(QMainWindow):
    def __init__(self, path_ant=None, path_post=None):
        super(MyWindow, self).__init__()
        self.setWindowTitle("HBS_Tools")
        self.setFixedSize(1400, 773)
        centralwidget = QWidget(self)
        self.computed = False
        self.mask_l = None
        self.mask_b = None
        self.ell = np.zeros((128, 128), dtype=np.bool)
        self.ell[ellipse(52, 66, 30, 25, rotation=np.deg2rad(0))] = 1
        plt.ion()

        self.s = HLayout(centralwidget, [MySlider(), QLabel()], [None,'0'])
        self.s.setGeometry(150, 510, 451, 61)
        self.s.wid_list[0].setMaximum(35)
        self.s.wid_list[0].setOrientation(QtCore.Qt.Horizontal)
        #self.s.wid_list[0].setStyleSheet("QSlider:focus { border: 1px solid #999999} ")
        self.s.wid_list[0].valueChanged['int'].connect(self.s.wid_list[1].setNum)
        self.s.wid_list[1].setMinimumSize(30, 0)

        self.group_ant = GroupImg(centralwidget, "Anterior projection", 5, 10, 370, 419, self.s.wid_list[0])
        self.group_ant.add_widget(QPushButton(), 'Select')
        self.group_ant.wid_list[2].setFont(QtGui.QFont('Arial', 20))
        self.group_post = GroupImg(centralwidget, "Posterior projection", 380, 10, 370, 419, self.s.wid_list[0], True)
        self.group_post.add_widget(QPushButton(), 'Select')
        self.group_post.wid_list[2].setFont(QtGui.QFont('Arial', 20))
        self.group_mean = GroupImg(centralwidget, "Gmean dataset", 755, 10, 639, 757, self.s.wid_list[0])
        filters = HLayout(self.group_mean,[QRadioButton() for i in range(3)],['Raw','Median filter','Negative'],(90,0,0,0))
        filters.wid_list[0].setFont(QtGui.QFont('Arial', 14))
        filters.wid_list[1].setFont(QtGui.QFont('Arial', 14))
        filters.wid_list[2].setFont(QtGui.QFont('Arial', 14))
        filters.setMaximumHeight(33)
        filters.wid_list[0].setChecked(True)
        self.group_mean.add_widget(filters)
        mean_l1 = HLayout(self.group_mean,[QPushButton(), QPushButton()],['Compute geometric mean', 'Show time-activity curves'],(0,0,0,0))
        mean_l1.setMaximumHeight(30)
        #mean_l1.setMaximumHeight(24)
        self.group_mean.add_widget(mean_l1)
        self.group_mean.wid_list[-1].wid_list[0].clicked.connect(self.compute_mean)
        mean_l2 = HLayout(self.group_mean,[QPushButton(), QPushButton()],['Save parameters', 'Export'],(0,0,0,0))
        mean_l2.setMaximumHeight(30)
        #mean_l2.setMaximumHeight(24)
        self.group_mean.add_widget(mean_l2)

        self.s.wid_list[0].valueChanged['int'].connect(self.call_update_display)
        self.group_liver = Group_param(centralwidget, 'Liver detection', 5, 577, 370, 190)
        self.group_liver.clicked.connect(self.liver_check)
        self.group_blood = Group_param(centralwidget, 'Blood pool detection', 380, 577, 370, 190)
        self.group_blood.clicked.connect(self.blood_check)

        self.setCentralWidget(centralwidget)
        update_plt_param()

        if path_ant and path_post:
            self.group_ant.load_dicom(path_ant)
            self.group_post.load_dicom(path_post)
            self.compute_mean()
            self.group_liver.setChecked(True)
            self.group_blood.setChecked(True)
            self.group_liver.l1.wid_list[1].setValue(self.group_liver.l1.wid_list[1].value()+1)
            self.group_liver.l1.wid_list[1].setValue(self.group_liver.l1.wid_list[1].value()-1)


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
            if self.computed: self.transfo_raw()
        elif event.key()==QtCore.Qt.Key_M:
            self.group_mean.wid_list[2].wid_list[1].setChecked(True)
            if self.computed: self.transfo_med()
        elif event.key()==QtCore.Qt.Key_N:
            self.group_mean.wid_list[2].wid_list[2].setChecked(True)
            if self.computed: self.transfo_inv()
        elif event.key()==QtCore.Qt.Key_L:
            if self.group_liver.isChecked(): self.group_liver.setChecked(False)
            else: self.group_liver.setChecked(True)
            self.liver_check()
        elif event.key()==QtCore.Qt.Key_B:
            if self.group_blood.isChecked(): self.group_blood.setChecked(False)
            else: self.group_blood.setChecked(True)
            self.blood_check()
        elif event.key()==QtCore.Qt.Key_E:
            if self.computed: self.export()
        else:
            super().keyPressEvent(event)


    def wheelEvent(self, event):
        delta = int(event.angleDelta().y()/8)/15
        self.s.wid_list[0].setValue(self.s.wid_list[0].value() + delta)


    def mousePressEvent(self, event):
        if 69 <= event.x() <= 96 and 474 <= event.y() <= 489:
            x, okPressed = QInputDialog.getInt(self,"Weight input",
            "Select weight manually :", 50.0, 0.0, 500.0, 1)
            if okPressed: self.group_ant.setW(x)
        elif 101 <= event.x() <= 136 and 474 <= event.y() <= 489:
            x, okPressed = QInputDialog.getInt(self,"Size input",
            "Select height manually :", 160, 50, 250, 1)
            if okPressed: self.group_ant.setH(x)


    def compute_mean(self):
        if hasattr(self.group_ant, 'img_f64') and hasattr(self.group_post, 'img_f64'):
            ant = self.group_ant.getImg()
            post = self.group_post.getImg()
            if ant.shape == post.shape:
                self.mean_f64 = (ant*post)**(1/2)
                self.mean_u8 = f64_2_u8(self.mean_f64)

                self.group_liver.mask_init(self.mean_f64, start=25, end=35)
                self.group_liver.l5.wid_list[0].setText('25-35')
                start_blood = best_match(self.mean_f64[:10])
                self.group_blood.l5.wid_list[0].setText(str(start_blood))
                self.group_blood.mask_init(self.mean_f64, start=start_blood, end=start_blood+1, offset=50)
                #self.group_liver.mask_init(self.avg_last10_f64, len(self.mean_f64))
                #self.group_blood.mask_init(self.avg_first5_f64, len(self.mean_f64), 0.9)
                self.s.wid_list[0].setMaximum(min(ant.shape[0],post.shape[0])-1)

                if self.group_mean.wid_list[2].wid_list[1].isChecked(): self.transfo_med()
                elif self.group_mean.wid_list[2].wid_list[2].isChecked(): self.transfo_inv()
                else: self.transfo_raw()

                if not self.computed:
                    self.group_mean.wid_list[2].wid_list[0].clicked.connect(self.transfo_raw)
                    self.group_mean.wid_list[2].wid_list[1].clicked.connect(self.transfo_med)
                    self.group_mean.wid_list[2].wid_list[2].clicked.connect(self.transfo_inv)
                    self.group_liver.l1.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_liver.l2.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_liver.l3.wid_list[1].valueChanged['int'].connect(self.liver_check)
                    self.group_blood.l1.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_blood.l2.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_blood.l3.wid_list[1].valueChanged['int'].connect(self.blood_check)
                    self.group_mean.wid_list[-1].wid_list[0].clicked.connect(self.save)
                    self.group_mean.wid_list[-1].wid_list[1].clicked.connect(self.export)
                    self.group_mean.wid_list[-2].wid_list[1].clicked.connect(lambda :self.show_curve(show=True))
                    self.group_liver.l5.wid_list[0].editingFinished.connect(self.range_edited_liv)
                    self.group_blood.l5.wid_list[0].editingFinished.connect(self.range_edited_blo)
                    self.computed = True

                    self.group_liver.l4.wid_list[1].clicked.connect(lambda :(self.group_liver.\
                    update_shift(1,0,0,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_liver.l4.wid_list[2].clicked.connect(lambda :(self.group_liver.\
                    update_shift(0,0,1,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_liver.l4.wid_list[3].clicked.connect(lambda :(self.group_liver.\
                    update_shift(0,0,0,1,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_liver.l4.wid_list[4].clicked.connect(lambda :(self.group_liver.\
                    update_shift(0,1,0,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))

                    self.group_blood.l4.wid_list[1].clicked.connect(lambda :(self.group_blood.\
                    update_shift(1,0,0,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_blood.l4.wid_list[2].clicked.connect(lambda :(self.group_blood.\
                    update_shift(0,0,1,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_blood.l4.wid_list[3].clicked.connect(lambda :(self.group_blood.\
                    update_shift(0,0,0,1,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))
                    self.group_blood.l4.wid_list[4].clicked.connect(lambda :(self.group_blood.\
                    update_shift(0,1,0,0,self.s.wid_list[0].value()), self.call_update_display(self.s.wid_list[0].value())))

                scinty_id =  self.group_ant.getUID()
                directory = '/'.join(self.group_ant.getPath().split('/')[:-1])+'/'
                found = False
                if os.path.exists(directory+'.hbs_presets.txt'):
                    with open(directory+'.hbs_presets.txt', "r") as f:
                        for line in f.readlines():
                            if line.strip().split(',')[0]==scinty_id:
                                found = True
                                print('presets found')
                                split = line.strip().split(',')
                                self.group_liver.l5.wid_list[0].setText(split[5])
                                self.range_edited_liv()
                                self.group_blood.l5.wid_list[0].setText(split[6])
                                self.range_edited_blo()
                                self.group_liver.l1.wid_list[1].setValue(int(split[1]))
                                self.group_liver.l2.wid_list[1].setValue(int(split[2]))
                                self.group_blood.l1.wid_list[1].setValue(int(split[3]))
                                self.group_blood.l2.wid_list[1].setValue(int(split[4]))
                                self.group_ant.setW(float(split[7]))
                                self.group_ant.setH(float(split[8]))
                                shift_l = [int(i) for i in split[9:9+2*len(self.mean_f64)]]
                                shift_b = [int(i) for i in split[9+2*len(self.mean_f64):9+4*len(self.mean_f64)]]
                                shift_l = np.reshape(shift_l, (len(self.mean_f64), 2))
                                shift_b = np.reshape(shift_b, (len(self.mean_f64), 2))
                                self.group_liver.set_shift(shift_l.tolist())
                                self.group_blood.set_shift(shift_b.tolist())
                                break


                if not found: self.respi()

            else:
                QMessageBox(QMessageBox.Warning, "Error",\
                "Projections must have same format :\
                \nAnterior " + str(self.group_ant.getImg().shape) +\
                "\nPosteror" + str(self.group_post.getImg().shape)).exec_()
        else:
            QMessageBox(QMessageBox.Warning, "Error",\
            "Posterior and/or anterior projection not selected").exec_()


    def liver_check(self):
        thresh = self.group_liver.l1.wid_list[1].value()
        morpho = self.group_liver.l2.wid_list[1].value()

        if self.computed and self.group_liver.isChecked():
            self.mask_l = self.group_liver.build_mask(thresh, morpho)
            if self.group_blood.isChecked(): self.blood_check()
            else: self.group_mean.update_display(self.s.wid_list[0].value(),self.mask_l,None,
            self.group_liver.get_trans(), self.group_blood.get_trans(),self.group_liver.get_shift(), self.group_blood.get_shift())

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
                self.group_mean.update_display(i, None , self.mask_b, self.group_liver.get_trans(),
                self.group_blood.get_trans(), self.group_liver.get_shift(), self.group_blood.get_shift())
            else:
                self.group_mean.update_display(i, self.mask_l, self.mask_b, self.group_liver.get_trans(),
                self.group_blood.get_trans(), self.group_liver.get_shift(), self.group_blood.get_shift())
        elif self.computed and not self.group_blood.isChecked():
            self.mask_b = None
            self.call_update_display(self.s.wid_list[0].value())

    def respi(self):
        print('respi check')
        thresh = self.group_liver.l1.wid_list[1].value()
        morpho = self.group_liver.l2.wid_list[1].value()
        mask_l = self.group_liver.build_mask(thresh, morpho)
        shift = [0 for i in range(len(self.mean_f64))]
        for im in range(5,len(self.mean_f64)):
            tot = np.sum(mask_l*self.mean_f64[im])
            for i in range(1,6):
                matrix = transform.EuclideanTransform(translation=(0,i))
                shifted_liv = transform.warp(mask_l, matrix.inverse)
                if np.sum(shifted_liv*self.mean_f64[im])>tot:
                    tot=np.sum(shifted_liv*self.mean_f64[im])
                    print('{} shifted to {}'.format(im, i))
                    shift[im]=i

        for i in range(len(shift)):
            if shift[i]: self.group_liver.update_shift(0,0,0,shift[i],i)


    def call_update_display(self, i):
        if self.group_ant.getImg() is not None:
            self.group_ant.update_display(i, None, None, None, None, None, None)
        if self.group_post.getImg() is not None:
            self.group_post.update_display(i, None, None, None, None, None, None)
        if self.computed:
            self.group_mean.update_display(i, self.mask_l, self.mask_b,self.group_liver.get_trans(),
            self.group_blood.get_trans(), self.group_liver.get_shift(), self.group_blood.get_shift())

    def transfo_med(self):
        to_display = self.mean_u8.copy()
        for i in range(len(self.mean_u8)):
            to_display[i] = median(self.mean_u8[i], disk(1))
        self.group_mean.setImg(to_display)
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l, self.mask_b,
        self.group_liver.get_trans(), self.group_blood.get_trans(),self.group_liver.get_shift(), self.group_blood.get_shift())

    def transfo_inv(self):
        self.group_mean.setImg(np.invert(self.mean_u8))
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l,
        self.mask_b,self.group_liver.get_trans(), self.group_blood.get_trans(),
        self.group_liver.get_shift(), self.group_blood.get_shift())

    def transfo_raw(self):
        self.group_mean.setImg(self.mean_u8)
        self.group_mean.update_display(self.s.wid_list[0].value(), self.mask_l,
        self.mask_b,self.group_liver.get_trans(), self.group_blood.get_trans(),
        self.group_liver.get_shift(), self.group_blood.get_shift())

    def show_curve(self, show=True):
        if self.mask_l is not None and self.mask_b is not None:
            plot = graph(self.group_ant.getTimeStep(), self.mean_f64, self.mask_l,
            self.mask_b, self.group_ant.getH(), self.group_ant.getW(), self.group_liver.get_shift(), self.group_blood.get_shift())
            if show: plt.show()
            else: return(plot)
        elif show:
            plot = graph(self.group_ant.getTimeStep(), self.mean_f64, self.mask_l,
            self.mask_b, None, None, self.group_liver.get_shift(), self.group_blood.get_shift())
            plt.show()


    def range_edited_liv(self):
        txt = self.group_liver.l5.wid_list[0].text()
        start, end = check_range_input(txt, len(self.mean_f64))
        if start and end:
            self.group_liver.mask_init(self.mean_f64, start=start, end=end)
            self.liver_check()

    def range_edited_blo(self):
        txt = self.group_blood.l5.wid_list[0].text()
        start, end = check_range_input(txt, len(self.mean_f64))
        if start and end:
            self.group_blood.mask_init(self.mean_f64, start=start, end=end, offset=50)
            self.blood_check()

    def export(self):
        items = ("Raw times series (.csv)", "Screenshot (.png)", "Dicom file (.dcm)")
        item, ok_pressed = QInputDialog.getItem(self, "Export",
         "Select exportation format", items, 1)

        if ok_pressed:
            if item == "Raw times series (.csv)": self.export_raw()
            elif item == "Screenshot (.png)": self.export_screenshot()
            elif item == "Dicom file (.dcm)": self.export_dicom()


    def export_raw(self):
        if self.mask_l is not None and self.mask_b is not None:
            lt, ct, ft, time_steps = time_series(self.group_ant.getTimeStep(),
            self.mean_f64, self.mask_l, self.mask_b, self.group_liver.get_shift(), self.group_blood.get_shift())
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fname, _ = QFileDialog.getSaveFileName(self,"Save as","RawData.csv","All (.*)", options=options)
            if fname:
                with open(fname, "w") as f:
                    f.write('#time, liver_count, blood_count, full_count\n')
                    for i in range(len(time_steps)):
                        f.write('{},{},{},{}\n'.format(time_steps[i], lt[i], ct[i], ft[i]))
        else: QMessageBox(QMessageBox.Warning, "Error","Both mask sould be checked").exec_()


    def export_screenshot(self):
        prefix = self.group_ant.getPath().split('/')[-1].split('_')[-1].split('.')[0]
        self.win = ScreenshotWindow(self.group_ant.getImg().shape[0], prefix)
        if self.win.exec_():
            #self.win.generate_img(self.mean_f64, self.mask_l, self.mask_b, self.group_liver.get_shift(), self.group_blood.get_shift(),
            #self.group_ant.getH(), self.group_ant.getW(), self.group_ant.getTimeStep())
            selection, res, view, fname = self.win.get_info()
            if len(selection)>0 and res:
                prefix = fname.split('.png')[0]
                fname1 = prefix+'_slices.png'
                fname2 = prefix+'_timeSeries.png'
            else: fname1 = fname2 = fname
            gird_y, gird_x = gird_shape(len(selection))
            plt.figure(figsize=[12,6])
            plt.suptitle(self.group_ant.patient+' - '+self.group_ant.date)
            for i in range(len(selection)):
                plt.subplot(gird_y,gird_x,i+1)
                plt.axis('off')
                plt.title("GMean {}".format(selection[i]), fontdict={'fontsize': 8})
                #plt.imshow(self.mean_f64[selection[i]-1],cmap=plt.cm.gray)
                plt.imshow(self.group_mean.getImg()[selection[i]-1],cmap=plt.cm.gray)
                mask_liv, mask_blo = self.group_mean.update_display(selection[i]-1,self.mask_l, self.mask_b,
                0, 0, self.group_liver.get_shift(), self.group_blood.get_shift(), apply=False)
                if self.mask_l is not None:
                    plt.imshow(mask_liv, cmap='coolwarm', interpolation="nearest")
                if self.mask_b is not None:
                    plt.imshow(mask_blo, cmap='RdYlBu', interpolation="nearest")
                if i==len(selection)-1:
                    plt.tight_layout()
                    plt.savefig(fname1, bbox_inches='tight')
                    plt.close()
                    if view:
                        plt.figure(1,figsize=[9,5])
                        plt.axis('off')
                        plt.tight_layout()
                        plt.imshow(mpimg.imread(fname1))
            if res:
                if self.mask_l is not None and self.mask_b is not None:
                    plot = self.show_curve(show=False)
                    plot.savefig(fname2, bbox_inches='tight')
                    plt.close()
                    if view:
                        plt.figure(2,figsize=[9,5])
                        plt.axis('off')
                        plt.tight_layout()
                        plt.imshow(mpimg.imread(fname2))
                else: QMessageBox(QMessageBox.Warning, "Error",
                "Plot failed, both masks sould be selected to generate results").exec_()
            if view: plt.show()


    def export_dicom(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fname, _ = QFileDialog.getSaveFileName(self,"Save as","Export.dcm","All (.*)", options=options)
        #mean = np.round(self.mean_f64).astype(np.uint16)

        if fname:
            '''
            for img in range(len(mean)):
                ma = np.amax(mean[img])
                mask_liv, mask_blo = self.group_mean.update_display(img,self.mask_l, self.mask_b,
                0, 0, self.group_liver.get_shift(), self.group_blood.get_shift(), apply=False)
                for i in range(len(mean[img])):
                    for j in range(len(mean[img,i])):
                        if self.mask_l is not None and mask_liv[i,j]:
                            mean[img,i,j] = ma
                        if self.mask_b is not None and mask_blo[i,j]:
                            mean[img,i,j] = ma'''

            if self.mask_l is not None and self.mask_b is not None:
                plot = self.show_curve(show=False)
                plot.savefig('.temporary1.png', bbox_inches='tight')
                plt.close()

                gird_y, gird_x = gird_shape(self.mean_u8.shape[0])
                plt.figure(figsize=[12,6])
                plt.suptitle(self.group_ant.patient+' - '+self.group_ant.date)
                for i in range(self.mean_u8.shape[0]):
                    plt.subplot(gird_y,gird_x,i+1)
                    plt.axis('off')
                    plt.title("GMean {}".format(i), fontdict={'fontsize': 8})
                    plt.imshow(self.group_mean.getImg()[i],cmap=plt.cm.gray)
                    mask_liv, mask_blo = self.group_mean.update_display(i,self.mask_l, self.mask_b,
                    0, 0, self.group_liver.get_shift(), self.group_blood.get_shift(), apply=False)
                    if self.mask_l is not None:
                        if self.group_mean.wid_list[2].wid_list[2].isChecked():
                            plt.imshow(mask_liv, cmap='hot', interpolation="nearest")
                        else:
                            plt.imshow(mask_liv, cmap='Reds', interpolation="nearest")
                    if self.mask_b is not None:
                        if self.group_mean.wid_list[2].wid_list[2].isChecked():
                            plt.imshow(mask_blo, cmap='hot', interpolation="nearest")
                        else:
                            plt.imshow(mask_blo, cmap='Reds', interpolation="nearest")
                    if i==self.mean_u8.shape[0]-1:
                        plt.tight_layout()
                        plt.savefig('.temporary2.png', bbox_inches='tight')
                        plt.close()

                with pd.dcmread(self.group_ant.getPath()) as template:
                    im = io.imread(".temporary1.png")
                    im_gray_1 = rgb2gray(rgba2rgb(im))
                    im_gray_1 = (im_gray_1*255).astype(np.uint16)

                    im = io.imread(".temporary2.png")
                    im = resize(im, im_gray_1.shape)
                    im_gray_2 = rgb2gray(rgba2rgb(im))
                    im_gray_2 = (im_gray_2*255).astype(np.uint16)

                    arr = np.empty((2,im_gray_1.shape[0],im_gray_1.shape[1]), dtype=np.uint16)
                    arr[0] = im_gray_2
                    arr[1] = im_gray_1
                    template[0x0018, 0x0070].value = np.sum(arr)          #tot_count
                    template[0x0028, 0x0010].value = im_gray_1.shape[0]   #rows
                    template[0x0028, 0x0011].value = im_gray_1.shape[1]   #columns
                    template[0x0028, 0x0008].value = 2
                    template[0x0008,0x0012].value = date.today().strftime("%Y%m%d")
                    template[0x0008,0x103E].value = 'DYN FOIE RESULTS'
                    template.PixelData = arr.tobytes()
                    template.save_as(fname)
                    if os.path.exists(".temporary1.png"): os.remove(".temporary1.png")
                    if os.path.exists(".temporary2.png"): os.remove(".temporary2.png")

            else: QMessageBox(QMessageBox.Warning, "Error",
            "Plot failed, both masks sould be selected to generate results").exec_()




    def save(self):
        scinty_id =  self.group_ant.getUID()
        directory = '/'.join(self.group_ant.getPath().split('/')[:-1])+'/'
        lines = []

        if os.path.exists(directory+'.hbs_presets.txt'):
            with open(directory+'.hbs_presets.txt', "r") as f:
                lines = f.readlines()
        with open(directory+'.hbs_presets.txt', "w") as f:
            f.write('#UID,liver_thresh,liver_morpho,blood_thresh,blood_morpho,liver_range,blood_range,weight,size,shift_liver(2*i),shift_blood(2*i)'+'\n')
            for line in lines[1:]:
                if line.strip().split(',')[0] != scinty_id:
                    f.write(line)
            t1=str(self.group_liver.l1.wid_list[1].value())
            m1=str(self.group_liver.l2.wid_list[1].value())
            t2=str(self.group_blood.l1.wid_list[1].value())
            m2=str(self.group_blood.l2.wid_list[1].value())
            txt1 = self.group_liver.l5.wid_list[0].text()
            txt2 = self.group_blood.l5.wid_list[0].text()
            w=str(self.group_ant.getW())
            h=str(self.group_ant.getH())
            shift_l = [item for sublist in self.group_liver.get_shift() for item in sublist]
            shift_l = str(shift_l)[1:-1]
            shift_b = [item for sublist in self.group_blood.get_shift() for item in sublist]
            shift_b = str(shift_b)[1:-1]
            f.write(','.join([scinty_id, t1, m1, t2, m2, txt1, txt2, w, h, shift_l, shift_b])+'\n')
        print('saved')
