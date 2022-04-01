import keyword
import sys
import threading
import time
import argparse
import json

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message, check_port, validation_address_ipv4, \
    get_addr_port
from common.variables import ACTION, ACCOUNT_NAME, PRESENCE, RESPONSE, TIME, USER, ERROR, MESSAGE, \
    MESSAGE_TEXT, DEFAULT_PORT, DEFAULT_IP_ADDRESS, SENDER, DESTINATION, EXIT, FOR_ALL

from errors import ReqFieldMissingError, NonDictInputError, IncorrectDataRecivedErrors
from decos import log
import logging

import logs_config.client_log_config


LOGGER = logging.getLogger('client')


@log
def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос по протоколу JIM о присутсвии клиента
    : param account_name:
    :return:
    """
    LOGGER.debug(f'Подготовка сообщения для сервера от пользователя {account_name}')
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
    }
    LOGGER.debug(f'Сообщения для сервера подготовлено {message}')
    return message


@log
def create_message(account_name='Guest'):
    """
    Функция запрашивает кому отправить сообщение и текст сообщения и генерация сообщения по протоколу
    JIM для отправки на сервер.
    :param account_name:
    :return:
    """
    while True:
        to_user = input('\nВведите имя получателя сообщения или отправьте для всех (оставьте пустым):\n')
        if to_user == '':
            to_user = FOR_ALL
            LOGGER.info(f'Получатели выбраны {to_user}')
        # elif to_user in clients_name.keys():
        #     LOGGER.info(f'Получатель выбран {to_user}')
        elif to_user in ['help', 'exit', 'users']:
            return to_user
        # else:
        #     continue

        text = input(f'Введите текст сообщения для {to_user}:\n')
        if text == '':
            continue
        LOGGER.info(f'Текст сообщения получен {text}')

        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: account_name,
            DESTINATION: to_user,
            MESSAGE_TEXT: text
        }
        LOGGER.debug(f'Сообщения для сервера подготовлено {message}')
        print(message)
        return message


@log
def create_exit_message(account_name='Guest'):
    """
    Функция обрабатые ввод польователя: завершение работы  и генерация сообщения по протоколу
    JIM для отправки на сервер.
    :param account_name:
    :return:
    """
    LOGGER.debug(f'Сообщения ACTION:EXIT для сервера подготовлено')
    return {
        ACTION: EXIT,
        TIME: time.time(),
        SENDER: account_name,
    }


@log
def process_answer(message):
    """
    Функция разирает ответ сервера
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от сервера {message}')
    if isinstance(message, dict):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                LOGGER.info(f'Код:200, ОК')
                return 'Код:200, ОК'
            elif message[RESPONSE] == 400:
                LOGGER.critical(f'Код:400, {message[ERROR]}')
                return
            else:
                raise IncorrectDataRecivedErrors
        raise ReqFieldMissingError
    raise NonDictInputError


@log
def message_from_server(sock, my_username):
    """
    Функция - обработчик сообщений других пользователей, поступающих с сервера
    :param sock:
    :param my_username:
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            print('----------', message)
            send_time = time.strftime('%H:%M', time.gmtime(message[TIME]))
            if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                    and SENDER in message and DESTINATION in message \
                    and message[DESTINATION] in [my_username, FOR_ALL] \
                    and MESSAGE_TEXT in message:
                if message[DESTINATION] == my_username:
                    print(f' {send_time} личное сообщение от {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'личное сообщение от клиента: {message[SENDER]}')
                if message[DESTINATION] == FOR_ALL:
                    print(f' {send_time} публичное сообщение от {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'публичное сообщение от клиента: {message[SENDER]}')
            elif ACTION in message and message[ACTION] == EXIT and TIME in message \
                    and SENDER in message:
                LOGGER.info(f'Информация: клиент {message[SENDER]} отключился')
                print(f'{send_time} клиент {message[SENDER]} отключился')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except (IncorrectDataRecivedErrors, json.JSONDecodeError) as e:
            LOGGER.error(f'{e} Не удалось декодировать полученное сообщение')
            break
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            LOGGER.critical(f'Потеряно соединение с сервером')
            break


@log
def user_interactive(sock, username):
    """
    Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    :param sock:
    :param username:
    :return:
    """
    print_help()
    while True:
        message = create_message(username)
        print(message)
        if message not in ['help', 'exit', 'users']:
            try:
                send_message(sock, message)
                LOGGER.info(f'Сообщение от пользователя {username} отправлено')
            except Exception as e:
                print(f'Потеряно соединение с сервером. Сообщение не отправлено')
                LOGGER.critical(f'{e}, Потеряно соединение с сервером. Сообщение не отправлено')
                sock.close()
                LOGGER.info(f'Сокет закрыт {get_addr_port(sock)}')
                sys.exit(1)
        elif message == 'help':
            print_help()
        elif message == 'exit':
            try:
                send_message(sock, create_exit_message(username))
                LOGGER.info(f'Завершение соединения по команде пользователя {username}')
                time.sleep(1)
                LOGGER.info(f'Сокет закрыт {get_addr_port(sock)}')
                sock.close()
                break
            except Exception as e:
                LOGGER.critical(f'{e}, Потеряно соединение с сервером. Сообщение не отправлено')
                LOGGER.info(f'Сокет закрыт {get_addr_port(sock)}')
                sock.close()
                break

        else:
            print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды')


def print_help():
    """
    Функция выводит справку по использованию клиент приложения
    :return:
    """
    print(f'Поддерживаемые команды:\n'
          f'message - отправить сообщение. Кому и текст будет запрошены отдельно\n'
          f'help - вывести подсказки по командам\n'
          f'exit - выход из программы\n')


@log
def arg_parser():
    """
    Создаем парсер аргументов командной строки и читаем параметры
    :return server_address, server_port, client_name:
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('-p', '--port', default=DEFAULT_PORT, nargs='?')
        parser.add_argument('-n', '--name', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        arg_server_address = namespace.addr
        arg_server_port = int(namespace.port)
        client_name = namespace.name
    except Exception as e:
        print(f'{e}\nВведены некорректные параметры запуска клиента')
        LOGGER.error(f'{e} Введены некорректные параметры запуска клиента')
        sys.exit(1)

    # проверка адреса сервера
    try:
        server_address = validation_address_ipv4(arg_server_address)
        LOGGER.debug(f'Адрес сервера определен {server_address}')
    except IndexError:
        LOGGER.error('Не указан IP сервера, после параметра -a')
        sys.exit(1)
    except TypeError:
        LOGGER.error(f'IP адрес указан не правильно - {arg_server_address}')
        sys.exit(1)
    except ValueError:
        LOGGER.error(f'Указан некорректный IP адрес сервера - {arg_server_address}')
        sys.exit(1)

    # проверка номера порта
    try:
        server_port = check_port(arg_server_port)
        LOGGER.debug(f'Порт сервера определен {server_port}')
    except IndexError:
        LOGGER.error('Не указан порт сервера, после параметра -p')
        sys.exit(1)
    except ValueError:
        LOGGER.error('Указан не корректный порт')
        sys.exit(1)

    # проверка имени клиента
    if not client_name:
        client_name = input('Введите имя пользователя:\n')

    LOGGER.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}'
                f'порт: {server_port}, имя пользователя: {client_name}')
    return server_address, server_port, client_name


def main():
    LOGGER.info(f'Запуск клиента')

    server_address, server_port, client_name = arg_parser()

    try:
        # готовим сокет
        LOGGER.debug(f'Запуск сокета')
        transport = socket(AF_INET, SOCK_STREAM)
        LOGGER.debug(f'Установка параметров сокета')
        transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # подключение к серверу
        transport.connect((server_address, server_port))
        LOGGER.info(f'Подключение к серверу: {server_address}:{server_port}')
        message_to_server = create_presence(client_name)
        send_message(transport, message_to_server)
        LOGGER.debug(f'Сообщение отправлено к серверу: {server_address}:{server_port}')
        LOGGER.info(f'Ожидание ответа от сервера {server_address}:{server_port}: ')
        process_answer(get_message(transport))
    except json.JSONDecodeError:
        LOGGER.critical(f'Не удалось декодировать сообщение от сервера')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)
    except IncorrectDataRecivedErrors:
        LOGGER.critical(f'Некорректное сообщение от сервера {server_address}:{server_port}')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)
    except NonDictInputError:
        LOGGER.critical(f'сообщение от сервера {server_address}:{server_port} не является словарем')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)
    except ReqFieldMissingError:
        LOGGER.critical(f'отсутствует обязательное поле в сообщении от сервера {server_address}:{server_port}')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, ConnectionAbortedError):
        LOGGER.critical(f'Не удалось пожключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)
    except TimeoutError:
        LOGGER.critical(f'Не удалось пожключиться к серверу {server_address}:{server_port}. '
                        f'Попытка установить соединение была безуспешной, т.к. от другого компьютера за требуемое '
                        f'время не получен нужный отклик, или было разорвано уже установленное соединение из-за '
                        f'неверного отклика уже подключенного компьютера')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)

    # Если соединение с сервером установлено корректно,
    # запускаем клиентский процесс приёма сообщений
    receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
    receiver.daemon = True
    LOGGER.debug(f'Запущен сервис receiver')
    receiver.start()

    # затем запускаем процесс отправки сообщений и взаимодействие пользователя
    user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
    user_interface.daemon = True
    LOGGER.debug(f'Запущен сервис user_interface')
    user_interface.start()

    while True:
        time.sleep(1)
        if receiver.is_alive() and user_interface.is_alive():
            continue
        LOGGER.error(f'Клиент остановлен из за остановки сервисов receiver или user_interface')
        break


if __name__ == '__main__':
    main()
