import streamlit as st
from assembly.repository import AssemblyRepository

def show_assembly():
    st.header("Montagem")
    repo = AssemblyRepository()

    try:
        # Obtém e ordena as montagens por ID
        assemblies = sorted(repo.get_assemblies(), key=lambda x: x['id'])  # ✅ Ordenação aqui
        if assemblies is None:
            return

        # Lista de montagens (agora ordenada)
        st.subheader("Lista de Montagens")
        for assembly in assemblies:
            st.write(f"ID: {assembly['id']} | Nome: {assembly['name']}")

        # Formulário de criação
        with st.form("create_assembly_form"):  # Nome único para o formulário
            assembly_name = st.text_input("Nome da Montagem")
            
            # Botão de submit dentro do formulário
            submitted = st.form_submit_button("Criar")  # ✅ Botão dentro do form
            
            if submitted:
                if not assembly_name.strip():
                    st.error("O nome da montagem não pode ser vazio.")
                else:
                    new_assembly = {"name": assembly_name}
                    result = repo.create_assembly(new_assembly)
                    st.success("Montagem criada com sucesso!")
                    st.rerun()

    except Exception as e:
        st.error(f"Erro: {str(e)}")