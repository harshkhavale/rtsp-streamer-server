from django.contrib import admin
from .models import Stream, Detection, Alert, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Stream)
admin.site.register(Detection)
admin.site.register(Alert)
