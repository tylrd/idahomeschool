from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # SchoolYear URLs
    path("school-years/", views.SchoolYearListView.as_view(), name="schoolyear_list"),
    path(
        "school-years/create/",
        views.SchoolYearCreateView.as_view(),
        name="schoolyear_create",
    ),
    path(
        "school-years/<int:pk>/",
        views.SchoolYearDetailView.as_view(),
        name="schoolyear_detail",
    ),
    path(
        "school-years/<int:pk>/update/",
        views.SchoolYearUpdateView.as_view(),
        name="schoolyear_update",
    ),
    path(
        "school-years/<int:pk>/delete/",
        views.SchoolYearDeleteView.as_view(),
        name="schoolyear_delete",
    ),
    # Resource Library URLs
    path("library/", views.ResourceListView.as_view(), name="resource_list"),
    path("library/create/", views.ResourceCreateView.as_view(), name="library_create"),
    path("library/<int:pk>/", views.ResourceDetailView.as_view(), name="resource_detail"),
    path(
        "library/<int:pk>/update/",
        views.ResourceUpdateView.as_view(),
        name="library_update",
    ),
    path(
        "library/<int:pk>/delete/",
        views.ResourceDeleteView.as_view(),
        name="library_delete",
    ),
    # HTMX endpoints
    path(
        "library/search/",
        views.resource_search_htmx,
        name="resource_search_htmx",
    ),
    # Tag URLs
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/create/", views.TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/", views.TagDetailView.as_view(), name="tag_detail"),
    path(
        "tags/<int:pk>/update/",
        views.TagUpdateView.as_view(),
        name="tag_update",
    ),
    path(
        "tags/<int:pk>/delete/",
        views.TagDeleteView.as_view(),
        name="tag_delete",
    ),
    # CourseTemplate URLs
    path(
        "course-templates/",
        views.CourseTemplateListView.as_view(),
        name="coursetemplate_list",
    ),
    path(
        "course-templates/create/",
        views.CourseTemplateCreateView.as_view(),
        name="coursetemplate_create",
    ),
    path(
        "course-templates/<int:pk>/",
        views.CourseTemplateDetailView.as_view(),
        name="coursetemplate_detail",
    ),
    path(
        "course-templates/<int:pk>/update/",
        views.CourseTemplateUpdateView.as_view(),
        name="coursetemplate_update",
    ),
    path(
        "course-templates/<int:pk>/delete/",
        views.CourseTemplateDeleteView.as_view(),
        name="coursetemplate_delete",
    ),
    # CourseEnrollment URLs
    path(
        "enrollments/",
        views.CourseEnrollmentListView.as_view(),
        name="courseenrollment_list",
    ),
    path(
        "enrollments/create/",
        views.CourseEnrollmentCreateView.as_view(),
        name="courseenrollment_create",
    ),
    path(
        "enrollments/<int:pk>/",
        views.CourseEnrollmentDetailView.as_view(),
        name="courseenrollment_detail",
    ),
    path(
        "enrollments/<int:pk>/update/",
        views.CourseEnrollmentUpdateView.as_view(),
        name="courseenrollment_update",
    ),
    path(
        "enrollments/<int:pk>/delete/",
        views.CourseEnrollmentDeleteView.as_view(),
        name="courseenrollment_delete",
    ),
    # Student URLs
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/create/", views.StudentCreateView.as_view(), name="student_create"),
    path(
        "students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"
    ),
    path(
        "students/<int:pk>/update/",
        views.StudentUpdateView.as_view(),
        name="student_update",
    ),
    path(
        "students/<int:pk>/delete/",
        views.StudentDeleteView.as_view(),
        name="student_delete",
    ),
    # Course URLs
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path(
        "courses/<int:pk>/update/",
        views.CourseUpdateView.as_view(),
        name="course_update",
    ),
    path(
        "courses/<int:pk>/delete/",
        views.CourseDeleteView.as_view(),
        name="course_delete",
    ),
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
    path(
        "attendance/",
        views.AttendanceCalendarView.as_view(),
        name="attendance_calendar",
    ),
    path(
        "attendance/report/",
        views.AttendanceReportView.as_view(),
        name="attendance_report",
    ),
    path(
        "attendance/report/pdf/",
        views.AttendanceReportPDFView.as_view(),
        name="attendance_report_pdf",
    ),
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
    # HTMX Quick Actions
    path(
        "attendance/quick-toggle/<int:student_pk>/<str:log_date>/",
        views.attendance_quick_toggle,
        name="attendance_quick_toggle",
    ),
    path(
        "attendance/quick-update/<int:student_pk>/<str:log_date>/",
        views.attendance_quick_update,
        name="attendance_quick_update",
    ),
    path(
        "attendance/quick-delete/<int:student_pk>/<str:log_date>/",
        views.attendance_quick_delete,
        name="attendance_quick_delete",
    ),
    path(
        "attendance/course-notes/<int:student_pk>/<str:log_date>/",
        views.attendance_course_notes,
        name="attendance_course_notes",
    ),
    path(
        "attendance/save-course-notes/<int:student_pk>/<str:log_date>/",
        views.attendance_save_course_notes,
        name="attendance_save_course_notes",
    ),
    path("daily-logs/", views.DailyLogListView.as_view(), name="dailylog_list"),
    path(
        "daily-logs/create/", views.DailyLogCreateView.as_view(), name="dailylog_create"
    ),
    path(
        "daily-logs/<int:pk>/",
        views.DailyLogDetailView.as_view(),
        name="dailylog_detail",
    ),
    path(
        "daily-logs/<int:pk>/update/",
        views.DailyLogUpdateView.as_view(),
        name="dailylog_update",
    ),
    path(
        "daily-logs/<int:pk>/delete/",
        views.DailyLogDeleteView.as_view(),
        name="dailylog_delete",
    ),
]
