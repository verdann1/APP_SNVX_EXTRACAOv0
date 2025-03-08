import streamlit as st
from login.service import Auth

def show_login():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        auth = Auth()
        response = auth.get_token(username, password)
        
        if 'access' in response:
            st.session_state['token'] = response['access']
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error(f"Erro: {response.get('error', 'Credenciais inválidas')}")