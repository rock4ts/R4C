import json
from typing import Dict

from django.http import HttpRequest


class RequestDataDeserializer:
    """Класс конвертации данных тела запроса в Python объект 'dict'.

    Атрибуты:
        request: HttpRequest - объект django request
    """
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def _deserialize_body_data(self) -> Dict[str, str]:
        """
        Преобразует данные тела запроса в Python dict.
        """
        return json.loads(self.request.body.decode('utf-8'))

    def extract_data(self) -> Dict[str, str]:
        """
        Публичный эндпоинт, отдающий преобразованные данные запроса.
        """
        return self._deserialize_body_data()


def deserialize_request_body(request: HttpRequest) -> Dict[str, str]:
    """
    Инициализирует класс конвертации данных тела запроса
    и возвращает их в виде Python объекта 'dict'.

    Аргументы:
        request: HttpRequest - объект django request
    """
    try:
        return RequestDataDeserializer(request).extract_data()
    except Exception as error:
        print("Ошибка конвертации данных запроса:", error)
