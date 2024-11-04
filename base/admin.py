from django.contrib import admin


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined', 'avi', "user_type",  'is_demo', 'points')
    list_filter = ('email', 'username', 'is_staff', 'is_active', "user_type",  'is_demo', 'points')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ( 'date_joined', 'avi', 'contact_number', "user_type",'location','is_demo',"area", "community", 'points')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active','is_staff', 'is_demo' ,'is_superuser', "user_type", 'points','user_permissions', 'bio', 'avi', 'auth_provider', 'contact_number', 'location'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('date_joined',)  # Make date_joined non-editable

# Register the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Community)
admin.site.register(Trash)
admin.site.register(AdminArea)
admin.site.register(Point)
admin.site.register(Report)
admin.site.register(IndividualLeaderboard)
admin.site.register(CommunityLeaderboard)
admin.site.register(Questionnaire)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Notice)

admin.site.register(Comment)
admin.site.register(Response)
admin.site.register(ResponseBlock)
admin.site.register(Insights)
admin.site.register(CommunityBlackList)


admin.site.register(Organization)













