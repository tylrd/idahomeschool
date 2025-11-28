from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


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
                pk=self.pk
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


class Course(models.Model):
    """Represents a course for a student in a specific school year."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    name = models.CharField(max_length=100, help_text="e.g., 'Math 5', 'Idaho History'")
    description = models.TextField(blank=True, help_text="Optional course description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["school_year", "student", "name"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        unique_together = [["student", "school_year", "name"]]

    def __str__(self):
        return f"{self.name} - {self.student.name} ({self.school_year.name})"

    def get_absolute_url(self):
        return reverse("academics:course_detail", kwargs={"pk": self.pk})


class CurriculumResource(models.Model):
    """Represents a textbook or workbook used for a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="resources",
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
        return f"{self.title} ({self.course.name})"


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
    """Represents notes for a specific course on a specific day."""

    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="course_notes",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_notes",
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
        ordering = ["course__name"]
        verbose_name = "Course Note"
        verbose_name_plural = "Course Notes"
        unique_together = [["daily_log", "course"]]
        indexes = [
            models.Index(fields=["daily_log", "course"]),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.daily_log.date}"
