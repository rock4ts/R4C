import os
from collections import OrderedDict
from dataclasses import fields
from pathlib import Path
from typing import Iterable, List

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from R4C.settings import WEEKLY_PRODUCTION_REPORTS
from services.datetime import DateTimeIndexes

from .data_handlers import RobotInfo, RobotWeeeklyProduction


class RobotWeeklyProductionReport:
    """
    Класс создания excel отчёта о роботах, произведённых за прошедшую неделю.
    """

    display_fields = OrderedDict(
        [
            ('model', 'Модель'),
            ('version', 'Версия'),
            ('produced_amount', 'Произведено за неделю')
        ]
    )

    @property
    def report_file_name(self) -> str:
        """Возвращает имя файла отчёта."""
        datetime_indexes = DateTimeIndexes()
        return (
            f"{datetime_indexes.previous_week_start.day}"
            f".{datetime_indexes.previous_week_end.month}"
            f"-{datetime_indexes.previous_week_end.day}"
            f".{datetime_indexes.previous_week_end.month}.xlsx"
        )

    @property
    def report_file_path(self) -> str:
        """Возвращает путь к файлу отчёта."""
        return os.path.join(
            WEEKLY_PRODUCTION_REPORTS, self.report_file_name
        )

    def _get_robot_data(self) -> Iterable[List[RobotInfo]]:
        """
        Возвращает генератор списков RobotInfo для каждой модели робота,
        произведённого за прошлую неделю.
        """
        robot_data_service = RobotWeeeklyProduction()
        return robot_data_service.robot_weekly_production_data()

    def _create_workbook(self) -> Workbook:
        """
        Создаёт excel файл по указанному в настройках проекта адресу,
        и возвращает экземпляр класса Workbook для создания таблиц и записи данных.
        """
        return Workbook(self.report_file_path)

    def _add_header_to_worksheet(self, worksheet: Worksheet) -> None:
        """
        Добавляет названия заголовков таблицы.

        Атрибуты:
            worksheet: Worksheet - объект таблицы для записи данных
        """
        row_index = 0
        field_names = RobotWeeklyProductionReport.display_fields.values()
        for col_index, field_name in enumerate(field_names):
            worksheet.write(row_index, col_index, field_name)

    def _get_worksheet_name(
            self,
            robot_data_object: RobotInfo) -> str:
        """
        Возвращает название таблицы, аналогичное названию модели робота.

        Атрибуты:
            robot_data_object: RobotInfo - объект RobotInfo,
                                            хранящий данные о роботе
        """
        return robot_data_object.model

    def _add_robot_data_to_worksheet(
            self,
            worksheet: Worksheet,
            row_index: int,
            robot_data_object: RobotInfo) -> None:
        """
        Добавляет данные о роботе в excel таблицу.

        Атрибуты:
            worksheet: Worksheet -  объект таблицы для записи данных
            row_index: int - индекс строки в таблице для записи данных о роботе
            robot_data_object: RobotInfo - объект RobotInfo,
                                            хранящий данные о роботе
        """
        for col_index, field in enumerate(fields(robot_data_object)):
            field_name = field.name
            field_value = getattr(robot_data_object, field_name)
            worksheet.write(row_index, col_index, field_value)

    def _add_many_robot_data_to_new_worksheet(
            self,
            workbook: Workbook,
            robot_data_list: List[RobotInfo]) -> None:
        """
        Создаёт таблицу и сохраняет в неё данные
        о версиях робота определённой модели.

        Атрибуты:
            workbook - экземпляр класса Workbook для создания таблиц и записи данных
            robot_data_list: List[RobotInfo] - список объектов RobotInfo,
                                                хранящих данные о роботах
        """
        worksheet = workbook.add_worksheet(
            self._get_worksheet_name(robot_data_list[0])
        )
        self._add_header_to_worksheet(worksheet)
        row_index = 1
        for robot_data in robot_data_list:
            self._add_robot_data_to_worksheet(
                worksheet,
                row_index,
                robot_data
            )
            row_index += 1

    def _check_report_file_exists(self) -> bool:
        """
        Проверяет, что отчёт ранее не создавался.
        """
        return Path(self.report_file_path).is_file()

    def create_report(self) -> str:
        """
        Публичный эндпоинт, создающий excel отчёт о роботах,
        произведённых за прошедшую неделю.

        Возвращает путь к файлу отчёта.
        """
        if not self._check_report_file_exists():
            robot_data = self._get_robot_data()
            workbook = self._create_workbook()
            for robot_model_data in robot_data:
                self._add_many_robot_data_to_new_worksheet(
                    workbook, robot_model_data
                )
            workbook.close()
        return self.report_file_path


def create_weekly_report():
    """
    Инициализирует класс и запускает функцию создания отчёта,
    о произведённых за прошедшую неделю роботах.

    Возвращает путь к файлу отчёта.
    """
    try:
        return RobotWeeklyProductionReport().create_report()
    except Exception as error:
        print("Ошибка при формировании недельного отчёта:", error)
