import inspect
import sys
import logging
import logs_config.server_log_config
import logs_config.client_log_config


def log(func_to_log):
    """Функция декоратор"""

    def log_saver(*args, **kwargs):
        logger_name = 'server' if 'server.py' in sys.argv[0] else 'client'
        LOGGER = logging.getLogger(logger_name)

        ret = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Функция {func_to_log.__name__}  вызвана из функции {inspect.currentframe().f_back.f_code.co_name}')
        if args != ():
            LOGGER.debug(f'функция {func_to_log.__name__} была вызвана с параметрами {args}')
        elif kwargs != {}:
            LOGGER.debug(f'функция {func_to_log.__name__}  была вызвана с параметрами {kwargs}')
        elif args != () and kwargs != {}:
            LOGGER.debug(f'функция {func_to_log.__name__}  была вызвана с параметрами {args}, {kwargs}')
        else:
            LOGGER.debug(f'функция {func_to_log.__name__} без параметров')
        return ret
    return log_saver