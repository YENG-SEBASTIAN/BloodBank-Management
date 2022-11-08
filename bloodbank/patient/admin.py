from django.contrib import admin

# Register your models here.
from .models import Patient, PaystackPayment

admin.site.register(Patient)
admin.site.register(PaystackPayment)
