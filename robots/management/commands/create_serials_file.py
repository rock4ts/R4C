'''
Команда, генирирующая и сохраняющая
в txt-файл пятизначные буквенно-цифровые серийные номера,
которые присваиваются каждому произведённому роботу при занесении
о нём записи в базу данных.
'''

from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand, CommandError

from R4C import settings


class Command(BaseCommand):
    help = (
        """
        Создаёт txt файл с серийными номерами роботов
        формата латинская буква - четырёхзначное число от 0001 до 9999.
        Адрес файла определён в настройках Django проекта
        в переменной SERIAL_CODES_FILE_PATH.
        """
    )

    def _generate_serial_codes_list(self) -> List[str]:
        serials_list = list()
        for i in range(1, 10000):
            str_i = str(i).zfill(4)
            char_code = 65 + int(str_i[0])
            serials_list.append(chr(char_code) + str_i)
        return serials_list

    def handle(self, *args, **kwargs) -> None:
        serials_list = self._generate_serial_codes_list()
        file_path = settings.SERIAL_CODES_FILE_PATH
        file_exists = Path(file_path).is_file()
        if file_exists:
            raise CommandError(
                "Вы уже создавали файл с серийными кодами для роботов."
            )
        with open(file_path, 'w') as serials_file:
            for item in serials_list:
                serials_file.write(f"{item}" + ' ')
