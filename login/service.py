import logging
import requests

logging.basicConfig(level=logging.INFO)

class Auth:
    def __init__(self):
        self.__base_url = 'https://verdann.pythonanywhere.com/api/v1/'
        self.__auth_url = f'{self.__base_url}authentication/token/'

    def get_token(self, username, password):
        try:
            self.validate_credentials(username, password)
            auth_payload = {'username': username, 'password': password}
            logging.info("Fazendo requisição de autenticação...")
            auth_response = requests.post(
                self.__auth_url,
                data=auth_payload,
                timeout=10
            )
            return self._handle_response(auth_response)
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao conectar à API: {e}")
            return {'error': f'Erro ao conectar à API: {str(e)}'}

    def validate_credentials(self, username, password):
        if not username or not isinstance(username, str):
            raise ValueError("O nome de usuário deve ser uma string válida.")
        if not password or not isinstance(password, str):
            raise ValueError("A senha deve ser uma string válida.")

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            error_message = response.json().get('detail', 'Erro desconhecido')
            logging.error(f"Erro na API. Status code: {response.status_code}, Detalhes: {error_message}")
            return {'error': f'Erro ao acessar a API. Status code: {response.status_code}, Detalhes: {error_message}'}