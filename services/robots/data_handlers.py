from dataclasses import dataclass
from typing import Iterable, List

from django.db.models import Count, QuerySet

from robots.models import Robot
from services.datetime import DateTimeIndexes


@dataclass(frozen=True)
class RobotInfo:
    """
    Датакласс, содержащий информацию о роботе определённой модели и версии,
    а также о произведённом количестве таких роботов.
    """
    model: str
    version: str
    produced_amount: int


class RobotWeeeklyProduction:
    """
    Класс подготовки данных недельного отчёта о прозведённых роботах.

    Изолирует взаимодействие с Django ORM для модели Robot.

    Имеет единственный публичный эндпоинт,
    возвращающий генератор списков RobotInfo для каждой модели робота,
    произведённого за прошлую неделю.
    """

    def _fetch_last_week_robots(self) -> QuerySet:
        """
        Возвращает всех роботов, произведённых за прошлую неделю.
        """
        datetime_indexes = DateTimeIndexes()
        return Robot.objects.filter(
            created__range=[
                datetime_indexes.previous_week_start,
                datetime_indexes.previous_week_end
            ]
        )

    def _annotate_with_version_count(self, robot_qset: QuerySet) -> QuerySet:
        """
        Группирует роботов по принципу модель-версия
        и добавляет информацию о произведённом количестве.

        Атрибуты:
            robot_qset: Queryset - список роботов
        """
        return robot_qset.values('model', 'version').annotate(
            produced_amount=Count('version')
        )

    def _group_and_annotate_last_week_robots(self) -> QuerySet:
        """
        Комбинирует результат функции поиска произведённых за последнюю неделю
        роботов и функции группировки по модели и версии.
        """
        last_week_robots = self._fetch_last_week_robots()
        return self._annotate_with_version_count(last_week_robots)

    def _list_robot_models(self, robot_qset: QuerySet) -> List[str]:
        """
        Возвращает список моделей произведённых роботов.

        Атрибуты:
            robot_qset: Queryset - список роботов
        """
        return robot_qset.values_list('model', flat=True).distinct()

    def _filter_robots_by_model(self,
                                robot_qset: QuerySet,
                                robot_model: str) -> QuerySet:
        """
        Возвращает отфильтрованный по модели список роботов.

        Атрибуты:
            robot_qset: Queryset - список роботов
            robot_model: str - название модели робота
        """
        return robot_qset.filter(model=robot_model)

    def _robot_data_to_info_dataclass(self, robot: dict) -> RobotInfo:
        """
        Упаковывает необходимые для отчёта данные о роботе в объект RobotInfo.

        Атрибуты:
            robot: dict - словарь с данными о конкретном роботе
        """
        return RobotInfo(
            model=robot.get('model'),
            version=robot.get('version'),
            produced_amount=robot.get('produced_amount')
        )

    def _robots_to_list_of_info_dataclasses(self,
                                            robots_qset: QuerySet
                                            ) -> List[RobotInfo]:
        """
        Преобразует Django Queryset, содержащий список роботов,
        в список объектов RobotInfo.

        Атрибуты:
            robots_qset: Queryset - Django Queryset, содержащий список роботов
        """
        return [
            self._robot_data_to_info_dataclass(robot) for robot
            in robots_qset
        ]

    def robot_weekly_production_data(self) -> Iterable[List[RobotInfo]]:
        """
        Публичный эндпоинт,
        возвращающий генератор списков RobotInfo для каждой модели робота,
        произведённого за прошлую неделю.
        """
        all_last_week_robots = self._group_and_annotate_last_week_robots()
        last_week_robot_models = self._list_robot_models(all_last_week_robots)
        for model in last_week_robot_models:
            robots_by_model = self._filter_robots_by_model(
                all_last_week_robots, model
            )
            yield self._robots_to_list_of_info_dataclasses(robots_by_model)
