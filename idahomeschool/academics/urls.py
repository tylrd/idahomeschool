from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # SchoolYear URLs
    path("school-years/", views.SchoolYearListView.as_view(), name="schoolyear_list"),
    path("school-years/create/", views.SchoolYearCreateView.as_view(), name="schoolyear_create"),
    path("school-years/<int:pk>/", views.SchoolYearDetailView.as_view(), name="schoolyear_detail"),
    path("school-years/<int:pk>/update/", views.SchoolYearUpdateView.as_view(), name="schoolyear_update"),
    path("school-years/<int:pk>/delete/", views.SchoolYearDeleteView.as_view(), name="schoolyear_delete"),
    # Student URLs
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/create/", views.StudentCreateView.as_view(), name="student_create"),
    path("students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("students/<int:pk>/update/", views.StudentUpdateView.as_view(), name="student_update"),
    path("students/<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
    # Course URLs
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:pk>/update/", views.CourseUpdateView.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
    # CurriculumResource URLs
    path(
        "courses/<int:course_pk>/resources/create/",
        views.CurriculumResourceCreateView.as_view(),
        name="resource_create",
    ),
    path(
        "resources/<int:pk>/update/",
        views.CurriculumResourceUpdateView.as_view(),
        name="resource_update",
    ),
    path(
        "resources/<int:pk>/delete/",
        views.CurriculumResourceDeleteView.as_view(),
        name="resource_delete",
    ),
    # DailyLog / Attendance URLs
    path("attendance/", views.AttendanceCalendarView.as_view(), name="attendance_calendar"),
    path("attendance/report/", views.AttendanceReportView.as_view(), name="attendance_report"),
    path("attendance/entry/", views.DailyLogEntryView.as_view(), name="dailylog_entry"),
    path(
        "attendance/entry/<int:student_pk>/",
        views.DailyLogEntryView.as_view(),
        name="dailylog_entry_student",
    ),
    path(
        "attendance/entry/<int:student_pk>/<str:log_date>/",
        views.DailyLogEntryView.as_view(),
        name="dailylog_entry_date",
    ),
    path("daily-logs/", views.DailyLogListView.as_view(), name="dailylog_list"),
    path("daily-logs/create/", views.DailyLogCreateView.as_view(), name="dailylog_create"),
    path("daily-logs/<int:pk>/", views.DailyLogDetailView.as_view(), name="dailylog_detail"),
    path("daily-logs/<int:pk>/update/", views.DailyLogUpdateView.as_view(), name="dailylog_update"),
    path("daily-logs/<int:pk>/delete/", views.DailyLogDeleteView.as_view(), name="dailylog_delete"),
]
