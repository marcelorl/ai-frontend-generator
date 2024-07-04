import streamlit as st
import streamlit.components.v1 as components
import maestro_groq
import styles

st.set_page_config(layout='wide')
st.markdown(styles.button_css, unsafe_allow_html=True)
st.title('Frontend Builder App')

request = st.text_area("Descreva brevemente o app que voce gostaria de montar? (Se falhar tente novamente depois de 1 minuto)", placeholder='crie um app de lista de tarefas\ncrie um app de treino\ncrie um app para guardar receitas')
button = st.button("Montar agora", type="primary")

if button and request:
    st.write("""
        Preview your App
    """)
    with st.expander("App Preview"):
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        try:
            with st.spinner("waiting"):
                response = maestro_groq.run_maestro(request)
            print(response)
            url='http://localhost/'+response[0].replace('../results/', '')
            iframe_code = f"""
                <iframe
                    src={url}
                    width="100%"
                    height="600"
                    style="border:none; overflow:auto;" scrolling="yes"></iframe>
                """
            st.markdown(iframe_code, unsafe_allow_html=True)
        except KeyError:
            st.error("Desculpe, não conseguimos criar seu app, tente novamente.")
        st.markdown('</div>', unsafe_allow_html=True)