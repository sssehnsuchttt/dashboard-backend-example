from aiohttp import web
from bot.data.config import web_secret_key
import bcrypt, sqlite3
import jwt
import secrets
import datetime


def verify_token(token):
    try:
        payload = jwt.decode(token, web_secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Expired token')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def generate_access_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    access_token = jwt.encode(payload, web_secret_key, algorithm='HS256')
    print(access_token)
    access_token = access_token.decode('utf-8')
    return access_token
    
def create_tokens_table():
    conn = sqlite3.connect('web_admins.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS tokens
                     (refresh_token TEXT PRIMARY KEY, user_id INTEGER)''')
    conn.commit()
    conn.close()

def generate_refresh_token(user_id):
    refresh_token = secrets.token_urlsafe(32) 
    conn = sqlite3.connect('web_admins.db')
    conn.execute("INSERT INTO tokens (refresh_token, user_id) VALUES (?, ?)", (refresh_token, user_id))
    conn.commit()
    conn.close()
    return refresh_token

def verify_refresh_token(refresh_token):
    conn = sqlite3.connect('web_admins.db')
    cursor = conn.execute("SELECT refresh_token FROM tokens WHERE refresh_token = ?", (refresh_token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def get_user_refresh_token(refresh_token):
    conn = sqlite3.connect('web_admins.db')
    cursor = conn.execute("SELECT user_id FROM tokens WHERE refresh_token = ?", (refresh_token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

create_tokens_table()

async def auth_handler(request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('web_admins.db')
    cursor = conn.execute("SELECT password FROM accounts WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        hashed_password = row[0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            user_id = username

            access_token = generate_access_token(user_id)

            refresh_token = generate_refresh_token(user_id)
            data = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            return web.json_response(data, status=200)
        else:
            return web.Response(status=404, text="Account not found")

    return web.Response(status=404, text="Account not found")


async def refresh_token_handler(request):
    data = await request.json()
    refresh_token = data.get('refresh_token')
    check_refresh_token = verify_refresh_token(refresh_token)
    user_id = get_user_refresh_token(refresh_token)
    if check_refresh_token:
        access_token = generate_access_token(user_id)
        data = {
            "access_token": access_token
        }
        return web.json_response(data, status=200)
    else:
        return web.Response(status=401, text="Invalid refresh token")