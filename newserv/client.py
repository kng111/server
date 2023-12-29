import aiohttp
import asyncio
import os
import psutil
import platform
import socket
from passlib.hash import pbkdf2_sha256

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





async def get_all_disks(session, user_id, url_serv):
    url = f'http://{url_serv}/get_all_disks?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()




async def update_user_status_on_exit(user_id, url_serv):
    url = f'http://{url_serv}/update_user_status_on_exit?user_id={user_id}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                return await response.text()
        except  aiohttp.ClientConnectorError as e:
            print(f"An error occurred during exit_server: {e}")



async def get_all_history_clients(session, user_id, url_serv):
    url = f'http://{url_serv}/get_all_history_clients?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()



async def update_client_data(session, user_id, url_serv):
    url = f'http://{url_serv}/update_client_data?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()


async def update_password(session, user_id, url_serv,new_password):
    url = f'http://{url_serv}/update_password?user_id={user_id}&password={new_password}'
    async with session.get(url) as response:
        return await response.text()

async def delete_user(session, user_id, url_serv,id_user):
    url = f'http://{url_serv}/delete_user?user_id={user_id}&id_user={id_user}'
    async with session.get(url) as response:
        return await response.text()


async def disk_size_all(session, user_id, url_serv):
    url = f'http://{url_serv}/disk_size_all?user_id={user_id}'
    async with session.get(url) as response:
        return await response.text()
    

async def ram_all(session, user_id, url_serv):
    url_serv = f'http://{url_serv}/ram_all?user_id={user_id}'
    async with session.get(url_serv) as response:
        return await response.text()

async def get_all_clients(session, user_id, url_serv):
    url_serv = f'http://{url_serv}/get_all_clients?user_id={user_id}'
    async with session.get(url_serv) as response:
        return await response.text()


async def get_all_users(session, user_id, url_serv):
    url_serv = f'http://{url_serv}/get_all_users?user_id={user_id}'
    async with session.get(url_serv) as response:
        return await response.text()




async def main():
    url_serv = input("Enter url server: ")
    # '127.0.0.1:8080'
    password = input("Enter password: ")

    async with aiohttp.ClientSession() as session:
            response = await register_user(session, password, url_serv)
            print(f"Server Response: {response}")

            user_id, user_level = await extract_user_info(response)

            while True:
                action = input("Enter 'q' to quit: ")

                if action.lower() == 'q':
                    break

                elif action.lower() == 'my':
                    machine_info = await get_machine_info(session, user_id,url_serv)
                    print(f"\nMachine Info:\n{machine_info}\n")

                elif action.lower() == 'update_ram':
                    if user_level == 'admin':
                        # Поменять, сделаать так что бы только инт можно было
                        new_ram = int(input("Enter new RAM size: "))
                        response = await update_ram(session, user_id, new_ram,url_serv)
                        print(f"Server Response: {response}")
                    else:
                        print("y dont admin")

                elif action.lower() == 'helps':
                    help_response = await helps(session, user_id, url_serv)
                    print(f"\nHelp Response:\n{help_response}\n")
                elif action.lower() == 'all_h' :
                    if user_level == 'admin':
                        all_history = await get_all_history_clients(session, user_id, url_serv)
                        print(f'All_history:{all_history}')
                    else:
                        print("y dont admin")

                elif action.lower() == 'get_all_disks':
                    if user_level == 'admin':
                        get_all_disks_x = await get_all_disks(session, user_id, url_serv)

                        print(f"\n:{get_all_disks_x}\n")
                    else:
                        print("y dont admin")

                elif action.lower() == 'update_password':
                    new_password = input("Enter new Password: ")
                    help_response = await update_password(session, user_id, url_serv,new_password)
                    print(f"\n:{help_response}\n")

                elif action.lower() == 'delete_user':
                    if user_level == 'admin':
                        id_user = input("Enter id users: ")
                        delete_user_x = await delete_user(session, user_id, url_serv,id_user)
                        print(f"\n:{delete_user_x}\n")
                    else:
                        print("y dont admin")

                elif action.lower() == 'disk_size_all':
                    disk_size_all_x = await disk_size_all(session, user_id, url_serv)
                    print(disk_size_all_x)

                elif action.lower() == 'ram_all':
                    ram_all_x = await ram_all(session, user_id, url_serv)
                    print(f'\n{ram_all_x}\n')

                elif action.lower() == 'get_all_clients':
                    if user_level == 'admin':
                        all_client_x = await get_all_clients(session, user_id, url_serv)
                        print(f"\n:{all_client_x}\n")
                elif action.lower() == 'get_all_users':
                    if user_level == 'admin':
                        all_client_x = await get_all_users(session, user_id, url_serv)
                        print(f"\n:{all_client_x}\n")

            

    return(user_id, url_serv)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    user_id, url_serv =(asyncio.run(main()))
    asyncio.run(update_user_status_on_exit(user_id, url_serv))
