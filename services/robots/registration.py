from pathlib import Path
from typing import Dict

from django.forms.models import model_to_dict

from R4C import settings
from robots.models import Robot


class RobotRegistrationCommand:
    """
    Класс обработки и регистрации поступивших в запросе данных о роботе.
    """
    def __init__(
            self,
            robot_data: Dict[str, str],
            serials_file_path: str = settings.SERIAL_CODES_FILE_PATH) -> None:
        self.errors = dict()
        self.robot_data = robot_data
        self.serials_file_path = serials_file_path

    def _check_serials_file_exists(self) -> bool:
        """
        Проверяет наличие файла с серийными номерами для роботов.
        """
        file_exists = Path(self.serials_file_path).is_file()
        if not file_exists:
            self.errors.update(
                {
                    'serial_file':
                    "Не удалось зарегистрировать робота, "
                    "так как не найден файл с серийными номерами."
                }
            )
        return file_exists

    def _get_serial_code_value(self) -> str:
        """
        Берёт и удаляет из файла серийный номер, а затем возвращает его.
        """
        if not self._check_serials_file_exists():
            return
        with open(settings.SERIAL_CODES_FILE_PATH, 'r') as file:
            serials_list = file.read().split(' ')
        with open(settings.SERIAL_CODES_FILE_PATH, 'w') as file:
            file.write(' '.join(serials_list[1:]))
        return serials_list[0]

    def _add_serial_to_robot_registration_data(self) -> Dict[str, str]:
        """
        Добавляет серийный номер в словарь с данными произведённого робота
        """
        self.robot_data.update({'serial': self._get_serial_code_value()})

    def _add_robot_to_database(
            self,
            robot_registration_data: Dict[str, str]) -> Robot:
        """
        Регистрирует робота в базе данных и возвращает его объект.

        Атрибуты:
            robot_registration_data: Dict[str, str] - словарь с данными о роботе
        """
        return Robot.objects.create(**robot_registration_data)

    def _errors_raised_in_data_preparation(self) -> bool:
        """
        Проверяет наличие ошибок,
        возникших при подготовки данных для регистрации робота.
        """
        return bool(self.errors)

    def is_configured(self) -> bool:
        """
        Публичный эндпоинт проверки наличия ошибок
        при подготовке данных для регистрации робота.
        """
        self._add_serial_to_robot_registration_data()
        return not self._errors_raised_in_data_preparation()

    def execute(self) -> None:
        """
        Публичный эндпоинт,
        который регистрирует робота в базе данных
        и возвращает его данные в виде словаря.
        """
        new_robot = self._add_robot_to_database(self.robot_data)
        return model_to_dict(new_robot)
