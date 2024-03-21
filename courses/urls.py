# urls here
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path('contact/', views.contact, name='contact'),
    path("contact_form/", views.contact_form, name="contact_form"),
    path("course/<int:course_id>/review/", views.course_review, name="course_review"),
    path("course/getallcourses/", views.get_all_courses, name="get_all_courses"),
    path(
        "course/check_enrollment/<int:course_id>",
        views.check_enrollment,
        name="check_enrollment",
    ),
    path(
        "course/<int:course_id>/video/<int:video_id>",
        views.course_video,
        name="course_video",
    ),
    path("quiz/submit_quiz/", views.submit_quiz, name="submit_quiz"),
    path(
        "course/<int:course_id>/course_notes/<int:note_id>",
        views.course_notes,
        name="course_notes",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("course/create_course/", views.create_course, name="create_course"),
    path(
        "course/course_details/<int:course_id>",
        views.course_details,
        name="course_details",
    ),
    path(
        "course/update_course/<int:course_id>",
        views.update_course,
        name="update_course",
    ),
    path(
        "course/delete_course/<int:course_id>",
        views.delete_course,
        name="delete_course",
    ),
    path("couse/get_courses/", views.get_courses, name="get_courses"),
    path(
        "course/create_module/<int:course_id>",
        views.create_module,
        name="create_module",
    ),
    path(
        "course/<int:course_id>/update_module/<int:module_id>",
        views.update_module,
        name="update_module",
    ),
    path(
        "course/<int:course_id>/delete_module/<int:module_id>",
        views.delete_module,
        name="delete_module",
    ),
    path("course/get_modules/<int:course_id>", views.get_modules, name="get_modules"),
    path("quiz/quiz_list/<int:video_id>", views.quiz_list, name="quiz_list"),
    path("quiz/view_quiz/<int:quiz_id>", views.view_quiz, name="view_quiz"),
    path("quiz/create_quiz/<int:video_id>", views.create_quiz, name="create_quiz"),
    path("quiz/update_quiz/<int:quiz_id>", views.update_quiz, name="update_quiz"),
    path("quiz/delete_quiz/<int:quiz_id>", views.delete_quiz, name="delete_quiz"),
    path("status/make_teacher/", views.make_teacher, name="make_teacher"),
    path("org/teacher_list/", views.teacher_list, name="teacher_list"),
    path("course/enroll_course/", views.enroll_course, name="enroll_course"),
    path("comment/add_video_comment/", views.add_video_comment, name="add_video_comment"),
    path("comment/get_video_comments/<int:video_id>", views.get_video_comments, name="get_video_comments"),
]
