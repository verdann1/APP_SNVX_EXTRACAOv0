import logging
import streamlit as st
from assembly.repository import AssemblyRepository


# Configuração básica de logging
logging.basicConfig(level=logging.INFO)


class AssemblyService:

    def __init__(self):
        self.assembly_repository = AssemblyRepository()

    def get_assemblies(self):
        """
        Obtém todas as montagens e armazena na sessão do Streamlit.

        Returns:
            list: Lista de montagens.
        """
        if 'assemblies' in st.session_state:
            logging.info("Montagens carregadas do cache.")
            return st.session_state.assemblies
        try:
            logging.info("Buscando montagens na API...")
            assemblies = self.assembly_repository.get_assemblies()
        except Exception as e:
            logging.error(f"Erro ao obter montagens: {e}")
            st.error(f"Erro ao obter montagens: {e}")
            return []
        st.session_state.assemblies = assemblies
        logging.info(f"{len(assemblies)} montagens carregadas e armazenadas no cache.")
        return assemblies

    def create_assembly(self, name):
        """
        Cria uma nova montagem com base nos parâmetros fornecidos e atualiza a sessão.

        Args:
            name (str): Nome da montagem.

        Returns:
            dict: Nova montagem criada.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info("Tentando criar nova montagem...")
        self.validate_assembly_data(name)

        assembly = dict(
            name=name,
        )
        try:
            new_assembly = self.assembly_repository.create_assembly(assembly)
        except Exception as e:
            logging.error(f"Erro ao criar montagem: {e}")
            st.error(f"Erro ao criar montagem: {e}")
            return None

        # Inicializar o estado de sessão se necessário
        if 'assemblies' not in st.session_state:
            st.session_state.assemblies = []
        st.session_state.assemblies.append(new_assembly)
        logging.info("Nova montagem criada e adicionada ao cache.")
        return new_assembly

    def validate_assembly_data(self, name):
        """
        Valida os dados da montagem antes de enviá-los para o repositório.

        Raises:
            ValueError: Se os dados forem inválidos.
        """
        if not name or not isinstance(name, str):
            raise ValueError("O nome da montagem deve ser uma string válida.")
        if len(name.strip()) < 3:
            raise ValueError("O nome da montagem deve ter pelo menos 3 caracteres.")

    def update_assembly(self, assembly_id, updated_data):
        """
        Atualiza uma montagem existente.

        Args:
            assembly_id (int): ID da montagem a ser atualizada.
            updated_data (dict): Dados atualizados da montagem.

        Returns:
            dict: Dados da montagem atualizada.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info(f"Tentando atualizar montagem com assembly_id={assembly_id}...")
        if not assembly_id or not isinstance(assembly_id, int):
            raise ValueError("assembly_id deve ser um inteiro válido.")
        if not updated_data or not isinstance(updated_data, dict):
            raise ValueError("updated_data deve ser um dicionário válido.")

        try:
            updated_assembly = self.assembly_repository.update_assembly(assembly_id, updated_data)
        except Exception as e:
            logging.error(f"Erro ao atualizar montagem: {e}")
            st.error(f"Erro ao atualizar montagem: {e}")
            return None

        # Atualizar o cache
        if 'assemblies' in st.session_state:
            st.session_state.assemblies = [
                updated_assembly if assembly['id'] == assembly_id else assembly
                for assembly in st.session_state.assemblies
            ]
        logging.info("Montagem atualizada e cache atualizado.")
        return updated_assembly

    def delete_assembly(self, assembly_id):
        """
        Exclui uma montagem existente.

        Args:
            assembly_id (int): ID da montagem a ser excluída.

        Returns:
            bool: True se a exclusão for bem-sucedida, False caso contrário.

        Raises:
            ValueError: Se os dados fornecidos forem inválidos.
        """
        logging.info(f"Tentando excluir montagem com assembly_id={assembly_id}...")
        if not assembly_id or not isinstance(assembly_id, int):
            raise ValueError("assembly_id deve ser um inteiro válido.")

        try:
            success = self.assembly_repository.delete_assembly(assembly_id)
        except Exception as e:
            logging.error(f"Erro ao excluir montagem: {e}")
            st.error(f"Erro ao excluir montagem: {e}")
            return False

        # Atualizar o cache
        if 'assemblies' in st.session_state:
            st.session_state.assemblies = [
                assembly for assembly in st.session_state.assemblies if assembly['id'] != assembly_id
            ]
        logging.info("Montagem excluída e cache atualizado.")
        return success