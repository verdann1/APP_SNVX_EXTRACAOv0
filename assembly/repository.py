import logging
import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)

class AssemblyRepository:

    def __init__(self):
        self.__base_url = 'https://verdann.pythonanywhere.com/api/v1/'
        self.__assemblies_url = f'{self.__base_url}assembly/'
        
        if 'token' not in st.session_state:
            logging.error("Token de autorização não encontrado.")
            raise Exception("Token de autorização não encontrado.")
            
        self.__headers = {
            'Authorization': f'Bearer {st.session_state.token}'
        }

    @st.cache_data(ttl=300, hash_funcs={type('AssemblyRepository', (), {}): lambda _: None})
    def get_assemblies(_self):
        """Obtém as montagens da API"""
        try:
            logging.info(f"GET {_self.__assemblies_url}")
            response = requests.get(_self.__assemblies_url, headers=_self.__headers, timeout=10)
            result = _self._handle_response(response)
            
            if result is None:
                st.error("Sessão expirada. Faça login novamente.")
                st.session_state.clear()
                st.rerun()
                
            return result
        except Exception as e:
            logging.error(f"Erro ao obter montagens: {e}")
            raise

    # ... (demais métodos permanecem iguais)
    
    def _handle_response(self, response):
        """Trata a resposta da API"""
        if response.status_code in (200, 201):
            return response.json()
            
        if response.status_code == 401:
            logging.error("Token inválido ou expirado.")
            return None
            
        logging.error(f"Erro na API. Status code: {response.status_code}, Detalhes: {response.text}")
        response.raise_for_status()

    def create_assembly(self, assembly_data):
        """Cria uma nova montagem e limpa o cache"""
        try:
            response = requests.post(
                self.__assemblies_url,
                headers=self.__headers,
                json=assembly_data,
                timeout=10
            )
            result = self._handle_response(response)
            
            # Limpar cache do método get_assemblies
            st.cache_data.clear()  # 👈 Limpa todo o cache
            return result
        except Exception as e:
            logging.error(f"Erro ao criar montagem: {e}")
            raise

    # Adicione também os métodos update e delete se necessário:
    def update_assembly(self, assembly_id, updated_data):
        """Atualiza uma montagem existente"""
        url = f"{self.__assemblies_url}{assembly_id}/"
        response = requests.put(
            url,
            headers=self.__headers,
            json=updated_data,
            timeout=10
        )
        return self._handle_response(response)

    def delete_assembly(self, assembly_id):
        """Exclui uma montagem"""
        url = f"{self.__assemblies_url}{assembly_id}/"
        response = requests.delete(
            url,
            headers=self.__headers,
            timeout=10
        )
        return self._handle_response(response)