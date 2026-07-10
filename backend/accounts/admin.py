from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'stage_name', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_verified', 'role')
    search_fields = ('email', 'full_name', 'stage_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'stage_name', 'bio', 'genres', 'profile_photo', 'city', 'country')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_verified'),
        }),
    )
