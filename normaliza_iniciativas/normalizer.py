from re import sub

from unidecode import unidecode

SUBSTITUTIONS = r"[\(\.\)\'\n\-\\#;:/\[\]|]"


def clear_string(data, substitute=""):
    if not data:
        return data
    string = data.strip()
    string = string.lower()
    string = sub(SUBSTITUTIONS, substitute or "", string)
    string = unidecode(string)
    string = sub(" ", "_", string)
    string = sub(r"_{2,}", "_", string)
    if string[0].isnumeric():
        string = string[1:]
    string = string.strip(substitute)
    return string


def set_none(data):
    def aply(item):
        if item in ("", "#REF!"):
            return None
        return item

    ds = [list(map(aply, line)) for line in data]
    return [line for line in ds if line.count(None) < len(line)]
