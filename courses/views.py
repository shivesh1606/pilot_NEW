from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .forms import ReviewForm
from django.utils import timezone
from .models import Course, Review, Module, Video, Comment, SubComment, Notes, Monitor, Tags, Quiz, Question, Answer, Enrollment
from .serializers import CommentSerializer
from users.models import Profile, Student, Organization, Teacher
from datetime import datetime, timedelta
# from django.contrib.gis.geoip2 import GeoIP2
from django_user_agents.utils import get_user_agent
import requests
import json
from django.urls import reverse
from .utils import searchCourses
from django.shortcuts import redirect
from django.http import JsonResponse

# Create your views here.

# an api which returns the complete course model without id, the complete list


def index(request):
    course = Course.objects.all()
    course = list(course.values())
    for i in course:
        i.pop('id')
    return JsonResponse(course, safe=False)

# rest api for review form, only if user is authenticated


@login_required
@api_view(['POST'])
def course_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.course = course
        review.user = request.user
        review.save()
        messages.success(request, 'Review added successfully')
        # You can add additional logic here if needed

        return JsonResponse({'status': 'success', 'message': 'Review added successfully'})
    else:
        form = ReviewForm()
        return JsonResponse({'status': 'error', 'message': 'Review not added successfully'})


@login_required
@api_view(['GET'])
def get_all_courses(request):
    courses = Course.objects.all()
    courses, search_query = searchCourses(request)

    return JsonResponse({'courses': courses, 'search_query': search_query}, safe=False)


@login_required
@api_view(['POST'])
def contact_form(request):
    name = request.data['name']
    email = request.data['email']
    desc = request.data['desc']
    contact = Contact_us(name=name, email=email,
                         desc=desc, date=datetime.today())
    contact.save()

    return JsonResponse({'status': 'success', 'message': 'Contact form submitted successfully'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def check_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course)
    if enrollment.exists():
        return JsonResponse({'status': 'success', 'message': 'Enrolled', 'course': course})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not Enrolled'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def course_video(request, course_id, video_id):
    course = get_object_or_404(Course, id=course_id)
    video = get_object_or_404(Video, id=video_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course)
    if enrollment.exists():
        quiz = Quiz.objects.filter(video=video).first()
        questions = quiz.question_set.all() if quiz else []

        return JsonResponse({'status': 'success', 'message': 'Enrolled', 'course': course, 'video': video, 'quiz': quiz, 'questions': questions})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not Enrolled'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def submit_quiz(request):
    try:
        # quiz_id = request.POST.get('quiz_id')
        selected_answers = request.POST.getlist('selected_answers[]')
        qs_ids = request.POST.getlist('question_ids')
        score = 0
        for index, id in enumerate(qs_ids):
            id = id.strip('[]')
            question = Question.objects.get(id=id)
            # correct_answer = question.answer_set.get(correct=True)
            if selected_answers[index] is not 0:
                ans = Answer.objects.get(id=selected_answers[index])
                if ans.is_correct:
                    score += 1

        # if request.method == 'POST':
    #     quiz_id = request.POST.get('quiz_id')
    #     question_ids = request.POST.getlist('question_ids[]')
    #     answer_ids = request.POST.getlist('answer_ids[]')

    #     # Do something with the form data, for example:
    #     quiz = Quiz.objects.get(id=quiz_id)
    #     total_marks = 0
    #     obtained_marks = 0
    #     for question_id, answer_id in zip(question_ids, answer_ids):
    #         question = Question.objects.get(id=question_id)
    #         answer = Answer.objects.get(id=answer_id)
    #         if answer.is_correct:
    #             obtained_marks += question.marks
    #         total_marks += question.marks
    #     percentage = obtained_marks / total_marks * 100
    #     if percentage >= quiz.pass_percentage:
    #         message = 'Congratulations! You passed the quiz with a score of {}%.'.format(round(percentage))
    #     else:
    #         message = 'Sorry, you failed the quiz with a score of {}%.'.format(round(percentage))
        return JsonResponse({'status': 'success', 'message': 'Quiz submitted successfully', 'score': score})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Quiz not submitted successfully', 'error': str(e)})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def course_notes(request, course_id, note_id):
    course = get_object_or_404(Course, id=course_id)
    notes = get_object_or_404(Notes, id=note_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course)
    if enrollment.exists():
        return JsonResponse({'status': 'success', 'message': 'Enrolled', 'course': course, 'notes': notes})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not Enrolled'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    if profile.exists():
        return JsonResponse({'status': 'success', 'message': 'Profile exists', 'profile': profile})
    else:
        return JsonResponse({'status': 'error', 'message': 'Profile does not exist'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_course(request):
    teacher_status = True if request.user.profile_status == 'Teacher' else False
    if teacher_status:
        name = request.data['name']
        desc = request.data['desc']
        price = request.data['price']
        image = request.data['image']
        small_desc = request.data['small_desc']
        learned = request.data['learned']
        tags = request.data['tags']
        tags_list = [tags.strip() for tag in tags.split(',') if tag.strip()]
        tags_new = []
        for tag in tags_list:
            tag_obj, created = Tags.objects.get_or_create(name=tag)
            tags_new.append(tag_obj)

        teacher = Teacher.objects.get(profile=request.user.profile)
        course = Course(name=name, description=desc, price=price, image_course=image, small_description=small_desc, learned=learned,
                        teacher=teacher, organization=teacher.organization, created_at=datetime.today(), updated_at=datetime.today())
        course.save()
        course.tags.set(tags_new)
        return JsonResponse({'status': 'success', 'message': 'Course created successfully', 'course': course})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not a teacher'})


@login_required
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    try:
        if request.user.is_authenticated:
            try:
                monitor = Monitor.objects.get(user=request.user, landing_page=request.META.get(
                    'HTTP_HOST') + request.META.get('PATH_INFO'), ip=request.META.get('REMOTE_ADDR'))
                monitor.frequency += 1
                monitor.save()

                profile = Profile.objects.get(user=request.user) if Profile.objects.filter(
                    user=request.user).exists() else None

                return JsonResponse({'status': 'success', 'message': 'Course details', 'course': course, 'profile': profile})
            except Monitor.DoesNotExist:
                pass
        else:
            try:
                monitor = Monitor()
                monitor.ip = request.META.get('REMOTE_ADDR')
                g = 'https://geolocation-db.com/jsonp/' + str(monitor.ip)
                response = requests.get(g)
                data = response.content.decode()
                data = data.split("(")[1].strip(")")
                location = json.loads(data)
                monitor.country = location['country_name']
                monitor.city = location['city']
                monitor.region = location['region']
                monitor.timeZone = location['time_zone']
                user_agent = get_user_agent(request)
                monitor.browser = user_agent.browser.family
                monitor.browser_version = user_agent.browser.version_string
                monitor.operating_system = user_agent.os.family
                monitor.device = user_agent.device.family
                monitor.language = request.headers.get('Accept-Language')
                monitor.screen_resolution = request.headers.get(
                    'X-Original-Request-Screen-Resolution')
                monitor.referrer = request.META.get('HTTP_REFERER')
                monitor.landing_page = request.META.get(
                    'HTTP_HOST') + request.META.get('PATH_INFO')
                monitor.frequency = 1
                monitor.save()
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'Monitor not created', 'error': str(e)})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Course not found', 'error': str(e)})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if (course.teacher.profile.user == request.user):
        course.name = request.data['name']
        course.description = request.data['desc']
        course.price = request.data['price']
        course.image_course = request.data['image']
        course.small_description = request.data['small_desc']
        course.learned = request.data['learned']
        tags = request.data['tags'].split(',')
        course.updated_at = datetime.today()
        for tag in tags:
            tag = tag.strip()
            if tag:
                tag_obj, created = Tags.objects.get_or_create(name=tag)
                course.tags.add(tag_obj)
        course.save()
        return JsonResponse({'status': 'success', 'message': 'Course updated successfully', 'course': course})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if (course.teacher.profile.user == request.user):
        course.delete()
        return JsonResponse({'status': 'success', 'message': 'Course deleted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})


@login_required
@api_view(['GET'])
def get_courses(request):
    teacher = get_object_or_404(Teacher, profile=request.user.profile)
    courses = Course.objects.filter(teacher=teacher)
    return JsonResponse({'status': 'success', 'message': 'Courses', 'courses': courses})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        total_module = course.total_module
        module = Module(name=request.data['name'], course=course, number=(
            course.total_module + 1))
        module.save()
        course.total_module = total_module + 1

        num = 0
        for video in request.FILES.getlist('videos'):
            video_name = video.name.split('.')[0]
            num += 1
            video_obj = Video(name=video_name, module=module,
                              number=num, video=video)
            video_obj.save()

        for note in request.data.getlist('notes'):
            if note.strip():
                module.total_notes += 1
                note_obj = Notes(user=request.user, module=module,
                                 description=note, number=module.total_notes)
                note_obj.save()

        course.save()
        return JsonResponse({'status': 'success', 'message': 'Module created successfully', 'module': module, 'course': course})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Module not created', 'error': str(e)})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_module(request, course_id, module_id):
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id)
    if (course.teacher.profile.user == request.user):
        module.name = request.data['module_name']
        module.save()

        vids_to_delete = request.data.getlist('vids_to_delete')
        for vid_id in vids_to_delete:
            Video.objects.filter(id=vid_id).delete()

        for video in request.FILES.getlist('videos'):
            video_name = video.name.split('.')[0]
            video_obj = Video(name=video_name, module=module, video=video)
            video_obj.save()

        notes_to_delete = request.data.getlist('notes_to_delete')
        for note_id in notes_to_delete:
            Notes.objects.filter(id=note_id).delete()

        for note in request.data.getlist('notes'):
            if note.strip():
                note_obj = Notes(user=request.user,
                                 module=module, description=note)
                note_obj.save()

        return JsonResponse({'status': 'success', 'message': 'Module updated successfully', 'module': module, 'course': course})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_module(request, course_id, module_id):
    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id)
    if (course.teacher.profile.user == request.user):
        module.delete()
        return JsonResponse({'status': 'success', 'message': 'Module deleted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})


@login_required
@api_view(['GET'])
def get_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course)
    return JsonResponse({'status': 'success', 'message': 'Modules', 'modules': modules})


@login_required
@api_view(['GET'])
def quiz_list(request, video_id):
    quizs = Quiz.objects.filter(video=video_id)
    return JsonResponse({'status': 'success', 'message': 'Quizs', 'quizs': quizs})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return JsonResponse({'status': 'success', 'message': 'Quiz', 'quiz': quiz})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_quiz(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.user.profile != video.module.course.teacher.profile:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})
    else:
        try:
            pass_marks = request.data.get('pass_marks')
            timestamp = request.data.get('timestamp')
            if timestamp is not None and timestamp:
                timestamp_parts = [int(part) for part in timestamp.split(':')]
                timestamp_td = timedelta(
                    hours=timestamp_parts[0], minutes=timestamp_parts[1], seconds=timestamp_parts[2])
                timestamp = timestamp_parts[0]*60*60 + \
                    timestamp_parts[1]*60+timestamp_parts[2]
                start_time = int(timestamp)
                start_time = timedelta(seconds=float(start_time))
            else:
                start_time = 0
            quiz = Quiz(video=video, pass_marks=pass_marks,
                        start_time=start_time)
            quiz.save()

            # input will be like -
            # questions = [
            #     {
            #         question_text:'sdfsdfsd',
            #         answers = [
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': True
            #             },
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': True
            #             },
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': False
            #             }
            #         ]
            #     },
            #     {
            #         question_text:'sdfsdfsd',
            #         answers = [
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': True
            #             },
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': True
            #             },
            #             {
            #                 'answer_text': 'asdasd',
            #                 'is_correct': False
            #             }
            #         ]
            #     }
            # ]

            for question in request.data.get('questions'):
                question_text = question.get('question_text')
                Question.objects.create(quiz=quiz, text=question_text)

                answers = question.get('answers')
                for answer in answers:
                    answer_text = answer.get('answer_text')
                    is_correct = answer.get('is_correct')
                    Answer.objects.create(
                        question=question, text=answer_text, is_correct=is_correct)

            return JsonResponse({'status': 'success', 'message': 'Quiz created successfully', 'quiz': quiz, 'video': video})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user.profile != quiz.video.module.course.teacher.profile:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})
    else:
        try:
            quiz.video_id = request.data.get('video_id')
            quiz.pass_marks = request.data.get('pass_marks')
            quiz.start_time = request.data.get('start_time')
            quiz.save()

            for question in request.data.get('questions'):
                question_text = question.get('question_text')
                que_obj = Question(quiz=quiz, text=question_text)
                que_obj.save()

                answers = question.get('answers')
                for answer in answers:
                    answer_text = answer.get('answer_text')
                    is_correct = answer.get('is_correct')
                    ans_obj = Answer(question=question,
                                     text=answer_text, is_correct=is_correct)
                    ans_obj.save()

            return JsonResponse({'status': 'success', 'message': 'Quiz updated successfully', 'quiz': quiz})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user.profile != quiz.video.module.course.teacher.profile:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this course'})
    else:
        quiz.delete()
        return JsonResponse({'status': 'success', 'message': 'Quiz deleted successfully'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def make_teacher(request):
    r_profile = get_object_or_404(Profile, user=request.user)
    org = Organization.objects.filter(profile=r_profile)
    if org:
        org = Organization.objects.get(profile=r_profile)
        profiles = Profile.objects.all()

        profile_id = request.data.get('profile_id')
        r_profile = get_object_or_404(Profile, id=profile_id)
        r_profile.status = 'Teacher'
        r_profile.save()
        teacher = Teacher.objects.create(profile=r_profile, organization=org)
        student = get_object_or_404(Student, profile=r_profile)
        student.delete()
        teacher.save()

        return JsonResponse({'status': 'success', 'message': 'Teacher created successfully', 'teacher': teacher, 'profiles': profiles})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to make a teacher'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def teacher_list(request):
    r_profile = get_object_or_404(Profile, user=request.user)
    org = Organization.objects.filter(profile=r_profile)
    if org:
        org = Organization.objects.get(profile=r_profile)
        teachers = Teacher.objects.filter(organization=org)
        return JsonResponse({'status': 'success', 'message': 'Teachers', 'teachers': teachers})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to view teachers'})


@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        course=course, student=request.user)
    if created:
        return JsonResponse({'status': 'success', 'message': 'Enrolled successfully', 'enrollment': enrollment})
    else:
        return JsonResponse({'status': 'error', 'message': 'Already enrolled'})

@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_video_comment(request):
    video = get_object_or_404(Video, id=request.data.get('video_id'))
    description = request.data.get('description')
    print(request.user, description, video)
    comment = Comment.objects.create(
        user=request.user,description=description,video=video)
    return JsonResponse({'status': 'success', 'message': 'Comment added successfully', 'comment': comment.id})

@login_required
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_reply(request):
    comment=get_object_or_404(Comment,id=request.data.get('comment_id'))
    description = request.data.get('description')
    reply=Comment.objects.create(
        user=request.user, description=description, parent_comment=comment)
    
    return JsonResponse({'status': 'success', 'message': 'Reply added successfully', 'reply': reply})

@api_view(['GET'])
def get_video_comments(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    comments = Comment.objects.filter(video=video)
    comments = CommentSerializer(comments, many=True).data
    return JsonResponse({'status': 'success', 'message': 'Comments', 'comments': comments})

@login_required
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.description = request.data.get('description')
        comment.save()
        return JsonResponse({'status': 'success', 'message': 'Comment updated successfully', 'comment': comment})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this comment'})
