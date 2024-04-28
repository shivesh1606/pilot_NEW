from django.db.models import Q
from .models import Course, Review, Module, Video, Comment, SubComment, Notes,Monitor, Tags, Quiz, Question, Answer, Enrollment
from users.models import Profile, Student, Organization, Teacher
from .serializers import CourseSerializer
def searchCourses(request):
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    courses = Course.objects.distinct().filter(
        Q(name__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(small_description__icontains=search_query) |
        Q(learned__icontains=search_query) |
        Q(tags__name__icontains=search_query) |
        Q(module__name__icontains=search_query) |
        Q(module__description__icontains=search_query)
    )
    courses = CourseSerializer(courses, many=True,context={'request': request}).data
    return courses, search_query


