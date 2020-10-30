from PyQt5.QtWidgets import QFileDialog, QMessageBox
from matplotlib import pyplot as plt
import numpy as np


def load_file():
    dialog = QFileDialog()
    dialog.setWindowTitle("Choose a dicom file to open")
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter("Dicom (*.dcm)")
    dialog.setViewMode(QFileDialog.Detail)

    if dialog.exec_():
        file_path = str(dialog.selectedFiles()[0])
        print(file_path, "selected")
        return(file_path)
    else:
        return(0)


def aryth_avg(img_stack):
    avg = np.zeros(img_stack[0].shape, dtype=img_stack.dtype)
    for i in range(len(img_stack)):
        avg += img_stack[-i]
    return(avg/len(img_stack))


def f64_2_u8(img_stack):
    if len(img_stack.shape)==2:
        stretched = 255 * (img_stack / max(np.unique(img_stack)))
        new_stack = stretched.astype(np.uint8)
    elif len(img_stack.shape)==3:
        new_stack = np.empty(img_stack.shape, np.uint8)
        for i in range(len(img_stack)):
            stretched = 255 * (img_stack[i] / max(np.unique(img_stack[i])))
            new_stack[i] = stretched.astype(np.uint8)
    else:
        raise ValueError('Array of wrong number of dimentions given to f64_2_u8')
    return(new_stack)


def process_date(date):
    year = str(date[:4])
    month = str(date[4:6])
    day = str(date[6:])
    return(day+'/'+month+'/'+year)


def update_plt_param():
    plt.rcParams.update({
    "lines.color": "white",
    "patch.edgecolor": "white",
    "text.color": "white",
    "axes.facecolor": "#151515",
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "#353535",
    "figure.facecolor": "#151515",
    "figure.edgecolor": "#151515",
    "toolbar": "None"})


def graph(time_step, img_stack, liver_mask, blood_mask):
    time_series = []
    for img in range(len(img_stack)):
        time_series.append([0,0])
        for i in range(len(img_stack[img])):
            for j in range(len(img_stack[img,i])):
                if liver_mask is not None and liver_mask[i,j]:
                    time_series[-1][0] += img_stack[img,i,j]
                if blood_mask is not None and blood_mask[i,j]:
                    time_series[-1][1] += img_stack[img,i,j]
    time_steps = [float(time_step)*(i+1) for i in range(len(time_series))]

    plt.figure(figsize=[8,4])
    plt.title('Activity vs. Time', color="white")
    plt.xlabel('Time (sec)')
    plt.ylabel('Gamma event count')
    if liver_mask is not None:
        plt.plot(time_steps,
        [time_series[i][0] for i in range(len(time_series))], color='#478bff')
    if blood_mask is not None:
        plt.plot(time_steps,
        [time_series[i][1] for i in range(len(time_series))], color='#ff4a4a')
    plt.grid(linewidth=1)
    plt.tight_layout()
    plt.show()
