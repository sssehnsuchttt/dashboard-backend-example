from aiohttp import web
from bot.data.config import admin_id, web_secret_key, token, web_url
from bot.data.loader import bot
from bot.services.api_sqlite import (
    fetch_data,
    add_data
)
from bot.utils.const_functions import do_round
from bot.utils.text_strings import text
from bot.web_app.auth import verify_token
import hmac
import hashlib
import json
import asyncio
from urllib.parse import unquote
from datetime import datetime, timedelta


async def handle_request(request, handler):
    """Функция для обработки запросов с верификацией."""
    hash = request.headers.get("Authorization")
    init_data = request.headers.get("initData")
    c_str = "WebAppData"

    init_data = sorted(
        [chunk.split("=") for chunk in unquote(init_data).split("&") if not chunk.startswith("hash=")],
        key=lambda x: x[0]
    )
    init_data_str = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])
    secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data_str.encode(), hashlib.sha256)

    if hash == data_check.hexdigest():
        return await handler(request)
    else:
        return web.json_response({"error": "Invalid hash"}, status=401)


async def check_availability(request):
    async def handler(request):
        data = await request.json()
        user_id = data["userid"]
        user = "admin" if user_id == admin_id else ""
        return web.json_response({"is_available": True, "user": user}, status=200)
    
    return await handle_request(request, handler)


async def get_balance(request):
    async def handler(request):
        with open("payoutOptions.json", "r", encoding="utf-8") as f:
            payout_options = json.load(f)

        data = await request.json()
        user_id = data["userid"]
        if user_id == admin_id:
            balance = 10500.35
            return web.json_response({"balance": balance, "payout_options": payout_options}, status=200)
        return web.json_response({"error": "User Not Found"}, status=404)
    
    return await handle_request(request, handler)


async def make_payout(request):
    async def handler(request):
        data = await request.json()
        user_id = int(data["userid"])

        if user_id == admin_id:
            amount = do_round(float(data["amount"]))
            balance = 10500.35

            if amount <= balance:
                # Заглушка успешного ответа
                request_response = {
                    "status": "success",
                    "remain_balance": balance - amount,
                    "data": {
                        "payout_id": 12345,
                        "payout_status_text": "DONE"
                    }
                }
                
                remain_balance = str(request_response['remain_balance'])
                method_str = f"СБП ({data['bank']})" if data["method"] == "sbp" else data["method_name"]
                formatted_datetime = datetime.now().strftime("%d.%m.%y %H:%M")

                add_data("payouts_history", payoutid=request_response["data"]["payout_id"], amount=amount, 
                         amount_orig=do_round(float(data["amount_orig"])), 
                         commission_type=data["commission_type"], props=data["formattedProps"],
                         method=data["method"], method_str=method_str, bank=data["bank"],
                         userid=user_id, status_str=request_response["data"]["payout_status_text"], 
                         date=formatted_datetime)

                payout_msg = text("payout_message", user_id).replace("{amount}", str(amount)).replace("{balance}", remain_balance)
                await bot.send_message(user_id, payout_msg)

        return web.json_response({}, status=200)
    
    return await handle_request(request, handler)


async def stats(request):
    async def handler(request):
        data = await request.json()
        user_id = data["userid"]

        if user_id == admin_id:
            data_traffic = fetch_data("traffic_month_stats", "fetchall") or [{"date": datetime.now().strftime("%d.%m"), "amount": 0}]
            data_profit = fetch_data("profit_month_stats", "fetchall") or [{"date": datetime.now().strftime("%d.%m"), "amount": 0}]

            if len(data_traffic) < 30:
                for i in range(30 - len(data_traffic)):
                    previous_day = (datetime.strptime(data_traffic[0]["date"], "%d.%m") - timedelta(days=1)).strftime('%d.%m')
                    data_traffic.insert(0, {"date": previous_day, "amount": 0})

            if len(data_profit) < 30:
                for i in range(30 - len(data_profit)):
                    previous_day = (datetime.strptime(data_profit[0]["date"], "%d.%m") - timedelta(days=1)).strftime('%d.%m')
                    data_profit.insert(0, {"date": previous_day, "amount": 0})

            await asyncio.sleep(3)  # Симуляция загрузки данных
            stats = fetch_data("stats", "fetchone")
            return web.json_response({
                "traffic": data_traffic,
                "profit": data_profit,
                "profit_month": do_round(stats["profit_month"]),
                "profit_general": do_round(stats["profit"]),
                "traffic_month": stats["users_month"],
                "traffic_general": stats["users"]
            }, status=200)

        return web.json_response({"error": "User not found"}, status=404)
    
    return await handle_request(request, handler)


async def get_payouts_history(request):
    async def handler(request):
        data = await request.json()
        user_id = int(data["userid"])
        payouts = fetch_data("payouts_history", "fetchall", userid=user_id)[::-1][:50]
        return web.json_response(payouts, status=200)
    
    return await handle_request(request, handler)
