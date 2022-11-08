import secrets
from urllib import request
from django.db import models
from django.contrib.auth.models import User
from .paystack import PayStack
class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Patient/',null=True,blank=True)

    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10) 
    disease=models.CharField(max_length=100)
    doctorname=models.CharField(max_length=50)

    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name
    


class PaystackPayment(models.Model):
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=100)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_paid = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_paid', )
        
    def __str__(self):
        return f"An amount of {self.amount} has being paid for blood"
    
    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = PaystackPayment.objects.filter(ref = ref)
            if not object_with_similar_ref:
                self.ref = ref
            super().save()
        
    def amount_value(self):
        return self.amount * 100
    
    def verify_payment(self):
        paystack = PayStack()
        result = paystack.verify_payment(self.ref, self.amount)
        if result:
            self.verified = True
            self.save()
            if not self.verified:
                return True
            return False