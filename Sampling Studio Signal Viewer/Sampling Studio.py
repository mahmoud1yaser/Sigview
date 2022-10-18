from ast import Global
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
import time as time_library
import csv 
import mpld3
st.header("Sampling Studio ")
st.markdown("---")

global signal 
global frequency
global functionType
global addFunctionType
global addFunctionFrequency
global addFunctionAmplituide
amplituide =1
signalResolution =[0,5]


a1Col3,a1Col4 =st.columns([1,1])
with a1Col3 :
    signalGeneration =st.checkbox('Generate Signal')
    if(signalGeneration):
        frequency=st.slider("frequency",min_value=0,max_value=100,step=1)
        #checkBox to add noise to the signal 
        addnoise=st.checkbox("add noise to signal ")
        if(addnoise):
            SNR_DB=st.number_input("SNR DB",min_value=0.,max_value=100.,format="%.2f")

#function to add noise to the signal 
def getNoise(signal):
    if(addnoise):
        signalAvgPowerDB=10*np.log10(np.mean(signal**2))
        noiseDB=signalAvgPowerDB-SNR_DB
        noiseWatt=10**(noiseDB/10)
        meanNoise=0
        noise=np.random.normal(meanNoise,np.sqrt(noiseWatt),len(signal))
        noiseSignal=noise+signal
        return noiseSignal
    else :
        return signal


with a1Col4 :
    if(signalGeneration):
        functionType=st.selectbox("choose a signal",("Sine(t)",'Cos(t)'))
        amplituide=st.number_input("Amplituide",max_value=100.,format="%.2F") 




a2Col1,a2Col2 =st.columns((3,1))

if(signalGeneration):

    with a2Col2 : 
        signaleResolution =st.slider("Resolution",-20,20,(0,5))
        addFunction =st.checkbox("Add function")
        if(addFunction):
            addFunctionType=st.selectbox("Signal",('Sine(t)','Cos(t)'))
            addFunctionFrequency=st.slider("Frequqncy :",min_value=0,max_value=100,step=1,value=0)
            addFunctionAmplituide=st.number_input("Amplituide :",max_value=100.,format='%.2f')
    
    
    time = np.linspace(signaleResolution[0],signaleResolution[1],1000)
    phaseshift=0

    if(functionType=="Cos(t)"):
        phaseshift=np.pi/2

    signal=amplituide * np.sin(frequency*time+phaseshift)

    if(addFunction):
        if(addFunctionType=="Cos(t)"):
            phaseshift=np.pi/2
        else :
            phaseshift=0
        signal=signal+addFunctionAmplituide*np.sin(addFunctionFrequency*time+phaseshift)
    signal=getNoise(signal)
    

    fig=plt.figure()
    plt.plot(time,signal)
    # plt.grid()
    with a2Col1 :
        # st.pyplot(fig)
        htmlFig=mpld3.fig_to_html(fig)
        components.html(htmlFig,height=600)
        chart=st.line_chart(np.zeros(shape=(1,1)))
        numOfPoints=len(time)
        
        for i in range (int(numOfPoints/10)):
            y=signal[i:i+11]
            st.write(type(y))
            chart.add_rows([y])
            time_library.sleep(0.005)