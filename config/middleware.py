from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse

class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(' ')[1]
                decoded_token = AccessToken(token)
                is_customer = decoded_token.payload.get('is_customer')

                # Check if user is accessing the correct pages
                if is_customer and '' in request.path:
                    return redirect(reverse('home_page'))
                elif not is_customer and '/seller/dashboard/' in request.path:
                    return redirect(reverse('seller_dashboard'))

            except Exception:
                pass

        response = self.get_response(request)
        return response