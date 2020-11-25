from PyQt5.QtWidgets import QFileDialog, QMessageBox
from skimage.morphology import disk, closing
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import trapz
from scipy import ndimage
from math import exp
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

def gird_shape(n):
    if n==0: return((0,0))
    if n==1: return((1,1))
    elif n==2: return((1,2))
    elif n==3: return((1,3))
    elif n==4: return((2,2))
    elif n==5 or n==6: return((2,3))
    elif n==7 or n==8: return((2,4))
    elif n==9: return((2,5))
    elif n==10 or n==11 or n==12: return((3,4))
    elif n==13 or n==14 or n==15: return((3,5))
    elif n==16 or n==17 or n==18: return((3,6))
    elif n==19 or n==20: return((4,5))
    elif n==21 or n==22 or n==23 or n==24: return((4,6))
    elif n==25 or n==26 or n==27 or n==28: return((4,7))
    elif n==29 or n==30 or n==31 or n==32: return((4,8))
    elif n==33 or n==34 or n==35: return((5,7))
    elif n==36: return((5,8))

def match_file(file_list):
    pairs = []
    list_copy = file_list.copy()
    for i in range(len(file_list)):
        if 'Ant' in file_list[i]: list_copy[i]=file_list[i].replace('Ant', '')
        elif 'ant' in file_list[i]: list_copy[i]=file_list[i].replace('ant', '')
        elif 'Post' in file_list[i]: list_copy[i]=file_list[i].replace('Post', '')
        elif 'post' in file_list[i]: list_copy[i]=file_list[i].replace('post', '')
    for i in range(len(list_copy)):
        for j in range(i+1, len(list_copy)):
            if list_copy[i]==list_copy[j]:
                pairs.append([i,j,list_copy[i].split('_')[-1].split('.')[0]])
    return(pairs)


def liv_utr(ft1, ft2, lt1, lt2, ct1, ct2, t1, t2, tdemi):
    bcl = 0.693147/tdemi
    cnormt2 = ct2/ct1
    at1 = (ft2-lt1-(ft1-lt1)*cnormt2)/(1-cnormt2)
    integral = (np.exp(-bcl*t1)-np.exp(-bcl*t2))/(bcl*(np.exp(-bcl*t1)))
    lcl = (lt2-lt1)/(at1*integral)
    return(bcl*60, lcl*60)


def bsa(height, weight):
    bsa = (height*weight/3600)**(1/2) # Mosteller
    return(bsa)


def time_series(time_step, img_stack, liver_mask, blood_mask, shift):
    time_series = []
    for img in range(len(img_stack)):
        time_series.append([0,0,0])
        shifted_mask=None
        if shift and shift[img]:
            print('shifted mask for calcul')
            shifted_mask = ndimage.shift(liver_mask, [shift[img],0])
            shifted_mask = closing(shifted_mask,disk(3))
            #shifted_mask = np.ma.masked_where(shifted_mask==0, shifted_mask)
        for i in range(len(img_stack[img])):
            for j in range(len(img_stack[img,i])):
                if shifted_mask is not None and shifted_mask[i,j]:
                    time_series[-1][0] += img_stack[img,i,j]
                elif liver_mask is not None and shifted_mask is None and liver_mask[i,j]:
                    time_series[-1][0] += img_stack[img,i,j]
                if blood_mask is not None and blood_mask[i,j]:
                    time_series[-1][1] += img_stack[img,i,j]
        time_series[-1][2] = np.sum(img_stack[img])

    time_steps = np.array([float(time_step)*(i+1) for i in range(len(time_series))])
    decay = 0.69315/(6*60*60)
    corr_factor = [1/np.exp(-decay*i) for i in (time_steps-(float(time_step)/2))]
    lt = [time_series[i][0]*corr_factor[i] for i in range(len(time_series))]
    ct = [time_series[i][1]*corr_factor[i] for i in range(len(time_series))]
    ft = [time_series[i][2]*corr_factor[i] for i in range(len(time_series))]
    return(lt,ct,ft,time_steps)


def graph(time_step, img_stack, liver_mask, blood_mask, h, w, shift):
    lt, ct, ft, time_steps = time_series(time_step, img_stack, liver_mask, blood_mask, shift)
    fig = plt.figure(figsize=[10,5])
    plt.xlabel('Time (sec)')
    plt.ylabel('Gamma event count')
    if liver_mask is not None:
        plt.plot(time_steps, lt, color='#478bff', label='Liver activity')
    if blood_mask is not None:
        plt.plot(time_steps, ct, color='#ff4a4a', label='Blood pool activity')
        popt, pcov = curve_fit(lambda t,c0,l: c0*np.exp(-l*t), time_steps[15:35], ct[15:35], p0 = (3000, 0.001))
        plt.plot(time_steps[15:35], [popt[0]*np.exp(-popt[1]*i) for i in time_steps[15:35]],
        color='lightgray', linestyle='--', label="Expo fit : "+r"$\lambda$"+" = {:.5f}".format(popt[1]))
        tdemi = 0.693147/popt[1]
        print('tdemi : {:.2f}'.format(tdemi))
    #plt.plot(time_steps, [time_series[i][2] for i in range(len(time_series))],
    #color='lightgray',linestyle='--')

    if liver_mask is not None and blood_mask is not None:
        bcl, liver_clr = liv_utr(ft[15], ft[35], lt[15], lt[35], ct[15], ct[35], time_steps[15], time_steps[35], tdemi)
        print('Clearance rate : {:.5f}'.format(liver_clr))
        print('bsa : {:.5f}'.format(bsa(h, w)))
        corrected = liver_clr/bsa(h, w)
        corrected_bcl = bcl/bsa(h, w)
        plt.title('Activity vs. Time\nLiver uptake rate of {:.3f}%/min (corrected at {:.3f}%/min/m^2) and bcl of {:.3f}%/min/m^2'.\
        format(liver_clr*100, corrected*100, corrected_bcl*100), color="white")
    else:
        plt.title('Activity vs. Time', color="white")

    plt.grid(linewidth=1)
    plt.tight_layout()
    plt.legend()
    return(fig)
