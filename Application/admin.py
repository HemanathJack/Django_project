from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUser(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  
        (                      
            'Team Information',  
            {
                'fields': (
                    'designation',
                    'team',
                    'department',
                    'date_of_birth',
                    'is_admin',
                    'is_user',
                    'is_manager'
                ),
            },
        ),
    )

admin.site.register(User, CustomUser)

# Competency
admin.site.register(module)
admin.site.register(product)
admin.site.register(update_competency)
admin.site.register(training)
admin.site.register(comments_field)


