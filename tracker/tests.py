from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from tracker.models import Employee, Task
from tracker.serializers import BusyEmployeeSerializer, EmployeeSerializer, ImportantTaskSerializer, TaskSerializer
from tracker.services import get_current_employee, get_free_employee
from tracker.validators import NameValidator


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Иван", last_name="Иванов", patronymic="Иванович", post="Разработчик"
        )

    def test_employee_creation(self):
        self.assertEqual(self.employee.first_name, "Иван")
        self.assertEqual(self.employee.last_name, "Иванов")
        self.assertEqual(str(self.employee), "Иван Иванов Иванович")


class TaskModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Петр", last_name="Петров")
        self.task = Task.objects.create(name="Тестовая задача", term=5, status="in_progress", employee=self.employee)

    def test_task_creation(self):
        self.assertEqual(self.task.name, "Тестовая задача")
        self.assertEqual(self.task.term, 5)
        self.assertEqual(str(self.task), "Тестовая задача 5")


class EmployeeSerializerTest(TestCase):
    def setUp(self):
        self.employee_data = {
            "first_name": "Сергей",
            "last_name": "Сергеев",
            "patronymic": "Сергеевич",
            "post": "Тестировщик",
        }
        self.serializer = EmployeeSerializer(data=self.employee_data)

    def test_valid_serializer(self):
        self.assertTrue(self.serializer.is_valid())
        employee = self.serializer.save()
        self.assertEqual(employee.last_name, "Сергеев")

    def test_invalid_name_serializer(self):
        invalid_data = self.employee_data.copy()
        invalid_data["first_name"] = "сергей"  # С маленькой буквы
        serializer = EmployeeSerializer(data=invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class BusyEmployeeSerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Алексей", last_name="Алексеев")
        Task.objects.create(name="Задача 1", term=3, status="in_progress", employee=self.employee)

    def test_task_data_field(self):
        serializer = BusyEmployeeSerializer(self.employee)
        self.assertEqual(serializer.data["task_data"], ["Задача 1"])


class TaskSerializerTest(TestCase):
    def test_task_serializer(self):
        employee = Employee.objects.create(first_name="Дмитрий", last_name="Дмитриев")
        task_data = {"name": "Новая задача", "term": 7, "status": "in_progress", "employee": employee.id}
        serializer = TaskSerializer(data=task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, "Новая задача")


class ServicesTest(TestCase):
    def setUp(self):
        self.employee1 = Employee.objects.create(first_name="Елена", last_name="Еленова")
        self.employee2 = Employee.objects.create(first_name="Ольга", last_name="Ольгова")

        # Создаем задачи для employee1 (более загружен)
        for i in range(3):
            Task.objects.create(name=f"Задача {i}", term=i + 1, status="in_progress", employee=self.employee1)

        Task.objects.create(name="Легкая задача", term=1, status="in_progress", employee=self.employee2)

    def test_get_free_employee(self):
        free_employee = get_free_employee()
        self.assertEqual(free_employee.id, self.employee2.id)

    def test_get_current_employee(self):
        Task.objects.all().delete()

        parent_task = Task.objects.create(name="Родительская задача", term=10, status="in_progress", employee=None)

        for i in range(3):
            Task.objects.create(name=f"Задача {i}", term=i + 1, status="in_progress", employee=self.employee1)

        Task.objects.create(
            name="Дочерняя задача", term=5, status="in_progress", parent_task=parent_task, employee=self.employee1
        )

        current_employee = get_current_employee(parent_task)
        self.assertEqual(current_employee.id, self.employee1.id)
        self.assertEqual(Task.objects.filter(employee=self.employee1, status="in_progress").count(), 4)


class ImportantTaskSerializerTest(TestCase):
    def setUp(self):
        self.employee1 = Employee.objects.create(first_name="Анна", last_name="Аннова", patronymic="Анновна")
        self.employee2 = Employee.objects.create(first_name="Мария", last_name="Марнова", patronymic="Марновна")

        for i in range(3):
            Task.objects.create(name=f"Задача {i}", term=i + 1, status="in_progress", employee=self.employee1)

        Task.objects.create(name="Легкая задача", term=1, status="in_progress", employee=self.employee2)

        self.parent_task = Task.objects.create(name="Важная задача", term=10, status="in_progress", parent_task=None)

        self.child_task = Task.objects.create(
            name="Подзадача", term=5, status="in_progress", parent_task=self.parent_task, employee=self.employee1
        )

    def test_available_employee(self):
        serializer = ImportantTaskSerializer(self.parent_task)
        available_employee = serializer.data["available_employee"]

        self.assertIn("Марнова", available_employee)

        self.assertEqual(available_employee, "Марнова Мария Марновна")


class NameValidatorTest(TestCase):
    def setUp(self):
        self.validator = NameValidator(field=["first_name", "last_name"])

    def test_valid_names(self):
        valid_data = {"first_name": "Александр", "last_name": "Александров"}
        self.validator(valid_data)

    def test_invalid_names(self):
        invalid_data = {"first_name": "александр", "last_name": "Александров"}
        with self.assertRaises(ValidationError):
            self.validator(invalid_data)


class EmployeeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee1 = Employee.objects.create(
            first_name="Иван", last_name="Иванов", patronymic="Иванович", post="Разработчик"
        )
        self.employee2 = Employee.objects.create(first_name="Петр", last_name="Петров", post="Тестировщик")
        self.valid_payload = {
            "first_name": "Сергей",
            "last_name": "Сергеев",
            "patronymic": "Сергеевич",
            "post": "Аналитик",
        }
        self.invalid_payload = {"first_name": "сергей", "last_name": "Сергеев", "post": "Аналитик"}

    def test_get_all_employees(self):
        response = self.client.get(reverse("tracker:employee_list"))
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_employee(self):
        response = self.client.get(reverse("tracker:employee_retrieve", kwargs={"pk": self.employee1.pk}))
        employee = Employee.objects.get(pk=self.employee1.pk)
        serializer = EmployeeSerializer(employee)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_employee(self):
        response = self.client.get(reverse("tracker:employee_retrieve", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_employee(self):
        response = self.client.post(reverse("tracker:employee_create"), data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_employee(self):
        response = self.client.post(reverse("tracker:employee_create"), data=self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_update_employee(self):
        response = self.client.put(
            reverse("tracker:employee_update", kwargs={"pk": self.employee1.pk}), data=self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_employee(self):
        response = self.client.put(
            reverse("tracker:employee_update", kwargs={"pk": self.employee1.pk}),
            data=self.invalid_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_employee(self):
        response = self.client.delete(reverse("tracker:employee_destroy", kwargs={"pk": self.employee1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaskAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(first_name="Алексей", last_name="Алексеев", post="Менеджер")
        self.task1 = Task.objects.create(name="Тестовая задача 1", term=5, status="in_progress", employee=self.employee)
        self.task2 = Task.objects.create(name="Тестовая задача 2", term=3, status="completed")
        self.valid_payload = {"name": "Новая задача", "term": 7, "status": "in_progress", "employee": self.employee.pk}
        self.invalid_payload = {"name": "", "term": 7, "status": "invalid_status", "employee": self.employee.pk}

    def test_get_all_tasks(self):
        response = self.client.get(reverse("tracker:tasks_list"))
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_task(self):
        response = self.client.get(reverse("tracker:tasks_retrieve", kwargs={"pk": self.task1.pk}))
        task = Task.objects.get(pk=self.task1.pk)
        serializer = TaskSerializer(task)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_task(self):
        response = self.client.post(reverse("tracker:tasks_create"), data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_task(self):
        response = self.client.post(reverse("tracker:tasks_create"), data=self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_update_task(self):
        response = self.client.put(
            reverse("tracker:tasks_update", kwargs={"pk": self.task1.pk}), data=self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        response = self.client.delete(reverse("tracker:tasks_destroy", kwargs={"pk": self.task1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BusyEmployeeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee1 = Employee.objects.create(first_name="Иван", last_name="Иванов")
        self.employee2 = Employee.objects.create(first_name="Петр", last_name="Петров")

        for i in range(3):
            Task.objects.create(name=f"Задача {i}", term=i + 1, status="in_progress", employee=self.employee1)

        Task.objects.create(name="Задача 4", term=1, status="in_progress", employee=self.employee2)

    def test_busy_employee_list_ordering(self):
        response = self.client.get(reverse("tracker:busy_employee_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]["last_name"], "Иванов")
        self.assertEqual(len(response.data[0]["task_data"]), 3)

        self.assertEqual(response.data[1]["last_name"], "Петров")
        self.assertEqual(len(response.data[1]["task_data"]), 1)


class ImportantTasksAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee1 = Employee.objects.create(first_name="Анна", last_name="Аннова", patronymic="Анновна")
        self.employee2 = Employee.objects.create(first_name="Мария", last_name="Марнова", patronymic="Марновна")

        for i in range(3):
            Task.objects.create(name=f"Задача {i}", term=i + 1, status="in_progress", employee=self.employee1)

        Task.objects.create(name="Легкая задача", term=1, status="in_progress", employee=self.employee2)

        self.parent_task = Task.objects.create(name="Важная задача", term=10, status="in_progress", parent_task=None)

        Task.objects.create(
            name="Подзадача", term=5, status="in_progress", parent_task=self.parent_task, employee=self.employee1
        )

    def test_important_tasks_list(self):
        response = self.client.get(reverse("tracker:important_tasks"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        important_task_names = [task["name"] for task in response.data]
        self.assertIn("Важная задача", important_task_names)

        important_task = next(task for task in response.data if task["name"] == "Важная задача")

        self.assertIn("Марнова", important_task["available_employee"])
