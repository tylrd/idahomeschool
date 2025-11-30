import random

from django.conf import settings
from django.db import models
from django.urls import reverse


def student_photo_path(instance, filename):
    """Generate upload path for student photos."""
    # Store photos in: media/students/<user_id>/<student_id>_<filename>
    return f"students/{instance.user.id}/{instance.id or 'new'}_{filename}"


def resource_image_path(instance, filename):
    """Generate upload path for resource images."""
    # Store images in: media/resources/<user_id>/<resource_id>_<filename>
    return f"resources/{instance.user.id}/{instance.id or 'new'}_{filename}"


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


class AttendanceStatus(models.Model):
    """User-defined attendance status types with custom colors."""

    # Default statuses that will be created for new users
    DEFAULT_STATUSES = [
        {
            "code": "PRESENT",
            "label": "Present",
            "abbreviation": "P",
            "color": "#198754",  # Bootstrap success green
            "is_instructional": True,
            "is_default": True,
        },
        {
            "code": "ABSENT",
            "label": "Absent",
            "abbreviation": "A",
            "color": "#dc3545",  # Bootstrap danger red
            "is_instructional": False,
            "is_default": False,
        },
        {
            "code": "SICK",
            "label": "Sick",
            "abbreviation": "S",
            "color": "#ffc107",  # Bootstrap warning yellow
            "is_instructional": False,
            "is_default": False,
        },
        {
            "code": "HOLIDAY",
            "label": "Holiday",
            "abbreviation": "H",
            "color": "#0dcaf0",  # Bootstrap info cyan
            "is_instructional": False,
            "is_default": False,
        },
        {
            "code": "FIELD_TRIP",
            "label": "Field Trip",
            "abbreviation": "F",
            "color": "#0d6efd",  # Bootstrap primary blue
            "is_instructional": True,
            "is_default": False,
        },
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_statuses",
    )
    code = models.CharField(
        max_length=50,
        help_text="Internal code for this status (e.g., 'PRESENT', 'SICK')",
    )
    label = models.CharField(
        max_length=50,
        help_text="Display name for this status (e.g., 'Present', 'Sick')",
    )
    abbreviation = models.CharField(
        max_length=3,
        help_text="Short code shown on calendar (e.g., 'P', 'A', 'S')",
    )
    color = models.CharField(
        max_length=7,
        help_text="Hex color code for the status badge (e.g., #007bff)",
    )
    is_instructional = models.BooleanField(
        default=True,
        help_text="Whether this status counts as an instructional day",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default status for new daily logs",
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which statuses are displayed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user", "display_order", "label"]
        verbose_name = "Attendance Status"
        verbose_name_plural = "Attendance Statuses"
        unique_together = [["user", "code"]]
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["user", "display_order"]),
        ]

    def __str__(self):
        return f"{self.label} ({self.abbreviation})"

    def save(self, *args, **kwargs):
        # If setting this as default, unset all other defaults for this user
        if self.is_default:
            AttendanceStatus.objects.filter(
                user=self.user,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def create_defaults_for_user(cls, user):
        """Create default attendance statuses for a new user."""
        for idx, status_data in enumerate(cls.DEFAULT_STATUSES):
            # Try to find a color in user's active palette
            color_value = status_data["color"]
            active_palette = ColorPalette.objects.filter(
                user=user,
                is_active=True,
            ).first()

            if active_palette:
                # Try to find a close match in the palette
                palette_color = active_palette.colors.filter(
                    color=color_value,
                ).first()
                if palette_color:
                    color_value = palette_color.color

            cls.objects.create(
                user=user,
                code=status_data["code"],
                label=status_data["label"],
                abbreviation=status_data["abbreviation"],
                color=color_value,
                is_instructional=status_data["is_instructional"],
                is_default=status_data["is_default"],
                display_order=idx,
            )

    @classmethod
    def get_default_for_user(cls, user):
        """Get the default status for a user, or create defaults if none exist."""
        default_status = cls.objects.filter(user=user, is_default=True).first()
        if not default_status:
            # No statuses exist, create defaults
            cls.create_defaults_for_user(user)
            default_status = cls.objects.filter(user=user, is_default=True).first()
        return default_status


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
    image = models.ImageField(
        upload_to=resource_image_path,
        blank=True,
        null=True,
        help_text="Optional cover image or thumbnail",
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

    # Legacy STATUS_CHOICES kept for migration purposes
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
    # NEW: Use custom AttendanceStatus
    attendance_status = models.ForeignKey(
        AttendanceStatus,
        on_delete=models.PROTECT,
        related_name="daily_logs",
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text="Attendance status for this day",
    )
    # OLD: Keep old status field temporarily for migration
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
        blank=True,
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
        if self.attendance_status:
            return f"{self.student.name} - {self.date} ({self.attendance_status.label})"
        return f"{self.student.name} - {self.date} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("academics:dailylog_detail", kwargs={"pk": self.pk})

    @property
    def is_instructional_day(self):
        """Returns True if this counts as an instructional day."""
        if self.attendance_status:
            return self.attendance_status.is_instructional
        # Fallback for old status field during migration
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


class BookTagPreference(models.Model):
    """Stores which tags identify resources as 'books' for the reading list."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_tag_preference",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="book_preferences",
        help_text="Tags that identify resources as books for the reading list",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book Tag Preference"
        verbose_name_plural = "Book Tag Preferences"

    def __str__(self):
        tag_names = ", ".join(self.tags.values_list("name", flat=True))
        if tag_names:
            return f"Book tags for {self.user}: {tag_names}"
        return f"Book tags for {self.user}: (none)"

    @classmethod
    def get_book_tags_for_user(cls, user):
        """Get the tags that identify books for this user."""
        pref, _created = cls.objects.get_or_create(user=user)
        return pref.tags.all()

    @classmethod
    def get_book_resources_for_user(cls, user):
        """Get all resources that match the user's book tag preferences."""
        book_tags = cls.get_book_tags_for_user(user)
        if book_tags.exists():
            return Resource.objects.filter(
                user=user,
                tags__in=book_tags,
            ).distinct()
        return Resource.objects.none()


class ReadingList(models.Model):
    """Tracks which books a student has read or is reading."""

    STATUS_CHOICES = [
        ("TO_READ", "To Read"),
        ("READING", "Currently Reading"),
        ("COMPLETED", "Completed"),
        ("DID_NOT_FINISH", "Did Not Finish"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_lists",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="reading_list",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="reading_list_entries",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="TO_READ",
    )
    started_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the student started reading this book",
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the student completed or stopped reading this book",
    )
    rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rating from 1-5 stars",
    )
    notes = models.TextField(
        blank=True,
        help_text="Personal notes, review, or thoughts about the book",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reading_list_entries",
        help_text="Optional school year when this book was read",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "student__name"]
        verbose_name = "Reading List Entry"
        verbose_name_plural = "Reading List Entries"
        unique_together = [["student", "resource"]]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["student", "school_year"]),
        ]

    def __str__(self):
        status_display = self.get_status_display()
        return f"{self.student.name} - {self.resource.title} ({status_display})"

    def get_absolute_url(self):
        return reverse("academics:readinglist_detail", kwargs={"pk": self.pk})

    @property
    def status_badge_class(self):
        """Return Bootstrap badge class based on status."""
        badge_map = {
            "TO_READ": "secondary",
            "READING": "primary",
            "COMPLETED": "success",
            "DID_NOT_FINISH": "warning",
        }
        return badge_map.get(self.status, "secondary")
