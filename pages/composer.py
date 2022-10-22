import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import plotly.express as px

st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide",
                   initial_sidebar_state='collapsed')
st.markdown("""
<style>
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container.css-18e3th9.egzxvld2 {padding: 30px 30px 30px 30px;}
.css-1vencpc.e1fqkh3o10{visibility: hidden;}
.css-1rs6os.edgvbvh3{visibility: hidden;}
</style>
""", unsafe_allow_html=True)

with open('css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

header_code = (open("templates/header.html", 'r', encoding='utf-8')).read()
st.markdown(f'{header_code}', unsafe_allow_html=True)

plt.style.use("ggplot")


# Our program starts here


def cb_generate_active():
    st.session_state.cb_generate = True
    st.session_state.cb_add = False
    st.session_state.cb_sample = False
    st.session_state.cb_remove = False
    st.session_state.cb_snr = False


def cb_add_active():
    st.session_state.cb_add = True
    st.session_state.cb_generate = False
    st.session_state.cb_sample = False
    st.session_state.cb_remove = False
    st.session_state.cb_snr = False


def cb_snr_active():
    st.session_state.cb_snr = True
    st.session_state.cb_generate = False
    st.session_state.cb_add = False
    st.session_state.cb_sample = False
    st.session_state.cb_remove = False


def cb_remove_active():
    st.session_state.cb_remove = True
    st.session_state.cb_generate = False
    st.session_state.cb_add = False
    st.session_state.cb_sample = False
    st.session_state.cb_snr = False


def cb_sample_active():
    st.session_state.cb_sample = True
    st.session_state.cb_generate = False
    st.session_state.cb_add = False
    st.session_state.cb_remove = False
    st.session_state.cb_snr = False


with st.container():
    b1, b2, b3, b4, b5 = st.columns(5)
    cb_generate = b1.checkbox("Generate Signal", key='cb_generate', on_change=cb_generate_active)
    cb_add = b2.checkbox("Add Signal", key='cb_add', on_change=cb_add_active)
    cb_snr = b3.checkbox("Add SNR", key='cb_snr', on_change=cb_snr_active)
    cb_remove = b4.checkbox("Remove Signal", key='cb_remove', on_change=cb_remove_active)
    cb_sample = b5.checkbox("Sample Signal", key='cb_sample', on_change=cb_sample_active)

with st.container():
    left_up_col, right_up_col = st.columns([3, 1])
    uploaded_csv = right_up_col.file_uploader("Upload your CSV file", type='csv',
                                              label_visibility='collapsed')
    right_up_col.markdown(' <center> <h3> Maximum Time </h3> </center>', unsafe_allow_html=True)
    signalRange = right_up_col.slider('Resolution', value=15000, min_value=0, max_value=40000, step=1000)
    signalRange += 1
    uploaded_df = pd.DataFrame()
    if uploaded_csv is not None:
        uploaded_df = pd.read_csv(uploaded_csv)
    with st.container():
        if st.session_state["cb_add"]:
            right_up_col.markdown(' <center> <h3> Add Signal </h3> </center>', unsafe_allow_html=True)
            add_combo_type = right_up_col.selectbox("Signal Type", ['Sine', 'Cosine'], index=1,
                                                    on_change=cb_add_active)
            add_slider_freq = right_up_col.slider('Frequency', value=5,
                                                  on_change=cb_add_active)
            add_slider_amp = right_up_col.slider('Amplitude', value=1,
                                                 on_change=cb_add_active)
        elif st.session_state["cb_snr"]:
            right_up_col.markdown(' <center> <h3> SNR </h3> </center>', unsafe_allow_html=True)
            snr_number_main = right_up_col.number_input('SNR(dB)', min_value=0, max_value=120, value=30, step=1,
                                                        on_change=cb_snr_active)
        elif st.session_state["cb_remove"]:
            right_up_col.markdown(' <center> <h3> Remove Signal </h3> </center>', unsafe_allow_html=True)
            remove_combo_choose = right_up_col.selectbox("Remove Added Signal", ['alo', 'alo2'],
                                                         on_change=cb_remove_active)
            remove_slider_freq = right_up_col.slider('Frequency',
                                                     on_change=cb_remove_active)
            remove_slider_amp = right_up_col.slider('Amplitude',
                                                    on_change=cb_remove_active)
        elif st.session_state["cb_sample"]:
            right_up_col.markdown(' <center> <h3> Sample Signal </h3> </center>', unsafe_allow_html=True)
            sample_number_main = right_up_col.number_input('Sampling Number',
                                                           on_change=cb_sample_active)
            sample_btn_recons = right_up_col.button('Reconstruct',
                                                    on_click=cb_sample_active)
        elif st.session_state["cb_generate"]:
            right_up_col.markdown(' <center> <h3> Generate Signal </h3> </center>', unsafe_allow_html=True)
            generate_combo_type = right_up_col.selectbox("Signal Type", ['Sine', 'Cosine'], index=1,
                                                         on_change=cb_generate_active)
            generate_slider_freq = right_up_col.slider('Frequency',
                                                       on_change=cb_generate_active)
            generate_slider_amp = right_up_col.slider('Amplitude',
                                                      on_change=cb_generate_active)
        # x = [1, 2, 3]
        # y = [80, 180, 480]

        ti = np.arange(1, 100, .001)
        df_default = pd.DataFrame()
        df_default['Time(s)'] = ti
        df_default['Amplitude(mV)'] = pd.Series(np.cos(ti))

        # df = pd.read_csv('data/ecg_1000hz_cleaned.csv')
        if len(uploaded_df) >= 1:
            df = uploaded_df.iloc[:int(signalRange)]
        else:
            df = df_default[:int(signalRange)]

        t = np.array(df.iloc[:, 0])
        a = np.array(df.iloc[:, 1])

        fig_main = px.line(x=t, y=a, height=740, labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        fig_main.update_layout(title_text='Active Viewer', title_x=0.5, font=dict(
            family="Sans serif",
            size=15,
            color="white"))
        fig_main.update_traces(line_color='#2596be')
        left_up_col.plotly_chart(fig_main, use_container_width=True)

    with st.container():
        fig_main = px.line(x=t, y=a, height=740, labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        fig_main.update_layout(title_text='Accumulative Viewer', title_x=0.5, font=dict(
            family="Sans serif",
            size=15,
            color="white"))
        fig_main.update_traces(line_color='#2596be')
        st.plotly_chart(fig_main, use_container_width=True)