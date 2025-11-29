from django.contrib import admin

from .models import (
    Course,
    CourseEnrollment,
    CourseNote,
    CourseTemplate,
    CurriculumResource,
    DailyLog,
    GradeLevel,
    Resource,
    SchoolYear,
    Student,
    StudentGradeYear,
    Tag,
)


class CurriculumResourceInline(admin.TabularInline):
    """Inline admin for curriculum resources."""

    model = CurriculumResource
    extra = 1
    fields = ["title", "author", "publisher", "isbn"]


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    """Admin for SchoolYear model."""

    list_display = ["name", "start_date", "end_date", "is_active", "user", "created_at"]
    list_filter = ["is_active", "created_at", "user"]
    search_fields = ["name", "user__name", "user__email"]
    date_hierarchy = "start_date"
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": ["name", "start_date", "end_date", "is_active", "user"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for Tag model."""

    list_display = ["name", "color", "user", "created_at"]
    list_filter = ["created_at", "user"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Tag Information",
            {
                "fields": ["user", "name", "color"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    """Admin for GradeLevel model."""

    list_display = ["name", "order", "user", "created_at"]
    list_filter = ["created_at", "user"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Grade Level Information",
            {
                "fields": ["user", "name", "order", "description"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin for Resource model."""

    list_display = ["title", "author", "publisher", "resource_type", "user", "created_at"]
    list_filter = ["resource_type", "created_at", "user", "tags"]
    search_fields = ["title", "author", "publisher", "isbn", "description"]
    filter_horizontal = ["tags"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Resource Information",
            {
                "fields": ["user", "title", "author", "publisher", "isbn", "resource_type"],
            },
        ),
        (
            "Description & Tags",
            {
                "fields": ["description", "tags"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(CourseTemplate)
class CourseTemplateAdmin(admin.ModelAdmin):
    """Admin for CourseTemplate model."""

    list_display = ["name", "user", "created_at"]
    list_filter = ["created_at", "user"]
    search_fields = ["name", "description"]
    filter_horizontal = ["suggested_resources"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Template Information",
            {
                "fields": ["user", "name", "description"],
            },
        ),
        (
            "Suggested Resources",
            {
                "fields": ["suggested_resources"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin for CourseEnrollment model."""

    list_display = [
        "student",
        "course",
        "school_year",
        "status",
        "user",
        "created_at",
    ]
    list_filter = ["status", "school_year", "created_at", "user"]
    search_fields = [
        "student__name",
        "course__name",
        "school_year__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Enrollment Information",
            {
                "fields": [
                    "user",
                    "student",
                    "course",
                    "school_year",
                    "status",
                ],
            },
        ),
        (
            "Dates and Progress",
            {
                "fields": [
                    "started_date",
                    "completed_date",
                    "completion_percentage",
                    "final_grade",
                ],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


class StudentGradeYearInline(admin.TabularInline):
    """Inline admin for student grade assignments."""

    model = StudentGradeYear
    extra = 0
    fields = ["school_year", "grade_level"]
    verbose_name = "Grade Assignment"
    verbose_name_plural = "Grade Assignments by Year"


@admin.register(StudentGradeYear)
class StudentGradeYearAdmin(admin.ModelAdmin):
    """Admin for StudentGradeYear model."""

    list_display = ["student", "school_year", "grade_level", "user", "created_at"]
    list_filter = ["school_year", "grade_level", "created_at", "user"]
    search_fields = ["student__name", "school_year__name", "grade_level__name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Grade Assignment Information",
            {
                "fields": ["user", "student", "school_year", "grade_level"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student model."""

    list_display = ["name", "date_of_birth", "grade_level", "user", "created_at"]
    list_filter = ["grade_level", "created_at", "user"]
    search_fields = ["name", "user__name", "user__email"]
    filter_horizontal = ["school_years"]
    readonly_fields = ["created_at", "updated_at", "age"]
    date_hierarchy = "created_at"
    inlines = [StudentGradeYearInline]
    fieldsets = [
        (
            "Student Information",
            {
                "fields": ["name", "date_of_birth", "grade_level", "age"],
            },
        ),
        (
            "Enrollment",
            {
                "fields": ["user", "school_years"],
            },
        ),
        (
            "Paperless Integration",
            {
                "fields": ["paperless_tag_id"],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin for Course model."""

    list_display = ["name", "grade_level", "user", "created_at"]
    list_filter = ["grade_level", "created_at", "user"]
    search_fields = ["name", "description", "user__name", "user__email"]
    filter_horizontal = ["resources"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    inlines = [CurriculumResourceInline]
    fieldsets = [
        (
            "Course Information",
            {
                "fields": ["user", "name", "grade_level", "description"],
            },
        ),
        (
            "Template and Resources",
            {
                "fields": ["course_template", "resources"],
            },
        ),
        (
            "Deprecated Fields",
            {
                "fields": ["student", "school_year"],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(CurriculumResource)
class CurriculumResourceAdmin(admin.ModelAdmin):
    """Admin for CurriculumResource model."""

    list_display = ["title", "author", "publisher", "course", "created_at"]
    list_filter = ["created_at", "course__school_year"]
    search_fields = ["title", "author", "publisher", "isbn", "course__name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Resource Information",
            {
                "fields": ["course", "title", "author", "publisher", "isbn"],
            },
        ),
        (
            "Notes",
            {
                "fields": ["notes"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


class CourseNoteInline(admin.TabularInline):
    """Inline admin for course notes."""

    model = CourseNote
    extra = 0
    fields = ["course", "notes"]
    verbose_name = "Course Note"
    verbose_name_plural = "Course Notes"


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    """Admin for DailyLog model."""

    list_display = ["student", "date", "status", "user", "created_at"]
    list_filter = ["status", "date", "created_at", "user"]
    search_fields = ["student__name", "general_notes", "user__name", "user__email"]
    readonly_fields = ["created_at", "updated_at", "is_instructional_day"]
    date_hierarchy = "date"
    inlines = [CourseNoteInline]
    fieldsets = [
        (
            "Attendance Information",
            {
                "fields": ["student", "date", "status", "is_instructional_day"],
            },
        ),
        (
            "Notes",
            {
                "fields": ["general_notes"],
            },
        ),
        (
            "User",
            {
                "fields": ["user"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    """Admin for CourseNote model."""

    list_display = ["course", "daily_log", "user", "created_at"]
    list_filter = ["created_at", "course__school_year", "user"]
    search_fields = ["course__name", "notes", "daily_log__student__name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    fieldsets = [
        (
            "Course Note Information",
            {
                "fields": ["daily_log", "course", "notes"],
            },
        ),
        (
            "User",
            {
                "fields": ["user"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]
