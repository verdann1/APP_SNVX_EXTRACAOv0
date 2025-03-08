import logging
import requests
import streamlit as st
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class ResultRepository:
    def __init__(self):
        self.__base_url = 'https://verdann.pythonanywhere.com/api/v1/'
        self.__results_endpoint = f'{self.__base_url}results/'
        
        # Validação de token
        if 'token' not in st.session_state:
            logging.error("Token de autorização não encontrado")
            st.error("Sessão expirada. Faça login novamente.")
            st.session_state.clear()
            st.rerun()
            
        self.__headers = {
            'Authorization': f'Bearer {st.session_state.token}',
            'Content-Type': 'application/json'
        }

    @st.cache_data(ttl=300, hash_funcs={requests.sessions.Session: id})
    def get_results(_self) -> list:
        """Obtém resultados da API com cache inteligente"""
        try:
            logging.info(f"GET {_self.__results_endpoint}")
            response = requests.get(
                _self.__results_endpoint,
                headers=_self.__headers,
                timeout=10
            )
            return _self.__handle_response(response)    
        except Exception as e:
            logging.error(f"Erro na requisição: {str(e)}")
            st.error("Falha na comunicação com o servidor")
            raise

    def create_result(self, result_data: dict) -> dict:
        """Cria novo resultado na API"""
        try:
            logging.info(f"POST {self.__results_endpoint}")
            response = requests.post(
                self.__results_endpoint,
                json=result_data,
                headers=self.__headers,
                timeout=10
            )
            return self.__handle_response(response)
        except Exception as e:
            logging.error(f"Falha ao criar: {str(e)}")
            st.error("Erro ao registrar resultado")
            raise

    def update_result(self, result_id: int, updated_data: dict) -> dict:
        """Atualiza resultado existente"""
        try:
            endpoint = f"{self.__results_endpoint}{result_id}/"
            logging.info(f"PUT {endpoint}")
            response = requests.put(
                endpoint,
                json=updated_data,
                headers=self.__headers,
                timeout=10
            )
            return self.__handle_response(response)
        except Exception as e:
            logging.error(f"Falha ao atualizar: {str(e)}")
            st.error("Erro ao atualizar registro")
            raise

    def delete_result(self, result_id: int) -> bool:
        """Exclui resultado"""
        try:
            endpoint = f"{self.__results_endpoint}{result_id}/"
            logging.info(f"DELETE {endpoint}")
            response = requests.delete(
                endpoint,
                headers=self.__headers,
                timeout=10
            )
            return self.__handle_response(response)
        except Exception as e:
            logging.error(f"Falha ao excluir: {str(e)}")
            st.error("Erro ao remover resultado")
            raise

    def __handle_response(self, response) -> dict:
        """Trata respostas da API com logging detalhado"""
        if response.status_code in (200, 201):
            logging.info(f"Resposta bem-sucedida: {response.status_code}")
            return response.json()
            
        if response.status_code == 401:
            logging.error("Token inválido/expirado")
            st.error("Sessão expirada. Faça login novamente.")
            st.session_state.clear()
            st.rerun()
            
        if response.status_code >= 500:
            logging.critical(f"Erro servidor: {response.text}")
            st.error("Falha no servidor. Tente mais tarde.")
            
        logging.error(f"Erro {response.status_code}: {response.text}")
        response.raise_for_status()
        return {}