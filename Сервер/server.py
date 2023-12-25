import asyncio
import sqlite3

class Server:
    def __init__(self):
        self.clients = {}
        self.db_connection = sqlite3.connect('virtual_machines.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_machines (
                id INTEGER PRIMARY KEY,
                client_id INTEGER,
                ram INTEGER,
                cpu INTEGER,
                disk_size INTEGER,
                disk_id INTEGER,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        ''')
        self.db_connection.commit()

    def authenticate_client(self, username, password):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT id FROM clients WHERE username=? AND password=?', (username, password))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def add_client(self, username, password):
        cursor = self.db_connection.cursor()
        cursor.execute('INSERT INTO clients (username, password) VALUES (?, ?)', (username, password))
        client_id = cursor.lastrowid
        self.db_connection.commit()
        return client_id

    def add_virtual_machine(self, client_id, ram, cpu, disk_size, disk_id):
        cursor = self.db_connection.cursor()
        cursor.execute('INSERT INTO virtual_machines (client_id, ram, cpu, disk_size, disk_id) VALUES (?, ?, ?, ?, ?)',
                       (client_id, ram, cpu, disk_size, disk_id))
        self.db_connection.commit()

    def get_all_clients(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM clients')
        return cursor.fetchall()

    def get_all_virtual_machines(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM virtual_machines')
        return cursor.fetchall()


async def handle_client(reader, writer, server):
    while True:
        data = await reader.read(100)
        if not data:
            break

        message = data.decode()
        command, *args = message.split()

        if command == "AUTH":
            username, password = args
            client_id = server.authenticate_client(username, password)
            if client_id is not None:
                writer.write(f"AUTH_SUCCESS {client_id}\n".encode())
            else:
                writer.write(b"AUTH_FAIL\n")
            await writer.drain()
        elif command == "ADD_CLIENT":
            username, password = args
            client_id = server.add_client(username, password)
            writer.write(f"CLIENT_ADDED {client_id}\n".encode())
            await writer.drain()
        elif command == "GET_ALL_CLIENTS":
            clients = server.get_all_clients()
            writer.write(f"ALL_CLIENTS {clients}\n".encode())
            await writer.drain()
        elif command == "GET_ALL_VMS":
            vms = server.get_all_virtual_machines()
            writer.write(f"ALL_VMS {vms}\n".encode())
            await writer.drain()
        else:
            writer.write(b"UNKNOWN_COMMAND\n")
            await writer.drain()

    writer.close()

async def main():
    server = Server()
    server_address = ('127.0.0.1', 2000)

    async def handle_client_wrapper(reader, writer):
        await handle_client(reader, writer, server)

    server = await asyncio.start_server(handle_client_wrapper, *server_address, reuse_address=True)


    async with server:
        await server.serve_forever()

asyncio.run(main())
