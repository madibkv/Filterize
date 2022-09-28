import numpy as np
import cv2
from PIL import Image, ImageEnhance
from CustomFilters import *
import streamlit as st
from io import BytesIO, BufferedReader
import s3fs
import os



def change_saturation(img, s=-17):
    sat = (100 + s)/100

    img = ImageEnhance.Color(img)
    img = img.enhance(sat)
    return img

def change_exposure(img, gamma=-24):
    gamma = (100 + gamma)/100
    #img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gamma_table=[np.power(x/255,gamma)*255 for x in range(256)]
    gamma_table=np.round(np.array(gamma_table)).astype(np.uint8)
    img = cv2.LUT(img,gamma_table)
    return img

def change_brightness(img, val=5):
    val = val * 2.55

    # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, val)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def change_contrast(img, c=-23):
    cont = (100 + (c/2.5))/100

    img = ImageEnhance.Contrast(img)
    img = img.enhance(cont)
    return img

def change_sharpness(img, sh=16):
    sharp = (300 + sh)/100

    img = ImageEnhance.Sharpness(img)
    img = img.enhance(sharp)
    return img


def change_warmth(img, w=20):
    # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    w = w / 2.55

    b,g,r = cv2.split(img)
    r = cv2.add(r, w)
    b = cv2.add(b,-w)
    r[r > 255] = 255
    r[r < 0] = 0
    b[b > 255] = 255
    b[b < 0] = 0
    img = cv2.merge((b, g, r))
    return img

def change_tint(img, t=29):
    # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    t = t / 2.55

    b,g,r = cv2.split(img)
    g = cv2.add(g, -t)
    g[g > 255] = 255
    g[g < 0] = 0
    img = cv2.merge((b, g, r))
    return img


def edit_image_custom(img, name):
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #img = Image.fromarray(img)
    img = Image.open(img)

    img = change_saturation(img,int(name['saturation']))
    img = change_sharpness(img,int(name['sharpness']))
    img = change_contrast(img,int(name['contrast']))

    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    img = change_brightness(img,int(name['brightness']))
    img = change_exposure(img,int(name['exposure']))
    img = change_warmth(img,int(name['warmth']))
    img = change_tint(img,int(name['tint']))

    return img





# img = cv2.imread("mcdonalds.jpeg")
# cv2.imwrite("macdonalds_vintage.jpeg", edit_image_custom(img,VintagePollaroid))
fs = s3fs.S3FileSystem(anon=False)
# @st.experimental_memo(ttl=600)
def read_file(filename):
    with fs.open(filename) as f:
        return f.read().decode('latin1')

content = read_file("filterize-bucket/db_test.txt")

options = []
# Print results.
for line in content.strip().split("\n"):
    # print(line)
    filter_name = line.split(",")[0]
    options.append(filter_name)
    #st.write(filter_name)


st.write(""" # Filterize! """
)

uploaded_file = st.file_uploader("Choose an image", type=['jpg','jpeg','png'])

option = st.selectbox(
    'Choose Filter',
    (options))


if uploaded_file is not None:

    # st.write("filename:", uploaded_file.name.split(".")[0])
    # st.write(bytes_data)
    # st.image(uploaded_file)
    for line in content.strip().split("\n"):
        print(line)
        filter_name, sat, exp, br, ct, sh, wm, tn = line.split(",")
        if filter_name == option:
            my_filter = {
                'saturation':sat,
                'exposure':exp,
                'brightness':br,
                'contrast':ct,
                'sharpness':sh,
                'warmth':wm,
                'tint':tn,
            }


    filtered = edit_image_custom(uploaded_file, my_filter)
    st.image(filtered, channels='BGR')

    im_rgb = filtered[:, :, [0, 1, 2]] #numpy.ndarray
    ret, img_enco = cv2.imencode(".jpeg", im_rgb)  #numpy.ndarray
    srt_enco = img_enco.tostring()  #bytes
    img_BytesIO = BytesIO(srt_enco) #_io.BytesIO
    img_BufferedReader = BufferedReader(img_BytesIO) #_io.BufferedReader
    #img = Image.open(result)




    btn = st.download_button(
    label="Download image",
    data=img_BufferedReader,
    file_name=uploaded_file.name.split(".")[0]+"_"+option+".jpeg",
    mime="image/jpeg"
      )
