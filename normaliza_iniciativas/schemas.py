from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str
    api_key: str
    url: str

class FormDownload(BaseModel):
    format: str
    url: str

class KoboForm(BaseModel):
    name: str
    uid: str
    data: str
    downloads: list

    @property
    def xls_link(self):
        return [d["url"] for d in self.downloads if d["format"] == "xls"][0]

    @property
    def xml_link(self):
        return [d["url"] for d in self.downloads if d["format"] == "xml"][0]
