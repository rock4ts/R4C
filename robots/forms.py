from django.forms import ModelForm

from .models import Robot


class RobotForm(ModelForm):

    class Meta:
        model = Robot
        fields = ('model', 'version', 'created')
