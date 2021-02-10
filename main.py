#!/usr/bin/env python3
import os
import sys
from func import match_file
from PyQt5 import QtGui, QtCore
from class_myWindow import MyWindow
from without_gui import get_liv_uptr
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25,25,25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45,111,197))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)

    if len(sys.argv)==2: #python3 images
        if not sys.argv[1].endswith('/'): sys.argv[1]+='/'
        if os.path.isdir(sys.argv[1]):
            files = os.listdir(sys.argv[1])
            files = [i for i in files if i.endswith('.dcm')]
            if len(files)>0:
                saved = []
                if os.path.exists(sys.argv[1]+'.hbs_presets.txt'):
                    with open(sys.argv[1]+'.hbs_presets.txt', "r") as f:
                        lines = f.readlines()
                        saved = [line.strip().split(',')[0] for line in lines[1:]]
                pairs = sorted(match_file(files), key=lambda x: x[-1])
                if len(pairs)>0:
                    for pair in pairs:
                        if pair[2] in saved:
                            idx = saved.index(pair[2])
                            p1 = int(lines[idx+1].strip().split(',')[1])
                            p2 = int(lines[idx+1].strip().split(',')[2])
                            p3 = int(lines[idx+1].strip().split(',')[3])
                            p4 = int(lines[idx+1].strip().split(',')[4])
                            w = float(lines[idx+1].strip().split(',')[5])
                            h = float(lines[idx+1].strip().split(',')[6])
                            res = get_liv_uptr(sys.argv[1]+files[pair[0]], sys.argv[1]+files[pair[1]], p1, p2, p3, p4, w, h)
                        else:
                            res = get_liv_uptr(sys.argv[1]+files[pair[0]], sys.argv[1]+files[pair[1]])
                        print(pair[2], '\t{:.3f} %/min/m^2'.format(res*100), end='\t', sep='')
                        if pair[2] not in saved:
                            print('Warning : arbitrary values may have been used', end='')
                        print()
                else: print('No matching pairs found in {}'.format(sys.argv[1]))
            else: print('No dicom files found in {}'.format(sys.argv[1]))
        else: print('{} is not a directory'.format(sys.argv[1]))

    elif len(sys.argv) == 3: #python3 main.py file1 file2
        path_ant = sys.argv[1]
        path_post = sys.argv[2]
        win = MyWindow(path_ant, path_post)
        win.show()
        sys.exit(app.exec_())

    else: #python3 main.py
        win = MyWindow()
        win.show()
        sys.exit(app.exec_())
