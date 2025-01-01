from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "phone", "is_active", "is_staff"]
    search_fields = ["email", "name", "phone"]
    list_filter = ["is_active", "is_staff"]

admin.site.register(User, UserAdmin)
