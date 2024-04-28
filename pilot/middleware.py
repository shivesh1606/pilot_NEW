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
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))

    @staticmethod
    def get_jwt_user(request):
        user_jwt = get_user(request)
        print("user_jwt",user_jwt)
        print("try"*100)
        if user_jwt is not None and user_jwt.is_authenticated:
            return user_jwt
        token = request.META.get('HTTP_AUTHORIZATION', None)
        print(token)
        token=token.split(' ')[1]
        token=str(token)
        user_jwt = AnonymousUser()
        if token is not None:
            try:
                user_jwt = jwt.decode(
                    token,
                    "secret", algorithm="HS256"
                )
                print("Try"*100)
                print("user_jwt",user_jwt)
                user_jwt = User.objects.get(
                    username=user_jwt['username'])
            except Exception as e: # NoQA
                print('Error decoding token',e)
                traceback.print_exc()
        return user_jwt