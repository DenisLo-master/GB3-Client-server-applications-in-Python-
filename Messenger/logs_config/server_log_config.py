"""Конфигурация логгера на сервере"""

import logging
import os.path
import sys
from logging import handlers
sys.path.append('../')
from common.variables import LOGGING_REGISTRAR_LEVEL, STREAM_LOGGING_LEVEL, FILE_LOGGING_LEVEL


# формировщик логов (dormatter)
SERVER_FORMATTER = logging.Formatter('%(asctime)-26s %(levelname)-10s %(filename)-23s %(message)s')

# подготовка файла для сбора логов
print('__file__-', __file__)
PATH = os.path.dirname(os.path.abspath(__file__))
print('print(PATH)-', PATH)
MODULE_NAME = (str(PATH).split('/')[-1:][0])
print('MODULE_NAME-', MODULE_NAME)
LOG_DIR_NAME = MODULE_NAME + '_logs'
print('LOG_DIR_NAME-', LOG_DIR_NAME)
FILE_NAME = MODULE_NAME + '.log'
print('FILE_NAME-', FILE_NAME)
if not os.path.exists(LOG_DIR_NAME):
    os.mkdir(LOG_DIR_NAME)


PATH = os.path.join(PATH, LOG_DIR_NAME)
PATH = os.path.join(PATH, FILE_NAME)
print(PATH)

#потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(STREAM_LOGGING_LEVEL)

LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='s')
LOG_FILE.setFormatter(SERVER_FORMATTER)
LOG_FILE.setLevel(FILE_LOGGING_LEVEL)

#регистратор

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_REGISTRAR_LEVEL)

#отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.warning('Предупреждения')
    LOGGER.info('Информационное сообщение')