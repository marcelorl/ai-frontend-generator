import streamlit as st
import streamlit.components.v1 as components
import maestro_groq
import styles

st.set_page_config(layout='wide')
st.markdown(styles.button_css, unsafe_allow_html=True)
st.markdown(styles.spinner_css, unsafe_allow_html=True)
st.title('Frontend Builder App')

st.write("""
    Crie Aplicações Frontend com o poder da IA!         
""")


request = st.text_area("Descreva brevemente o app que voce gostaria de montar?", placeholder='crie um app de lista de tarefas\ncrie um app de treino\ncrie um app para guardar receitas')
button = st.button("Montar agora", type="primary")

if button and request:
    st.write("""
        Preview your App
    """)
    box = st.container(height=500)
    with box:
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        try:
            with st.spinner("waiting"):
                response = maestro_groq.run_maestro(request)
            print(response)
            components.iframe('http://localhost/'+response[0].replace('../results/', ''), height=500)
        except KeyError:
            box.write("Desculpe, não conseguimos criar seu app.")
        st.markdown('</div>', unsafe_allow_html=True)