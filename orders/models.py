from django.db import models

from customers.models import Customer


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # изначально не увидел readme и что серийник формируется из модели и версии
    # поэтому для поиска заказа удалил поле robot_serial и добавил model, version
    model = models.CharField(max_length=5, blank=False, null=False)
    version = models.CharField(max_length=5, blank=False, null=False)
