from django.db.models import Count
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView

from tracker.models import Employee, Task
from tracker.serializers import BusyEmployeeSerializer, EmployeeSerializer, ImportantTaskSerializer, TaskSerializer


class EmployeeCreateAPIView(CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class BusyEmployeeListAPIView(ListAPIView):
    serializer_class = BusyEmployeeSerializer

    def get_queryset(self):
        return Employee.objects.annotate(tasks_count=Count("task")).order_by("-tasks_count")


class EmployeeListAPIView(ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeUpdateAPIView(UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDestroyAPIView(DestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeRetrieveAPIView(RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class TaskCreateAPIView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskListAPIView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskUpdateAPIView(UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDestroyAPIView(DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskRetrieveAPIView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class ImportantTasksListAPIView(ListAPIView):
    """Поиск важных задач и доступных сотрудников."""

    serializer_class = ImportantTaskSerializer

    def get_queryset(self):
        important_task_ids = (
            Task.objects.filter(
                is_completed="in_progress",
                employee__isnull=True,
            )
            .exclude(task__isnull=True)
            .filter(
                task__is_completed="in_progress",
                task__employee__isnull=False,
            )
            .values_list("id", flat=True)
            .distinct()
        )

        return Task.objects.filter(id__in=important_task_ids)
