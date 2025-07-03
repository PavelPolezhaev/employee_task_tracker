from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Employee, Task
from tracker.serializers import EmployeeSerializer, TaskSerializer


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Иван",
            last_name="Иванов",
            patronymic="Иванович",
            post="Разработчик",
        )

    def test_employee_creation(self):
        """Тестирование создания сотрудника"""
        self.assertEqual(self.employee.first_name, "Иван")
        self.assertEqual(self.employee.last_name, "Иванов")
        self.assertEqual(self.employee.patronymic, "Иванович")
        self.assertEqual(self.employee.post, "Разработчик")
        self.assertEqual(str(self.employee), "Иван Иванов Иванович")


class TaskModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Петр", last_name="Петров", post="Тестировщик")
        self.task = Task.objects.create(
            name="Написать тесты",
            employee=self.employee,
            term=5,
            is_completed="in_progress",
        )

    def test_task_creation(self):
        """Тестирование создания задачи"""
        self.assertEqual(self.task.name, "Написать тесты")
        self.assertEqual(self.task.employee, self.employee)
        self.assertEqual(self.task.term, 5)
        self.assertEqual(self.task.is_completed, "in_progress")
        self.assertEqual(str(self.task), "Написать тесты 5")


class EmployeeSerializerTest(TestCase):
    def setUp(self):
        self.employee_data = {
            "first_name": "Сергей",
            "last_name": "Сергеев",
            "patronymic": "Сергеевич",
            "post": "Менеджер",
        }

    def test_valid_serializer(self):
        """Тестирование валидного сериализатора"""
        serializer = EmployeeSerializer(data=self.employee_data)
        self.assertTrue(serializer.is_valid())
        employee = serializer.save()
        self.assertEqual(employee.first_name, "Сергей")

    def test_invalid_name_serializer(self):
        """Тестирование невалидных имен"""
        invalid_data = [
            {"first_name": "сергей", "last_name": "Сергеев"},
            {"first_name": "Сергей1", "last_name": "Сергеев"},
            {"first_name": "Сергей", "last_name": "сергеев"},
        ]

        for data in invalid_data:
            serializer = EmployeeSerializer(data={**self.employee_data, **data})
            self.assertFalse(serializer.is_valid())
            self.assertIn("должно начинаться с заглавной буквы", str(serializer.errors))


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Алексей", last_name="Алексеев", post="Аналитик")
        self.task_data = {
            "name": "Проанализировать требования",
            "employee": self.employee.id,
            "term": 3,
            "is_completed": "in_progress",
        }

    def test_valid_serializer(self):
        """Тестирование валидного сериализатора"""
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, "Проанализировать требования")


class EmployeeViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(first_name="Тест", last_name="Тестов", post="Тестер")
        self.valid_payload = {
            "first_name": "Новый",
            "last_name": "Сотрудник",
            "post": "Разработчик",
        }

    def test_create_employee(self):
        """Тестирование создания сотрудника"""
        response = self.client.post(reverse("tracker:employee_create"), data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

    def test_get_employee_list(self):
        """Тестирование получения списка сотрудников"""
        response = self.client.get(reverse("tracker:employee_list"))
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(first_name="Работник", last_name="Задачник", post="Исполнитель")
        self.task = Task.objects.create(
            name="Тестовая задача",
            employee=self.employee,
            term=1,
            is_completed="in_progress",
        )
        self.valid_payload = {
            "name": "Новая задача",
            "term": 2,
            "is_completed": "in_progress",
            "employee": self.employee.id,
        }

    def test_create_task(self):
        """Тестирование создания задачи"""
        response = self.client.post(reverse("tracker:tasks_create"), data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_get_task_list(self):
        """Тестирование получения списка задач"""
        response = self.client.get(reverse("tracker:tasks_list"))
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
