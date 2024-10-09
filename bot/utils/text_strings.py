import json, sqlite3
from bot.data.config import languages_list, language_names, admin_language
from bot.services.api_sqlite import fetch_data

def languageToName(request):
    success = False
    for i in range(len(language_names)):
        if (language_names[i][0] == request):
            success = True
            return language_names[i][1]
    if (success == False):
        return request


def getUserLang(id):
    try:
        lang = fetch_data("userlist", "fetchone", userid=id)["lang"]
        if lang in languages_list:
            return lang
        else:
            return admin_language
    except:
        return admin_language




def text(name, id=""):
    lang_code = ""
    if id in languages_list:
        lang_code = id
    else:
        lang_code = getUserLang(id)
    with open(f"{lang_code}.json", "r", encoding="utf-8") as strokes:
        try:
            strings_json = strokes.read()
            strings = json.loads(strings_json)
            return strings[name]
        except:
            return name

def get_text(name):
    result = []
    for i in languages_list:
        with open(f"{i}.json", "r", encoding="utf-8") as strokes:
            try:
                strings_json = strokes.read()
                strings = json.loads(strings_json)
                result.append(strings[name])
            except:
                result.append(name)
    return result