from django.urls import path

from . import views

app_name = 'robots'

urlpatterns = [
    path('add/', views.add_robot, name='add'),
    path('weekly_report/', views.weekly_report, name='weekly_report')
]
