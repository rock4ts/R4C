from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from robots.forms import RobotForm
from services.request import deserialize_request_body
from services.robots.registration import RobotRegistrationCommand


@csrf_exempt
@require_POST
def add_robot(request: HttpRequest) -> JsonResponse:
    robot_data = deserialize_request_body(request)
    form = RobotForm(robot_data)
    if not form.is_valid():
        return JsonResponse(form.errors)
    robot_registration_command = RobotRegistrationCommand(form.cleaned_data)
    if not robot_registration_command.is_configured():
        return JsonResponse(robot_registration_command.errors)
    new_robot = robot_registration_command.execute()
    return JsonResponse(new_robot)
