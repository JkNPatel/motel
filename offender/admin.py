from django.contrib import admin
from .models import Extra_info
from .models import Offender
from .models import Experience

# Register your models here.

admin.site.register(Extra_info)
admin.site.register(Offender)
admin.site.register(Experience)