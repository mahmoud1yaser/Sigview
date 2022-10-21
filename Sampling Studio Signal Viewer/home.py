import streamlit as st

st.set_page_config(page_title="SigView", page_icon="https://i.ibb.co/FKFT3Pn/audio-waves.png", layout="wide")
st.markdown("""
<style>
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


with open('css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

html_code = (open("home.html", 'r', encoding='utf-8')).read()
st.markdown(f'{html_code}', unsafe_allow_html=True)


