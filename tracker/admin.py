from django.contrib import admin

from tracker.models import Employee, Task

# Register your models here.


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "patronymic", "post")
    search_fields = ("last_name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "employee", "term", "is_completed")
    list_filter = ("name",)
    search_fields = ("name",)
