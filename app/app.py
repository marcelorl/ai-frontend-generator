import streamlit as st
import streamlit.components.v1 as components
import maestro_groq

st.set_page_config(layout='wide')
st.title('Frontend Builder App')

st.write("""
    Crie Aplicações Frontend com o poder da IA!         
""")


request = st.text_area("Descreva brevemente o app que voce gostaria de montar?", placeholder='criar um app de lista de tarefas\ncriar um app de treino\ncriar um app para guardar receitas')
button = st.button("Montar agora")

if button and request:
    st.write("""
        Preview your App
    """)
    box = st.container(height=500)
    with box:
        with st.spinner("waiting"):
            response = maestro_groq.run_maestro(request)
        print(response)
        try:
            components.iframe('http://localhost/'+response[0].replace('../results/', ''), height=500)
        except KeyError:
            box.write("Desculpe, não conseguimos criar seu app.")