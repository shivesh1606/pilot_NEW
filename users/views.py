from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from .models import Profile, Teacher, Student, Organization
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .serializers import ProfileSerializer, TeacherSerializer, StudentSerializer, OrganizationSerializer
import random
from django.http import JsonResponse
import json
from rest_framework.authtoken.models import Token
from datetime import datetime,timedelta
import jwt
from .token import generate_token,confirm_token
from django.views.decorators.csrf import ensure_csrf_cookie
# Create your views here.

@api_view(['GET'])
def coursebase(request):
    return Response({'success': True, 'message': 'Welcome to the course base'})

from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
@csrf_exempt
@ensure_csrf_cookie
@api_view(['POST'])
def loginUser(request):
    if request.user.is_authenticated:
        return Response({'success': True, 'login': True, 'message': 'User already Authenticated'})
    
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user = authenticate(request, username=email, password=password)
    profile=Profile.objects.get(user=user)
    if profile.is_verified == False:
        return Response({'success': False, 'message': 'User not Verified'}, status=status.HTTP_401_UNAUTHORIZED)
    if user is not None:
        # Generate token
        payload = {
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(weeks=8),
            "iat": datetime.utcnow()
        }
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile,context={'request': request})

        token = get_tokens_for_user(user)['access']
        print(token)
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {
            "jwt": token,
            "user": serializer.data,
        }

        return response
        
    else:
        return Response({'success': False, 'message': 'Username or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)


def generate_otp():
    new_otp = random.randint(100000, 999999)
    return new_otp

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutUser(request):
    logout(request)
    return Response({'success': True,'message': 'Logout successful'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def registerUser(request):
    if request.user.is_authenticated:
        return Response({'success': True,'message': 'User already authenticated'}, status=status.HTTP_226_IM_USED)
    else: 
        if 'otp' in request.data:
            otp = request.data['otp']
            # Print Request cokkies
            print(request.session.session_key)
            print(request.COOKIES)
            print(request.session.get('email'))
            print(request.session.get('otp'))
            session_otp = request.session.get('otp')
            print("otp", otp)
            print("session_otp", session_otp)
            if str(session_otp) == otp:
                try:
                    username = request.data['username']
                    email = request.data['email']
                    phone = request.data['phone']
                    pwd = request.data['password1']
                    cnfrm_pwd = request.data['password2']
                    print(username, email, phone, pwd, cnfrm_pwd)
                
                    if pwd == cnfrm_pwd:
                        profile = Profile.objects.filter(email=email)
                        user = User.objects.filter(email=email)

                        if not user.exists():
                            user = User.objects.create_user(username=email, email=email)
                            user.set_password(pwd)
                            profile = Profile.objects.create(user=user, name=username, email=email, phone=phone)
                            student = Student.objects.create(profile=profile)
                            user.save()
                            profile.save()
                            student.save()
                            login(request, user)
                            return Response({'success': True,'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({'sucesss':False, 'message': 'User already exists'}, status=status.HTTP_409_CONFLICT)
                    else:
                        return Response({'sucesss':False, 'message': 'Confirm Password is not equal to Password'}, status=status.HTTP_400_BAD_REQUEST)

                except Exception as e:
                    return Response({'sucesss':False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'sucesss':False, 'message':'OTP is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # try:
            username = request.data['username']
            email = request.data['email']
            phone = request.data['phone']
            user_status = request.data['status']
            pwd = request.data['password1']
            cnfrm_pwd = request.data['password2']
            print(username, email, phone, pwd, cnfrm_pwd)
            print(pwd==cnfrm_pwd)
            if pwd == cnfrm_pwd:
                user = User.objects.create_user(username=email, email=email)
                user.set_password(pwd)
                profile = Profile.objects.create(user=user, name=username, email=email, phone=phone)
                student = Student.objects.create(profile=profile)
                user.save()
                profile.save()
                student.save()  
                token = generate_token(user.email)
                try:
                    print("otp sent ig",f'Your verification link is http://127.0.0.1:8000/user/confirm/{token}')
                    send_mail(
                        'OTP Verification',
                        f'Your verification link is http://127.0.0.1:8000/user/confirm/{token}',
                        'pilotlms.kgp@gmail.com',
                        [email],
                        fail_silently=False,
                    )

                except Exception as e:
                    print("otp not sent", e)
                    return Response({'success': False, 'message': 'Error in sending email'+str(e)}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'success': True, 'message': 'OTP sent successfully'}, status=status.HTTP_201_OK)
            else:
                return Response({'success': False, 'message': 'Password does not match'}, status=status.HTTP_400_BAD_REQUEST)
            # except Exception as e:
            #     print("error in generating otp", e)
            #     return Response({'success': False, 'message': 'Unprecendented error'}, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
@api_view(['GET', 'PUT', 'PATCH','UPDATE'])
def update_profile(request):
    # print(request.user.is_authenticated)
    # print("Something")
    # print(request.user)
    # if request.user.is_authenticated:
    try:
        r_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({'success':True, 'message': 'Profile does not exist for user'}, status=status.HTTP_404_NOT_FOUND)

    # if request.method in ['PUT', 'PATCH','UPDATE']:
    #     serializer = ProfileSerializer(r_profile, data=request.data, partial=True)
    if request.method in ['PUT', 'PATCH']:
        data = request.data.copy()

        # Remove any fields with null values from the request data
        for key, value in data.items():
            if value is None:
                del data[key]

        serializer = ProfileSerializer(r_profile, data=data, partial=True)
        if serializer.is_valid():
            updated_profile = serializer.save()

            if r_profile.status == "Student":
                student = Student.objects.filter(profile=r_profile).first()
                if student:
                    student_serializer = StudentSerializer(student, data=data, partial=True)
                    if student_serializer.is_valid():
                        student_serializer.save()
                    else:

                        return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif r_profile.status == "Teacher":
                teacher = Teacher.objects.filter(profile=r_profile).first()
                if teacher:
                    teacher_serializer = TeacherSerializer(teacher, data=data, partial=True)
                    if teacher_serializer.is_valid():
                        teacher_serializer.save()
                    else:
                        return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif r_profile.status == "Organization":
                organization = Organization.objects.filter(profile=r_profile).first()
                if organization:
                    organization_serializer = OrganizationSerializer(organization, data=data, partial=True)
                    if organization_serializer.is_valid():
                        organization_serializer.save()
                    else:
                        return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            profile_serializer = ProfileSerializer(updated_profile)

            return Response({'success': True, 'message': 'Profile updated successfully', 'profile': profile_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # else:
    #     return Response({'message': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if profile.status == 'Organization':
        organization = get_object_or_404(Organization, profile=profile)
        organization_serializer = OrganizationSerializer(organization,context={'request': request})
        return Response(organization_serializer.data)

    elif profile.status == 'Teacher':
        teacher = get_object_or_404(Teacher, profile=profile)
        teacher_serializer = TeacherSerializer(teacher)
        # also i need details from the corresponding profile model of that teacher
        profile_serializer = ProfileSerializer(profile)
        data = {
            'teacher': teacher_serializer.data,
            'profile': profile_serializer.data
        }
        return Response(data)

    else:
        student = get_object_or_404(Student, profile=profile)
        student_serializer = StudentSerializer(student,context={'request': request})
        return Response(student_serializer.data)

def reset_password(request):
    page = 'reset_password'
    if request.user.is_authenticated:
        return Response({'success': True, 'message': 'Password reset'})
    
    if request.method == 'POST':
        try:
            if 'otp' in request.POST:
                otp = request.POST.get('otp')
                if otp == str(request.session['otp']):
                    password = request.POST.get('password')
                    confirm_password = request.POST.get('confirmpassword')
                    if password == confirm_password:
                        email = request.POST.get('email')
                        print("here", email)
                        user = User.objects.get(email=email)
                        user.set_password(password)
                        user.save()
                        messages.success(request, "Password reset successful")
                        return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_202_ACCEPTED)
                    else:
                        messages.error(request, "Passwords don't match")
                        return Response({'success': False, 'message': 'Password does not match'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'success': False, 'message': 'OTP Verification failed'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                otp = generate_otp()
                data = json.loads(request.body)
                email = data.get('email')
                print('email', email)
                request.session['otp'] = otp
                request.session['email'] = email
                try:
                    send_mail(
                        'OTP Verification',
                        f'Your OTP is {otp}',
                        'pilotlms.kgp@gmail.com',
                        [email],
                        fail_silently=False,
                    )
                    print("otp sent", otp)
                    return Response({'success': True, 'message': 'Verification mail sent'}, status=status.HTTP_200_OK)
                except Exception as e:
                    print("otp not sent", e)
                    return Response({'sucess': False, 'message': 'Error in sending mail'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            print("user does not exist")
            messages.error(request, "User does not exist")
            return Response({'success': False, 'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@permission_classes([AllowAny])
@api_view(['GET'])
def get_user_profile(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        user_obj= User.objects.get(username=request.user)
        profile = Profile.objects.get(user=user_obj)
        serializer = ProfileSerializer(profile,context={'request': request})
        return Response(serializer.data)
    else:
        return Response({'message': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def confirm_email(request,token):
    print("token", token)
    email = confirm_token(token)
    print(email)
    user = User.objects.get(email=email)
    profile=Profile.objects.get(user=user)
    profile.is_verified = True
    profile.verified_on = datetime.now()
    profile.save()
    return Response({'success': True, 'message': 'User confirmed successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.status != 'Organization':
            return Response({'error': 'Access denied. Only organizations can access this endpoint.'}, status=403)
        
        teacher_profiles = Profile.objects.filter(teacher__isnull=False)

        # Get all student profiles
        student_profiles = Profile.objects.filter(student__isnull=False)

        # Serialize the data
        teacher_profile_serializer = ProfileSerializer(teacher_profiles, many=True)
        student_profile_serializer = ProfileSerializer(student_profiles, many=True)

        # Combine the serialized data
        user_data = teacher_profile_serializer.data + student_profile_serializer.data

        # Return the response with user_data as a list
        return Response(user_data)