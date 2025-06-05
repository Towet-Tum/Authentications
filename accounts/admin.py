from django.contrib import admin

from accounts.models import Book, User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "role",
    ]
    search_fields = ["username", "role", "email"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "name"]
