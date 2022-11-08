from django.contrib import admin

# Register your models here.
from .models import Donor, BloodDonate

admin.site.register(Donor)
# admin.site.register(BloodDonate)