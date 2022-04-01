""" Лаунчер для тестирования"""

import subprocess

PROCESS = []

while True:
    ACTION =input('Выберите действие: q - выход, '
                  's - запустить сервер, x - закрыть окна: ')

    if ACTION == 'q':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        PROCESS.append(subprocess.Popen('python client.py -n Den', creationflags=subprocess.CREATE_NEW_CONSOLE))

        PROCESS.append(subprocess.Popen('python client.py -n Sam', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()