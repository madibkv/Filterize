import numpy as np
import cv2
from PIL import Image, ImageEnhance
import streamlit as st
import randomname
from io import BytesIO, BufferedReader
import s3fs
import os



import sys
sys.path.append('..')
from EditImage import *

fs = s3fs.S3FileSystem(anon=False)
# @st.experimental_memo(ttl=600)
def write_to_file(filename, filter):
    with fs.open(filename, 'a') as f:
        parameters = ",".join((filter.values()))
        new_filter = name+','+parameters+"\n"
        print(name)
        print(new_filter)
        f.write(new_filter)




st.write("# Create Your Own Filter!")
uploaded_f = st.file_uploader("Choose your image", type=['jpg','jpeg','png'])



if uploaded_f is not None:
    bytes_data = uploaded_f.read()

    #filtered = edit_image_custom(uploaded_file, filter_chosen)
    st.header("Create a name for your filter")
    title = st.text_input(label="Input filter name",placeholder='Your Cool Filter Name')
    col1, col2, col3 = st.columns(3)

    with col1:
        sat = start_time = st.slider("Saturation", min_value=-100, value=0)
        exp = st.slider("Exposure", min_value=-100, value=0)
        br = st.slider("Brightness", min_value=-100, value=0)


    with col2:
        sharp = st.slider("Sharpness", min_value=-100, value=0)
        wrm = st.slider("Warmth", min_value=-100, value=0)
        shd = st.slider("Shadows", min_value=0, value=0)


    with col3:
        cont = st.slider("Contrast", min_value=-100, value=0)
        tn = st.slider("Tint", min_value=-100, value=0)
        hgl = st.slider("Highlights", min_value=0, value=0)

    my_filter = {
        'saturation':str(sat),
        'exposure':str(exp),
        'brightness':str(br),
        'shadows':str(shd),
        'highlights':str(hgl),
        'contrast':str(cont),
        'sharpness':str(sharp),
        'warmth':str(wrm),
        'tint':str(tn),
    }
    # print(my_filter['saturation'])
    filtered = edit_image_custom(uploaded_f, my_filter)
    st.image(filtered, channels='BGR')



    im_rgb = filtered[:, :, [0, 1, 2]] #numpy.ndarray
    ret, img_enco = cv2.imencode(".jpeg", im_rgb)  #numpy.ndarray
    srt_enco = img_enco.tostring()  #bytes
    img_BytesIO = BytesIO(srt_enco) #_io.BytesIO
    img_BufferedReader = BufferedReader(img_BytesIO) #_io.BufferedReader
    #img = Image.open(result)


    btn1 = st.download_button(
    label="Download image",
    data=img_BufferedReader,
    file_name=uploaded_f.name.split(".")[0]+"_"+title+".jpeg",
    mime="image/jpeg"
      )

    if st.button("Save Filter"):
        if title != "":
            name = title
        else:
            name = randomname.get_name()
        write_to_file("filterize-bucket/db_test.txt", my_filter)
        st.success('Your filter is saved!', icon="✅")
