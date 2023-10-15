from datetime import datetime, time, timedelta


class DateTimeIndexes:
    """Класс создания пользовательских временных точек."""

    @property
    def today(self) -> datetime:
        """"Возвращает текущую дату и время."""
        return datetime.today()

    @property
    def todays_weekday(self) -> int:
        """Возвращает текущий день недели."""
        return self.today.weekday()

    @property
    def previous_week_start(self) -> datetime:
        """Возвращает начало прошлой недели в формате дата-время."""
        start_delta = timedelta(days=self.todays_weekday, weeks=1)
        return datetime.combine(self.today - start_delta, time.min)

    @property
    def previous_week_end(self) -> datetime:
        """Возвращает конец прошлой недели в формате дата-время."""
        end_delta = timedelta(days=self.todays_weekday + 1)
        return datetime.combine(self.today - end_delta, time.max)
