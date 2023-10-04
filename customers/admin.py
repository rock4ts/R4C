from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('email',)
