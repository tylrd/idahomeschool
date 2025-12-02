from datetime import datetime
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from idahomeschool.academics.models import Course
from idahomeschool.academics.models import CourseEnrollment
from idahomeschool.academics.models import DailyLog
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard showing overview of all academic records."""

    template_name = "academics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get active school year
        active_year = SchoolYear.objects.filter(user=user, is_active=True).first()
        context["active_year"] = active_year

        if active_year:
            context["active_enrollments"] = CourseEnrollment.objects.filter(
                user=user,
                school_year=active_year,
                status="IN_PROGRESS",
            ).select_related("student", "course", "school_year")

            # Get attendance statistics for active year
            logs_in_year = DailyLog.objects.filter(
                user=user,
                date__gte=active_year.start_date,
                date__lte=active_year.end_date,
            )
            context["total_attendance_days"] = logs_in_year.count()
            context["instructional_days"] = logs_in_year.filter(
                status__in=["PRESENT", "FIELD_TRIP"],
            ).count()

        # Recent daily logs
        context["recent_daily_logs"] = (
            DailyLog.objects.filter(user=user)
            .select_related("student")
            .order_by("-date")[:5]
        )

        context["recent_students"] = Student.objects.filter(user=user).order_by(
            "-created_at",
        )[:5]
        context["recent_courses"] = (
            Course.objects.filter(user=user)
            .prefetch_related("enrollments")
            .order_by("-created_at")[:5]
        )

        # Weekly summary
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday

        week_logs = DailyLog.objects.filter(
            user=user,
            date__gte=week_start,
            date__lte=week_end,
        )

        context["week_days_logged"] = week_logs.values("date").distinct().count()
        context["week_instructional_days"] = week_logs.filter(
            status__in=["PRESENT", "FIELD_TRIP"],
        ).values("date").distinct().count()
        context["week_students_count"] = week_logs.values("student").distinct().count()

        if active_year:
            context["active_courses_count"] = Course.objects.filter(
                user=user,
                enrollments__school_year=active_year,
                enrollments__status="IN_PROGRESS",
            ).distinct().count()
            # For template conditional check
            context["active_courses"] = context["active_enrollments"].exists()

        return context
