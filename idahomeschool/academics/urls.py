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
    path(
        "library/<int:pk>/", views.ResourceDetailView.as_view(), name="resource_detail",
    ),
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
    path(
        "resources/create-modal/",
        views.resource_create_modal_htmx,
        name="resource_create_modal_htmx",
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
    path(
        "tags/autocomplete/",
        views.tag_autocomplete_htmx,
        name="tag_autocomplete_htmx",
    ),
    path(
        "tags/create-modal/",
        views.tag_create_modal_htmx,
        name="tag_create_modal_htmx",
    ),
    # Color Palette URLs
    path(
        "settings/color-palette/",
        views.ColorPaletteListView.as_view(),
        name="color_palette_list",
    ),
    path(
        "settings/color-palette/add/",
        views.ColorPaletteCreateView.as_view(),
        name="color_palette_create",
    ),
    path(
        "settings/color-palette/import/",
        views.color_palette_import_csv,
        name="color_palette_import",
    ),
    path(
        "settings/color-palette/preview/",
        views.color_palette_preview_htmx,
        name="color_palette_preview_htmx",
    ),
    path(
        "settings/color-palette/<int:pk>/update/",
        views.ColorPaletteUpdateView.as_view(),
        name="color_palette_update",
    ),
    path(
        "settings/color-palette/<int:pk>/delete/",
        views.ColorPaletteDeleteView.as_view(),
        name="color_palette_delete",
    ),
    path(
        "settings/color-palette/<int:pk>/set-active/",
        views.set_active_palette,
        name="color_palette_set_active",
    ),
    path(
        "settings/color-palette/<int:palette_pk>/remove-color/<int:color_pk>/",
        views.remove_color_from_palette,
        name="remove_color_from_palette",
    ),
    # Color URLs (individual colors)
    path(
        "settings/colors/add/",
        views.ColorCreateView.as_view(),
        name="color_create",
    ),
    path(
        "settings/colors/<int:pk>/update/",
        views.ColorUpdateView.as_view(),
        name="color_update",
    ),
    path(
        "settings/colors/<int:pk>/delete/",
        views.ColorDeleteView.as_view(),
        name="color_delete",
    ),
    # GradeLevel URLs
    path("grade-levels/", views.GradeLevelListView.as_view(), name="gradelevel_list"),
    path(
        "grade-levels/create/",
        views.GradeLevelCreateView.as_view(),
        name="gradelevel_create",
    ),
    path(
        "grade-levels/create-pk12/",
        views.create_pk12_grades,
        name="gradelevel_create_pk12",
    ),
    path(
        "grade-levels/<int:pk>/",
        views.GradeLevelDetailView.as_view(),
        name="gradelevel_detail",
    ),
    path(
        "grade-levels/<int:pk>/update/",
        views.GradeLevelUpdateView.as_view(),
        name="gradelevel_update",
    ),
    path(
        "grade-levels/<int:pk>/delete/",
        views.GradeLevelDeleteView.as_view(),
        name="gradelevel_delete",
    ),
    # StudentGradeYear URLs
    path(
        "student-grades/create/",
        views.StudentGradeYearCreateView.as_view(),
        name="studentgradeyear_create",
    ),
    path(
        "students/<int:student_pk>/assign-grade/",
        views.StudentGradeYearCreateView.as_view(),
        name="studentgradeyear_create_for_student",
    ),
    path(
        "student-grades/<int:pk>/update/",
        views.StudentGradeYearUpdateView.as_view(),
        name="studentgradeyear_update",
    ),
    path(
        "student-grades/<int:pk>/delete/",
        views.StudentGradeYearDeleteView.as_view(),
        name="studentgradeyear_delete",
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
    # HTMX endpoint for course filtering
    path(
        "enrollments/filter-courses/",
        views.filter_courses_by_student,
        name="filter_courses_by_student",
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
        "students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail",
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
    # Student Reading List URLs
    path(
        "students/<int:pk>/reading-list/",
        views.StudentReadingListView.as_view(),
        name="student_reading_list",
    ),
    # Reading List URLs
    path("reading-list/", views.ReadingListView.as_view(), name="reading_list"),
    path(
        "reading-list/add/",
        views.ReadingListCreateView.as_view(),
        name="readinglist_create",
    ),
    path(
        "reading-list/<int:pk>/",
        views.ReadingListDetailView.as_view(),
        name="readinglist_detail",
    ),
    path(
        "reading-list/<int:pk>/update/",
        views.ReadingListUpdateView.as_view(),
        name="readinglist_update",
    ),
    path(
        "reading-list/<int:pk>/delete/",
        views.ReadingListDeleteView.as_view(),
        name="readinglist_delete",
    ),
    # HTMX endpoint for reading list quick updates
    path(
        "reading-list/<int:pk>/quick-update/",
        views.reading_list_quick_update_htmx,
        name="reading_list_quick_update",
    ),
    # Book Tag Preferences (Settings)
    path(
        "settings/book-tags/",
        views.BookTagPreferenceView.as_view(),
        name="book_tag_preferences",
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
    # Attendance Status Management URLs
    path(
        "settings/attendance-statuses/",
        views.AttendanceStatusListView.as_view(),
        name="attendance_status_list",
    ),
    path(
        "settings/attendance-statuses/add/",
        views.AttendanceStatusCreateView.as_view(),
        name="attendance_status_create",
    ),
    path(
        "settings/attendance-statuses/<int:pk>/update/",
        views.AttendanceStatusUpdateView.as_view(),
        name="attendance_status_update",
    ),
    path(
        "settings/attendance-statuses/<int:pk>/delete/",
        views.AttendanceStatusDeleteView.as_view(),
        name="attendance_status_delete",
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
        "daily-logs/create/", views.DailyLogCreateView.as_view(), name="dailylog_create",
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
