import streamlit as st;

st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide",
                   initial_sidebar_state='collapsed')

show = st.container()
signal = st.container()

with show:
    upload,a,show_sig, show_samp,add,const=st.columns([2,0.5,1,1,1,1])
    upload.file_uploader("Upload your CSV file", type='csv', label_visibility='collapsed')
    show_sig.checkbox('show main signal')
    show_samp.checkbox('show samples')
    add.checkbox('show added')
    const.checkbox('show constructed')

with signal:
    control1,control2, graph = st.columns([1.1,1.1,5])
    with control1:
        type = st.selectbox("Signal Type", ['Cosine', 'Sine'], index=0)
        freq = st.slider('Frequency', min_value=1., max_value=200., step=0.5)
        amp = st.slider('Amplitude', min_value=1., max_value=200., step=0.5)
        add = st.button('add signal')
        # st.markdown("<br>", unsafe_allow_html=True)
        # down = st.button('download')




    with control2 :
        # resolition = st.slider('Resolution', value=20, min_value=1, max_value=2000, step=10)
        snr=st.slider('SNR(dB)', min_value=0, max_value=120, value=120 , step=1)
        sa = st.checkbox('ma')
        samp_no = st.slider('Ssmpling number', min_value=2.0 , max_value=150., value=2.0, step=.1)

        remove = st.selectbox("Signals", ['sig1', 'sig2'], index=0)


        remove_btn = st.button('Remove')

        # snr=st.number_input('SNR(dB)', min_value=0, max_value=120, value=120, step=1)
        # samp_no=st.number_input('Sampling Number',value=2., min_value=2.,max_value=150., step=.1)


    # with graph:
        # gr = st.button('graph');


