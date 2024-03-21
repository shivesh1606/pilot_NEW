from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from .models import Profile, Teacher, Student, Organization
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileSerializer, TeacherSerializer, StudentSerializer, OrganizationSerializer
import random
from django.http import JsonResponse
import json
from rest_framework.authtoken.models import Token

# Create your views here.

@api_view(['GET'])
def coursebase(request):
    return Response({'success': True, 'message': 'Welcome to the course base'})

@csrf_exempt
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

    if user is not None:
        login(request, user)
        # Generate token
        token, created = Token.objects.get_or_create(user=user)
        return Response({'success': True, 'token': token.key, 'message': 'Login successful'}, status=status.HTTP_202_ACCEPTED)
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
            session_otp = request.session.get('otp')
            if str(session_otp) == otp:
                try:
                    username = request.data.get('name')
                    email = request.data.get('email')
                    phone = request.data.get('phone')
                    pwd = request.data.get('password')
                    cnfrm_pwd = request.data.get('confirmpassword')
                
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
            try:
                username = request.data.get('name')
                email = request.data.get('email')
                phone = request.data.get('phone')
                # status = request.data.get('status')
                pwd = request.data.get('password')
                cnfrm_pwd = request.data.get('confirmpassword')
                if pwd == cnfrm_pwd:
                    print("here to generate otp")
                    otp = generate_otp()
                    print("otp generated")
                    request.session['otp'] = otp
                    request.session['email'] = email
                    request.session['username'] = username
                    request.session['phone'] = phone
                    # request.session['status'] = status
                    request.session['password'] = pwd
                    print("email:", email)
                    print(f"the otp is {otp}")
                    try:
                        send_mail(
                            'OTP Verification',
                            f'Your OTP is {otp}',
                            'pilotlms.kgp@gmail.com',
                            [email],
                            fail_silently=False,
                        )
                        print("otp sent ig")
                    except Exception as e:
                        print("otp not sent", e)
                        return Response({'success': False, 'message': 'Error in sending email'+str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({'success': True, 'message': 'OTP sent successfully'}, status=status.HTTP_201_OK)
            except Exception as e:
                print("error in generating otp", e)
                return Response({'success': False, 'message': 'Unprecendented error'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    if request.user.is_authenticated:
        try:
            r_profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'success':True, 'message': 'Profile does not exist for user'}, status=status.HTTP_404_NOT_FOUND)

        if request.method in ['PUT', 'PATCH']:
            serializer = ProfileSerializer(r_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                if r_profile.status == "Student":
                    student = Student.objects.filter(profile=r_profile).first()
                    if student:
                        student_serializer = StudentSerializer(student, data=request.data, partial=True)
                        if student_serializer.is_valid():
                            student_serializer.save()
                        else:
                            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                elif r_profile.status == "Teacher":
                    teacher = Teacher.objects.filter(profile=r_profile).first()
                    if teacher:
                        teacher_serializer = TeacherSerializer(teacher, data=request.data, partial=True)
                        if teacher_serializer.is_valid():
                            teacher_serializer.save()
                        else:
                            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                elif r_profile.status == "Organization":
                    organization = Organization.objects.filter(profile=r_profile).first()
                    if organization:
                        organization_serializer = OrganizationSerializer(organization, data=request.data, partial=True)
                        if organization_serializer.is_valid():
                            organization_serializer.save()
                        else:
                            return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({'success': True, 'message': 'Profile updated successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return Response({'message': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if profile.status == 'Organization':
        organization = get_object_or_404(Organization, profile=profile)
        organization_serializer = OrganizationSerializer(organization)
        return Response(organization_serializer.data)

    elif profile.status == 'Teacher':
        teacher = get_object_or_404(Teacher, profile=profile)
        teacher_serializer = TeacherSerializer(teacher)
        return Response(teacher_serializer.data)

    else:
        student = get_object_or_404(Student, profile=profile)
        student_serializer = StudentSerializer(student)
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
        