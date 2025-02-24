from dotenv import load_dotenv

load_dotenv()
import json
import os

import requests

from normaliza_iniciativas.errors import SurveyNotFound, MissingSurveyUID
from normaliza_iniciativas.normalizer import clear_string
from normaliza_iniciativas.schemas import KoboForm
from normaliza_iniciativas.utils import get_credentials


class KoboEndpoints:
    def __init__(self, url: str):
        self.url = url

    @property
    def token(self):
        return f"{self.url}/token/"

    @property
    def assets(self):
        return f"{self.url}/api/v2/assets.json"

    @property
    def form_data(self, uid: str):
        return f"{self.url}/api/v2/assets/{uid}/data.json"


class KoboHandler:
    """Classe que faz o download de dados do KoboToolbox"""

    def __init__(self, url: str = None, data_folder: str = None):
        self.credentials = get_credentials()
        self.username = self.credentials.username
        self.password = self.credentials.password
        self.api_key = self.credentials.api_key
        self.url = url or self.credentials.url
        self.endpoints = KoboEndpoints(self.url)
        self.token = self.get_token()
        self.headers = {"Authorization": f"Token {self.token}"}
        self.data_folder = data_folder or os.path.join(".", "data")
        os.makedirs(os.path.dirname(self.data_folder), exist_ok=True)
        self.asset_path = os.path.join(self.data_folder, "kobo_assets.json")
        self.replace = self.get_replace()

    def get_token(self):
        """Obtém o token de acesso"""
        response = requests.post(
            self.endpoints.token,
            auth=(self.username, self.password),
            params={"format": "json"},
        )
        response.raise_for_status()
        token = response.json()["token"]
        return token

    def get_replace(self):
        REPLACE = os.getenv("REPLACE", False)
        if REPLACE:
            return True
        return False

    def download_assets(self, output_file: str = None, replace: bool = False) -> dict:
        """Faz o download dos assets do KoboToolbox

        Parâmetros:
            - output_file: str: caminho do arquivo de saída
            - replace: bool: substituir o arquivo de saída, caso exista

        Retorno:
            - dict: assets do KoboToolbox
        """
        if output_file is None:
            output_file = self.asset_path
        else:
            self.asset_path = output_file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if not replace and os.path.exists(output_file):
            print(f"Arquivo de assets {output_file} já existe, pulando download")
            return json.load(open(output_file))
        print("Baixando assets...")
        response = requests.get(self.endpoints.assets, headers=self.headers)
        response.raise_for_status()
        assets = response.json()
        with open(output_file, "w") as f:
            json.dump(assets, f, indent=2, ensure_ascii=False)
        print("Assets baixados com sucesso!")
        return assets

    def get_survey_by_uid(self, uid: str):
        if uid is None:
            raise MissingSurveyUID()
        if not os.path.exists(self.asset_path):
            assets = self.download_assets()
        else:
            assets = json.load(open(self.asset_path))
        survey = next(filter(lambda x: x["uid"] == uid, assets["results"]), None)
        if survey is None:
            raise SurveyNotFound(uid)
        survey = KoboForm(**survey)
        return survey

    def download_form_data_by_uid(
        self,
        uid: str,
        output_file: str = None,
        replace: bool = False,
    ) -> dict:
        """Faz o download dos dados de um formulário específico

        Parâmetros:
            - uid: str: uid do formulário
            - output_file: str: caminho do arquivo de saída
            - replace: bool: substituir o arquivo de saída, caso exista

        Retorno:
            - dict: dados do formulário
        """
        if uid is None:
            raise MissingSurveyUID()
        form = self.get_survey_by_uid(uid)
        if output_file is None:
            form_name = clear_string(form.name)
            output_file = os.path.join(self.data_folder, f"{form_name}_{uid}_data.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if not replace and os.path.exists(output_file):
            print(f"Arquivo {output_file} já existe, pulando download")
            return json.load(open(output_file))

        print(f"Baixando dados do formulário {form.name} - {uid}...")
        response = requests.get(form.data, headers=self.headers)
        response.raise_for_status()
        form_data = response.json()
        with open(output_file, "w") as f:
            json.dump(form_data, f, indent=2, ensure_ascii=False)
        print("Dados baixados com sucesso!")
        return form_data

    def download_survey_xls_by_uid(
        self, uid, output_file: str = None, replace: bool = False
    ) -> str:
        """Baixa o XLS de um formulário específico pelo UID

        Parameters:
            - uid: str: UID do formulário
            - output_file: str: caminho do arquivo de saída
            - replace: bool: substituir o arquivo de saída, caso exista

        Returns:
            - str: caminho do arquivo de saída
        """
        if uid is None:
            raise MissingSurveyUID()
        survey = self.get_survey_by_uid(uid)
        survey_name = clear_string(survey.name)
        if output_file is None:
            output_file = os.path.join(
                self.data_folder, f"{survey_name}_{uid}_configs.xls"
            )
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if not replace and os.path.exists(output_file):
            print(f"Arquivo {output_file} já existe, pulando download")
            return output_file
        print(f"Baixando o XLS do formulário {survey.name} - {uid}...")
        response = requests.get(survey.xls_link, headers=self.headers)
        response.raise_for_status()
        with open(output_file, "wb") as f:
            f.write(response.content)
        print("XLS baixado com sucesso!")
        return output_file

    def download_foto(self, url,path, replace=None):
        """Baixa a imagem de uma URL

        Parameters:
            - url: str: URL da imagem
            - path: str: caminho do arquivo de saída

        Returns:
            - True
        """

        if replace is None:
            replace = self.replace

        if os.path.exists(path) and not replace:
            print(f"Arquivo {path} já existe, pulando download")
            return True

        folder = os.path.dirname(path)

        # Cria a pasta se não existir
        os.makedirs(folder, exist_ok=True)
        if not replace and os.path.exists(path):
            print(f"Arquivo {path} já existe, pulando download")
            return True

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        return True




if __name__ == "__main__":
    k_handler = KoboHandler()
    k_handler.download_assets()
    survey_uid = os.getenv("KOBO_FORM_ID")
    k_handler.download_form_data_by_uid(survey_uid)
    k_handler.download_survey_xls_by_uid(survey_uid)
