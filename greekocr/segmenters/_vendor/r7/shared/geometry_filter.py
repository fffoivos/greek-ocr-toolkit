"""Native Gaussian samples at requested columns; no image downsampling.

The row observer only reads one column per half letter height. Evaluate the
horizontal finite convolution at precisely those x positions, then the same
vertical convolution. Both axes retain OpenCV REFLECT_101 boundary extension.
Floating accumulation order differs; the row/partition audit checks decisions.
"""
import cv2
import numpy as np


def gaussian_columns(values,sigma_x,sigma_y,xs):
    nx=int(round(sigma_x*8+1))|1;ny=int(round(sigma_y*8+1))|1
    kx=cv2.getGaussianKernel(nx,sigma_x,cv2.CV_32F).ravel()
    ky=cv2.getGaussianKernel(ny,sigma_y,cv2.CV_32F)
    padded=cv2.copyMakeBorder(values,0,0,nx//2,nx//2,cv2.BORDER_REFLECT_101)
    windows=np.lib.stride_tricks.sliding_window_view(padded,nx,axis=1)[:,xs,:]
    horizontal=np.einsum('hsk,k->hs',windows,kx,optimize=False)
    return cv2.sepFilter2D(horizontal,cv2.CV_32F,np.ones(1,np.float32),ky,borderType=cv2.BORDER_REFLECT_101)
