import random

from django.conf import settings
from django.db import models
from django.urls import reverse


def student_photo_path(instance, filename):
    """Generate upload path for student photos."""
    # Store photos in: media/students/<user_id>/<student_id>_<filename>
    return f"students/{instance.user.id}/{instance.id or 'new'}_{filename}"


class SchoolYear(models.Model):
    """Represents an academic school year (e.g., 2024-2025)."""

    name = models.CharField(max_length=50, unique=True, help_text="e.g., '2024-2025'")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=False,
        help_text="Only one school year should be active at a time",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_years",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "School Year"
        verbose_name_plural = "School Years"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:schoolyear_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Ensure only one active school year per user
        if self.is_active:
            SchoolYear.objects.filter(user=self.user, is_active=True).exclude(
                pk=self.pk,
            ).update(is_active=False)
        super().save(*args, **kwargs)


class Student(models.Model):
    """Represents a homeschool student."""

    GRADE_CHOICES = [
        ("PK", "Pre-Kindergarten"),
        ("K", "Kindergarten"),
        ("1", "1st Grade"),
        ("2", "2nd Grade"),
        ("3", "3rd Grade"),
        ("4", "4th Grade"),
        ("5", "5th Grade"),
        ("6", "6th Grade"),
        ("7", "7th Grade"),
        ("8", "8th Grade"),
        ("9", "9th Grade"),
        ("10", "10th Grade"),
        ("11", "11th Grade"),
        ("12", "12th Grade"),
    ]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    grade_level = models.CharField(max_length=2, choices=GRADE_CHOICES)
    photo = models.ImageField(
        upload_to=student_photo_path,
        blank=True,
        null=True,
        help_text="Student photo (optional)",
    )
    paperless_tag_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Paperless-NGX tag ID for this student",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="students",
    )
    school_years = models.ManyToManyField(
        SchoolYear,
        related_name="students",
        blank=True,
        help_text="School years this student is enrolled in",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:student_detail", kwargs={"pk": self.pk})

    @property
    def age(self):
        """Calculate student's current age."""
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    def get_grade_for_year(self, school_year):
        """Get the grade level for a specific school year."""
        if not school_year:
            return None

        try:
            grade_year = self.grade_years.get(school_year=school_year)
        except StudentGradeYear.DoesNotExist:
            return None
        else:
            return grade_year.grade_level


class GradeLevel(models.Model):
    """Represents a user-defined grade level (e.g., '1st Grade', 'Year 1', 'Junior')."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_levels",
    )
    name = models.CharField(
        max_length=100,
        help_text="Grade name (e.g., '1st Grade', 'Year 1', 'Upper Elementary')",
    )
    order = models.IntegerField(
        help_text="Numeric order for sorting (e.g., 0 for PK, 1 for K, 2 for 1st)",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of this grade level",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Grade Level"
        verbose_name_plural = "Grade Levels"
        unique_together = [
            ["user", "name"],
            ["user", "order"],
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:gradelevel_detail", kwargs={"pk": self.pk})


class StudentGradeYear(models.Model):
    """Links a student to a specific grade level for a specific school year."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_grade_years",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grade_years",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name="student_grades",
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name="student_years",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["school_year__start_date", "student__name"]
        verbose_name = "Student Grade Assignment"
        verbose_name_plural = "Student Grade Assignments"
        unique_together = [["student", "school_year"]]
        indexes = [
            models.Index(fields=["student", "school_year"]),
            models.Index(fields=["school_year", "grade_level"]),
        ]

    def __str__(self):
        return (
            f"{self.student.name} - {self.grade_level.name} ({self.school_year.name})"
        )

    def get_absolute_url(self):
        return reverse("academics:student_detail", kwargs={"pk": self.student.pk})


class ColorPalette(models.Model):
    """Represents a named collection of colors for tag organization."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="color_palettes",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(
        default=False,
        help_text="Only colors from the active palette are used for random tag colors",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "name"]
        verbose_name = "Color Palette"
        verbose_name_plural = "Color Palettes"
        unique_together = [["user", "name"]]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:color_palette_list")


class Color(models.Model):
    """Represents a color in a user's custom color palette for tags."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="colors",
    )
    name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional name for the color (e.g., 'Ocean Blue')",
    )
    color = models.CharField(
        max_length=7,
        help_text="Hex color code (e.g., #007bff)",
    )
    palettes = models.ManyToManyField(
        ColorPalette,
        blank=True,
        related_name="colors",
        help_text="Palettes this color belongs to",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Color"
        verbose_name_plural = "Colors"

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.color})"
        return self.color

    def get_absolute_url(self):
        return reverse("academics:color_palette_list")

    @staticmethod
    def get_default_colors():
        """Returns a list of default color palette colors."""
        return [
            "#007bff",  # Blue
            "#28a745",  # Green
            "#dc3545",  # Red
            "#ffc107",  # Yellow
            "#17a2b8",  # Cyan
            "#6f42c1",  # Purple
            "#fd7e14",  # Orange
            "#e83e8c",  # Pink
            "#20c997",  # Teal
            "#6c757d",  # Gray
            "#343a40",  # Dark
            "#f8f9fa",  # Light Gray
        ]


class Tag(models.Model):
    """Represents a tag for organizing resources."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Hex color code for the tag badge",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        unique_together = [["user", "name"]]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:tag_detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_palette_colors_for_user(user):
        """Get colors from user's active palette, or all colors if no active palette."""
        # Try to get the active palette
        active_palette = ColorPalette.objects.filter(
            user=user,
            is_active=True,
        ).first()

        if active_palette:
            # Get colors from the active palette
            palette_colors = list(
                active_palette.colors.values_list("color", flat=True),
            )
        else:
            # If no active palette, use all user's colors
            palette_colors = list(
                Color.objects.filter(user=user).values_list("color", flat=True),
            )

        # If still no colors, use defaults
        if not palette_colors:
            palette_colors = Color.get_default_colors()

        return palette_colors

    @staticmethod
    def get_random_color_from_palette(user):
        """Get a random color from the user's active colors."""
        palette_colors = Tag.get_palette_colors_for_user(user)
        return random.choice(palette_colors)


class Resource(models.Model):
    """Represents a curriculum resource in the central library."""

    RESOURCE_TYPE_CHOICES = [
        ("BOOK", "Book"),
        ("WORKBOOK", "Workbook"),
        ("ONLINE", "Online Course"),
        ("VIDEO", "Video Course"),
        ("SOFTWARE", "Software"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources",
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(
        max_length=20,
        blank=True,
        help_text="ISBN-10 or ISBN-13",
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        default="BOOK",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description or notes",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="resources",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        indexes = [
            models.Index(fields=["user", "title"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("academics:resource_detail", kwargs={"pk": self.pk})


class CourseTemplate(models.Model):
    """Represents a reusable course template with suggested resources."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_templates",
    )
    name = models.CharField(max_length=200, help_text="e.g., 'Algebra 1', 'Latin'")
    description = models.TextField(
        blank=True,
        help_text="Optional description of the course",
    )
    suggested_resources = models.ManyToManyField(
        Resource,
        blank=True,
        related_name="course_templates",
        help_text="Suggested resources for this course template",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Course Template"
        verbose_name_plural = "Course Templates"
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:coursetemplate_detail", kwargs={"pk": self.pk})


class Course(models.Model):
    """Represents a course that can span multiple school years."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200, help_text="e.g., 'Algebra 1', 'Latin'")
    description = models.TextField(
        blank=True,
        help_text="Optional course description",
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        help_text="Optional grade level this course is designed for",
    )
    course_template = models.ForeignKey(
        CourseTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        help_text="Template this course was created from (if any)",
    )
    resources = models.ManyToManyField(
        Resource,
        blank=True,
        related_name="courses",
        help_text="Resources for this course",
    )
    # OLD FIELDS - Keep temporarily for migration, will be removed later
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="old_courses",
        null=True,
        blank=True,
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name="old_courses",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("academics:course_detail", kwargs={"pk": self.pk})


class CurriculumResource(models.Model):
    """DEPRECATED - use Resource instead. Textbook or workbook used for a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="old_curriculum_resources",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(
        max_length=13,
        blank=True,
        help_text="ISBN-10 or ISBN-13",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Curriculum Resource"
        verbose_name_plural = "Curriculum Resources"

    def __str__(self):
        if self.course:
            return f"{self.title} ({self.course.name})"
        return self.title


class CourseEnrollment(models.Model):
    """Represents a student's enrollment in a course for a specific school year."""

    STATUS_CHOICES = [
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("PAUSED", "Paused"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="IN_PROGRESS",
    )
    started_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the student started this course",
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the student completed this course",
    )
    final_grade = models.CharField(
        max_length=5,
        blank=True,
        help_text="Final grade (e.g., 'A', '95%', 'Pass')",
    )
    completion_percentage = models.IntegerField(
        null=True,
        blank=True,
        help_text="Completion percentage (0-100)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["school_year__start_date", "course__name"]
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        unique_together = [["student", "course", "school_year"]]
        indexes = [
            models.Index(fields=["student", "school_year"]),
            models.Index(fields=["course", "school_year"]),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.course.name} ({self.school_year.name})"

    def get_absolute_url(self):
        return reverse("academics:courseenrollment_detail", kwargs={"pk": self.pk})


class DailyLog(models.Model):
    """Represents daily attendance for a student."""

    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("SICK", "Sick"),
        ("HOLIDAY", "Holiday"),
        ("FIELD_TRIP", "Field Trip"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="daily_logs",
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
    )
    general_notes = models.TextField(
        blank=True,
        help_text="Optional notes for the day",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__name"]
        verbose_name = "Daily Log"
        verbose_name_plural = "Daily Logs"
        unique_together = [["student", "date"]]
        indexes = [
            models.Index(fields=["date", "student"]),
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("academics:dailylog_detail", kwargs={"pk": self.pk})

    @property
    def is_instructional_day(self):
        """Returns True if this counts as an instructional day (Present or Field Trip)."""
        return self.status in ["PRESENT", "FIELD_TRIP"]


class CourseNote(models.Model):
    """Represents notes for a specific course enrollment on a specific day."""

    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="course_notes",
    )
    course_enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name="course_notes",
        null=True,
        blank=True,
    )
    # OLD FIELD - Keep temporarily for migration, will be removed later
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="old_course_notes",
        null=True,
        blank=True,
    )
    notes = models.TextField(
        help_text="Notes about what was covered in this course today",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course_enrollment__course__name"]
        verbose_name = "Course Note"
        verbose_name_plural = "Course Notes"
        indexes = [
            models.Index(fields=["daily_log", "course_enrollment"]),
            models.Index(fields=["daily_log", "course"]),  # Keep for migration
        ]

    def __str__(self):
        if self.course_enrollment:
            return f"{self.course_enrollment.course.name} - {self.daily_log.date}"
        if self.course:
            return f"{self.course.name} - {self.daily_log.date}"
        return f"CourseNote {self.pk}"
