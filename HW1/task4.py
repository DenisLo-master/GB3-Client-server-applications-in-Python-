# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
# байтовое и выполнить обратное преобразование (используя методы encode и decode).


list_words = ["разработка", "администрирование", "protocol", "standard"]
list_words_enc=[]


for list_item in list_words:
    list_item_enc = list_item.encode(encoding="utf-8")
    list_words_enc.append(list_item_enc)
    print(list_item_enc)

print("_"*20,"\n","Декодирование: ","\n")

for list_item in list_words_enc:
    list_item_dec = list_item.decode(encoding="utf-8")
    print(list_item_dec)