from rest_framework import serializers
from .models import Tags, Course, Review, Enrollment, Module, Video, Comment, SubComment, Notes, UserProgress, CourseProgress, Quiz, Question, Answer, Monitor
from .serializerhelper import get_user_course_progress
class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        print(instance.image_course)
        try:
            if instance.image_course:
                data['image_course'] = request.build_absolute_uri(instance.image_course.url)
            else:
                data['image_course'] = None
            print(data['image_course'])
        except Exception as e:
            print(e)
        return data

class DashboardCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        print(instance.image_course)
        data['user_progress']=get_user_course_progress(request.user, instance)
        try:
            if instance.image_course:
                data['image_course'] = request.build_absolute_uri(instance.image_course.url)
            else:
                data['image_course'] = None
            print(data['image_course'])
        except Exception as e:
            print(e)
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class SubCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubComment
        fields = '__all__'

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'

class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'
