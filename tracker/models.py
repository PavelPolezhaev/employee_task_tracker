from django.db import models

COMPLETED_STATUS_CHOICES = (
    ("completed", "Выполнена"),
    ("in_progress", "В процессе"),
)


class Employee(models.Model):
    """Модель сотрудника"""

    first_name = models.CharField(max_length=50, verbose_name="Имя сотрудника", help_text="Введите имя сотрудника")
    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия сотрудника",
        help_text="Введите фамилию сотрудника",
    )
    patronymic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Отчество сотрудника",
        help_text="Введите отчество сотрудника",
    )
    post = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Должность сотрудника",
        help_text="Введите должность сотрудника",
    )

    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"


class Task(models.Model):
    """Модель задачи"""

    name = models.CharField(max_length=100, verbose_name="Наименование задачи", help_text="Введите задачу")
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Родительская задача",
        help_text="Выберите задачу которую необходимо сделать перед выполнением этой",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Исполнитель задачи",
    )
    term = models.PositiveSmallIntegerField(
        verbose_name="Срок исполнения задачи в днях",
        help_text="Введите сроки исполнения задачи в днях",
    )
    status = models.CharField(
        choices=COMPLETED_STATUS_CHOICES,
        default="in_progress",
        verbose_name="Статус выполнения задачи",
        help_text="Выберите статус выполнения задачи",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return f"{self.name} {self.term}"
