import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('localhost', 3030))  # Подключаемся к нашему серверу.
s.sendall('Hello, Habr!'.encode('utf-8'))  # Отправляем фразу в виде байтов.
data = s.recv(1024)  # Получаем данные из сокета.
print(data.decode('utf-8'))  # Выводим полученные данные
s.close()
