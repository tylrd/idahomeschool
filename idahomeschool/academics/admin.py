from django.contrib import admin

from .models import Course, CurriculumResource, SchoolYear, Student


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


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student model."""

    list_display = ["name", "date_of_birth", "grade_level", "user", "created_at"]
    list_filter = ["grade_level", "created_at", "user"]
    search_fields = ["name", "user__name", "user__email"]
    filter_horizontal = ["school_years"]
    readonly_fields = ["created_at", "updated_at", "age"]
    date_hierarchy = "created_at"
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

    list_display = ["name", "student", "school_year", "created_at"]
    list_filter = ["school_year", "created_at"]
    search_fields = ["name", "student__name", "school_year__name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    inlines = [CurriculumResourceInline]
    fieldsets = [
        (
            None,
            {
                "fields": ["student", "school_year", "name", "description"],
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
