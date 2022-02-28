# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе. Важно:
# решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.

list_words = ["attribute", "класс", "функция", "type"]


for list_item in list_words:
    try:
        list_item_dec=bytes(list_item, encoding='ascii',)
    except:
        print(list_item)