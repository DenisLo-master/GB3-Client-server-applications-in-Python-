# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из
# файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого: Создать
# функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных. В
# этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
# соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
# os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
# поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
# «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для
# каждого файла); Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать
# получение данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий
# CSV-файл; Проверить работу программы через вызов функции write_to_csv().

from chardet import detect
import re
import numpy as np
import csv

os_prod_list=[]
os_name_list=[]
os_code_list=[]
os_type_list=[]


parameter_os_list=['Изготовитель системы:', 'Название ОС:', 'Код продукта:', 'Тип системы:']
file_list = ['info_1.txt', 'info_2.txt', 'info_3.txt']

def get_data():

# Вариант 1 (пункт ДЗ, фиксированный список параметров)
#     main_data =[]
##########

# Вариант 2  (зависиит от исходного списка параметров в переменной parameter_os_list)
    main_data = [[" " for m in range(len(file_list))] for n in range(len(parameter_os_list))]
##########

    for i in range(len(file_list)):
        with open(file_list[i], 'rb') as f:
            file_content = f.read()
            encoding = detect(file_content)['encoding']

        with open(file_list[i], encoding=encoding) as f:
            file_content = f.read()


#Вариант 1 (пункт ДЗ, фиксированный список параметров)
    #     match_prod= re.search('Изготовитель\sсистемы:\s*(.*\S)(\s*\n|\n)', file_content)
    #     os_prod_list.append(match_prod[1])
    #     match_name = re.search('Название\sОС:\s*(.*\S)(\s*\n|\n)', file_content)
    #     os_name_list.append(match_name[1])
    #     match_code = re.search('Код\sпродукта:\s*(.*\S)(\s*\n|\n)', file_content)
    #     os_code_list.append(match_code[1])
    #     match_type = re.search('Тип\sсистемы:\s*(.*\S)(\s*\n|\n)', file_content)
    #     os_type_list.append(match_type[1])
    # main_data = [os_prod_list, os_name_list, os_code_list, os_type_list]
##########

# Вариант 2 (зависиит от исходного списка параметров в переменной parameter_os_list)
        for j in range(len(parameter_os_list)):
            match_regexp= f"r\'{parameter_os_list[j]}\\s*(.*\S)(\s*\\n|\\n)\'"
            match_regexp=eval(match_regexp)
            match = re.search(match_regexp, file_content)
            main_data[j][i]=match[1]

##########

    main_data = np.array(main_data)
    main_data = np.transpose(main_data)
    main_data = np.row_stack((parameter_os_list, main_data))
    return main_data.tolist()


def write_to_csv(file_link):
    with open(file_link, 'w',encoding='utf-8') as result_file:
        file_writer = csv.writer(result_file)
        data=get_data()
        for row in data:
            file_writer.writerow(row)





write_to_csv('result_data.csv')

with open('result_data.csv', 'r', encoding='utf-8') as f_n:
    f_n_reader = csv.reader(f_n)
    for row in f_n_reader:
        print(row)