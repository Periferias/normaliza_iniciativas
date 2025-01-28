class SurveyNotFound(Exception):
    def __init__(self, uid: str):
        message = f"Formulário com o uid {uid} não encontrado"
        super().__init__(message)

class MissingSurveyUID(Exception):
    def __init__(self):
        message = "É necessário informar o UID do formulário"
        super().__init__(message)
