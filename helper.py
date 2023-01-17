
from glob import glob

import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

import rasterio as rio

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
import rioxarray as rxr
import xarray as xr
import earthpy as et
import earthpy.plot as ep
import earthpy.mask as em

import plotly.graph_objects as go

from glob import glob
import rasterio
from rasterio.enums import Resampling

np.seterr(divide='ignore', invalid='ignore')
def open_clean_band(band_path, crop_layer=None):
    if crop_layer is not None:
        try:
            clip_bound = crop_layer.geometry
            cleaned_band = rxr.open_rasterio(band_path,
                                             masked=True).rio.clip(clip_bound,
                                                                   from_disk=True).squeeze()
        except Exception as err:
            print("Oops, I need a geodataframe object for this to work.")
            print(err)
    else:
        cleaned_band = rxr.open_rasterio(band_path,
                                         masked=True).squeeze()

    return cleaned_band


def process_bands(paths, crop_layer=None, stack=False):

    all_bands = []
    for i, aband in enumerate(paths):
        cleaned = open_clean_band(aband, crop_layer)
        print("Band {} stats: min = {}, max = {}".format(i+1,
                                                        cleaned.min().values,
                                                        cleaned.max().values))
                                                        
        cleaned["band"] = i+1
        all_bands.append(cleaned)
    if stack:
        print("I'm stacking your data now.")
        return xr.concat(all_bands, dim="band")
    else:
        print("Returning a list of xarray objects.")
        return all_bands



def re_scaling_img(img_path,ouput_path, res_x=2400, res_y=2400):
    with rasterio.Env():

        with rasterio.open(img_path) as dataset:
            data = dataset.read(1, out_shape=(res_x, res_y), resampling=Resampling.bilinear)
            # scale image transform
            transform = dataset.transform * dataset.transform.scale(
                (dataset.height / data.shape[0]),  # rows
                (dataset.width / data.shape[1])  # cols
            )

            profile = dataset.profile
            profile.update(transform=transform, width=data.shape[1], height=data.shape[0])

        with rasterio.open(ouput_path, 'w', **profile) as dataset:
            dataset.write(data, 1)
import tarfile

def extract_tar(filename,output_dir):
    tar = tarfile.open(filename,'r')
    tar.extractall(output_dir)
    tar.close()