from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from robots.forms import RobotForm
from services.orders.notification import notify_customers_about_new_robot
from services.request import deserialize_request_body
from services.robots.registration import RobotRegistrationCommand
from services.robots.report import create_weekly_report


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
    notify_customers_about_new_robot(model=new_robot.get('model'),
                                     version=new_robot.get('version'))
    return JsonResponse(new_robot)


@csrf_exempt
@require_GET
def weekly_report(request: HttpRequest) -> HttpResponse:
    report_file_path = create_weekly_report()
    with open(report_file_path, 'rb') as xlsx_file:
        response = HttpResponse(
            xlsx_file.read(),
            content_type=('application/ms-excel')
        )
        response['Content-Disposition'] = (
            f"inline; filename={report_file_path.rsplit('/')[-1]}"
        )
    return response
