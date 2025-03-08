# app.py
import streamlit as st
from home.page import show_home
from login.page import show_login
from results.page import show_results

# Configuração DEVE ser a PRIMEIRA instrução Streamlit
st.set_page_config(
    page_title="Extração App",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if 'token' not in st.session_state:
        show_login()
    else:
        st.title('Extração App')

        with st.sidebar:
            menu_option = st.selectbox(
                'Selecione uma opção',
                ['Início', 'Cadastrar Resultados']
            )
            
            if st.button('Logout', use_container_width=True):
                st.session_state.clear()
                st.rerun()

        if menu_option == 'Início':
            show_home()
        elif menu_option == 'Cadastrar Resultados':
            show_results()

if __name__ == '__main__':
    main()