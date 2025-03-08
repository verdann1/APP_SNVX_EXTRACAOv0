import logging
import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)

class SampleRepository:
    def __init__(self):
        self.__base_url = 'https://verdann.pythonanywhere.com/api/v1/'
        self.__samples_url = f'{self.__base_url}samples/'
        self.__sample_stats_url = f'{self.__base_url}samples/stats/'
        
        if 'token' not in st.session_state:
            logging.error("Token de autorização não encontrado.")
            raise Exception("Token de autorização não encontrado.")
            
        self.__headers = {
            'Authorization': f'Bearer {st.session_state.token}'
        }

    @st.cache_data(ttl=300)
    def get_samples(_self):
        """Obtém todas as amostras"""
        try:
            response = requests.get(_self.__samples_url, headers=_self.__headers, timeout=10)
            result = _self._handle_response(response)
            
            if result is None:
                st.error("Sessão expirada. Faça login novamente.")
                st.session_state.clear()
                st.rerun()
                
            return result
        except Exception as e:
            logging.error(f"Erro ao obter amostras: {e}")
            raise

    @st.cache_data(ttl=300)
    def get_sample_stats(_self):
        """Obtém estatísticas das amostras"""
        try:
            response = requests.get(
                _self.__sample_stats_url,
                headers=_self.__headers,
                timeout=10
            )
            result = _self._handle_response(response)
            
            if result is None:
                st.error("Sessão expirada. Faça login novamente.")
                st.session_state.clear()
                st.rerun()
                
            return result
        except Exception as e:
            logging.error(f"Erro ao obter estatísticas: {e}")
            raise

    def create_sample(self, sample_data):
        """Cria uma nova amostra"""
        try:
            response = requests.post(
                self.__samples_url,
                headers=self.__headers,
                json=sample_data,
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            logging.error(f"Erro ao criar amostra: {e}")
            raise

    def _handle_response(self, response):
        """Trata a resposta da API"""
        if response.status_code in (200, 201):
            return response.json()
            
        if response.status_code == 401:
            logging.error("Token inválido ou expirado.")
            return None
            
        logging.error(f"Erro na API. Status code: {response.status_code}, Detalhes: {response.text}")
        response.raise_for_status()