import numpy as np
import pydicom as pd
from math import exp
from scipy import ndimage
from skimage.draw import ellipse
from scipy.optimize import curve_fit
from skimage.filters.rank import median
from skimage.filters import threshold_otsu
from skimage.morphology import disk, closing
from func import aryth_avg, f64_2_u8, liv_utr, bsa
from skimage.morphology import erosion, dilation, closing

def get_liv_uptr(file1, file2, liv_thresh=None, liv_morpho=0,
blood_thresh=None, blood_morpho=0, w=65, h=160):

    ant = pd.dcmread(file1)
    post = pd.dcmread(file2)
    ant_pix = ant.pixel_array
    post_pix = post.pixel_array[:,:,::-1]
    mean_f64 = (ant_pix*post_pix)**(1/2)
    shift = [0 for i in range(len(mean_f64))]
    #mean_u8 = f64_2_u8(mean_f64)

    avg_last10_f64 = aryth_avg(mean_f64[-10:])
    avg_last10_u8 = f64_2_u8(avg_last10_f64)
    liv_med = median(avg_last10_u8, disk(2))
    if liv_thresh is None:
        liv_thresh = threshold_otsu(liv_med)
    liv_mask = liv_med > liv_thresh
    liv_mask = closing(liv_mask, disk(3))
    if liv_morpho>0: liv_mask = dilation(liv_mask, disk(liv_morpho))
    elif liv_morpho<0: liv_mask = erosion(liv_mask, disk(-liv_morpho))
    for im in range(len(mean_f64)):
        tot = np.sum(liv_mask*mean_f64[im])
        for i in range(1,6):
            shifted_liv = ndimage.shift(liv_mask, [i,0])
            shifted_liv = closing(shifted_liv,disk(3))
            shifted_liv = np.ma.masked_where(shifted_liv==0, shifted_liv)
            if np.sum(shifted_liv*mean_f64[im])>tot:
                tot=np.sum(shifted_liv*mean_f64[im])
                #print('{} shifted to {}'.format(im, i))
                shift[im]=i

    avg_first5_f64 = aryth_avg(mean_f64[2:6])
    avg_first5_u8 = f64_2_u8(avg_first5_f64)
    blood_med = median(avg_first5_u8, disk(2))
    if blood_thresh is None:
        blood_thresh = threshold_otsu(blood_med)
    blood_mask = blood_med > blood_thresh
    blood_mask = closing(blood_mask, disk(3))
    if blood_morpho>0: blood_mask = dilation(blood_mask, disk(blood_morpho))
    elif blood_morpho<0: blood_mask = erosion(blood_mask, disk(-blood_morpho))
    ell = np.zeros((128, 128), dtype=np.bool)
    ell[ellipse(45, 66, 20, 25, rotation=np.deg2rad(0))] = 1
    blood_mask*=ell
    for i in range(len(liv_mask)):
        for j in range(len(liv_mask[i])):
            if liv_mask[i,j]: blood_mask[i,j]=0

    time_series = []
    for img in range(len(mean_f64)):
        time_series.append([0,0,0])
        shifted_mask=None
        if shift[img]:
            shifted_mask = ndimage.shift(liv_mask, [shift[img],0])
            shifted_mask = closing(shifted_mask,disk(3))
            shifted_mask = np.ma.masked_where(shifted_mask==0, shifted_mask)
        for i in range(len(mean_f64[img])):
            for j in range(len(mean_f64[img,i])):
                if shifted_mask is not None and shifted_mask[i,j]:
                    time_series[-1][0] += mean_f64[img,i,j]
                elif shifted_mask is None and liv_mask[i,j]:
                    time_series[-1][0] += mean_f64[img,i,j]

                if blood_mask[i,j]:
                    time_series[-1][1] += mean_f64[img,i,j]
        time_series[-1][2] = np.sum(mean_f64[img])

    time_steps = np.array([float(10)*(i+1) for i in range(len(time_series))])
    decay = 0.69315/(6*60*60)
    corr_factor = [1/np.exp(-decay*i) for i in (time_steps-(float(10)/2))]
    lt = [time_series[i][0]*corr_factor[i] for i in range(len(time_series))]
    ct = [time_series[i][1]*corr_factor[i] for i in range(len(time_series))]
    ft = [time_series[i][2]*corr_factor[i] for i in range(len(time_series))]
    popt, pcov = curve_fit(lambda t,c0,l: c0*np.exp(-l*t), time_steps[15:35], ct[15:35], p0 = (3000, 0.001))
    tdemi = 0.693147/popt[1]
    blood_clr, liv_clr = liv_utr(ft[15], ft[35], lt[15], lt[35], ct[15], ct[35], time_steps[15], time_steps[35], tdemi)
    return(liv_clr/bsa(h,w))
