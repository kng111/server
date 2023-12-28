# import sqlite3
# def get_all_clients():
#     conn = sqlite3.connect('example.db')
#     cursor = conn.cursor()

#     try:
#         cursor.execute('SELECT * FROM machines')
#         all_clients = cursor.fetchall()

#         response_text = "All Connected Clients:\n"
#         for client in all_clients:
#             response_text += f"Client ID: {client[0]}, IP: {client[1]}, RAM: {client[3]}, CPU: {client[4]}, Disk Size: {client[5]}, Disk ID: {client[6]}\n"

#     except sqlite3.Error as e:
#         response_text = f"Error retrieving clients: {e}"
#     finally:
#         conn.close()

#     return response_text

# # print(get_all_clients())

import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      ip TEXT,
                      user_id INTEGER,
                      time_online TEXT,
                      is_online INTEGER DEFAULT 0)''')
