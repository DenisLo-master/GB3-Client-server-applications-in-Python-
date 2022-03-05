from socket import socket, AF_INET, SOCK_STREAM

CLIENT_SOCK = socket(AF_INET, SOCK_STREAM)
CLIENT_SOCK.connect(('127.0.0.1', 7777))
MSG = 'Привет сервер'
CLIENT_SOCK.send(MSG.encode('utf-8'))
TIMEDATA = CLIENT_SOCK.recv(1024)
print("Время на сервере: %s" % TIMEDATA.decode('ascii'))
DATA = CLIENT_SOCK.recv(4096)
print(f"Сообщение от сервера: \"{DATA.decode('utf-8')}\" - длиной {len(DATA.decode('utf-8'))} букв")
CLIENT_SOCK.close()

