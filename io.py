# IO utils

from os import listdir, path
import numpy as np
import yaml
import re
from skimage import io
import pandas as pd
from ast import literal_eval

def list_images(base_path, filename):
    '''Returns list of all images in base_path that start with filename.

        Inputs:
            - base_path (str), the directory
            - filename (str), start of filename

        Returns:
            - list of all image files found in directory (list of strings)
    '''

    all_files = listdir(base_path)
    selected = [a for a in all_files if (filename in a) and ('.tif' in a)]

    exp = re.compile(filename+'_(\d+)_(\d+).tif')
    idx = list_index(selected,exp)

    return selected, idx

def list_index(image_list,exp):
    ''' Returns array of x, y indexes found in image_list for supplied regex.

        Inputs:
            - image_list (list of str), from list_images
            - exp (re.compile object), regex to match

        Returns:
            - (n x 2) array
    '''
    idx = []
    for item in image_list:
        t = exp.match(item)
        if t:
            idx.append(np.asarray([int(a) for a in t.groups()]))

    idx = np.vstack(idx)

    return idx

def read(x,y,t,cfg='kchip_config.yml',number=4, ret=(0,1,2,3)):
    ''' Read in image corresponding to position (x,y) and t (string) '''
    with open(cfg) as ymlfile:
        config = yaml.load(ymlfile)

    fname = path.join(config['image']['base_path'],config['image']['names'][t]+'_'+str(x)+'_'+str(y)+'.tif')
    img = io.imread(fname)

    # a) Transpose if necessary to (x,y,z)
    if img.shape[2] > img.shape[0]:
        img_ = img.transpose((1,2,0))
    else:
        img_ = img

    # b) return slices if necessary
    if img_.shape[2] > number:
        return img_[:,:,ret]
    else:
        return img_


def read_excel_barcodes(config):
    ''' Read in excel barcodes and returns dictionary label -> barcode '''

    barcodes = pd.read_excel(config['barcodes']['path'],sheetname='Barcodes')
    labels = pd.read_excel(config['barcodes']['path'],sheetname='Labels')

    d = dict(zip(labels.values.reshape(-1),barcodes.values.reshape(-1)))

    for item in d.keys():
        if item == item:
            d[item] = literal_eval(d[item])
        else:
            del d[item]

    return d