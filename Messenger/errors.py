class IncorrectDataRecivedErrors(Exception):
    """
    исключение - некорректные данные получены от сокета
    """
    def __str__(self):
        return 'Принято некорректные сообщение от удаленного клиента'


class NonDictInputError(Exception):
    """
    исключение - аргумент функции не словарь
    """
    def __str__(self):
        return 'аргумент функции должен быть словарем'


class ReqFieldMissingError(Exception):
    """
    исключение - отсутствует обязательное поле в принятом словаре
    """
    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'