from rest_framework.serializers import ModelSerializer, SerializerMethodField

from tracker.models import Employee, Task
from tracker.services import get_current_employee, get_free_employee
from tracker.validators import NameValidator


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        validators = [NameValidator(field=["first_name", "last_name", "patronymic"])]


class BusyEmployeeSerializer(ModelSerializer):
    task_data = SerializerMethodField()

    def get_task_data(self, employee):
        return [task.name for task in Task.objects.filter(employee=employee)]

    class Meta:
        model = Employee
        fields = ("first_name", "last_name", "patronymic", "post", "task_data")


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ImportantTaskSerializer(ModelSerializer):
    available_employee = SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "name", "term", "available_employee")

    def get_available_employee(self, task):

        free_employee = get_free_employee()
        current_employee = get_current_employee(task)

        if current_employee is None:
            return f"{free_employee.last_name} {free_employee.first_name} {free_employee.patronymic}"

        if current_employee is not None and current_employee.task_count - free_employee.task_count < 2:
            return f"{current_employee.last_name} {free_employee.first_name} {free_employee.patronymic}"
        return f"{free_employee.last_name} {free_employee.first_name} {free_employee.patronymic}"
