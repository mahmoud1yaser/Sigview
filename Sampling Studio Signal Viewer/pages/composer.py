import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide")
st.markdown("""
<style>
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container.css-18e3th9.egzxvld2 {padding: 30px 30px 30px 30px;}
</style>
""", unsafe_allow_html=True)

with open('css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

header_code = (open("header.html", 'r', encoding='utf-8')).read()
st.markdown(f'{header_code}', unsafe_allow_html=True)

# Our program starts here


with st.container():
    b1, b2, b3, b4, b5 = st.columns(5)
    btn_generate = b1.button("Generate Signal")
    btn_add = b2.button("Add Signal")
    btn_snr = b3.button("Add SNR")
    btn_remove = b4.button("Remove Signal")
    btn_sample = b5.button("Sample Number")

with st.container():
    tools, browse = st.columns([3,1])
    browse.file_uploader("Upload your CSV file", type='csv', accept_multiple_files=True, label_visibility='collapsed')
    with st.container():
        if btn_add:
            add_combo_type = browse.selectbox("Signal Type", ['Sine', 'Cosine'], index=1)
            add_slider_freq = browse.slider('Frequency', value=5)
            add_slider_amp = browse.slider('Amplitude', value=1)
        elif btn_snr:
            snr_number_main = browse.number_input('SNR', min_value=0, max_value=100, value=30, step=1)
        elif btn_remove:
            remove_combo_choose = browse.selectbox("Remove Added Signal", ['alo', 'alo2'])
            remove_slider_freq = browse.slider('Frequency')
            remove_slider_amp = browse.slider('Amplitude')
        elif btn_sample:
            sample_number_main = browse.number_input('Sample')
            sample_btn_recons = browse.button('Reconstruct')
        else:
            generate_combo_type = browse.selectbox("Signal Type", ['Sine', 'Cosine'], index=1)
            generate_slider_freq = browse.slider('Frequency')
            generate_slider_amp = browse.slider('Amplitude')

with st.container():
    # garph_left, graph_right = st.columns(2)
    x= [1,2,3]
    y=  [80,180,480]
    fig, ax = plt.subplots()
    fig.set_size_inches(11, 8)
    # fig.update_layout(
    #     margin=dict(l=20, r=20, t=20, b=20),
    #     paper_bgcolor="LightSteelBlue",
    # )
    ax.plot(x,y)
    # ax[1].plot(x,y)
    tools.plotly_chart(fig, use_container_width=True)
    # st.plotly_chart(fig)