from ast import Global
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
import time as time_library
import csv 
import mpld3


# Setting the title of the page and its icon
st.set_page_config(page_title="sampling studio", page_icon=":bar_chart:",layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# Header of the page 
st.header("Sampling Studio ")
st.markdown("---")

# making new key and store it in streamlit to be able to use it again
if 'signal'not in st.session_state:
    st.session_state['signal']=0


global signal   #the signal to be generated 
frequency=0     #the frequency of the generated Signal 
amplituide =1   #The amplituide of the Generated Signal 
signalResolution =[0,5] #Setting the Resolution of the Generated Signal 
functionType =0 #the type of the function to be generated 
addFunctionType =0  #type of the added function to the main signal (could be sine or cosine )
addFunctionFrequency =0 #Setting the frequency of the added function
addFunctionAmplituide =0    #Setting the Amplituide of the Added function
addFunctionButton=False #The button that is responsible for adding the function to the signal 
removeFunctionButton=False  #The button that is responsible for removing a function from the Signal 




# Area number 1 Settin columns
a1Col1,a1Col2 =st.columns([1,1])
# Area 1 Column number 1
with a1Col1 :
    signalGeneration =st.checkbox('Generate Signal')
    if(signalGeneration):
        frequency=st.slider("frequency",min_value=0.,max_value=100.,step=0.5)
        
        #checkBox to add noise to the signal 
        addnoise=st.checkbox("add noise to signal ")
        if(addnoise):
            SNR_DB=st.number_input("SNR DB",min_value=0.,max_value=100.,format="%.2f",value=40.)

           

#function to add noise to the signal 
def getNoise(signal):
    if(addnoise):
        signalAvgPowerDB=10*np.log10(np.mean(signal**2)) #Getting the average of the power of the signal 
        noiseDB=signalAvgPowerDB-SNR_DB
        noiseWatt=10**(noiseDB/10)
        meanNoise=0
        noise=np.random.normal(meanNoise,np.sqrt(noiseWatt),len(signal))
        noiseSignal=noise+signal
        return noiseSignal
    else :
        return signal


# Area 1 col number 2
with a1Col2 :
    if(signalGeneration):
        functionType=st.selectbox("choose a signal",("Sine(t)",'Cos(t)'))
        amplituide=st.number_input("Amplituide",max_value=100.,format="%.2F") 



# Setting Area 2 Columns 
a2Col1,a2Col2 =st.columns((3,1))

if(signalGeneration):
    
    # Area 2 column 2
    with a2Col2 : 
        signaleResolution =st.slider("Resolution",-20,20,(0,5))
        addFunctionCheckBox =st.checkbox("Add function") 
        if(addFunctionCheckBox):
            addFunctionType=st.selectbox("Signal",('Sine(t)','Cos(t)'))
            addFunctionFrequency=st.slider("Frequqncy :",min_value=0.,max_value=100.,step=0.5,value=1.)
            addFunctionAmplituide=st.number_input("Amplituide :",max_value=100.,format='%.2f',value=1.)
            addFunctionButton=st.button("Add function")
            removeFunctionButton=st.button("Remove function")
        else :
            st.session_state['signal']=0 # saving zero to the memory of the session state


    #this function here for adding sine or cosine wave to the signal  
    def addFunctionMag():
            if(addFunctionType=="Cos(t)"):
                phaseshift=np.pi/2
            else :
                phaseshift=0
            return addFunctionAmplituide*np.sin(addFunctionFrequency*time+phaseshift)
             
    
    time = np.linspace(signaleResolution[0],signaleResolution[1],1000) 
    phaseshift=0

    if(functionType=="Cos(t)"):
        phaseshift=np.pi/2

    signal=amplituide * np.sin(frequency*time+phaseshift)
    
    signal=getNoise(signal) #adding some noise to the signal 
    
    if(addFunctionButton):
        st.session_state['signal']=st.session_state['signal']+addFunctionMag() #add the added Signal to the memory 
        addFunctionButton=False #Setting the button to false to be ready to another attempt
    
    elif(removeFunctionButton): #Checking if the remove button is clicked or not 
        
        st.session_state['signal']=st.session_state['signal']-addFunctionMag() #remove the signal from the memory        
        removeFunctionButton=False #Setting the button of remove for another attempt
    
    signal=signal+st.session_state['signal']


    fig=plt.figure()
    plt.plot(time,signal)
    # plt.grid()
    with a2Col1 :
        # st.pyplot(fig)
        htmlFig=mpld3.fig_to_html(fig)
        components.html(htmlFig,height=600)
        

        # for making animation graph 
        # chart=st.line_chart(np.zeros(shape=(1,1)))
        # numOfPoints=len(time)
        # for i in range (int(numOfPoints)):
        #     y=signal[i]
        #     chart.add_rows([y])
        #     time_library.sleep(0.005)