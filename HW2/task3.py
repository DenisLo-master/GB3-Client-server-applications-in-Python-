# 3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
# YAML-формата. Для этого: Подготовить данные для записи в виде словаря, в котором первому ключу соответствует
# список, второму — целое число, третьему — вложенный словарь, где значение каждого ключа — это целое число с
# юникод-символом, отсутствующим в кодировке ASCII (например, €); Реализовать сохранение данных в файл формата YAML —
# например, в файл file.yaml. При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
# а также установить возможность работы с юникодом: allow_unicode = True; Реализовать считывание данных из созданного
# файла и проверить, совпадают ли они с исходными.


import yaml

with open('file.yaml', 'w', encoding=' utf-8') as f_n:
    LIST_VALUE = [1, 2, 3, 4, 5]
    VALUE = 5456
    CURRENCY_SYMBOLS = {'euro': '€', 'pound': '£', 'ruble': '₽'}
    DATA_TO_YAML = {'list_value': LIST_VALUE, 'value': VALUE, 'currency_symbol': CURRENCY_SYMBOLS}
    yaml.dump(DATA_TO_YAML, f_n, default_flow_style=False, sort_keys=False, allow_unicode=True)


with open('file.yaml', encoding=' utf-8') as f_n:
    content = yaml.load(f_n, Loader=yaml.FullLoader)
    print(content)