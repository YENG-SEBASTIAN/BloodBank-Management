from django.contrib import admin

# Register your models here.
from .models import Stock, BloodRequest, CostOfBloodStock

admin.site.register(Stock)
admin.site.register(BloodRequest)
admin.site.register(CostOfBloodStock)