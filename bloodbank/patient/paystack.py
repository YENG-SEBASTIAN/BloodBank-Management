from django.conf import settings
import requests

class PayStack:
    PAYSTACK_TEST_SECRET_KEYS = settings.PAYSTACK_TEST_SECRET_KEYS
    base_url = 'https://api.paystack.co'
    
    def verify_payment(self, ref, *args, **kwargs):
        path = f"/transaction/verify/{ref}"
        
        headers = {
            "Authorization" : f"Bearer {self.PAYSTACK_TEST_SECRET_KEYS}",
            "Content-Type" : 'application/json',
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json
        #     return response_data(['status']), response_data(['data'])
        # response_data = response.json
        # return response_data['status'], response_data['message']