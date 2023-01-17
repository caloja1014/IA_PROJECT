import numpy as np
import matplotlib.pyplot as plt
import rasterio
from pathlib import Path
from glob import glob
import os
from PIL import Image
import re
from skimage import io, img_as_ubyte

def bit_str(value):
    d={
        "Fill":{
            "bit":(0,),
            "values":{
                (0,):"0 for image data",
                (1,):"1 for fill data"
            }
        },
        "Dilated Cloud":{
            "bit":(1,),
            "values":{
                (0,):"0 for cloud is not dilated or no cloud",
                (1,):"1 for cloud dilation"
            }
        },
        "Cirrus":{
            "bit":(2,),
            "values":{
                (0,):"0 for Cirrus Confidence: no confidence level set or Low Confidence",
                (1,):"1 for high confidence cirrus"
            }
        },
        "Cloud":{
            "bit":(3,),
            "values":{
                (0,):"0 for cloud confidence is not high",
                (1,):"1 for high confidence cloud"
            }
        },
        "Cloud Shadow":{
            "bit":(4,),
            "values":{
                (0,):"0 for Cloud Shadow Confidence is not high",
                (1,):"1 for high confidence cloud shadow"
            }
        },
        "Snow":{
            "bit":(5,),
            "values":{
                (0,):"0 for Snow/Ice Confidence is not high",
                (1,):"1 for high confidence snow/ice"
            }
        },
        "Clear":{
            "bit":(6,),
            "values":{
                (0,):"0 if Cloud or Dilated Cloud bits are set",
                (1,):"1 if Cloud and Dilated Cloud bits are not set"
            }
        },
        "Water":{
            "bit":(7,),
            "values":{
                (0,):"0 for land or cloud",
                (1,):"1 for water"
            }
        },
        "Cloud Confidence":{
            "bit":(8,9),
            "values":{
                (0,0):"00 for no confidence level set",
                (0,1):"01 Low confidence",
                (1,0):"10 Medium confidence",
                (1,1):"11 High confidence"
            }
        },
        "Cloud Shadow Confidence":{
            "bit":(10,11),
            "values":{
                (0,0):"00 for no confidence level set",
                (0,1):"01 Low confidence",
                (1,0):"10 Reserved",
                (1,1):"11 High confidence"
            }
        },
        "Snow/Ice Confidence":{
            "bit":(12,13),
            "values":{
                (0,0):"00 for no confidence level set",
                (0,1):"01 Low confidence",
                (1,0):"10 Reserved",
                (1,1):"11 High confidence"
            }
        },
        "Cirrus Confidence":{
            "bit":(14,15),
            "values":{
                (0,0):"00 for no confidence level set",
                (0,1):"01 Low confidence",
                (1,0):"10 Reserved",
                (1,1):"11 High confidence"
            }
        }
    }
    list_order=[
        "Fill",
        "Dilated Cloud",
        "Cirrus",
        "Cloud",
        "Cloud Shadow",
        "Snow",
        "Clear",
        "Water",
        "Cloud Confidence",
        "Cloud Shadow Confidence",
        "Snow/Ice Confidence",
        "Cirrus Confidence"
    ]
    i=0
    tamano=len(value)-1
    for index,flag in enumerate(list_order):
        d_flag=d[flag]
        bits=d_flag["bit"]
        values=d_flag["values"]
        if len(bits)==1:
            bits=bits[0]
            value_bit= int(value[tamano-bits])
            print(f"{flag}: {values[(value_bit,)]}")
        else:
            bit_1=bits[0]
            bit_2=bits[1]
            value_bit_1= int(value[tamano-bit_1])
            value_bit_2= int(value[tamano-bit_2])
            value_bit=(value_bit_1,value_bit_2)
            print(f"{flag}: {values[value_bit]}")
        
mask_values = {
               'Dilated cloud over land': 21826,
               'Dilated cloud over water': 21890,
               'Mid conf Cloud': 22280,
               'High conf cloud shadow': 23888,
               'Water with cloud shadow': 23952,
               'Mid conf cloud with shadow': 24088,
               'Mid conf cloud with shadow over water': 24216,
               'High conf cloud with shadow': 24344,
               'High conf cloud with shadow over water': 24472,
               'High conf Cirrus': 54596,
               'Cirrus, high cloud': 55052,
               'Cirrus, mid conf cloud, shadow': 56856,
               'Cirrus, mid conf cloud, shadow, over water': 56984,
               'Cirrus, high conf cloud, shadow': 57240,
              }

# def load_landsat_image(img_folder, bands):
#     image = {}
#     path = Path(img_folder)
#     for band in bands:
#         file = next(path.glob(f'*{band}.TIF'))
#         print(f'Opening file {file}')
#         ds = rasterio.open(file)
#         image.update({band: ds.read(1)})

#     return image
regex_bands= r'B[0-9]|QA_PIXEL'
def load_landsat_image(paths):
    image = {}
    for file in paths:
        # print(file)
        band=re.search(regex_bands,file).group()
        ds = rasterio.open(file)
        image.update({band: ds.read(1)})

    return image

bands=['B2', 'B3', 'B4','B5', 'QA_PIXEL']
bands_by_name={
    'B1': 'Coastal aerosol',
    'B2': 'blue',
    'B3': 'green',
    'B4': 'red',
    'B5': 'nir',
    'QA_PIXEL': 'gt'
}

# lansat_paths={
#     'LC08_L1TP_224078_20190701_20190701_01_RT':{
#         'B1': [
#             '/home/andres/Documentos/Proyectos/Proyecto_1/landsat/    
#         ],
#     }
# }
def crop(input_path, height, width, k, area):
    im = Image.open(input_path)
    imgwidth, imgheight = im.size
    d_crop = {}
    for i in range(0,imgheight,height):
        for j in range(0,imgwidth,width):
            box = (j, i, j+width, i+height)
            a = im.crop(box)
            try:
                o = a.crop(area)
                d_crop.setdefault(k, o)
            except Exception as err:
                d_crop.setdefault(k, a)
                pass

            k +=1
    return d_crop
def crop_landsat_image(path_to_save,landsat_paths_general):
    d_paths={}
    # regex_bands= r'B[0-9]|QA_PIXEL'
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    for id_path_landsat in landsat_paths_general:
        

        id_img_landsat=id_path_landsat.split('/')[-1]
        d_landsat_id=d_paths.setdefault(id_img_landsat,{})
        S_sentinel_bands=glob(f'{id_path_landsat}/*.TIF')

        # d_local_band={}

        for path_band in S_sentinel_bands:
            id_img_band=path_band.split('/')[-1]

            # band_match=re.match(regex_bands,path_band).group()
            
            d_crop=crop(path_band,256,256,0,(0,0,256,256))
            # d_local_band.setdefault(band_match,d_crop)
        
        

            for id_img,landsat_object_by_id in d_crop.items():
                    list_path_band=d_landsat_id.setdefault(id_img,[])

                    path_to_save_crop=f'{path_to_save}/{id_img_landsat}/{id_img}'
                    if not os.path.exists(path_to_save_crop):
                        os.makedirs(path_to_save_crop)
                    final_path_to_save=f'{path_to_save_crop}/{id_img_band}'
                    list_path_band.append(final_path_to_save)
                    landsat_object_by_id.save(final_path_to_save)
    return d_paths
    
import shutil
import subprocess
import unpackqa

def generate_landsat_imgs(path_to_save,landsat_paths_d):
    k=0
    a=[]
    b=[]
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    for id_img,landsat_object_by_id in landsat_paths_d.items():
        for cut_id,landsat_path in landsat_object_by_id.items():

            lansat_path_filter_1=[]
            landsat_path_filter_2=[]
            for path in landsat_path:
                if 'QA_PIXEL' in path:
                    lansat_path_filter_1.append(path)
                else:
                    landsat_path_filter_2.append(path)
            img = load_landsat_image(lansat_path_filter_1)
            
            final_mask = np.zeros_like(img['QA_PIXEL'])

            # for key, value in mask_values.items():
            #     mask = (img['QA_PIXEL'] == value)
            #     final_mask = final_mask | mask
            final_mask = unpackqa.unpack_to_array(img['QA_PIXEL'], 
                                           product='LANDSAT_8_C2_L2_QAPixel', 
                                           flags=['Cloud'])


            dir_to_save_img=f'{path_to_save}/train_gt'

            if not os.path.exists(dir_to_save_img):
                os.makedirs(dir_to_save_img)
            
            # save final_mask on TIF file



            # shutil.copy('',f'{dir_to_save_img}/{id_img}_{cut_id}_gt.TIF')
            # plt.imsave(f'{dir_to_save_img}/{id_img}_{cut_id}_gt.jpeg', final_mask, cmap='gray')

            #SAVE CLOUD MASK WITH RASTERIO
            # with rasterio.open(f'{dir_to_save_img}/{id_img}_{cut_id}_gt.TIF', 'w', driver='GTiff', height=final_mask.shape[0], width=final_mask.shape[1], count=1, dtype=final_mask.dtype, crs='+proj=latlong') as dst:
            #     dst.write(final_mask, 1)


            io.imsave(f'{dir_to_save_img}/{id_img}_{cut_id}_gt.TIF',final_mask)

            # print(f'{id_img}_{cut_id}_gt.TIF',landsat_path_filter_2,bands[:-1])
            for ls in landsat_path_filter_2:
                file_name=ls.split('/')[-1]
                
                band=re.search(regex_bands,file_name).group()
                dir_to_save_img=f'{path_to_save}/train_{bands_by_name[band]}'
                if not os.path.exists(dir_to_save_img):
                    os.makedirs(dir_to_save_img)
                # os.system(f'cp {ls} {dir_to_save_img}/{id_img}_{cut_id}_{bands_by_name[band]}.TIF')
                if 'B2' in file_name:
                    k+=1
                    a.append(file_name)
                    b.append(f'{dir_to_save_img}/{id_img}_{cut_id}_{bands_by_name[band]}.TIF')
                subprocess.call(f'cp {ls} {dir_to_save_img}/{id_img}_{cut_id}_{bands_by_name[band]}.TIF', shell=True)
                # shutil.copy(ls,f'{dir_to_save_img}/{id_img}_{cut_id}_{bands_by_name[band]}.TIF')
            # for band in bands[:-1]:
            #     file_source=[path for path in landsat_path_filter_2 if band in path][0]
            #     dir_to_save_img=f'{path_to_save}/train_{bands_by_name[band]}'
            #     if not os.path.exists(dir_to_save_img):
            #         os.makedirs(dir_to_save_img)

            #     shutil.copy(file_source,dir_to_save_img)
                # plt.imsave(f'{dir_to_save_img}/{id_img}_{cut_id}_{bands_by_name[band]}.jpeg', img[band], cmap='gray')
    print(k)
    print (len(a), len(b))
