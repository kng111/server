import asyncio
import sqlite3
from aiohttp import web
from passlib.hash import pbkdf2_sha256
from datetime import datetime

async def handle(request):
    print(111)
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
        print(1)
        existing_user = cursor.fetchone()
        print(2)

        if existing_user:
            print(3)
            password_attempt = data.get('password', None)

            if not password_attempt:
                print(4)
                return web.Response(text="Password is required", status=400)

            if pbkdf2_sha256.verify(password_attempt, existing_user[2]):
                print(5)
                response_text = f"User logged in successfully, user_id: {existing_user[0]}, level: {existing_user[3]}"
                
                # Обновление данных в таблице sessions
                cursor.execute('INSERT INTO sessions (ip, user_id, time_online, is_online) VALUES (?, ?, ?, ?)',
                            (client_ip, existing_user[0], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1))
                
                if existing_user[3] == 'admin':
                    print(6)
                    pass
                    # Выполнение действий, доступных только админу
                    # ...
                    
                else:
                    print(7)
                    pass
                    # Действия для обычного пользователя
                    # ...
                    
            else:
                print(8)
                response_text = "Invalid password. Connection closed."

        else:
            print(9)
            password = data.get('password', None)

            if not password:
                print(10)
                return web.Response(text="Password is required", status=400)

            password_hash = pbkdf2_sha256.hash(password)
            cursor.execute('INSERT INTO users (ip, password_hash) VALUES (?, ?)', (client_ip, password_hash))

            cursor.execute('SELECT id FROM users WHERE ip = ?', (client_ip,))
            user_id_row = cursor.fetchone()
            user_id = user_id_row[0] if user_id_row else None

            # Обновление данных в таблице sessions при регистрации нового пользователя
            cursor.execute('INSERT INTO sessions (ip, user_id, time_online, is_online) VALUES (?, ?, ?, ?)',
                        (client_ip, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1))

            cursor.execute('INSERT INTO machines (ip, user_id, ram, cpu, disk_size, disk_id) VALUES (?, ?, ?, ?, ?, ?)',
                        (client_ip, user_id, ram, cpu, disk_size, disk_id))

            response_text = f"User registered successfully, user_id: {user_id}, level: new"

        conn.commit()

    except sqlite3.Error as e:
        print(11)
        conn.rollback()
        response_text = f"Error processing request: {e}"

    finally:
        print(12)
        conn.close()
    print(13)
    return web.Response(text=response_text)


async def get_all_clients(request):
    # Ваш код для получения списка всех подключенных клиентов
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "List of all clients"})

async def get_authorized_clients(request):
    # Ваш код для получения списка всех авторизованных клиентов
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "List of authorized clients"})

async def get_all_history_clients(request):
    # Ваш код для получения списка всех когда-либо подключенных клиентов
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "List of all history clients"})

async def exit_server(request):
    # Ваш код для обработки выхода клиента с сервера
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "Client exited"})

async def update_client_data(request):
    # Ваш код для обновления данных авторизованного клиента
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "Client data updated"})

async def get_all_disks(request):
    # Ваш код для получения списка всех жестких дисков
    # Этот метод должен вернуть ответ в формате JSON
    return web.json_response({"message": "List of all disks"})

async def helps(request):
    user_id = request.query.get('user_id', None)

    if not user_id:
        return web.Response(text="User ID parameter is required", status=400)

    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT level FROM users WHERE id = ?', (user_id,))
        user_level = cursor.fetchone()

        if user_level and user_level[0] == 'admin':
            response_text = ":client_command: MY_\n:admin_command: UPDATE_RAM"
        else:
            response_text = ":\nMY_"

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

# import websockets
# async def ws_handler(request):
#     user_ip = request.query.get('ip', None)

#     if not user_ip:
#         return web.Response(text="IP parameter is required", status=400)

#     ws = web.WebSocketResponse()
#     await ws.prepare(request)

#     while True:
#         try:
#             conn = sqlite3.connect('example.db')
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM machines WHERE ip = ?', (user_ip,))
#             machine_info = cursor.fetchone()
#             conn.close()

#             if not machine_info:
#                 await ws.send_str(f"No information found for IP: {user_ip}")
#             else:
#                 response_text = f"Machine Info for IP: {user_ip}\n" \
#                                 f"RAM: {machine_info[3]}\n" \
#                                 f"CPU: {machine_info[4]}\n" \
#                                 f"Disk Size: {machine_info[5]}\n" \
#                                 f"Disk ID: {machine_info[6]}"
#                 await ws.send_str(response_text)

#             await asyncio.sleep(5)

#         except web.WebSocketError:
#             # Если возникает ошибка WebSocketError, это может означать разрыв соединения
#             print(f"WebSocket connection error for IP: {user_ip}")
#             break

#     return ws



async def get_all_clients(request):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM machines')
        all_clients = cursor.fetchall()

        response_text = "All Connected Clients:\n"
        for client in all_clients:
            response_text += f"Client ID: {client[0]}, IP: {client[1]}, RAM: {client[3]}, CPU: {client[4]}, Disk Size: {client[5]}, Disk ID: {client[6]}\n"

    except sqlite3.Error as e:
        response_text = f"Error retrieving clients: {e}"
    finally:
        conn.close()

    return web.Response(text=response_text)

async def get_authorized_clients(request):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM machines WHERE user_id IS NOT NULL')
        authorized_clients = cursor.fetchall()

        response_text = "Authorized Clients:\n"
        for client in authorized_clients:
            response_text += f"Client ID: {client[0]}, IP: {client[1]}, RAM: {client[3]}, CPU: {client[4]}, Disk Size: {client[5]}, Disk ID: {client[6]}\n"

    except sqlite3.Error as e:
        response_text = f"Error retrieving authorized clients: {e}"
    finally:
        conn.close()

    return web.Response(text=response_text)

async def get_all_history_clients(request):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM machines')
        history_clients = cursor.fetchall()

        response_text = "All History Clients:\n"
        for client in history_clients:
            response_text += f"Client ID: {client[0]}, IP: {client[1]}, RAM: {client[3]}, CPU: {client[4]}, Disk Size: {client[5]}, Disk ID: {client[6]}\n"

    except sqlite3.Error as e:
        response_text = f"Error retrieving history clients: {e}"
    finally:
        conn.close()

    return web.Response(text=response_text)

async def update_client_data(request):
    user_ip = request.query.get('ip', None)
    new_ram = request.query.get('new_ram', None)

    if not user_ip or not new_ram:
        return web.Response(text="IP and new RAM parameters are required", status=400)

    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE machines SET ram = ? WHERE ip = ?', (new_ram, user_ip))
        conn.commit()
        response_text = f"Client data updated successfully for IP: {user_ip}"

    except sqlite3.Error as e:
        conn.rollback()
        response_text = f"Error updating client data: {e}"
    finally:
        conn.close()

    return web.Response(text=response_text)



async def get_all_disks(request):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM disks')
        all_disks = cursor.fetchall()

        response_text = "All Disks:\n"
        for disk in all_disks:
            response_text += f"Disk ID: {disk[0]}, Disk Size: {disk[1]}, Disk Type: {disk[2]}, Client ID: {disk[3]}\n"

    except sqlite3.Error as e:
        response_text = f"Error retrieving disks: {e}"
    finally:
        conn.close()

    return web.Response(text=response_text)




async def exit_server(request):
    # Любая логика, которая должна выполняться при выходе с сервера
    return web.Response(text="Server Exiting")


async def update_user_status_on_exit(request):
    user_id = request.query.get('user_id', None)

    if not user_id:
        return web.Response(text="User ID parameter is required", status=400)

    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE sessions SET is_online=?, time_online=? WHERE user_id=?',
                       (0, datetime.now(), user_id))
        conn.commit()
        return web.Response(text=f"User with ID {user_id} has exited the server")

    except sqlite3.Error as e:
        conn.rollback()
        return web.Response(text=f"Error updating user status on exit: {e}", status=500)

    finally:
        conn.close()




async def init_app():
    app = web.Application()
    app.router.add_get('/helps', helps)
    app.router.add_post('/', handle)
    app.router.add_get('/machine_info', get_machine_info)
    app.router.add_get('/update_ram', update_ram)
    # app.router.add_get('/ws', ws_handler)
    app.router.add_get('/get_all_clients', get_all_clients)
    app.router.add_get('/get_authorized_clients', get_authorized_clients)
    app.router.add_get('/get_all_history_clients', get_all_history_clients)
    app.router.add_get('/exit_server', exit_server)
    app.router.add_get('/update_client_data', update_client_data)
    app.router.add_get('/get_all_disks', get_all_disks)
    app.router.add_get('/update_user_status_on_exit', update_user_status_on_exit)

    return app

if __name__ == '__main__':


    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    # print(f"host='127.0.0.1', port=8080")
    web.run_app(app, host='127.0.0.1', port=8080)
