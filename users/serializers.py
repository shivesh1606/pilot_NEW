from rest_framework import serializers
from .models import Profile, Organization, Teacher, Student

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    # send the image_profile url with baseUrl in the response
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        print(instance.image_profile)
        print("Some Random Reqiestr",request)
        try:
            if instance.image_profile:
                data['image_profile'] = request.build_absolute_uri(instance.image_profile.url)
            else:
                data['image_profile'] = None
        except Exception as e:
            print(e)
        print(data['image_profile'])
        return data

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
    # if it calls ProfileSerializer then pass request to it
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile:
            data['profile'] = ProfileSerializer(instance.profile, context={'request': request}).data
        return data
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
    # if it calls ProfileSerializer then pass request to it
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile:
            data['profile'] = ProfileSerializer(instance.profile, context={'request': request}).data
        return data


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
    # if it calls ProfileSerializer then pass request to it
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        print("Student request",request)
        if instance.profile:
            data['profile'] = ProfileSerializer(instance.profile, context={'request': request}).data
        return data
    # add read-only field to the serializer
    
  