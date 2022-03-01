# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах. Написать
# скрипт, автоматизирующий его заполнение данными. Для этого: Создать функцию write_order_to_json(),
# в которую передается 5 параметров — товар (item), количество (quantity), цена (price), покупатель (buyer),
# дата (date). Функция должна предусматривать запись данных в виде словаря в файл orders.json. При записи данных
# указать величину отступа в 4 пробельных символа; Проверить работу программы через вызов функции
# write_order_to_json() с передачей в нее значений каждого параметра.


import json
from pprint import pprint


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', encoding='utf-8') as j_file:
        orders_data = json.load(j_file)

    with open('orders.json', 'w', encoding='utf-8') as j_file:
        item_data = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date}
        orders_data['orders'].append(item_data)
        to_json = json.dumps(orders_data, sort_keys=False, indent=4, ensure_ascii=False)
        j_file.write(to_json)
    return


write_order_to_json('Видеокарта GT1050', 15, 16500, 'ООО "Интер"', '25.01.2022')
write_order_to_json('Монитор Dell', 3, 24000, 'ИП "Geek"', '15.02.2022')
write_order_to_json('Клавиатура A4Tech', 38, 800, 'ООО "Сатурн"', '30.12.2021')


with open('orders.json', 'r', encoding='utf-8') as j_file:
    data = json.load(j_file)
    pprint(data)

