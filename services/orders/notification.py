from smtplib import SMTPException
from typing import List

from django.core.mail import send_mail
from django.db.models import QuerySet

from orders.models import Order
from R4C.settings import ADMIN_EMAIL


class CustomerNotificationService:
    """
    Класс для отправки клиентам уведомления о наличии
    ранее запрошенного по заявке робота.

    Аттрибуты класса:
        model: str - модель запрошенного клиентом робота
        version: str - версия запрошенного клиентом робот
    """

    def __init__(self, model: str, version: str) -> None:
        self.model = model
        self.version = version

    def _get_orders(self) -> QuerySet:
        """
        Находит и возвращает все заявки на покупку робота
        определённой модели и версии.
        """
        return Order.objects.filter(model=self.model, version=self.version)

    def _get_customer_emails(self) -> List[str]:
        """
        Формирует список электронных адрессов клиентов,
        оставивших заявку на работа.
        """
        return self._get_orders().values_list('customer__email').distinct()

    def _parse_notification_message(self) -> str:
        """
        Подготавливает сообщение о поступление робота в наличие.
        """
        return (
            "Добрый день! \n"
            f"Недавно вы интересовались нашим роботом модели {self.model}, "
            f"версии {self.version}.\n"
            "Этот робот теперь в наличии. "
            "Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."
        )

    def notify_customers(self) -> None:
        """
        Отправляет всем клиентам, оставившим заявку,
        сообщение о поступление робота в наличие.
        """
        send_mail(
            subject='Уведомление о наличии запрошенного робота',
            message=self._parse_notification_message(),
            from_email=ADMIN_EMAIL,
            recipient_list=self._get_customer_emails(),
            fail_silently=False
        )


def notify_customers_about_new_robot(model: str, version: str) -> None:
    """
    Инициализирует класс отправки сообщения клиентам,
    заинтересованным в покупке поступившего в наличие робота,
    и вызывает функцию рассылки уведомлений.

    Аргументы:
        model: str - модель запрошенного клиентом робота
        version: str - версия запрошенного клиентом робот
    """
    try:
        CustomerNotificationService(model, version).notify_customers()
    except SMTPException as error:
        print("Ошибка отправки уведомления:", error)
