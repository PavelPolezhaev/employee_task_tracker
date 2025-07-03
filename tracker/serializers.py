from django.db.models import Count, Q
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from tracker.models import Employee, Task
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
    available_employees = SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "name", "term", "available_employees")

    def get_available_employees(self, task):
        dependent_tasks = Task.objects.filter(parent_task=task.id, is_completed="in_progress").select_related(
            "employee"
        )

        parent_employee_ids = {t.employee.id for t in dependent_tasks if t.employee}

        employees_data = Employee.objects.annotate(
            task_count=Count("task", filter=Q(task__is_completed="in_progress"))
        ).values("id", "first_name", "last_name", "task_count")

        if not employees_data:
            return []

        min_tasks = min(emp["task_count"] for emp in employees_data)

        employees_dict = {emp["id"]: emp for emp in employees_data}

        least_loaded = [emp for emp in employees_data if emp["task_count"] == min_tasks]

        parent_candidates = [
            employees_dict[emp_id]
            for emp_id in parent_employee_ids
            if emp_id in employees_dict and employees_dict[emp_id]["task_count"] <= min_tasks + 2
        ]

        all_candidates = {emp["id"]: emp for emp in least_loaded + parent_candidates}

        return [f"{emp['last_name']} {emp['first_name']}" for emp in all_candidates.values()]
