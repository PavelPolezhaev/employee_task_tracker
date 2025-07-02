from django.urls import path
from tracker.views import (EmployeeCreateAPIView, EmployeeUpdateAPIView, EmployeeDestroyAPIView,
                           EmployeeRetrieveAPIView, EmployeeListAPIView, BusyEmployeeListAPIView,
                           TaskCreateAPIView, TaskUpdateAPIView, TaskListAPIView,
                           TaskDestroyAPIView, TaskRetrieveAPIView, ImportantTasksListAPIView)

from tracker.apps import TasksConfig

app_name = TasksConfig.name

urlpatterns = [
    path("employee/create/", EmployeeCreateAPIView.as_view(), name="employee_create"),
    path("employee/", EmployeeListAPIView.as_view(), name="employee_list"),
    path("employee/busy/", BusyEmployeeListAPIView.as_view(), name="busy_employee_list"),
    path("employee/<int:pk>/update/", EmployeeUpdateAPIView.as_view(), name="employee_update"),
    path("employee/<int:pk>/destroy/", EmployeeDestroyAPIView.as_view(), name="employee_destroy"),
    path("employee/<int:pk>/retrieve/", EmployeeRetrieveAPIView.as_view(), name="employee_retrieve"),

    path("tasks/create/", TaskCreateAPIView.as_view(), name="tasks_create"),
    path("tasks/", TaskListAPIView.as_view(), name="tasks_list"),
    path("tasks/<int:pk>/update/", TaskUpdateAPIView.as_view(), name="tasks_update"),
    path("tasks/<int:pk>/destroy/", TaskDestroyAPIView.as_view(), name="tasks_destroy"),
    path("tasks/<int:pk>/retrieve", TaskRetrieveAPIView.as_view(), name="tasks_retrieve"),
    path("tasks/important/", ImportantTasksListAPIView.as_view(), name="important_tasks"),
]
