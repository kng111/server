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

async def register_user(session, password):
    ram = psutil.virtual_memory().total
    cpu_model = platform.processor()
    disk_size = psutil.disk_usage('/').total
    disk_id = await get_disk_serial()
    disk_id = str(disk_id) if disk_id is not None else None

    client_ip = await get_client_ip()

    url = 'http://127.0.0.1:8080/'
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

async def get_machine_info(session, user_id):
    async with session.get(f'http://127.0.0.1:8080/machine_info?ip={user_id}') as response:
        return await response.text()

async def update_ram(session, user_id, new_ram):
    url = f'http://127.0.0.1:8080/update_ram?user_id={user_id}&ram={new_ram}'
    async with session.get(url) as response:
        return await response.text()


async def extract_user_info(response):
    parts = response.split(',')
    user_id = parts[1].split(':')[1].strip()
    user_level = parts[2].split(':')[1].strip()
    return user_id, user_level


async def main():
    password = input("Enter password: ")
    
    async with aiohttp.ClientSession() as session:
        response = await register_user(session, password)
        print(f"Server Response: {response}")

        user_id, user_level = await extract_user_info(response)

        while True:
            action = input("Enter 'q' to quit: ")

            if action.lower() == 'q':
                break

            elif action.lower() == 'my_':
                machine_info = await get_machine_info(session, user_id)
                print(f"\nMachine Info:\n{machine_info}\n")

            elif action.lower() == 'update_ram':
                if user_level == 'admin':
                    new_ram = input("Enter new RAM size: ")
                    response = await update_ram(session, user_id, new_ram)
                    print(f"Server Response: {response}")
                else:
                    print("y dont admin")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
