"""Конфигурация логгера на сервере"""

import logging
import os.path
import sys

sys.path.append('../')
from common.variables import LOGGING_HANDLER_LEVEL, LOGGING_REGISTRAR_LEVEL

# формировщик логов (dormatter)
SERVER_FORMATTER = logging.Formatter('%(asctime)-26s %(levelname)-10s %(filename)-23s %(message)s')

# подготовка файла для сбора логов
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

#потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)


LOG_FILE = logging.FileHandler.
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encodings='utf-8', interval=1, when='S')
LOG_FILE.setFormatter(SERVER_FORMATTER)

#регистратор

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
# LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_REGISTRAR_LEVEL)

#отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')