# coding=utf-8
import jwt
import traceback

from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser, User
from django.conf import LazySettings
from django.contrib.auth.middleware import get_user
from django.urls import reverse, resolve
settings = LazySettings()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith(reverse('admin:index')):
            return
        request.user = self.get_jwt_user(request)

    @staticmethod
    def get_jwt_user(request):
        print('Getting JWT user')
        user_jwt = get_user(request)
        if user_jwt is not None and user_jwt.is_authenticated:
            return user_jwt
        token = request.META.get('HTTP_AUTHORIZATION', None)
        print('Token', token)
        user_jwt = AnonymousUser()
        if token is not None:
            try:
                token=token.split(' ')[1]
                token=str(token)
                user_jwt = jwt.decode(
                    token,
                    "secret",
                    algorithms=["HS256"]
                )
                user_jwt = User.objects.get(
                    id=user_jwt['user_id'])
                request.user = user_jwt
            except Exception as e: # NoQA
                print('Error decoding token',e)
                traceback.print_exc()
        print('Returning user_jwt', user_jwt)
        return user_jwt