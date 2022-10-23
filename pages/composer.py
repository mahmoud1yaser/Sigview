from pickle import NONE
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide",
                   initial_sidebar_state='collapsed')
st.markdown("""
<style>
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container.css-18e3th9.egzxvld2 {padding: 30px 30px 30px 30px;}
# .css-1vencpc.e1fqkh3o10{visibility: hidden;}
# .css-1rs6os.edgvbvh3{visibility: hidden;}
</style>
""", unsafe_allow_html=True)

with open('css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

header_code = (open("templates/header.html", 'r', encoding='utf-8')).read()
st.markdown(f'{header_code}', unsafe_allow_html=True)

plt.style.use("ggplot")

# Our program starts here
sample_number_main = 0
sample_btn_recons = False
add_btn_submit = False
removeFromListButtons = [0]  # the variable that saves the list of the buttons of the added functions
# checkbox in the sidebar for showing the added functions list
show_history = st.sidebar.checkbox("Show History")
if 'addedSignals' not in st.session_state:  # Storing the added Signals in the memory
    st.session_state['addedSignals'] = []  # we will add in 3 types : type of function then freq then amplituide

if 'viewAddedSignalButton' not in st.session_state:
    st.session_state['viewAddedSignalButton']=True

def cb_generate_active():
    st.session_state.cb_generate = True
    st.session_state.cb_add = False
    st.session_state.cb_sample = False
    st.session_state.cb_snr = False


def cb_add_active():
    st.session_state.cb_add = True
    st.session_state.cb_generate = False
    st.session_state.cb_sample = False
    st.session_state.cb_snr = False


def cb_snr_active():
    st.session_state.cb_snr = True
    st.session_state.cb_generate = False
    st.session_state.cb_add = False
    st.session_state.cb_sample = False


def cb_sample_active():
    st.session_state.cb_sample = True
    st.session_state.cb_generate = False
    st.session_state.cb_add = False
    st.session_state.cb_snr = False


# Signal to Noise Ratio Code
def get_snr(amplitude, snr):
    if st.session_state["cb_snr"]:
        signalAvgPowerDB = 10 * np.log10(
            np.mean(amplitude ** 2))  # Getting the average of the power of the signal
        noiseDB = signalAvgPowerDB - snr
        noiseWatt = 10 ** (noiseDB / 10)
        meanNoise = 0
        noise = np.random.normal(meanNoise, np.sqrt(noiseWatt), len(amplitude))
        noiseSignal = noise + amplitude
        return noiseSignal
    else:
        return amplitude


# Sampling Code
def sample(time, amplitude, fs):
    if len(time) == len(amplitude):
        points_per_indices = int((len(time) / time[-1]) / fs)
        if points_per_indices == 0:
            points_per_indices = 1
        amplitude = amplitude[::points_per_indices]
        time = time[::points_per_indices]
        return time, amplitude


# # Reconstruction Code
def signal_recons(time, sampled_time, sampled_amplitude):
    # shape = (sampled_time, time), sampled_time copies of time data span axis 1
    u = np.resize(time, (len(sampled_time), len(time)))
    # Must take transpose of u for proper broadcasting with sampled_time.
    # Apply Whittaker-Shannon interpolation formula
    v = (sampled_time - u.T) / (sampled_time[1] - sampled_time[0])
    # shape = (n_time, n_sampled_time), m(v) data spans axis 1
    m = sampled_amplitude * np.sinc(v)
    # Sum over m(v) (axis 1)
    analog_sampled_amplitude = np.sum(m, axis=1)
    return analog_sampled_amplitude


with st.container():
    b1, b2, b3, b4 = st.columns(4)
    cb_generate = b1.checkbox("Generate Signal", key='cb_generate', on_change=cb_generate_active)
    cb_add = b2.checkbox("Add Signal", key='cb_add', on_change=cb_add_active)
    cb_snr = b3.checkbox("Add SNR", key='cb_snr', on_change=cb_snr_active)
    cb_sample = b4.checkbox("Sample Signal", key='cb_sample', on_change=cb_sample_active)

with st.container():
    left_up_col, right_up_col = st.columns([3, 1])
    uploaded_csv = right_up_col.file_uploader("Upload your CSV file", type='csv',
                                              label_visibility='collapsed')
    right_up_col.markdown(' <center> <h3> Maximum Time </h3> </center>', unsafe_allow_html=True)
    signalRange = right_up_col.slider('Resolution', value=20, min_value=1, max_value=2000, step=10)

    if 'time' not in st.session_state:
        st.session_state['time'] = np.zeros(signalRange)
    if 'amplitude' not in st.session_state:
        st.session_state['amplitude'] = np.zeros(signalRange)

    def write_added_functions_list():
        if show_history:  # checking the checkbox for showing the list of the added functions in the sidebar
            index = 0
            for functions in st.session_state['addedSignals']:
                removeFromListButtons.append(0)
                functionsListAmp = str(functions[2])
                functionsListFreq = str(functions[1])
                if functions[0] == 'Cosine':
                    removeFromListButtons[index] = st.sidebar.button(label='🗑️ ' + str(
                        index + 1) + ') ' + functionsListAmp + 'Cos(' + functionsListFreq + 't)')
                else:
                    removeFromListButtons[index] = st.sidebar.button(label='🗑️ ' + str(
                        index + 1) + ') ' + functionsListAmp + 'Sin(' + functionsListFreq + 't)')
                if removeFromListButtons[index]:
                    st.session_state['addedSignals'].pop(index)
                    removeFromListButtons.pop(index)
                    st.experimental_rerun()

                index += 1
            if len(removeFromListButtons) != 0 and index != 0:
                removeFromListButtons.pop(index)


    uploaded_df = pd.DataFrame()
    if uploaded_csv is not None:
        if(st.session_state['viewAddedSignalButton']):
           st.session_state['viewAddedSignalButton']=False
           st.experimental_rerun()
        uploaded_df = pd.read_csv(uploaded_csv)
        if len(uploaded_df) >= 1:
            df = uploaded_df.iloc[:int(signalRange)]
    elif(not st.session_state['viewAddedSignalButton']):
            st.session_state['viewAddedSignalButton']=True
            st.experimental_rerun()
    with st.container():
        if st.session_state["cb_add"]:
            right_up_col.markdown(' <center> <h3> Add Signal </h3> </center>', unsafe_allow_html=True)
            add_combo_type = right_up_col.selectbox("Signal Type", ['Cosine', 'Sine'], index=0,
                                                    on_change=cb_add_active)
            add_slider_freq = right_up_col.slider('Frequency', value=1.,
                                                  on_change=cb_add_active, max_value=200., step=0.5)
            add_slider_amp = right_up_col.slider('Amplitude', value=1.,
                                                 on_change=cb_add_active, max_value=200., step=0.5)
            if(st.session_state['viewAddedSignalButton']):
                add_btn_submit = right_up_col.button('Add Signal', on_click=cb_add_active)
            else :
                st.session_state['addedSignals']=[]    

            st.session_state['func_type'] = add_combo_type
            st.session_state['time'] = np.linspace(0, signalRange, 1000)
            st.session_state.addFunctionButton = False

            # this function here for adding sine or cosine wave to the signal and saving it to the memory
            def add_function_mag():
                if add_combo_type == "Cosine":
                    phase_degree = np.pi / 2
                else:
                    phase_degree = 0
                return add_slider_amp * np.sin(2 * np.pi * add_slider_freq * st.session_state['time'] + phase_degree)


            def add_new_signal():
                signalArray = [add_combo_type, add_slider_freq, add_slider_amp]
                st.session_state['addedSignals'].append(signalArray)

            # Get all the added Signals from the memory
            def get_added_signals():
                signalsList = st.session_state['addedSignals']
                addedSignals = 0
                global add_slider_freq, add_slider_amp, add_combo_type
                for signal in signalsList:
                    add_combo_type = signal[0]
                    add_slider_freq = signal[1]
                    add_slider_amp = signal[2]
                    addedSignals += add_function_mag()
                return addedSignals


            phase_angle = 0
            if st.session_state['func_type'] == "Cosine":
                phase_angle = np.pi / 2
            st.session_state['amplitude'] = add_slider_amp * np.sin(
                2 * np.pi * add_slider_freq * st.session_state['time']
                + phase_angle)

            if add_btn_submit:
                add_new_signal()  # add the added Signal to the memory
                st.session_state.addFunctionButton = True  # Setting the button to false to be ready to another attempt

            # removeFromAddedFunctionList()
            write_added_functions_list()

            st.session_state['amplitude_sum'] = get_added_signals()

        elif st.session_state["cb_snr"]:
            if 'func_type' not in st.session_state:
                st.warning('You have to generate or upload a function first', icon="⚠️")
            else:
                right_up_col.markdown(' <center> <h3> SNR </h3> </center>', unsafe_allow_html=True)
                snr_number_main = right_up_col.number_input('SNR(dB)', min_value=0, max_value=120, value=120, step=1,
                                                            on_change=cb_snr_active)
                # Data for plotting
                if uploaded_csv:
                    st.session_state['time'] = np.array(df.iloc[:signalRange, 0])
                    st.session_state['amplitude'] = get_snr(np.array(df.iloc[:, 1]), snr_number_main)
                elif len(st.session_state['addedSignals']) >= 1:
                    st.session_state['time'] = np.linspace(0, signalRange, 1000)
                    st.session_state['amplitude'] = get_snr(st.session_state['amplitude_sum'], snr_number_main)
                else:
                    st.session_state['time'] = np.linspace(0, signalRange, 1000)
                    st.session_state['amplitude'] = get_snr(st.session_state['amplitude'], snr_number_main)

        elif st.session_state["cb_sample"]:
            right_up_col.markdown(' <center> <h3> Sample Signal </h3> </center>', unsafe_allow_html=True)
            sample_number_main = right_up_col.number_input('Sampling Number',
                                                           on_change=cb_sample_active, value=2., min_value=2.,
                                                           max_value=150., step=.1)
            sample_btn_recons = right_up_col.button('Reconstruct', on_click=cb_sample_active)
            if ('func_type' or 'amplitude_sampled' or 'time_sampled') not in st.session_state:
                st.warning('You have to generate or upload a function first', icon="⚠️")
            else:
                if uploaded_csv:
                    st.session_state['time'] = np.array(df.iloc[:signalRange, 0])
                    st.session_state['amplitude'] = np.array(df.iloc[:, 1])
                elif len(st.session_state['addedSignals']) >= 1:
                    st.session_state['time'] = np.linspace(0, signalRange, 1000)
                    st.session_state['amplitude'] = st.session_state['amplitude_sum']
                else:
                    st.session_state['time'] = np.linspace(0, signalRange, 1000)
                    phase = 0
                    if st.session_state['func_type'] == "Cosine":
                        phase = np.pi / 2
                    st.session_state['amplitude'] = \
                        st.session_state['generate_amp'] * np.sin(
                            (2 * np.pi * st.session_state['generate_freq'] * st.session_state['time']) + phase)

                if 'time_sampled' not in st.session_state:
                    st.session_state['time_sampled'] = \
                        np.zeros(
                            int((len(st.session_state['time']) / st.session_state['time'][-1]) / sample_number_main))
                if 'amplitude_sampled' not in st.session_state:
                    st.session_state['amplitude_sampled'] = \
                        np.zeros(
                            int((len(st.session_state['time']) / st.session_state['time'][-1]) / sample_number_main))

                st.session_state['time_sampled'], st.session_state['amplitude_sampled'] = \
                    sample(st.session_state['time'], st.session_state['amplitude'], sample_number_main)

                # Reconstruction
                st.session_state['amplitude_post'] = \
                    signal_recons(st.session_state['time'],
                                  st.session_state['time_sampled'], st.session_state['amplitude_sampled'])

                st.session_state.reconsFunctionButton = False

        elif st.session_state["cb_generate"]:
            right_up_col.markdown(' <center> <h3> Generate Signal </h3> </center>', unsafe_allow_html=True)
            generate_combo_type = right_up_col.selectbox("Signal Type", ['Cosine', 'Sine'], index=0,
                                                         on_change=cb_generate_active)
            generate_slider_freq = right_up_col.slider('Frequency',
                                                       on_change=cb_generate_active, value=1., max_value=200., step=0.5)
            generate_slider_amp = right_up_col.slider('Amplitude',
                                                      on_change=cb_generate_active, value=1., max_value=200., step=0.5)
            st.session_state['func_type'] = generate_combo_type

            if uploaded_csv:
                st.session_state['time'] = np.array(df.iloc[:signalRange, 0])
                st.session_state['amplitude'] = np.array(df.iloc[:, 1])
            else:
                # Data for plotting
                st.session_state['time'] = np.linspace(0, signalRange, 1000)
                phase = 0

                st.session_state['func_type'] = generate_combo_type
                st.session_state['generate_freq'] = generate_slider_freq
                st.session_state['generate_amp'] = generate_slider_amp

                if st.session_state['func_type'] == "Cosine":
                    phase = np.pi / 2
                st.session_state['amplitude'] = \
                    generate_slider_amp * np.sin((2 * np.pi * generate_slider_freq * st.session_state['time']) + phase)

        if uploaded_csv and not st.session_state['cb_snr']:
            st.session_state['time'] = np.array(df.iloc[:signalRange, 0])
            st.session_state['amplitude'] = np.array(df.iloc[:, 1])

        fig_main = px.line(x=st.session_state['time'], y=st.session_state['amplitude'], height=820,
                           labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        fig_main.update_layout(title_text='Active Viewer', title_x=0.5, font=dict(
            family="Sans serif",
            size=15,
            color="white"))
        fig_main.update_traces(line_color='#2596be', line_width=2)
        if ('func_type' or 'amplitude_sampled' or 'time_sampled') in st.session_state:
            if sample_number_main > 0:
                fig_main.add_scatter(x=st.session_state['time_sampled'], y=st.session_state['amplitude_sampled'],
                                     mode="markers",
                                     marker=dict(size=10, color="LightSeaGreen"),
                                     name="Samples")
            left_up_col.plotly_chart(fig_main, use_container_width=True)
        else:
            fig_main.add_scatter(x=[0, 0], y=[0, 0],
                                 mode="markers",
                                 marker=dict(size=10, color="LightSeaGreen"),
                                 name="Samples")
            left_up_col.plotly_chart(fig_main, use_container_width=True)

    with st.container():
        if sample_btn_recons:
            fig_sec = px.line(x=st.session_state['time'], y=st.session_state['amplitude_post'], height=820,
                              labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
            st.session_state.reconsFunctionButton = True
        elif cb_add and type(st.session_state['amplitude_sum'])!=int :
            fig_sec = px.line(x=st.session_state['time'], y=st.session_state['amplitude_sum'], height=820,
                              labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        else:
            fig_sec = px.line(x=[0, 0], y=[0, 0], height=780,
                              labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        fig_sec.update_layout(title_text='Accumulative Viewer', title_x=0.5, font=dict(
            family="Sans serif",
            size=15,
            color="white", ))
        fig_sec.update_traces(line_color='#2596be')
        st.plotly_chart(fig_sec, use_container_width=True)

    with st.container():
        @st.cache
        def convert_df(df_temp):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df_temp.to_csv().encode('utf-8')


        _, save_added, save_gen, save_recon, _ = st.columns([6, 3, 3, 3, 6])

        df_save_gen = pd.DataFrame()
        df_save_gen['time'] = st.session_state['time']
        df_save_gen['amplitude'] = st.session_state['amplitude']
        csv_gen = convert_df(df_save_gen)
        save_gen.download_button(
            label="Download generated data as CSV",
            data=csv_gen,
            file_name='sigview_generated.csv',
            mime='text/csv')

    if ('amplitude_post' in st.session_state) and st.session_state.reconsFunctionButton:
        df_save_recon = pd.DataFrame()
        df_save_recon['time'] = st.session_state['time']
        df_save_recon['amplitude'] = st.session_state['amplitude_post']
        csv_recon = convert_df(df_save_recon)
        save_recon.download_button(
            label="Download recons data as CSV",
            data=csv_recon,
            file_name='sigview_recon.csv',
            mime='text/csv')

    if ('amplitude_sum' in st.session_state) and st.session_state.addFunctionButton:
        df_save_added = pd.DataFrame()
        df_save_added['time'] = st.session_state['time']
        df_save_added['amplitude'] = st.session_state['amplitude_sum']
        csv_added = convert_df(df_save_added)
        save_added.download_button(
            label="Download added data as CSV",
            data=csv_added,
            file_name='sigview_added.csv',
            mime='text/csv')
