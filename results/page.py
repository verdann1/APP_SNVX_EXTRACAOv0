import pandas as pd
import streamlit as st
import time
from products.service import ProductService
from results.service import ResultService
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime

def show_results():
    result_service = ResultService()
    product_service = ProductService()

    tab1, tab2 = st.tabs(['Listar Resultados', 'Cadastrar Novo Resultado'])

    # --- Aba 1: Listar Resultados ---
    with tab1:
        try:
            results = result_service.get_results()
        except Exception as e:
            st.error(f'Erro ao carregar resultados: {str(e)}')
            results = []

        if results:
            st.write('Lista de Resultados:')
            results_df = pd.json_normalize(results)

            # Formatar datas
            if 'sample_taken_datetime' in results_df.columns:
                results_df['sample_taken_datetime'] = pd.to_datetime(
                    results_df['sample_taken_datetime']
                ).dt.strftime('%Y-%m-%d %H:%M:%S')
            if 'sample_extraction_datetime' in results_df.columns:
                results_df['sample_extraction_datetime'] = pd.to_datetime(
                    results_df['sample_extraction_datetime']
                ).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Seleção de colunas
            selected_columns = st.multiselect(
                'Selecionar Colunas',
                options=results_df.columns,
                default=list(results_df.columns[:5])
            )
            results_df = results_df[selected_columns]

            # Configurar AgGrid
            grid_options = GridOptionsBuilder.from_dataframe(results_df)
            grid_options.configure_pagination(enabled=True)
            grid_options.configure_default_column(
                sortable=True,
                filterable=True,
                resizable=True,
            )
            AgGrid(
                data=results_df,
                gridOptions=grid_options.build(),
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                reload_data=True,
                key='results_grid',
            )
        else:
            st.warning('Nenhum resultado encontrado.')

    # --- Aba 2: Cadastrar Resultado ---
    with tab2:  # ✅ Tudo dentro deste bloco pertence à aba de cadastro
        st.title('Cadastrar Novo Resultado')

        # Seleção de produtos
        try:
            products = product_service.get_products()
            product_titles = {product['part_number']: product['id'] for product in products}
        except Exception as e:
            st.error(f'Erro ao carregar produtos: {str(e)}')
            return

        selected_product = st.selectbox('Produto', list(product_titles.keys()))
        sample_types = st.multiselect(
            'Tipo de Amostra',
            options=['centragem', 'cone'],
            default=['centragem']
        )

        result_data = {}

        # Campos para cada tipo
        for sample_type in sample_types:
            with st.expander(f"Resultados para {sample_type}", expanded=True):
                force_key = f"force_{sample_type}"
                percentage_key = f"percentage_{sample_type}"

                force_N = st.number_input(
                    label=f'Força (N) - {sample_type}',
                    min_value=0.0,
                    step=0.1,
                    value=400.0 if sample_type == 'cone' else 500.0,
                    key=force_key
                )
                result_percentage = st.number_input(
                    label=f'Resultado (%) - {sample_type}',
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=percentage_key
                )

                result_data[sample_type] = {
                    'force_N': force_N,
                    'result_percentage': result_percentage
                }
                
                sample_side_key = f"sample_side_{sample_type}"
                sample_side = st.selectbox(f'Lado da Amostra - {sample_type}', ['direito', 'esquerdo'], key=sample_side_key)
                result_data[sample_type]['sample_side'] = sample_side

        # Campos comuns
        production_batch = st.text_input('Lote de Produção')
        comment = st.text_area('Comentário')

        # Botão de cadastro
        if st.button('Cadastrar'):
            if not production_batch.strip():
                st.error('Lote de produção é obrigatório')
                return

            # Validar força mínima
            errors = []
            for sample_type in sample_types:
                min_force = 400 if sample_type == 'cone' else 500
                if result_data[sample_type]['force_N'] < min_force:
                    errors.append(f"Força mínima para '{sample_type}' é {min_force} N")

            if errors:
                st.error("\n".join(errors))
                return

            # Cadastrar resultados
            try:
                for sample_type in sample_types:
                    new_result = result_service.create_result(
                        sample=product_titles[selected_product],
                        force_N=result_data[sample_type]['force_N'],
                        result_percentage=result_data[sample_type]['result_percentage'],
                        production_batch=production_batch,
                        sample_type=sample_type,
                        sample_side=result_data[sample_type]['sample_side'],
                         comment=comment,
                    )
                    if not new_result:
                        raise Exception("Falha ao cadastrar")

                st.success('Resultados cadastrados!')
                time.sleep(3)  # Delay de 3 segundos
                st.rerun()
            except Exception as e:
                st.error(f'Erro: {str(e)}')
