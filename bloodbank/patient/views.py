from email import message
from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect,reverse
from django.urls import is_valid_path
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from .models import PaystackPayment


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)

def patient_dashboard_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),

    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return redirect('initiate-payment')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})



def initiate_payment(request):
    payment_form = forms.PaystackPaymentForm(request.POST)
    bloodQuantity = bmodels.BloodRequest.objects.last()
    blood_cost = bmodels.CostOfBloodStock.objects.last()
    
    total_price = bloodQuantity.unit * blood_cost.blood_stock_price
    user = request.user
    if request.method == "POST":
        if payment_form.is_valid():
            payment = payment_form.save()
            return render(request, 'patient/makepayment.html', {'payment':payment, 
                                                                'PAYSTACK_TEST_PUBLIC_KEYS':settings.PAYSTACK_TEST_PUBLIC_KEYS})
        else:
            payment_form = forms.PaystackPaymentForm()
    return render(request,'patient/initiatePayment.html',{'payment_form':payment_form, 
                                                          'total_price':total_price, 
                                                          'bloodQuantity':bloodQuantity,
                                                          'user':user})


def verify_payment(request, ref):
    payment = get_object_or_404(PaystackPayment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, 'Payment verification was successful')
    else:
        payment.verified = True
        messages.error(request, 'Payment varification failed')
    return redirect('make-request')