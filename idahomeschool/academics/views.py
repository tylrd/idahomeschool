from datetime import date
from datetime import datetime
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from weasyprint import HTML

from .forms import CourseForm
from .forms import CourseNoteForm
from .forms import CurriculumResourceForm
from .forms import DailyLogForm
from .forms import ResourceForm
from .forms import SchoolYearForm
from .forms import StudentForm
from .models import Course
from .models import CourseNote
from .models import CurriculumResource
from .models import DailyLog
from .models import Resource
from .models import SchoolYear
from .models import Student


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
            context["active_courses"] = Course.objects.filter(
                school_year=active_year,
                student__user=user,
            ).select_related("student", "school_year")

            # Get attendance statistics for active year
            logs_in_year = DailyLog.objects.filter(
                user=user,
                date__gte=active_year.start_date,
                date__lte=active_year.end_date,
            )
            context["total_attendance_days"] = logs_in_year.count()
            context["instructional_days"] = logs_in_year.filter(
                status__in=["PRESENT", "FIELD_TRIP"]
            ).count()

        # Recent daily logs
        context["recent_daily_logs"] = (
            DailyLog.objects.filter(user=user)
            .select_related("student")
            .order_by("-date")[:5]
        )

        context["recent_students"] = Student.objects.filter(user=user).order_by(
            "-created_at"
        )[:5]
        context["recent_courses"] = (
            Course.objects.filter(student__user=user)
            .select_related("student", "school_year")
            .order_by("-created_at")[:5]
        )

        return context


# SchoolYear Views
class SchoolYearListView(LoginRequiredMixin, ListView):
    """List all school years for the current user."""

    model = SchoolYear
    template_name = "academics/schoolyear_list.html"
    context_object_name = "school_years"
    paginate_by = 20

    def get_queryset(self):
        return SchoolYear.objects.filter(user=self.request.user).annotate(
            student_count=Count("students", distinct=True),
            course_count=Count("courses", distinct=True),
        )


class SchoolYearDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a school year."""

    model = SchoolYear
    template_name = "academics/schoolyear_detail.html"
    context_object_name = "school_year"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school_year = self.get_object()

        context["students"] = school_year.students.all()
        context["courses"] = school_year.courses.select_related("student").all()

        return context


class SchoolYearCreateView(LoginRequiredMixin, CreateView):
    """Create a new school year."""

    model = SchoolYear
    form_class = SchoolYearForm
    template_name = "academics/schoolyear_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"School year '{form.instance.name}' created successfully!"
        )
        return super().form_valid(form)


class SchoolYearUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing school year."""

    model = SchoolYear
    form_class = SchoolYearForm
    template_name = "academics/schoolyear_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"School year '{form.instance.name}' updated successfully!"
        )
        return super().form_valid(form)


class SchoolYearDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a school year."""

    model = SchoolYear
    template_name = "academics/schoolyear_confirm_delete.html"
    success_url = reverse_lazy("academics:schoolyear_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "School year deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Resource Views
class ResourceListView(LoginRequiredMixin, ListView):
    """List all resources in the library for the current user."""

    model = Resource
    template_name = "academics/resource_list.html"
    context_object_name = "resources"
    paginate_by = 20

    def get_queryset(self):
        queryset = Resource.objects.filter(user=self.request.user)

        # Search functionality
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(author__icontains=search_query)
                | Q(publisher__icontains=search_query)
                | Q(isbn__icontains=search_query),
            )

        # Filter by resource type
        resource_type = self.request.GET.get("resource_type", "")
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        return queryset.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_resource_type"] = self.request.GET.get("resource_type", "")
        context["resource_types"] = Resource.RESOURCE_TYPE_CHOICES
        return context


class ResourceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a resource."""

    model = Resource
    template_name = "academics/resource_detail.html"
    context_object_name = "resource"

    def test_func(self):
        return self.get_object().user == self.request.user


class ResourceCreateView(LoginRequiredMixin, CreateView):
    """Create a new resource."""

    model = Resource
    form_class = ResourceForm
    template_name = "academics/resource_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Resource '{form.instance.title}' created successfully!",
        )
        return super().form_valid(form)


class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing resource."""

    model = Resource
    form_class = ResourceForm
    template_name = "academics/resource_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Resource '{form.instance.title}' updated successfully!",
        )
        return super().form_valid(form)


class ResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a resource."""

    model = Resource
    template_name = "academics/resource_confirm_delete.html"
    success_url = reverse_lazy("academics:resource_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Resource deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    """List all students for the current user."""

    model = Student
    template_name = "academics/student_list.html"
    context_object_name = "students"
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.filter(user=self.request.user).annotate(
            course_count=Count("courses", distinct=True)
        )

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search))

        return queryset


class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a student."""

    model = Student
    template_name = "academics/student_detail.html"
    context_object_name = "student"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()

        context["courses"] = student.courses.select_related("school_year").all()
        context["school_years"] = student.school_years.all()

        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    """Create a new student."""

    model = Student
    form_class = StudentForm
    template_name = "academics/student_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"Student '{form.instance.name}' created successfully!"
        )
        return super().form_valid(form)


class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing student."""

    model = Student
    form_class = StudentForm
    template_name = "academics/student_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"Student '{form.instance.name}' updated successfully!"
        )
        return super().form_valid(form)


class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a student."""

    model = Student
    template_name = "academics/student_confirm_delete.html"
    success_url = reverse_lazy("academics:student_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Student deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    """List all courses for the current user."""

    model = Course
    template_name = "academics/course_list.html"
    context_object_name = "courses"
    paginate_by = 20

    def get_queryset(self):
        queryset = Course.objects.filter(
            student__user=self.request.user
        ).select_related("student", "school_year")

        # Filter by school year if specified
        year_id = self.request.GET.get("year")
        if year_id:
            queryset = queryset.filter(school_year_id=year_id)

        # Filter by student if specified
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_years"] = SchoolYear.objects.filter(user=self.request.user)
        context["students"] = Student.objects.filter(user=self.request.user)
        return context


class CourseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a course."""

    model = Course
    template_name = "academics/course_detail.html"
    context_object_name = "course"

    def test_func(self):
        return self.get_object().student.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        context["resources"] = course.resources.all()

        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """Create a new course."""

    model = Course
    form_class = CourseForm
    template_name = "academics/course_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"Course '{form.instance.name}' created successfully!"
        )
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing course."""

    model = Course
    form_class = CourseForm
    template_name = "academics/course_form.html"

    def test_func(self):
        return self.get_object().student.user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"Course '{form.instance.name}' updated successfully!"
        )
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a course."""

    model = Course
    template_name = "academics/course_confirm_delete.html"
    success_url = reverse_lazy("academics:course_list")

    def test_func(self):
        return self.get_object().student.user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Course deleted successfully!")
        return super().delete(request, *args, **kwargs)


# CurriculumResource Views
class CurriculumResourceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new curriculum resource for a course."""

    model = CurriculumResource
    form_class = CurriculumResourceForm
    template_name = "academics/curriculumresource_form.html"

    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return course.student.user == self.request.user

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        form.instance.course = course
        messages.success(
            self.request, f"Resource '{form.instance.title}' added successfully!"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "academics:course_detail", kwargs={"pk": self.kwargs["course_pk"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return context


class CurriculumResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing curriculum resource."""

    model = CurriculumResource
    form_class = CurriculumResourceForm
    template_name = "academics/curriculumresource_form.html"

    def test_func(self):
        return self.get_object().course.student.user == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request, f"Resource '{form.instance.title}' updated successfully!"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CurriculumResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a curriculum resource."""

    model = CurriculumResource
    template_name = "academics/curriculumresource_confirm_delete.html"

    def test_func(self):
        return self.get_object().course.student.user == self.request.user

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Resource deleted successfully!")
        return super().delete(request, *args, **kwargs)


# DailyLog / Attendance Views
class DailyLogListView(LoginRequiredMixin, ListView):
    """List all daily logs for the current user."""

    model = DailyLog
    template_name = "academics/dailylog_list.html"
    context_object_name = "daily_logs"
    paginate_by = 20

    def get_queryset(self):
        queryset = DailyLog.objects.filter(user=self.request.user).select_related(
            "student"
        )

        # Filter by student if specified
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by date range
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["students"] = Student.objects.filter(user=self.request.user)
        return context


class DailyLogDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a daily log with course notes."""

    model = DailyLog
    template_name = "academics/dailylog_detail.html"
    context_object_name = "daily_log"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        daily_log = self.get_object()

        context["course_notes"] = daily_log.course_notes.select_related("course").all()

        return context


class DailyLogCreateView(LoginRequiredMixin, CreateView):
    """Create a new daily log."""

    model = DailyLog
    form_class = DailyLogForm
    template_name = "academics/dailylog_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["date"] = date.today()
        return initial

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Daily log for {form.instance.student.name} on {form.instance.date} created successfully!",
        )
        return super().form_valid(form)


class DailyLogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing daily log."""

    model = DailyLog
    form_class = DailyLogForm
    template_name = "academics/dailylog_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Daily log for {form.instance.student.name} on {form.instance.date} updated successfully!",
        )
        return super().form_valid(form)


class DailyLogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a daily log."""

    model = DailyLog
    template_name = "academics/dailylog_confirm_delete.html"
    success_url = reverse_lazy("academics:dailylog_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Daily log deleted successfully!")
        return super().delete(request, *args, **kwargs)


class DailyLogEntryView(LoginRequiredMixin, View):
    """View for entering daily log with course notes for all student's courses."""

    template_name = "academics/dailylog_entry.html"

    def get(self, request, student_pk=None, log_date=None):
        """Display the daily log entry form."""
        # Get or set the date
        if log_date:
            try:
                entry_date = date.fromisoformat(log_date)
            except ValueError:
                entry_date = date.today()
        else:
            entry_date = date.today()

        # Get students
        students = Student.objects.filter(user=request.user)

        # Get selected student
        if student_pk:
            student = get_object_or_404(Student, pk=student_pk, user=request.user)
        else:
            student = students.first()

        if not student:
            messages.warning(request, "Please create a student first.")
            return redirect("academics:student_create")

        # Try to get existing daily log (but don't create one yet)
        try:
            daily_log = DailyLog.objects.get(student=student, date=entry_date)
        except DailyLog.DoesNotExist:
            daily_log = None

        # Get student's courses for the active school year
        active_year = SchoolYear.objects.filter(
            user=request.user, is_active=True
        ).first()
        courses = Course.objects.filter(student=student)
        if active_year:
            courses = courses.filter(school_year=active_year)

        # Get existing course notes (if daily log exists)
        existing_notes = {}
        if daily_log:
            existing_notes = {
                note.course_id: note for note in daily_log.course_notes.all()
            }

        # Prepare course notes data
        course_notes_data = []
        for course in courses:
            note = existing_notes.get(course.id)
            course_notes_data.append(
                {
                    "course": course,
                    "note": note,
                    "notes_text": note.notes if note else "",
                }
            )

        context = {
            "daily_log": daily_log,
            "student": student,
            "students": students,
            "entry_date": entry_date,
            "course_notes_data": course_notes_data,
        }

        return render(request, self.template_name, context)

    def post(self, request, student_pk=None, log_date=None):
        """Handle the daily log entry form submission."""
        # Get the date
        if log_date:
            try:
                entry_date = date.fromisoformat(log_date)
            except ValueError:
                entry_date = date.today()
        else:
            entry_date = date.today()

        # Get student
        if student_pk:
            student = get_object_or_404(Student, pk=student_pk, user=request.user)
        else:
            messages.error(request, "Student is required.")
            return redirect("academics:dailylog_entry")

        # Get or create daily log
        daily_log, created = DailyLog.objects.get_or_create(
            student=student,
            date=entry_date,
            defaults={"user": request.user, "status": "PRESENT"},
        )

        # Update daily log fields
        status = request.POST.get("status", "PRESENT")
        general_notes = request.POST.get("general_notes", "")
        daily_log.status = status
        daily_log.general_notes = general_notes
        daily_log.save()

        # Process course notes
        courses = Course.objects.filter(student=student)
        active_year = SchoolYear.objects.filter(
            user=request.user, is_active=True
        ).first()
        if active_year:
            courses = courses.filter(school_year=active_year)

        for course in courses:
            notes_text = request.POST.get(f"course_notes_{course.id}", "").strip()
            if notes_text:
                # Create or update course note
                CourseNote.objects.update_or_create(
                    daily_log=daily_log,
                    course=course,
                    defaults={"notes": notes_text, "user": request.user},
                )
            else:
                # Delete course note if exists and notes are empty
                CourseNote.objects.filter(daily_log=daily_log, course=course).delete()

        messages.success(
            request,
            f"Daily log for {student.name} on {entry_date.strftime('%B %d, %Y')} saved successfully!",
        )

        # Redirect back to the entry form
        return redirect(
            "academics:dailylog_entry_date",
            student_pk=student.pk,
            log_date=entry_date.isoformat(),
        )


class AttendanceCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view showing attendance for the current week/month."""

    template_name = "academics/attendance_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get date range (default to current week)
        view_type = self.request.GET.get("view", "week")  # week or month

        # Get the reference date (default to today)
        ref_date_str = self.request.GET.get("date")
        if ref_date_str:
            try:
                ref_date = date.fromisoformat(ref_date_str)
            except ValueError:
                ref_date = date.today()
        else:
            ref_date = date.today()

        if view_type == "week":
            # Calculate the start of the week (Monday)
            start_date = ref_date - timedelta(days=ref_date.weekday())
            end_date = start_date + timedelta(days=6)
            date_range = [start_date + timedelta(days=i) for i in range(7)]
        else:  # month
            # Calculate the start and end of the month
            start_date = ref_date.replace(day=1)
            if ref_date.month == 12:
                end_date = ref_date.replace(
                    year=ref_date.year + 1, month=1, day=1
                ) - timedelta(days=1)
            else:
                end_date = ref_date.replace(
                    month=ref_date.month + 1, day=1
                ) - timedelta(days=1)
            date_range = [
                start_date + timedelta(days=i)
                for i in range((end_date - start_date).days + 1)
            ]

        # Get students
        students = Student.objects.filter(user=user).prefetch_related("daily_logs")

        # Get daily logs for the date range
        daily_logs = (
            DailyLog.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date,
            )
            .select_related("student")
            .prefetch_related("course_notes")
        )

        # Organize logs by student and date, and track which logs have course notes
        logs_by_student_date = {}
        logs_with_notes = set()
        for log in daily_logs:
            if log.student_id not in logs_by_student_date:
                logs_by_student_date[log.student_id] = {}
            logs_by_student_date[log.student_id][log.date.isoformat()] = log

            # Check if this log has any course notes
            if log.course_notes.exists():
                logs_with_notes.add(log.id)

        # Build attendance grid
        attendance_grid = []
        for student in students:
            row = {"student": student, "dates": []}
            for d in date_range:
                log = logs_by_student_date.get(student.id, {}).get(d.isoformat())
                has_notes = log.id in logs_with_notes if log else False
                row["dates"].append({"date": d, "log": log, "has_notes": has_notes})
            attendance_grid.append(row)

        context["view_type"] = view_type
        context["ref_date"] = ref_date
        context["start_date"] = start_date
        context["end_date"] = end_date
        context["date_range"] = date_range
        context["attendance_grid"] = attendance_grid
        context["prev_date"] = (
            start_date - timedelta(days=7 if view_type == "week" else 30)
        ).isoformat()
        context["next_date"] = (end_date + timedelta(days=1)).isoformat()

        return context


class AttendanceReportView(LoginRequiredMixin, TemplateView):
    """Report view for attendance statistics and compliance."""

    template_name = "academics/attendance_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get school year filter
        year_id = self.request.GET.get("year")
        if year_id:
            school_year = get_object_or_404(SchoolYear, pk=year_id, user=user)
        else:
            school_year = SchoolYear.objects.filter(user=user, is_active=True).first()

        # Get student filter
        student_id = self.request.GET.get("student")
        students_queryset = Student.objects.filter(user=user)
        if student_id:
            students_queryset = students_queryset.filter(pk=student_id)

        # Build report data
        report_data = []
        for student in students_queryset:
            # Get daily logs for this student in the school year
            logs_query = DailyLog.objects.filter(student=student)
            if school_year:
                logs_query = logs_query.filter(
                    date__gte=school_year.start_date, date__lte=school_year.end_date
                )

            total_days = logs_query.count()
            present_days = logs_query.filter(status="PRESENT").count()
            field_trip_days = logs_query.filter(status="FIELD_TRIP").count()
            absent_days = logs_query.filter(status="ABSENT").count()
            sick_days = logs_query.filter(status="SICK").count()
            holiday_days = logs_query.filter(status="HOLIDAY").count()
            instructional_days = present_days + field_trip_days

            report_data.append(
                {
                    "student": student,
                    "total_days": total_days,
                    "instructional_days": instructional_days,
                    "present_days": present_days,
                    "field_trip_days": field_trip_days,
                    "absent_days": absent_days,
                    "sick_days": sick_days,
                    "holiday_days": holiday_days,
                }
            )

        context["school_year"] = school_year
        context["school_years"] = SchoolYear.objects.filter(user=user)
        context["students"] = Student.objects.filter(user=user)
        context["selected_student_id"] = int(student_id) if student_id else None
        context["report_data"] = report_data

        return context


class AttendanceReportPDFView(LoginRequiredMixin, View):
    """PDF export view for attendance reports."""

    def get(self, request):
        """Generate and return PDF attendance report."""
        user = request.user

        # Get school year filter
        year_id = request.GET.get("year")
        if year_id:
            school_year = get_object_or_404(SchoolYear, pk=year_id, user=user)
        else:
            school_year = SchoolYear.objects.filter(user=user, is_active=True).first()

        # Get student filter
        student_id = request.GET.get("student")
        students_queryset = Student.objects.filter(user=user)
        if student_id:
            students_queryset = students_queryset.filter(pk=student_id)

        # Build report data (same logic as AttendanceReportView)
        report_data = []
        for student in students_queryset:
            logs_query = DailyLog.objects.filter(student=student)
            if school_year:
                logs_query = logs_query.filter(
                    date__gte=school_year.start_date, date__lte=school_year.end_date
                )

            total_days = logs_query.count()
            present_days = logs_query.filter(status="PRESENT").count()
            field_trip_days = logs_query.filter(status="FIELD_TRIP").count()
            absent_days = logs_query.filter(status="ABSENT").count()
            sick_days = logs_query.filter(status="SICK").count()
            holiday_days = logs_query.filter(status="HOLIDAY").count()
            instructional_days = present_days + field_trip_days

            # Get courses for this student in the school year
            courses_query = Course.objects.filter(student=student).prefetch_related(
                "resources"
            )
            if school_year:
                courses_query = courses_query.filter(school_year=school_year)

            report_data.append(
                {
                    "student": student,
                    "total_days": total_days,
                    "instructional_days": instructional_days,
                    "present_days": present_days,
                    "field_trip_days": field_trip_days,
                    "absent_days": absent_days,
                    "sick_days": sick_days,
                    "holiday_days": holiday_days,
                    "courses": courses_query,
                }
            )

        # Chunk report_data into groups of 3 for table layout
        report_data_chunks = []
        for i in range(0, len(report_data), 3):
            report_data_chunks.append(report_data[i : i + 3])

        # Prepare context for PDF template
        context = {
            "school_year": school_year,
            "report_data": report_data,
            "report_data_chunks": report_data_chunks,
            "user": user,
            "generated_date": date.today(),
        }

        # Render HTML template
        html_string = render_to_string("academics/attendance_report_pdf.html", context)

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # Return PDF response
        response = HttpResponse(pdf, content_type="application/pdf")
        filename = f"attendance_report_{school_year.name if school_year else 'all'}_{date.today().isoformat()}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


# =============================================================================
# HTMX Attendance Quick Actions
# =============================================================================


@require_http_methods(["GET"])
@login_required
def attendance_quick_toggle(request, student_pk, log_date):
    """
    HTMX endpoint: Show status selector dropdown for a specific student/date.
    Returns HTML fragment for status selection.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get existing log if any
    daily_log = DailyLog.objects.filter(student=student, date=date_obj).first()

    context = {
        "student": student,
        "date": date_obj,
        "date_str": log_date,
        "current_status": daily_log.status if daily_log else None,
    }

    return render(request, "academics/partials/status_selector.html", context)


@require_http_methods(["POST"])
@login_required
def attendance_quick_update(request, student_pk, log_date):
    """
    HTMX endpoint: Update attendance status for a specific student/date.
    Returns updated badge HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get new status from form
    new_status = request.POST.get("status")
    if new_status not in ["PRESENT", "ABSENT", "SICK", "HOLIDAY", "FIELD_TRIP"]:
        return HttpResponse("Invalid status", status=400)

    # Update or create daily log
    daily_log, created = DailyLog.objects.update_or_create(
        student=student,
        date=date_obj,
        defaults={"status": new_status, "user": request.user},
    )

    # Check if there are any course notes for this log
    has_notes = CourseNote.objects.filter(daily_log=daily_log).exists()

    context = {
        "student": student,
        "date_str": log_date,
        "log": daily_log,
        "has_notes": has_notes,
    }

    # Return updated badge
    response = render(request, "academics/partials/status_badge.html", context)

    # Close the dropdown by also clearing the selector container
    response["HX-Trigger"] = "closeDropdown"

    return response


@require_http_methods(["DELETE"])
@login_required
def attendance_quick_delete(request, student_pk, log_date):
    """
    HTMX endpoint: Delete attendance log for a specific student/date.
    Returns empty badge HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Delete daily log if exists (cascade will delete course notes)
    DailyLog.objects.filter(student=student, date=date_obj, user=request.user).delete()

    context = {
        "student": student,
        "date_str": log_date,
        "log": None,
        "has_notes": False,
    }

    return render(request, "academics/partials/status_badge.html", context)


@require_http_methods(["GET"])
@login_required
def attendance_course_notes(request, student_pk, log_date):
    """
    HTMX endpoint: Show course notes modal for a specific student/date.
    Returns modal HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get existing log if any
    daily_log = DailyLog.objects.filter(student=student, date=date_obj).first()

    # Get active school year
    active_year = SchoolYear.objects.filter(user=request.user, is_active=True).first()

    # Get courses for this student in the active school year
    courses = Course.objects.filter(student=student)
    if active_year:
        courses = courses.filter(school_year=active_year)
    courses = courses.select_related("school_year").order_by("name")

    # Get existing course notes if log exists
    course_notes = {}
    if daily_log:
        notes_qs = CourseNote.objects.filter(daily_log=daily_log).select_related(
            "course"
        )
        course_notes = {note.course.id: note.notes for note in notes_qs}

    context = {
        "student": student,
        "date": date_obj,
        "date_str": log_date,
        "daily_log": daily_log,
        "courses": courses,
        "course_notes": course_notes,
    }

    return render(request, "academics/partials/course_notes_modal.html", context)


@require_http_methods(["POST"])
@login_required
def attendance_save_course_notes(request, student_pk, log_date):
    """
    HTMX endpoint: Save course notes for a specific student/date.
    Returns success message or closes modal.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get or create daily log
    daily_log, created = DailyLog.objects.get_or_create(
        student=student,
        date=date_obj,
        defaults={"status": "PRESENT", "user": request.user},
    )

    # Get active school year
    active_year = SchoolYear.objects.filter(user=request.user, is_active=True).first()

    # Get courses for this student
    courses = Course.objects.filter(student=student)
    if active_year:
        courses = courses.filter(school_year=active_year)

    # Save course notes
    saved_count = 0
    for course in courses:
        note_text = request.POST.get(f"course_{course.id}", "").strip()

        if note_text:
            # Create or update course note
            CourseNote.objects.update_or_create(
                daily_log=daily_log,
                course=course,
                defaults={"notes": note_text, "user": request.user},
            )
            saved_count += 1
        else:
            # Delete course note if text is empty
            CourseNote.objects.filter(daily_log=daily_log, course=course).delete()

    # Check if there are any course notes for this log
    has_notes = CourseNote.objects.filter(daily_log=daily_log).exists()

    # Render updated badge with out-of-band swap to update the cell
    # The badge template already has the wrapper div with id, so we need to add hx-swap-oob to it
    badge_html = render_to_string(
        "academics/partials/status_badge.html",
        {
            "student": student,
            "date_str": log_date,
            "log": daily_log,
            "has_notes": has_notes,
        },
    )

    # Add hx-swap-oob attribute to the badge HTML
    # The badge template starts with <div id="cell-...">
    badge_html_with_oob = badge_html.replace(
        f'<div id="cell-{student_pk}-{log_date}"',
        f'<div id="cell-{student_pk}-{log_date}" hx-swap-oob="true"',
        1,
    )

    # Return updated badge HTML with OOB swap to update the badge, and closes modal
    return HttpResponse(badge_html_with_oob)
