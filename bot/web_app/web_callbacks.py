from aiohttp import web
from bot.data.config import admin_id, token
from bot.data.loader import bot
from bot.services.api_sqlite import (
    fetch_data,
    add_data,
    update_data,
    get_all_tables,
    get_table,
    add_new_row,
    update_table,
)
from bot.utils.const_functions import do_round
from bot.web_app.auth import verify_token
from datetime import datetime
import sys
import configparser

async def handle_request(request, handler):
    """Функция для обработки запросов с верификацией."""
    access_token = request.headers.get("Authorization")
    try:
        payload = verify_token(access_token)
        return await handler(request)
    except Exception as e:
        print(e)
        if str(e) == "Expired token":
            return web.json_response({"error": "Expired token"}, status=403)
        elif str(e) == "Invalid token":
            return web.json_response({"error": "Invalid token"}, status=401)
        return web.json_response({"error": str(e)}, status=400)


async def settings_handler(request):
    data = await request.json()
    action = data["action"]
    if action == "reload":
        sys.exit()


async def get_username(request):
    username = None
    try:
        info = await bot.get_me()
        username = info["username"]
    except:
        pass
    return web.json_response({"username": username}, status=200)


async def get_info(request):
    async def handler(request):
        avatar, username, nickname = None, None, "Недействительный токен"
        try:
            info = await bot.get_me()
            username = info["username"]
            nickname = info["first_name"]
            bot_id = info.id
            photos = await bot.get_user_profile_photos(user_id=bot_id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id
                file = await bot.get_file(file_id=file_id)
                avatar = file.file_path
        except:
            pass

        settings = fetch_data("settings", "fetchone")
        return web.json_response({
            "nickname": nickname,
            "username": username,
            "avatar": avatar,
            "token": token,
            "support": settings.get("support"),
            "website": settings.get("website"),
            "admin_id": admin_id,
            "status": "OK",
        }, status=200)

    return await handle_request(request, handler)


async def update_handler(request):
    async def handler(request):
        data = await request.json()
        if "token" in data:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            config['settings']['token'] = data["token"]
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)
        if "admin_id" in data:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            config['settings']['admin_id'] = data["admin_id"]
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)
        if "support" in data:
            update_data("settings", {"support": data["support"]})
        if "website" in data:
            update_data("settings", {"website": data["website"]})
        return web.json_response({"status": "OK"}, status=200)

    return await handle_request(request, handler)


async def statistics_handler(request):
    async def handler(request):
        user_list = []
        try:
            users = fetch_data("userlist", "fetchall")
            lang_codes = {}
            total_users = len(users)
            for user in users:
                lang_code = user["lang_code"]
                lang_codes[lang_code] = lang_codes.get(lang_code, 0) + 1

            for lang_code, count in lang_codes.items():
                percentage = round(count / total_users * 100, 2)
                if percentage >= 1:
                    user_list.append({"label": lang_code, "value": count, "percent": percentage})
                else:
                    others = next((item for item in user_list if item["label"] == "Другие"), None)
                    if others:
                        others["value"] += count
                        others["percent"] += percentage
                    else:
                        user_list.append({"label": "Другие", "value": count, "percent": percentage})
            user_list.sort(key=lambda x: x["percent"], reverse=True)
        except:
            pass

        data_traffic = fetch_data("traffic_month_stats", "fetchall") or [{"date": datetime.now().strftime("%d.%m"), "amount": 0}]
        data_profit = fetch_data("profit_month_stats", "fetchall") or [{"date": datetime.now().strftime("%d.%m"), "amount": 0}]
        stats = fetch_data("stats", "fetchone")
        data_traffic_month = stats["users_month"]
        data_traffic_general = stats["users"]
        data_profit_month = do_round(stats["profit_month"])
        data_profit_general = do_round(stats["profit"])

        return web.json_response({
            "traffic": data_traffic,
            "profit": data_profit,
            "profit_month": data_profit_month,
            "profit_general": data_profit_general,
            "traffic_month": data_traffic_month,
            "traffic_general": data_traffic_general,
            "users": user_list,
        }, status=200)

    return await handle_request(request, handler)


async def database_tables_handler(request):
    async def handler(request):
        tables = get_all_tables()
        return web.json_response(tables, status=200)

    return await handle_request(request, handler)


async def database_table_handler(request):
    async def handler(request):
        data = await request.json()
        table_data = get_table(data["table"])
        return web.json_response(table_data, status=200)

    return await handle_request(request, handler)


async def database_add_row_handler(request):
    async def handler(request):
        data = await request.json()
        row = add_new_row(data["table"])
        return web.json_response(row, status=200)

    return await handle_request(request, handler)


async def database_update_table(request):
    async def handler(request):
        data = await request.json()
        update_table(data)
        return web.json_response({"status": "OK"}, status=200)

    return await handle_request(request, handler)
