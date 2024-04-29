from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('get_profile/',views.get_user_profile,name='get_profile'),
    path('register/', views.registerUser, name='register'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),  
    path('profile/<uuid:profile_id>/',views.profile_detail, name='profile_detail'),
    path('coursebase/', views.coursebase, name='coursebase'),
    path('confirm/<str:token>/', views.confirm_email, name='confirm_email'),
    path('get_all_profiles/',views. user_list, name='all-profiles'),

]
