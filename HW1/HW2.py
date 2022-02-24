# 2. Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо в автоматическом,
# а не ручном режиме, с помощью добавления литеры b к текстовому значению, (т.е. ни в коем случае не используя методы
# encode, decode или функцию bytes) и определить тип, содержимое и длину соответствующих переменных.

listWords = ["class", "function", "method"]

for listItem in listWords:
    listItemBytes = 'b' + '"' + listItem + '"'
    listItemBytes = eval(listItemBytes)
    print(listItemBytes, type(listItemBytes), 'length =', len(listItemBytes))
