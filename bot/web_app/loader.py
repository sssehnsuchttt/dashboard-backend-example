from aiohttp import web
from bot.web_app.web_callbacks import (
    settings_handler, 
    get_info, 
    update_handler, 
    statistics_handler, 
    database_table_handler,
    database_tables_handler,
    database_add_row_handler,
    database_update_table,
    get_username

)

from bot.web_app.webapp_callbacks import (
    get_balance,
    check_availability,
    make_payout,
    get_payouts_history,
    stats
)
     
from bot.web_app.auth import auth_handler, refresh_token_handler
from bot.data.config import bot_url

middleware_exceptions = ["/payments_notification", "/payout_notification"]

async def add_cors_headers(request, handler):
    
    async def middleware(request):
        if request.path in middleware_exceptions:
                response = await handler(request)
        else:
            if request.method == "OPTIONS":
                response = web.Response()
            else:
                response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, InitData"
        return response

    return middleware

app = web.Application(middlewares=[add_cors_headers])

app.add_routes([web.post(f'/{bot_url}/settings', settings_handler)])
app.add_routes([web.get(f'/{bot_url}/info', get_info)])
app.add_routes([web.post(f'/{bot_url}/update', update_handler)])
app.add_routes([web.post(f'/{bot_url}/authorization', auth_handler)])
app.add_routes([web.post(f'/{bot_url}/refresh_token', refresh_token_handler)])
app.add_routes([web.get(f'/{bot_url}/statistics', statistics_handler)])
app.add_routes([web.get(f'/{bot_url}/tables', database_tables_handler)])
app.add_routes([web.post(f'/{bot_url}/table', database_table_handler)])
app.add_routes([web.post(f'/{bot_url}/add_row', database_add_row_handler)])
app.add_routes([web.post(f'/{bot_url}/update_table', database_update_table)])
app.add_routes([web.get(f'/{bot_url}/username', get_username)])

app.add_routes([web.post(f'/{bot_url}/webapp/check', check_availability)])
app.add_routes([web.post(f'/{bot_url}/webapp/balance', get_balance)])
app.add_routes([web.post(f'/{bot_url}/webapp/payout', make_payout)])
app.add_routes([web.post(f'/{bot_url}/webapp/payouts_history', get_payouts_history)])
app.add_routes([web.post(f'/{bot_url}/webapp/stats', stats)])