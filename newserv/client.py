import aiohttp
import asyncio
import os
import psutil
import platform
import socket

async def get_disk_serial():
    try:
        disk_info = os.stat(os.getcwd())
        serial_number = hex(hash(disk_info.st_dev))[2:]
        return serial_number
    except Exception as e:
        print(f"Error getting disk serial number: {e}")
        return None

async def get_client_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        client_ip = s.getsockname()[0]
        s.close()
        return client_ip
    except Exception as e:
        print(f"Error getting client IP address: {e}")
        return None







async def register_user(session, password,url_serv):
    ram = psutil.virtual_memory().total
    cpu_model = platform.processor()
    disk_size = psutil.disk_usage('/').total
    disk_id = await get_disk_serial()
    disk_id = str(disk_id) if disk_id is not None else None

    client_ip = await get_client_ip()
    # url_serv = '127.0.0.1:8080'
    url = f'http://{url_serv}/'
    data = {
        'password': password,
        'ram': ram,
        'cpu': cpu_model,
        'disk_size': disk_size,
        'disk_id': disk_id,
        'ip': client_ip if client_ip is not None else "unknown"
    }
    
    async with session.post(url, json=data) as response:
        return await response.text()

async def get_machine_info(session, user_id, url_serv):
    async with session.get(f'http://{url_serv}/machine_info?ip={user_id}') as response:
        return await response.text()

async def update_ram(session, user_id, new_ram, url_serv):
    url = f'http://{url_serv}/update_ram?user_id={user_id}&ram={new_ram}'
    async with session.get(url) as response:
        return await response.text()


async def helps(session, user_id, url_serv):
    url = f'http://{url_serv}/helps?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()


async def extract_user_info(response):
    parts = response.split(',')
    
    # Проверка на наличие разделителя ":"
    if len(parts) < 2 or ':' not in parts[1]:
        print("Invalid response format.")
        return None, None
    
    user_id = parts[1].split(':')[1].strip()
    
    # Проверка на наличие второго разделителя ":"
    if len(parts) < 3 or ':' not in parts[2]:
        print("Invalid response format.")
        return None, None

    user_level = parts[2].split(':')[1].strip()
    return user_id, user_level


# async def update_user_status_on_exit(session, user_id, url_serv):
#     url = f'http://{url_serv}/update_user_status_on_exit?user_id={user_id}'
#     async with session.get(url) as response:
#         return await response.text()



async def update_user_status_on_exit(user_id, url_serv):
    url = f'http://{url_serv}/update_user_status_on_exit?user_id={user_id}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                return await response.text()
        except  aiohttp.ClientConnectorError as e:
            print(f"An error occurred during exit_server: {e}")

async def update_client_data(session, user_id, url_serv):
    url = f'http://{url_serv}/update_client_data?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()

# Добавьте аналогичные методы для других действий

# В вашем цикле main добавьте соответствующие ветвления для новых действий
async def get_all_history_clients(session, user_id, url_serv):
    url = f'http://{url_serv}/get_all_history_clients?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()



async def update_client_data(session, user_id, url_serv):
    url = f'http://{url_serv}/update_client_data?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()

async def main():
    url_serv = '127.0.0.1:8080'

    password = input("Enter password: ")

    async with aiohttp.ClientSession() as session:
            response = await register_user(session, password, url_serv)
            print(f"Server Response: {response}")

            user_id, user_level = await extract_user_info(response)

            while True:
                action = input("Enter 'q' to quit: ")

                if action.lower() == 'q':
                    break

                elif action.lower() == 'my_':
                    machine_info = await get_machine_info(session, user_id,url_serv)
                    print(f"\nMachine Info:\n{machine_info}\n")

                elif action.lower() == 'update_ram':
                    if user_level == 'admin':
                        # Поменять сделаать так что бы только инт можно было
                        new_ram = int(input("Enter new RAM size: "))
                        response = await update_ram(session, user_id, new_ram,url_serv)
                        print(f"Server Response: {response}")
                    else:
                        print("y dont admin")

                elif action.lower() == 'helps':
                    help_response = await helps(session, user_id, url_serv)
                    print(f"\nHelp Response:\n{help_response}\n")
                elif action.lower() == 'all_h':
                    all_history = await get_all_history_clients(session, user_id, url_serv)
                    print(f'All_history:{all_history}')

            

    return(user_id, url_serv)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    user_id, url_serv =(asyncio.run(main()))
    asyncio.run(update_user_status_on_exit(user_id, url_serv))
