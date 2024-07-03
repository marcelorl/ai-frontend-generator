import streamlit as st
import streamlit.components.v1 as components
import maestro_groq

custom_css = """
<style>
    .stButton button {
        background-color: #4CAF50;
        border: none; /* Remove borders */
        cursor: pointer; /* Pointer/hand icon */
    }

    .stButton button:hover {
        background-color: #45a049; /* Darker green on hover */
    }
</style>
"""

st.set_page_config(layout='wide')
st.markdown(custom_css, unsafe_allow_html=True)
st.title('Frontend Builder App')

st.write("""
    Crie Aplicações Frontend com o poder da IA!         
""")


request = st.text_area("Descreva brevemente o app que voce gostaria de montar?", placeholder='criar um app de lista de tarefas\ncriar um app de treino\ncriar um app para guardar receitas')
button = st.button("Montar agora", type="primary")

if button and request:
    st.write("""
        Preview your App
    """)
    box = st.container(height=500)
    with box:
        try:
            with st.spinner("waiting"):
                response = maestro_groq.run_maestro(request)
            print(response)
            components.iframe('http://localhost/'+response[0].replace('../results/', ''), height=500)
        except KeyError:
            box.write("Desculpe, não conseguimos criar seu app.")