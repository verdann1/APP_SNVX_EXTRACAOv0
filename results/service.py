# result_service.py (versão corrigida)
import logging
import streamlit as st
from datetime import datetime
from results.repository import ResultRepository
from products.repository import ProductRepository
from dateutil.parser import parse

logging.basicConfig(level=logging.INFO)  # Corrigido typo

class ResultService:
    def __init__(self):
        self.result_repository = ResultRepository()
        self.product_repository = ProductRepository()  # Adicionado

    def get_results(self) -> list:
        if 'results' in st.session_state:
            logging.info("Resultados carregados do cache.")
            return st.session_state.results
        try:
            logging.info("Buscando resultados na API...")
            results = self.result_repository.get_results()
        except Exception as e:
            logging.error(f"Erro ao obter resultados: {e}")
            st.error(f"Erro ao obter resultados: {e}")
            return []
        
        st.session_state.results = results
        logging.info(f"{len(results)} resultados carregados e armazenados no cache.")
        return results

    def create_result(self, sample: int, force_N: float, result_percentage: float, comment: str, sample_type: str, sample_side: str, production_batch: str) -> dict:  # Parâmetro adicionado
        logging.info("Tentando criar novo resultado...")
        self.validate_result_data(
            sample=sample,
            force_N=force_N,
            result_percentage=result_percentage,
            production_batch=production_batch,
        )

        result = {
            "sample": sample,  # ID da amostra (deve ser um número inteiro válido)
            "force_N": force_N,  # Número decimal
            "result_percentage": result_percentage,  # Número decimal entre 0 e 100
            "comment": comment,  # String (opcional)
            "sample_type": sample_type,  # String: 'centragem' ou 'cone'
            "sample_side": sample_side,  # String: 'direito' ou 'esquerdo'
            "production_batch": production_batch  # String de até 100 caracteres
            }
        
        try:
            new_result = self.result_repository.create_result(result)
        except Exception as e:
            logging.error(f"Erro ao criar resultado: {e}")
            st.error(f"Erro ao criar resultado: {e}")
            return None

        if 'results' not in st.session_state:
            st.session_state.results = []
        st.session_state.results.append(new_result)
        logging.info("Novo resultado criado e adicionado ao cache.")
        return new_result

    def validate_result_data(self, sample: int, force_N: float, result_percentage: float, production_batch: str):
        if not isinstance(sample, int) or sample <= 0:
            raise ValueError("sample deve ser um ID válido")
        if not isinstance(force_N, (int, float)) or force_N < 0:
            raise ValueError("force_N deve ser positivo")
        if not (0 <= result_percentage <= 100):
            raise ValueError("Percentual deve estar entre 0-100")
        if not production_batch or not isinstance(production_batch, str):
            raise ValueError("Lote inválido")

    def get_results_with_products(self):
        results = self.get_results()
        products = self.product_repository.get_products()
        product_map = {p['id']: p for p in products}
        
        for result in results:
            product_id = result.get('product_id')
            product = product_map.get(product_id, {})
            result['part_number'] = product.get('part_number', 'N/A')  # Corrigido typo
            # Removido o código que deletava o campo 'id'
        
        return results

    def calculate_stats(self, results: list) -> dict:
        logging.info("Calculando estatísticas...")
        stats = {
            'total': len(results),
            'results_by_type': [],
            'force_stats': {'average': 0, 'max': 0, 'min': 0},
            'percentage_stats': {'average': 0, 'max': 0, 'min': 0},
            'sample_counts': {'centragem': 0, 'cone': 0},
            'comment_count': 0
        }

        type_counter = {}
        force_values = []
        percentage_values = []

        for result in results:
            # Contagem por tipo
            sample_type = result.get('sample_type', 'Não especificado')
            type_counter[sample_type] = type_counter.get(sample_type, 0) + 1

            # Coleta de valores numéricos
            if (force := result.get('force_N')) is not None:
                force_values.append(force)
                stats['sample_counts'][sample_type] += 1
            if (percentage := result.get('result_percentage')) is not None:
                percentage_values.append(percentage)
            if result.get('comment'):
                stats['comment_count'] += 1

        # Estatísticas de força
        if force_values:
            stats['force_stats'] = {
                'average': sum(force_values)/len(force_values),
                'max': max(force_values),
                'min': min(force_values)
            }

        # Estatísticas de percentual
        if percentage_values:
            stats['percentage_stats'] = {
                'average': sum(percentage_values)/len(percentage_values),
                'max': max(percentage_values),
                'min': min(percentage_values)
            }

        # Formata resultados por tipo
        stats['results_by_type'] = [{'type': k, 'count': v} for k, v in type_counter.items()]

        # Estatísticas específicas por tipo
        for sample_type in ['centragem', 'cone']:
            filtered = [r for r in results if r.get('sample_type') == sample_type]
            force_list = [r['force_N'] for r in filtered if 'force_N' in r]
            percent_list = [r['result_percentage'] for r in filtered if 'result_percentage' in r]

            stats[f'average_force_{sample_type}'] = sum(force_list)/len(force_list) if force_list else 0
            stats[f'average_percentage_{sample_type}'] = sum(percent_list)/len(percent_list) if percent_list else 0

        return stats