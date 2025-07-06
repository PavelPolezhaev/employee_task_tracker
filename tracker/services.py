from django.db.models import Count, Q

from tracker.models import Employee, Task


def get_free_employee():
    """Находит наименее загруженного сотрудника"""

    return (
        Employee.objects.annotate(task_count=Count("task", filter=Q(task__status="in_progress")))
        .order_by("task_count")
        .first()
    )


def get_current_employee(task):
    """Получает сотрудника который работает над задачей зависимой от текущей задачи"""

    subtask = (
        Task.objects.filter(parent_task=task.id, employee__isnull=False)
        .select_related("employee")
        .annotate(employee_task_count=Count("employee__task", filter=Q(employee__task__status="in_progress")))
        .first()
    )

    if subtask:
        employee = subtask.employee
        employee.task_count = subtask.employee_task_count
        return employee
    return None
