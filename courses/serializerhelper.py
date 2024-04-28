from .models import Video, UserVideoProgress

from datetime import timedelta
def get_user_course_progress(user, course):
    video_list=Video.objects.filter(course=course)
    course_progress=0
    for video in video_list:
        user_progres=UserVideoProgress(user=user,video=video)
        video_length=timedelta(seconds=user_progres.video.duration)
        print(video_length)
        print(user_progres.relative_timestamp)
        percentage_watched = ((video_length-user_progres.relative_timestamp) / video_length)*100
        course_progress+=percentage_watched
        print(percentage_watched)
        print("PErcenetage Watched",user_progres.percentage_watched)
    print(course_progress/len(video_list))
    return course_progress/len(video_list)