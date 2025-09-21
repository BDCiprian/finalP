from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_approved', 'trainer')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username',)
    list_editable = ('is_approved',)

admin.site.register(UserProfile, UserProfileAdmin)
