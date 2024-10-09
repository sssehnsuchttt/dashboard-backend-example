import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

token = config["settings"]["token"]
admin_id = int(config["settings"]["admin_id"])

languages_list = config["settings"]["languages"].split(" ")
language_names = [["ru_RU", "Русский"]]
admin_language = config["settings"]["admin_language"]
currencies = [{"lang": "ru_RU", "currency": "RUB", "symbol": "₽", "location": "end"}]
web_secret_key = config["settings"]["web_secret_key"]

PATH_DATABASE = "bot/data/database.db"
bot_url = config["settings"]["bot_url"]
bot_name = config["settings"]["bot_name"]
web_url = config["settings"]["web_url"]
port = int(config["settings"]["port"])