# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на
# кириллице.

import subprocess
import platform

param = '-n' if platform.system().lower() == 'windows' else '-c'
host_list = ['yandex.ru', 'youtube.com']
result = {}

for host_item in host_list:
    args = ['ping', param, '2', host_item]
    data_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    result[host_item] = []
    for line in data_ping:
        result[host_item].append(line.decode("utf-8",'replace'))
    print(*result[host_item],'-'*20)
