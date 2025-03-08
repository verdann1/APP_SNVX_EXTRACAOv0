import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
from results.service import ResultService
from products.service import ProductService

def show_home():
    result_service = ResultService()
    product_service = ProductService()

    with st.spinner("Carregando dados... 💾"):
        try:
            # Carregar dados com relacionamento
            results = result_service.get_results_with_products()  # Novo método
            products = product_service.get_products()
            result_stats = result_service.calculate_stats(results)
        except Exception as e:
            st.error(f"🚨 Erro ao carregar dados: {str(e)}", icon="🚨")
            return

    # Verificação de consistência
    if not results:
        st.warning("Nenhum resultado encontrado")
        return

    # Preparar dados para filtros
    part_numbers = list({
        result['product'].get('part_number', 'N/A') 
        for result in results 
        if 'product' in result
    })
    
    sample_types = list({result['sample_type'] for result in results})
    production_batches = list({result['production_batch'] for result in results})

    # --- Filtros ---
    with st.sidebar:
        # Filtro de part_number com opção "Todos"
        selected_parts = st.multiselect(
            "Número da Peça",
            options=["Todos"] + part_numbers,
            default="Todos"
        )
        
        # Filtro de lado da amostra
        sample_side = st.radio(
            "Lado da amostra",
            ["Todos", "Direito", "Esquerdo"],
            horizontal=True
        )
        
        # Filtro de tipo de amostra
        selected_types = st.multiselect(
            "Tipo de Amostra",
            options=["Todos"] + sample_types,
            default="Todos"
        )

        # Filtro de lote
        selected_batch = st.selectbox(
            "Lote de Produção",
            options=["Todos"] + production_batches
        )

    # --- Lógica de filtragem robusta ---
    filtered_data = []
    for result in results:
        # Verificação de produto
        part_number = result.get('product', {}).get('part_number', 'N/A')
        product_match = (
            "Todos" in selected_parts or
            part_number in selected_parts
        )
        
        # Verificação de tipo
        type_match = (
            "Todos" in selected_types or
            result['sample_type'] in selected_types
        )
        
        # Verificação de lote
        batch_match = (
            selected_batch == "Todos" or
            result['production_batch'] == selected_batch
        )
        
        # Verificação de lado
        side_match = (
            sample_side == "Todos" or
            result['sample_side'] == sample_side.lower()
        )

        if all([product_match, type_match, batch_match, side_match]):
            filtered_data.append(result)

    # --- Feedback visual ---
    if not filtered_data:
        st.warning("Nenhum resultado corresponde aos filtros selecionados")
        st.stop()

    # --- Recálculo de Estatísticas ---
    filtered_stats = result_service.calculate_stats(filtered_data)

    # --- Layout Principal ---
    st.title("📊 Dashboard de Testes de Amostras")
    
    # --- KPIs Principais ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label=" Total de Testes",
            value=f"{filtered_stats.get('total', 0):,}".replace(',', '.'),
            delta=f"{(filtered_stats.get('total',0)/result_stats.get('total',1))*100:.1f}% do total"
        )
    with col2:
        st.metric(
            label=" Força Média (N)",
            value=f"{filtered_stats.get('average_force', 0):.2f} N",
            delta=f"{filtered_stats.get('average_force',0) - result_stats.get('average_force',0):+.2f} N"
        )
    with col3:
        st.metric(
            label=" Percentual Médio",
            value=f"{filtered_stats.get('average_percentage', 0):.2f}%",
            delta=f"{filtered_stats.get('average_percentage',0) - result_stats.get('average_percentage',0):+.2f}%"
        )
    with col4:
        st.metric(
            label=" Comentários",
            value=filtered_stats.get('samples_with_comments', 0),
            delta=f"{filtered_stats.get('samples_with_comments',0)/result_stats.get('samples_with_comments',1)*100:.1f}%"
        )

    # --- Gráficos Dinâmicos ---
    tab1, tab2, tab3 = st.tabs(["📈 Análise Geral", "🔍 Detalhamento", "🗃️ Dados Brutos"])
    
    with tab1:
        # Gráfico de comparação entre tipos
        if filtered_data:
            df = pd.DataFrame(filtered_data)
            
            # Gráfico de linhas comparativo
            st.subheader("Comparação de Força por Tipo")
            fig_line = px.line(
                df.groupby(['sample_type', 'production_batch']).mean(numeric_only=True).reset_index(),
                x='production_batch',
                y='force_N',
                color='sample_type',
                markers=True,
                title="Evolução da Força por Lote e Tipo",
                labels={
                    "force_N": "Força (N)",
                    "production_batch": "Lote de Produção"
                }
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Gráfico de dispersão interativo
            st.subheader("Relação Força vs Percentual")
            fig_scatter = px.scatter(
                df,
                x='force_N',
                y='result_percentage',
                color='sample_type',
                size='result_percentage',
                hover_data=['production_batch', 'comment'],
                trendline='ols',
                title='Correlação entre Força e Percentual'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        else:
            st.warning("Nenhum dado disponível para exibição")

    with tab2:
        # Análise detalhada por tipo
        st.subheader("Análise por Tipo de Amostra")
        if filtered_stats.get('total', 0) > 0:
            # Verifica se filtered_data existe
            if 'filtered_data' in locals():
                df = pd.DataFrame(filtered_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    # Treemap de distribuição
                    st.subheader("Proporção de Tipos")
                    fig_tree = px.treemap(
                        pd.DataFrame(filtered_stats['results_by_type']),
                        path=['type'],
                        values='count',
                        title="Distribuição por Tipo",
                        color='count',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig_tree, use_container_width=True)
                    
                with col2:
                    # Histograma de força
                    st.subheader("Distribuição de Força")
                    fig_hist = px.histogram(
                        df,
                        x='force_N',
                        nbins=20,
                        color='sample_type',
                        marginal='box',
                        title='Distribuição de Força por Tipo'
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Selecione filtros para ver detalhes")

    with tab3:
        # Visualização de dados brutos
        st.subheader("Registros Filtrados")
        if filtered_data:
            df = pd.DataFrame(filtered_data)
            st.dataframe(
                df.style.background_gradient(cmap='Blues'),
                use_container_width=True,
                column_config={
                    "comment": st.column_config.TextColumn(
                        "Comentário",
                        help="Comentários adicionais sobre o teste"
                    )
                }
            )
            
            # Botão de download
            st.download_button(
                label=".Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='dados_filtrados.csv',
                mime='text/csv'
            )
        else:
            st.warning("Nenhum dado corresponde aos filtros selecionados")

    # --- Rodapé ---
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            padding: 10px;
            text-align: center;
            font-size: 0.9em;
        }
        </style>
        <div class="footer">
            Desenvolvido pelo Departamento de Qualidade 
            | Última atualização: 2024-01-15
        </div>
        """,
        unsafe_allow_html=True
    )