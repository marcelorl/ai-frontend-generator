import streamlit as st
import maestro
import styles

st.set_page_config(layout='wide')
st.markdown(styles.button_css, unsafe_allow_html=True)
st.title('Frontend App Builder')

request = st.text_area(
    "Descreva brevemente o app que voce gostaria de montar? (Se falhar tente novamente depois de 1 minuto)",
    placeholder="""crie um app de lista de tarefas
crie um app de treino
crie um app para guardar receitas
crie um app lista de compras
crie um app para guardar os filmes que ja assisti
crie um app de anotações
crie um app para controle de gastos""")
button = st.button("Montar agora", type="primary")

if button and request:
    with st.expander("Resultado", True):
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        try:
            with st.spinner("Espere um momento"):
                response = maestro.run_maestro(request)
            
            print('RESPONSE----->', *response)
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