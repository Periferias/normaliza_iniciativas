import os

from normaliza_iniciativas.schemas import Credentials


def get_credentials() -> dict:
    """Função que retorna as credenciais do KoboToolbox"""
    api_key = os.getenv("KOBO_API_KEY")
    username = os.getenv("KOBO_USERNAME")
    password = os.getenv("KOBO_PASSWORD")
    url = os.getenv("KOBO_URL")
    credentials = Credentials(
        api_key=api_key, username=username, password=password, url=url
    )

    return credentials
