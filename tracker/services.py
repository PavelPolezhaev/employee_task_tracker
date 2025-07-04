from django.db.models import Count, Q

from tracker.models import Employee, Task


def get_free_employee():
    """Находит наименее загруженного сотрудника"""

    employees = Employee.objects.annotate(task_count=Count("task", filter=Q(task__status="in_progress")))
    min_tasks = None
    free_employee = None
    for emp in employees:
        if free_employee is None or emp.task_count < min_tasks:
            min_tasks = emp.task_count
            free_employee = emp
    return free_employee


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
        employee.task_count = subtask.employee_task_count  # Добавляем поле "на лету"
        return employee
    return None
