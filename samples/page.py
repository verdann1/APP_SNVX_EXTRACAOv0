import streamlit as st
from samples.service import SampleService
from products.service import ProductService
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

def show_samples():
    sample_service = SampleService()
    product_service = ProductService()

    tab1, tab2 = st.tabs(['Listar Amostras', 'Cadastrar Nova Amostra'])

    with tab1:
        st.subheader("Lista de Amostras")
        try:
            samples = sample_service.get_samples()
            
            if samples:
                # Exibir estatísticas
                try:
                    stats = sample_service.get_sample_stats()
                    col1, col2 = st.columns(2)
                    col1.metric("Total de Amostras", stats.get('total_samples', 0))
                    col2.metric("Últimos 7 Dias", stats.get('last_week_samples', 0))
                except Exception as e:
                    st.error(f"Erro ao carregar estatísticas: {str(e)}")

                # Configurar tabela
                df = pd.json_normalize(samples)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_pagination(paginationPageSize=10)
                gb.configure_side_bar()
                AgGrid(df, gridOptions=gb.build(), key='samples_grid')
            else:
                st.warning("Nenhuma amostra encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar amostras: {str(e)}")

    with tab2:
        st.subheader("Cadastrar Nova Amostra")
        assembly_id = st.number_input('ID da Montagem', min_value=1, step=1)
        
        try:
            products = product_service.get_products()
            product_options = {p['part_number']: p['id'] for p in products}
            
            # ✅ Alterado para selectbox (seleção única)
            selected_product = st.selectbox(
                'Selecione um Produto',
                options=product_options.keys(),
                help='Escolha um único produto para a amostra'
            )
            
            if st.button('Cadastrar'):
                if not assembly_id:
                    st.error('ID da montagem obrigatório')
                elif not selected_product:
                    st.error('Selecione um produto')
                else:
                    # ✅ Garante que seja uma lista com um único elemento
                    product_id = product_options[selected_product]
                    new_sample = sample_service.create_sample(assembly_id, [product_id])
                    
                    if new_sample:
                        st.success('Amostra cadastrada com sucesso!')
                        st.rerun()
        except Exception as e:
            st.error(f"Erro no cadastro: {str(e)}")