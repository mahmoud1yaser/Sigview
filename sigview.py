import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Setting streamlit page configurations
st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide",
                   initial_sidebar_state='collapsed')

# Adding our Header HTML
header_code = (open("templates/header.html", 'r', encoding='utf-8')).read()
st.markdown(f'{header_code}', unsafe_allow_html=True)

# Adding CSS edits to our single page app
st.markdown("""
<style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.css-7oyrr6.euu6i2w0 {visibility: hidden;}
.css-1aehpvj.euu6i2w0 {visibility: hidden;}
.css-x8wxsk {
   padding: 0.5rem;
}
.block-container.css-18e3th9.egzxvld2 {padding: 30px 30px 30px 30px;}
.container {
  width: 85%;
  padding-right: 50px;
  padding-left: 50px;
  margin-right: auto;
  margin-left: auto;
}
@media (min-width: 576px) {
  .container {
    max-width: 540px;
  }
}
@media (min-width: 768px) {
  .container {
    max-width: 720px;
  }
}
@media (min-width: 992px) {
  .container {
    max-width: 960px;
  }
}
@media (min-width: 1200px) {
  .container {
    max-width: 1140px;
  }
}
.samp-logo{
  width: 45px;
  height: 45px;
  margin:3% ;
  text-align: center;
}
.css-10trblm{ 
position: relative;
flex: 1 1 0%;
margin-left: calc(0.5rem); }
</style>
""", unsafe_allow_html=True)

# Style our plot
plt.style.use("ggplot")

if 'addedSignals' not in st.session_state:  # Storing the added Signals in the memory
    st.session_state['addedSignals'] = []  # we will add in 3 types : type of function then freq then amplituide
if 'frequencies' not in st.session_state:
    st.session_state['frequencies'] = []
if 'sampling_frequency' not in st.session_state:
    st.session_state['sampling_frequency'] = 1.
if 'signal_sampling_frequency' not in st.session_state:
    st.session_state['signal_sampling_frequency'] = 0.5
if 'signal_snr' not in st.session_state:
    st.session_state['signal_snr'] = 60
if 'signal_type' not in st.session_state:
    st.session_state['signal_type'] = 'sin(t)'
if 'signal_frequency' not in st.session_state:
    st.session_state['signal_frequency'] = 1.
if 'signal_amplitude' not in st.session_state:
    st.session_state['signal_amplitude'] = 1.


def addedSignalsList():
    addedSignals = st.session_state['addedSignals']
    signals = []
    for signal in addedSignals:
        if signal[0] == 'sin(t)':
            signals.append(str(signal[2]) + '*sin(2π(' + str(signal[1]) + ')t)')
        else:
            signals.append(str(signal[2]) + '*cos(2π(' + str(signal[1]) + ')t')
    return signals


def removeAddedSignals(removeSignalList, selectedSignal):
    index = 0
    for signal in removeSignalList:
        if signal == selectedSignal:
            st.session_state['addedSignals'].pop(index)
            st.experimental_rerun()
        index += 1


# Define functions
# Signal to Noise Ratio Code
def add_noise(amplitude, snr):
    signalAvgPowerDB = 10 * np.log10(
        np.mean(amplitude ** 2))  # Getting the average of the power of the signal
    noiseDB = signalAvgPowerDB - snr
    noiseWatt = 10 ** (noiseDB / 10)
    meanNoise = 0
    noise = np.random.normal(meanNoise, np.sqrt(noiseWatt), len(amplitude))
    noiseSignal = noise + amplitude
    return noiseSignal


# Sampling Code
def sample(time, amplitude, fs):
    if len(time) == len(amplitude):
        points_per_indices = int((len(time) / time[-1]) / fs)
        if points_per_indices == 0:
            points_per_indices = 1
        amplitude = amplitude[::points_per_indices]
        time = time[::points_per_indices]
        return time, amplitude


# Reconstruction Code
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


# Convert to nyquist frequency function
def convert_to_nyquist():
    if not uploaded_csv:
        if st.session_state['signal_sampling_frequency'] == 0.5:
            if len(st.session_state['frequencies']) > 0:
                st.session_state['sampling_frequency'] = max(st.session_state['frequencies'])
            else:
                st.session_state['sampling_frequency'] = st.session_state['signal_frequency']
        elif st.session_state['signal_sampling_frequency'] == 1.0:
            if len(st.session_state['frequencies']) > 0:
                st.session_state['sampling_frequency'] = 2 * max(st.session_state['frequencies'])
            else:
                st.session_state['sampling_frequency'] = 2 * st.session_state['signal_frequency']
        elif st.session_state['signal_sampling_frequency'] == 1.5:
            if len(st.session_state['frequencies']) > 0:
                st.session_state['sampling_frequency'] = 3 * max(st.session_state['frequencies'])
            else:
                st.session_state['sampling_frequency'] = 3 * st.session_state['signal_frequency']


# Adding layout to our page
show_signals_container = st.container()
toolbox_container = st.container()

with show_signals_container:
    browse_position, save_position, _, show_main_signal_position, show_added_signal_position, show_recons_position, \
    show_samples_position = st.columns([1.5, 0.2, 0.5, 1, 1, 1.3, 1])

    uploaded_csv = browse_position.file_uploader("Browse", type='csv', label_visibility='collapsed')
    # browse_position.markdown('<h3 style="text-align: center"> Toolbox </h3>', unsafe_allow_html=True)

    show_main = show_main_signal_position.checkbox('Show Main Signal', value=True)
    show_samples = show_samples_position.checkbox('Show Samples')
    show_added_signal = show_added_signal_position.checkbox('Show Added Signal')
    show_recons = show_recons_position.checkbox('Show Reconstructed Signal')

with toolbox_container:
    toolbox_left_position, toolbox_right_position, main_graph_position = st.columns([1.1, 1.1, 5])
    with toolbox_left_position:
        signal_frequency = st.slider('Frequency', min_value=1., max_value=150., step=0.5, key='signal_frequency',
                                     on_change=convert_to_nyquist)
        if uploaded_csv:
            st.session_state['sampling_frequency'] = st.slider('Sampling Frequency', min_value=1.0, max_value=150.,
                                                               step=.5, on_change=convert_to_nyquist, value=1.0)
        else:
            signal_sampling_frequency = st.slider('Nyquist Frequency', min_value=0.5, max_value=1.5,
                                                  step=.5, on_change=convert_to_nyquist,
                                                  key="signal_sampling_frequency")
        signal_type = st.selectbox("Signal Type", ['sin(t)', 'cos(t)'], key='signal_type')
        signal_add = st.button('Add Signal')

    with toolbox_right_position:
        signal_amplitude = st.slider('Amplitude', min_value=1., max_value=150., step=0.5, key='signal_amplitude')
        signal_snr = st.slider('SNR(dB)', min_value=1, max_value=60, step=1, key='signal_snr')

        added_signals_list = addedSignalsList()
        signal_history = st.selectbox("Added Signals", added_signals_list)
        signal_remove = st.button('Remove Signal')
        if signal_remove:
            removeAddedSignals(added_signals_list, signal_history)
    # Upload signal
    uploaded_df = pd.DataFrame()
    if uploaded_csv is not None:
        df = pd.read_csv(uploaded_csv)
        if ('time' in df.columns) and ('amplitude' in df.columns):
            st.session_state['time'] = np.array(df['time'])
            st.session_state['amplitude'] = add_noise(np.array(df['amplitude']), st.session_state['signal_snr'])
        else:
            browse_position.error(f'The csv file has to contain time and amplitude columns', icon="⚠️")
        if len(df) > 0:
            signal_range = len(df)
    else:
        # Generate signal
        signal_range = 5
        st.session_state['time'] = np.linspace(0, signal_range, 1000)
        phase = 0
        if signal_type == "cos(t)":
            phase = np.pi / 2
        st.session_state['amplitude'] = add_noise(st.session_state.signal_amplitude *
                                                  np.sin((2 * np.pi * st.session_state.signal_frequency *
                                                          st.session_state['time']) + phase),
                                                  st.session_state.signal_snr)

    # this function here for adding sine or cosine wave to the signal and saving it to the memory
    def add_function_mag():
        if signal_type == "cos(t)":
            phase_degree = np.pi / 2
        else:
            phase_degree = 0
        if not uploaded_csv:
            return add_noise(st.session_state.signal_amplitude * np.sin(
                2 * np.pi * st.session_state.signal_frequency * st.session_state['time'] +
                phase_degree), st.session_state.signal_snr)
        else:
            return add_noise(st.session_state.signal_amplitude * np.sin(
                2 * np.pi * st.session_state.signal_frequency * st.session_state['time'] +
                phase_degree) + st.session_state['amplitude'], st.session_state.signal_snr)


    def add_new_signal():
        signalArray = [signal_type, signal_frequency, signal_amplitude]
        st.session_state['addedSignals'].append(signalArray)
        # Store all frequencies to get maximum frequency to find nyquist rate
        st.session_state['frequencies'].append(signal_frequency)


    # Get all the added Signals from the memory
    def get_added_signals():
        signalsList = st.session_state['addedSignals']
        addedSignals = 0
        global signal_type, signal_frequency, signal_amplitude
        for signal in signalsList:
            signal_type = signal[0]
            signal_frequency = signal[1]
            signal_amplitude = signal[2]
            addedSignals += add_function_mag()
        return addedSignals


    if signal_add:
        add_new_signal()  # add the added Signal to the memory
        st.experimental_rerun()

    st.session_state['amplitude_added'] = get_added_signals()

    # Sampling code
    if 'time_sampled' not in st.session_state:
        st.session_state['time_sampled'] = \
            np.zeros(
                int((len(st.session_state['time']) / st.session_state['time'][-1]) / st.session_state[
                    'sampling_frequency']))
    if 'amplitude_sampled' not in st.session_state:
        st.session_state['amplitude_sampled'] = \
            np.zeros(
                int((len(st.session_state['time']) / st.session_state['time'][-1]) / st.session_state[
                    'sampling_frequency']))

    if len(st.session_state['addedSignals']) > 0:
        st.session_state['time_sampled'], st.session_state['amplitude_sampled'] = \
            sample(st.session_state['time'], st.session_state['amplitude_added'],
                   st.session_state['sampling_frequency'])
    else:
        st.session_state['time_sampled'], st.session_state['amplitude_sampled'] = \
            sample(st.session_state['time'], st.session_state['amplitude'], st.session_state['sampling_frequency'])

    # Reconstruction
    st.session_state['amplitude_recons'] = \
        signal_recons(st.session_state['time'],
                      st.session_state['time_sampled'], st.session_state['amplitude_sampled'])

    # Data for plotting
    with main_graph_position:
        fig_sec = px.line(x=[0, 0], y=[0, 0], labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'})
        fig_sec.update_layout(title_text='Signal Plot', title_x=0.5, font=dict(
            family="Sans serif",
            size=15, ))
        if show_main:
            fig_sec.add_scatter(x=st.session_state['time'], y=st.session_state['amplitude'], name="Main Signal",
                                marker=dict(size=10, color="#3C69E7"))
        if show_added_signal and len(st.session_state['addedSignals']) > 0:
            fig_sec.add_scatter(x=st.session_state['time'], y=st.session_state['amplitude_added'], name="Added Signal",
                                marker=dict(size=10, color='#00FFFF'))
        elif show_added_signal:
            fig_sec.add_scatter(x=[0, 0], y=[0, 0], name="Added Signal",
                                marker=dict(size=10, color='#00FFFF'))

        if show_samples:
            fig_sec.add_scatter(x=st.session_state['time_sampled'], y=st.session_state['amplitude_sampled'],
                                mode="markers",
                                marker=dict(size=10, color="#ff6700"),
                                name="Sampled Signal")
        if show_recons:
            fig_sec.add_scatter(x=st.session_state['time'], y=st.session_state['amplitude_recons'],
                                name="Reconstructed Signal", marker=dict(size=10, color="#F75394"))

        st.plotly_chart(fig_sec, use_container_width=True)

    # Save signal
    with st.container():
        @st.cache
        def convert_df(df_temp):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df_temp.to_csv().encode('utf-8')

    df_save = pd.DataFrame()
    df_save['time'] = st.session_state['time']
    df_save['amplitude'] = st.session_state['amplitude_recons']
    csv = convert_df(df_save)
    save_position.download_button(
        label="💾",
        data=csv,
        file_name='sigview_reconstructed.csv',
        mime='text/csv')

    save_position.markdown('<br>', unsafe_allow_html=True)
    reset_button = save_position.button('🔄')
    if reset_button:
        st.session_state['sampling_frequency'] = 1
        for key in st.session_state:
            del st.session_state[key]
        st.experimental_rerun()
