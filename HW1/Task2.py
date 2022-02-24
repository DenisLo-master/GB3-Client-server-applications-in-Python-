# 2. Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом,
# а не ручном режиме, с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы
# encode, decode или функцию bytes) и определить тип, содержимое и длину соответствующих переменных.


list_words = ["class", "function", "method"]

for list_item in list_words:
    list_item_bytes = 'b' + '"' + list_item + '"'
    list_item_bytes = eval(list_item_bytes)
    print(list_item_bytes, type(list_item_bytes), 'length =', len(list_item_bytes))
