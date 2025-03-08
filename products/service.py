import logging
import streamlit as st
import re
from products.repository import ProductRepository


# Configuração básica de logging
logging.basicConfig(level=logging.INFO)


class ProductService:

    def __init__(self):
        self.product_repository = ProductRepository()

    def get_products(self):
        """
        Obtém todos os produtos e armazena na sessão do Streamlit.

        Returns:
            list: Lista de produtos.
        """
        if 'products' in st.session_state:
            logging.info("Produtos carregados do cache.")
            return st.session_state.products
        try:
            logging.info("Buscando produtos na API...")
            products = self.product_repository.get_products()
        except Exception as e:
            logging.error(f"Erro ao obter produtos: {e}")
            st.error(f"Erro ao obter produtos: {e}")
            return []
        st.session_state.products = products
        logging.info(f"{len(products)} produtos carregados e armazenados no cache.")
        return products

    def create_product(self, part_number, project):
        """
        Cria um novo produto com base nos parâmetros fornecidos e atualiza a sessão.

        Args:
            part_number (str): Número da peça (formato IM-XXXXX ou IM-XXXXX-SUFX).
            project (str): Projeto associado ao produto.

        Returns:
            dict: Novo produto criado.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info("Tentando criar novo produto...")
        self.validate_product_data(part_number, project)

        product = dict(
            part_number=part_number,
            project=project,
        )
        try:
            new_product = self.product_repository.create_product(product)
        except Exception as e:
            logging.error(f"Erro ao criar produto: {e}")
            st.error(f"Erro ao criar produto: {e}")
            return None

        # Inicializar o estado de sessão se necessário
        if 'products' not in st.session_state:
            st.session_state.products = []
        st.session_state.products.append(new_product)
        logging.info("Novo produto criado e adicionado ao cache.")
        return new_product

    def validate_product_data(self, part_number, project):
        """
        Valida os dados do produto antes de enviá-los para o repositório.

        Raises:
            ValueError: Se os dados forem inválidos.
        """
        # Validar part_number (ex.: IM-XXXXX ou IM-XXXXX-SUFX)
        pattern = r'^IM-\d{5}(-[A-Z0-9]+)?$'
        if not re.match(pattern, part_number):
            raise ValueError('O número da peça deve seguir o formato IM-XXXXX ou IM-XXXXX-SUFX.')

        # Validar project (projeto deve estar na lista de opções permitidas)
        allowed_projects = [
            'GM', 'VW', '23X', '216', 'ONIX', 'MCO', 
            'GEM', 'CRETA', 'BR2-HB20', 'SU2B-CRETA', 'Chery'
        ]
        if project not in allowed_projects:
            raise ValueError(f'O projeto "{project}" não é válido. Escolha um dos seguintes: {", ".join(allowed_projects)}.')

    def update_product(self, product_id, updated_data):
        """
        Atualiza um produto existente.

        Args:
            product_id (int): ID do produto a ser atualizado.
            updated_data (dict): Dados atualizados do produto.

        Returns:
            dict: Dados do produto atualizado.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info(f"Tentando atualizar produto com product_id={product_id}...")
        if not product_id or not isinstance(product_id, int):
            raise ValueError("product_id deve ser um inteiro válido.")
        if not updated_data or not isinstance(updated_data, dict):
            raise ValueError("updated_data deve ser um dicionário válido.")

        try:
            updated_product = self.product_repository.update_product(product_id, updated_data)
        except Exception as e:
            logging.error(f"Erro ao atualizar produto: {e}")
            st.error(f"Erro ao atualizar produto: {e}")
            return None

        # Atualizar o cache
        if 'products' in st.session_state:
            st.session_state.products = [
                updated_product if product['id'] == product_id else product
                for product in st.session_state.products
            ]
        logging.info("Produto atualizado e cache atualizado.")
        return updated_product

    def delete_product(self, product_id):
        """
        Exclui um produto existente.

        Args:
            product_id (int): ID do produto a ser excluído.

        Returns:
            bool: True se a exclusão for bem-sucedida, False caso contrário.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info(f"Tentando excluir produto com product_id={product_id}...")
        if not product_id or not isinstance(product_id, int):
            raise ValueError("product_id deve ser um inteiro válido.")

        try:
            success = self.product_repository.delete_product(product_id)
        except Exception as e:
            logging.error(f"Erro ao excluir produto: {e}")
            st.error(f"Erro ao excluir produto: {e}")
            return False

        # Atualizar o cache
        if 'products' in st.session_state:
            st.session_state.products = [
                product for product in st.session_state.products if product['id'] != product_id
            ]
        logging.info("Produto excluído e cache atualizado.")
        return success
