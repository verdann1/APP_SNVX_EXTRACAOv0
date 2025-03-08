import logging
import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)

class ProductRepository:

    def __init__(self):
        self.__base_url = 'https://verdann.pythonanywhere.com/api/v1/'
        self.__products_url = f'{self.__base_url}products/'
        
        if 'token' not in st.session_state:
            logging.error("Token de autorização não encontrado.")
            raise Exception("Token de autorização não encontrado.")
            
        self.__headers = {
            'Authorization': f'Bearer {st.session_state.token}'
        }

    @st.cache_data(ttl=300, hash_funcs={type('ProductRepository', (), {}): lambda _: None})
    def get_products(_self):
        """Obtém os produtos da API"""
        try:
            logging.info(f"GET {_self.__products_url}")
            response = requests.get(_self.__products_url, headers=_self.__headers, timeout=10)
            result = _self._handle_response(response)
            
            if result is None:
                st.error("Sessão expirada. Faça login novamente.")
                st.session_state.clear()
                st.rerun()
                
            return result
        except Exception as e:
            logging.error(f"Erro ao obter produtos: {e}")
            raise

    # ... (demais métodos permanecem iguais, mas aplique o mesmo padrão se usarem cache)

    def _handle_response(self, response):
        """Trata a resposta da API"""
        if response.status_code in (200, 201):
            return response.json()
            
        if response.status_code == 401:
            logging.error("Token inválido ou expirado.")
            return None
            
        logging.error(f"Erro na API. Status code: {response.status_code}, Detalhes: {response.text}")
        response.raise_for_status()