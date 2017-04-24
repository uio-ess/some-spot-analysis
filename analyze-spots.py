#!/usr/bin/env python3

# written by grey@christoforo.net

import argparse
import numpy as np
import mpmath
import matplotlib.pyplot as plt
from sdds import SDDS as ssds
from skimage.feature import blob_dog, blob_log, blob_doh
from math import sqrt
from scipy import optimize

parser = argparse.ArgumentParser(description='Spot analysis on image data taken from SDDS files.')

parser.add_argument('input', type=argparse.FileType('rb'), nargs='+', help="Single file or list of SDDS files to process")

args = parser.parse_args()

def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    p, success = optimize.leastsq(errorfunction, params)
    return p

for f in args.input:
    ds = ssds(f)
    xRes = ds.pageData[0]['parameters']['nbPtsInSet1']['value']
    yRes = ds.pageData[0]['parameters']['nbPtsInSet2']['value']
    imageData = ds.pageData[0]['arrays']['imageSet']['value'][0]
    imageData = imageData.reshape([yRes,xRes])
    pgmMax = imageData.max()
    pgmHeader = 'P2 {:} {:} {:}'.format(xRes,yRes,pgmMax)
    #f = open('/tmp/map.pgm', 'wb')
    #f.write(bytes(pgmHeader,'utf-8'))
    #imageData.tofile(f)
    np.savetxt('/tmp/map.pgm',imageData,header=pgmHeader,fmt='%i',comments='')    
    #f.close()
    
    data = imageData
    plt.matshow(data, cmap=plt.cm.gist_earth_r)
    
    params = fitgaussian(data)
    fit = gaussian(*params)
    
    plt.contour(fit(*np.indices(data.shape)), cmap=plt.cm.copper)
    ax = plt.gca()
    (height, x, y, width_x, width_y) = params
    
    plt.text(0.95, 0.05, """
    x : %.1f
    y : %.1f
    width_x : %.1f
    width_y : %.1f""" %(x, y, width_x, width_y),
                      fontsize=16, horizontalalignment='right',
            verticalalignment='bottom', transform=ax.transAxes)    
    
    
    
    #imageData = imageData/imageData.max()

    #image = imageData
    
    #print(f.name)
    ##fig, ax = plt.subplots()
    ##ax.imshow(imageData)
    ##ax.axis('off')  # clear x- and y-axes
    ##plt.show()
    #image_gray = imageData
    ##print('break')
    #blobs_log = blob_log(image_gray, max_sigma=50, num_sigma=10, threshold=.1)
    
    ## Compute radii in the 3rd column.
    #blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)
    
    #blobs_dog = blob_dog(image_gray, max_sigma=30, threshold=.1)
    #blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
    
    #blobs_doh = blob_doh(image_gray, max_sigma=30, threshold=.01)
    
    #blobs_list = [blobs_log, blobs_dog, blobs_doh]
    #colors = ['yellow', 'lime', 'red']
    #titles = ['Laplacian of Gaussian', 'Difference of Gaussian',
              #'Determinant of Hessian']
    #sequence = zip(blobs_list, colors, titles)
    
    #fig, axes = plt.subplots(1, 3, figsize=(9, 3), sharex=True, sharey=True,
                             #subplot_kw={'adjustable': 'box-forced'})
    #ax = axes.ravel()
    
    #for idx, (blobs, color, title) in enumerate(sequence):
        #ax[idx].set_title(title)
        #ax[idx].imshow(image, interpolation='nearest')
        #for blob in blobs:
            #y, x, r = blob
            #c = plt.Circle((x, y), r, color=color, linewidth=2, fill=False)
            #ax[idx].add_patch(c)
        #ax[idx].set_axis_off()
    
    #plt.tight_layout()
    plt.show()    