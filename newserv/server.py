import asyncio
import sqlite3
from aiohttp import web
from passlib.hash import pbkdf2_sha256

async def handle(request):
    data = await request.json()
    ram = data.get('ram', None)
    ram = round(ram / 1024 / 1024) if ram is not None else None
    cpu = data.get('cpu', None)
    disk_size = data.get('disk_size', None)
    disk_size = round(disk_size / 1024 / 1024) if disk_size is not None else None
    disk_id = data.get('disk_id', None)
    client_ip = data.get('ip', None)

    if not all([ram, cpu, disk_size, disk_id, client_ip]):
        return web.Response(text="All parameters are required", status=400)

    # Подключение к базе данных
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          ip TEXT,
                          password_hash TEXT,
                          level TEXT DEFAULT 'new')''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS machines (
                          id INTEGER PRIMARY KEY,
                          ip TEXT,
                          user_id TEXT,
                          ram TEXT,
                          cpu TEXT,
                          disk_size TEXT,
                          disk_id TEXT)''')

    try:
        cursor.execute('SELECT * FROM users WHERE ip = ?', (client_ip,))
        existing_user = cursor.fetchone()

        if existing_user:
            password_attempt = data.get('password', None)

            if not password_attempt:
                return web.Response(text="Password is required", status=400)

            if pbkdf2_sha256.verify(password_attempt, existing_user[2]):
                response_text = f"User logged in successfully, user_id: {existing_user[0]}, level: {existing_user[3]}"
                if existing_user[3] == 'admin':
                    print(':::admin ++++')
                    # Выполнение действий, доступных только админу
                    # Например, изменение данных в базе данных
                else:
                    print(':::admin -------')
            else:
                response_text = "Invalid password. Connection closed."

        else:
            password = data.get('password', None)

            if not password:
                return web.Response(text="Password is required", status=400)

            password_hash = pbkdf2_sha256.hash(password)
            cursor.execute('INSERT INTO users (ip, password_hash) VALUES (?, ?)', (client_ip, password_hash))

            cursor.execute('SELECT id FROM users WHERE ip = ?', (client_ip,))
            user_id_row = cursor.fetchone()
            user_id = user_id_row[0] if user_id_row else None

            cursor.execute('INSERT INTO machines (ip, user_id, ram, cpu, disk_size, disk_id) VALUES (?, ?, ?, ?, ?, ?)',
                           (client_ip, user_id, ram, cpu, disk_size, disk_id))

            response_text = f"User registered successfully, user_id: {user_id}, level: new"

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        response_text = f"Error processing request: {e}"

    finally:
        conn.close()

    return web.Response(text=response_text)

async def get_machine_info(request):
    user_ip = request.query.get('ip', None)

    if not user_ip:
        return web.Response(text="IP parameter is required", status=400)

    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM machines WHERE user_id = ?', (user_ip,))
        machine_info = cursor.fetchone()

        if not machine_info:
            return web.Response(text=f"No information found for IP: {user_ip}", status=404)

        response_text = f"Machine Info for IP: {user_ip}\n" \
                        f"RAM: {machine_info[3]}\n" \
                        f"CPU: {machine_info[4]}\n" \
                        f"Disk Size: {machine_info[5]}\n" \
                        f"Disk ID: {machine_info[6]}"

        return web.Response(text=response_text)

    except sqlite3.Error as e:
        return web.Response(text=f"Error retrieving machine info: {e}", status=500)

    finally:
        conn.close()

async def update_ram(request):
    user_id = request.query.get('user_id', None)
    new_ram = request.query.get('ram', None)

    if not all([user_id, new_ram]):
        return web.Response(text="Both user_id and ram parameters are required", status=400)

    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT level FROM users WHERE id = ?', (user_id,))
        user_level = cursor.fetchone()

        if user_level and user_level[0] == 'admin':
            # new_ram = input("Enter new RAM size: ")
            cursor.execute('UPDATE machines SET ram = ? WHERE user_id = ?', (new_ram, user_id))
            conn.commit()
            response_text = f"RAM updated successfully for user_id: {user_id}"
        else:
            response_text = "Permission denied. Only admin users can update RAM."

    except sqlite3.Error as e:
        conn.rollback()
        response_text = f"Error processing request: {e}"

    finally:
        conn.close()

    return web.Response(text=response_text)

async def ws_handler(request):
    user_ip = request.query.get('ip', None)

    if not user_ip:
        return web.Response(text="IP parameter is required", status=400)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    while True:
        try:
            conn = sqlite3.connect('example.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM machines WHERE ip = ?', (user_ip,))
            machine_info = cursor.fetchone()
            conn.close()

            if not machine_info:
                await ws.send_str(f"No information found for IP: {user_ip}")
            else:
                response_text = f"Machine Info for IP: {user_ip}\n" \
                                f"RAM: {machine_info[3]}\n" \
                                f"CPU: {machine_info[4]}\n" \
                                f"Disk Size: {machine_info[5]}\n" \
                                f"Disk ID: {machine_info[6]}"
                await ws.send_str(response_text)

            await asyncio.sleep(5)

        except web.WebSocketError:
            break

    return ws

async def init_app():
    app = web.Application()
    app.router.add_post('/', handle)
    app.router.add_get('/machine_info', get_machine_info)
    app.router.add_get('/update_ram', update_ram)
    app.router.add_get('/ws', ws_handler)
    return app

if __name__ == '__main__':
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          ip TEXT,
                          password_hash TEXT,
                          level TEXT DEFAULT 'new')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS machines (
                          id INTEGER PRIMARY KEY,
                          ip TEXT,
                          user_id TEXT,
                          ram TEXT,
                          cpu TEXT,
                          disk_size TEXT,
                          disk_id TEXT)''')
    conn.commit()
    conn.close()

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='127.0.0.1', port=8080)
