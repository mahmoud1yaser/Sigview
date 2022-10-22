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



if 'addedSignals' not in st.session_state: #Storing the added Signals in the memory 
    st.session_state['addedSignals']=[] #we will add in 3 types : type of function then freq then amplituide



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


removeFromListButtons=[0] #the variable that saves the list of the buttons of the added functions  

addedFunctionsListCheckBox=st.sidebar.checkbox("added Functions List") #checkbox in the sidebar for showing the added functions list 


# Area number 1 Settin columns
a1Col1,a1Col2 =st.columns([1,1])
# Area 1 Column number 1
with a1Col1 :
    signalGeneration =st.checkbox('Generate Signal') #checkbox for generating a signal
    if(signalGeneration):
        frequency=st.slider("frequency",min_value=0.,max_value=100.,step=0.5) #a slider for getting the value of the frequqncy 
        
        #checkBox to add noise to the signal 
        addnoise=st.checkbox("add noise to signal ") #checkbox for being able to add a noise to the function 
        if(addnoise):
            SNR_DB=st.number_input("SNR DB",min_value=0.,max_value=100.,format="%.2f",value=40.) #input box for entering the SNR in DB


#this function for the getting the list of the added functions to the sidebar and also and ability to remove them   
def write_added_functions_list(): 
    if(addedFunctionsListCheckBox): #checking the checkbox for showing the list of the added functions in the sidebar  
        index=0
        for functions in st.session_state['addedSignals']:
            removeFromListButtons.append(0) 
            functionsListAmplituide=str(functions[2])
            functionsListFrequency=str(functions[1])
            if(functions[0]=='Cos(t)'):
                removeFromListButtons[index]=st.sidebar.button(label='🗑️ '+str(index+1)+') '+functionsListAmplituide+'Cos('+functionsListFrequency+'t)')
            else :
                removeFromListButtons[index]=st.sidebar.button(label='🗑️ '+str(index+1)+') '+functionsListAmplituide+'Sine('+functionsListFrequency+'t)')
            if(removeFromListButtons[index]):
                st.session_state['addedSignals'].pop(index)
                removeFromListButtons.pop(index)
                st.experimental_rerun()
            index+=1
        if(len(removeFromListButtons)!=0 and index!=0):
            removeFromListButtons.pop(index)
        
    
        

#function to add noise to the signal 
def get_noise(signal):
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
        signaleResolution =st.slider("Resolution",min_value=0,max_value=20,value=5,step=1)
        addFunctionCheckBox =st.checkbox("Add function")
        if(addFunctionCheckBox):
            addFunctionType=st.selectbox("Signal",('Sine(t)','Cos(t)'))
            addFunctionFrequency=st.slider("Frequqncy :",min_value=0.,max_value=100.,step=0.5,value=1.)
            addFunctionAmplituide=st.number_input("Amplituide :",max_value=100.,format='%.2f',value=1.)
            addFunctionButton=st.button("Add function")
            removeFunctionButton=st.button("Remove function")
        else :
            del st.session_state['addedSignals']     # saving zero to the memory of the session state
            st.session_state['addedSignals']=[]


    #this function here for adding sine or cosine wave to the signal and saving it to the memory 
    def add_function_mag():
        if(addFunctionType=="Cos(t)"):
            phaseshift=np.pi/2
        else :
            phaseshift=0
        return addFunctionAmplituide*np.sin(addFunctionFrequency*time+phaseshift)
             


    #Add the added Signals to the session state to get them back again
    def add_new_signal():
        signalArray=[addFunctionType,addFunctionFrequency,addFunctionAmplituide]
        st.session_state['addedSignals'].append(signalArray)


    #Get all the added Signals from the memory 
    def get_added_signals():
        signalsList=st.session_state['addedSignals']
        addedSignals=0
        global addFunctionFrequency , addFunctionAmplituide , addFunctionType
        for signal in signalsList:
            addFunctionType=signal[0]
            addFunctionFrequency=signal[1]
            addFunctionAmplituide=signal[2]
            addedSignals+=add_function_mag()
        return addedSignals


    time = np.linspace(0,signaleResolution,1000) 
    phaseshift=0

    if(functionType=="Cos(t)"):
        phaseshift=np.pi/2

    signal=amplituide * np.sin(frequency*time+phaseshift)
    
    signal=get_noise(signal) #adding some noise to the signal 
    
    if(addFunctionButton):
        add_new_signal() #add the added Signal to the memory 
        addFunctionButton=False #Setting the button to false to be ready to another attempt
    
    elif(removeFunctionButton): #Checking if the remove button is clicked or not 
        #remove the signal from the memory        
        addFunctionAmplituide*=-1
        add_new_signal()
        removeFunctionButton=False #Setting the button of remove for another attempt
    
    
    # removeFromAddedFunctionList()
    write_added_functions_list()

    signal=signal+get_added_signals()
    


    fig=plt.figure()
    plt.plot(time,signal)
    # plt.grid()
    with a2Col1 :
        # st.pyplot(fig)
        htmlFig=mpld3.fig_to_html(fig)
        components.html(htmlFig,height=600)

