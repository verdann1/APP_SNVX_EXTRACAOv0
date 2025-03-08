import streamlit as st
import pandas as pd
import re
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, ExcelExportMode
from products.service import ProductService


def validate_part_number(part_number):
    """
    Valida o formato do part_number (ex.: IM-XXXXX).

    Args:
        part_number (str): Número da peça.

    Raises:
        ValueError: Se o formato for inválido.
    """
    pattern = r'^IM-\d{5}(-[A-Z0-9]+)?$'
    if not re.match(pattern, part_number):
        raise ValueError('O número da peça deve seguir o formato IM-XXXXX ou IM-XXXXX-SUFX.')


def show_products():
    # Instanciar o serviço de produtos
    product_service = ProductService()

    # Abas para organizar o layout
    tab1, tab2 = st.tabs(['Listar Produtos', 'Cadastrar Novo Produto'])

    with tab1:
        # Listar produtos
        try:
            products = product_service.get_products()
        except Exception as e:
            st.error(f'Erro ao carregar produtos: {str(e)}')
            products = []

        if products:
            st.write('Lista de Produtos:')
            products_df = pd.json_normalize(products)

            # Permitir que o usuário selecione colunas para exibir
            selected_columns = st.multiselect(
                'Selecionar Colunas',
                options=products_df.columns,
                default=list(products_df.columns[:5])
            )
            products_df = products_df[selected_columns]

            # Configurar AgGrid
            grid_options = GridOptionsBuilder.from_dataframe(products_df)
            grid_options.configure_pagination(enabled=True)
            grid_options.configure_side_bar()
            grid_options.configure_default_column(
                sortable=True,
                filterable=True,
                resizable=True,
            )
            grid_options.configure_column('project', filter=True)

            AgGrid(
                data=products_df,
                gridOptions=grid_options.build(),
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                reload_data=True,
                excel_export_mode=ExcelExportMode.MANUAL,
                key='products_grid',
            )
        else:
            st.warning('Nenhum Produto encontrado.')

    with tab2:
        # Formulário para cadastrar novos produtos
        st.title('Cadastrar Novo Produto')

        part_number = st.text_input('Part Number')
        project_choices = [
            'GM', 'VW', '23X', '216', 'ONIX', 'MCO', 
            'GEM', 'CRETA', 'BR2-HB20', 'SU2B-CRETA', 'Chery'
        ]
        project = st.selectbox(
            label='Projeto',
            options=project_choices,
        )

        if st.button('Cadastrar'):
            try:
                # Validar campos obrigatórios
                if not part_number.strip():
                    raise ValueError('Por favor, insira um valor válido para o campo "Part Number".')
                if not project:
                    raise ValueError('O campo "Projeto" é obrigatório.')

                # Validar formato do part_number
                validate_part_number(part_number)

                # Cadastrar o produto
                new_product = product_service.create_product(
                    part_number=part_number,
                    project=project,
                )
                if new_product:
                    st.success('Produto cadastrado com sucesso!')
                    st.rerun()
                else:
                    st.error('Erro ao cadastrar o Produto. Tente novamente.')
            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f'Erro inesperado: {str(e)}')