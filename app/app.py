import streamlit as st
import maestro
import styles

st.set_page_config(layout='wide')
st.markdown(styles.button_css, unsafe_allow_html=True)
st.title('Frontend App Builder')

request = st.text_area(
    "Briefly describe the app you would like to build?",
    placeholder="""create a task list app
create a workout app
create an app to store recipes
create a shopping list app
create an app to save the movies I've watched
create a notes app
create an expense tracking app""")
button = st.button("Build now", type="primary")

if button and request:
    with st.expander(f"Result{' - ' + request if request else ''}", True):
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        try:
            with st.spinner("Please wait a moment"):
                response = maestro.run_maestro(request)
            
            print(*response)
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
            st.error("Sorry, we couldn't create your app, please try again.")
        st.markdown('</div>', unsafe_allow_html=True)