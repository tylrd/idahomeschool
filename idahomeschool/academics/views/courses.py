from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import CourseEnrollmentForm
from idahomeschool.academics.forms import CourseForm
from idahomeschool.academics.models import Course
from idahomeschool.academics.models import CourseEnrollment
from idahomeschool.academics.models import GradeLevel
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student


# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    """List all courses for the current user."""

    model = Course
    template_name = "academics/course_list.html"
    context_object_name = "courses"
    paginate_by = None  # Disable pagination for grouped view

    def get_queryset(self):
        queryset = (
            Course.objects.filter(user=self.request.user)
            .prefetch_related(
                "resources",
                "enrollments",
            )
            .select_related("grade_level")
        )

        # Search functionality
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # Filter by grade level
        grade_filter = self.request.GET.get("grade", "")
        if grade_filter:
            queryset = queryset.filter(grade_level__id=grade_filter)

        return queryset.order_by("grade_level__order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["grade_filter"] = self.request.GET.get("grade", "")
        context["grade_levels"] = GradeLevel.objects.filter(
            user=self.request.user,
        )

        # Group courses by grade level
        courses = self.get_queryset()
        grouped_courses = {}
        unassigned_courses = []

        for course in courses:
            if course.grade_level:
                grade_level = course.grade_level
                if grade_level not in grouped_courses:
                    grouped_courses[grade_level] = []
                grouped_courses[grade_level].append(course)
            else:
                unassigned_courses.append(course)

        # Sort grade levels by order
        sorted_grade_levels = sorted(grouped_courses.items(), key=lambda x: x[0].order)

        context["grouped_courses"] = sorted_grade_levels
        context["unassigned_courses"] = unassigned_courses
        return context


class CourseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a course."""

    model = Course
    template_name = "academics/course_detail.html"
    context_object_name = "course"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        context["resources"] = course.resources.prefetch_related("tags").all()
        context["enrollments"] = course.enrollments.select_related(
            "student",
            "school_year",
        ).all()

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
            self.request, f"Course '{form.instance.name}' created successfully!",
        )
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing course."""

    model = Course
    form_class = CourseForm
    template_name = "academics/course_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request, f"Course '{form.instance.name}' updated successfully!",
        )
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a course."""

    model = Course
    template_name = "academics/course_confirm_delete.html"
    success_url = reverse_lazy("academics:course_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Course deleted successfully!")
        return super().delete(request, *args, **kwargs)


# CourseEnrollment Views
class CourseEnrollmentListView(LoginRequiredMixin, ListView):
    """List all course enrollments for the current user."""

    model = CourseEnrollment
    template_name = "academics/courseenrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 20

    def get_queryset(self):
        queryset = CourseEnrollment.objects.filter(
            user=self.request.user,
        ).select_related("student", "course", "course__grade_level", "school_year")

        # Filter by student
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by school year
        school_year_id = self.request.GET.get("school_year")
        if school_year_id:
            queryset = queryset.filter(school_year_id=school_year_id)

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["students"] = Student.objects.filter(user=self.request.user)
        context["school_years"] = SchoolYear.objects.filter(user=self.request.user)
        context["statuses"] = CourseEnrollment.STATUS_CHOICES
        context["selected_student"] = self.request.GET.get("student", "")
        context["selected_school_year"] = self.request.GET.get("school_year", "")
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class CourseEnrollmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a course enrollment."""

    model = CourseEnrollment
    template_name = "academics/courseenrollment_detail.html"
    context_object_name = "enrollment"

    def test_func(self):
        return self.get_object().user == self.request.user


class CourseEnrollmentCreateView(LoginRequiredMixin, CreateView):
    """Create a new course enrollment."""

    model = CourseEnrollment
    form_class = CourseEnrollmentForm
    template_name = "academics/courseenrollment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Course enrollment created successfully!")
        return super().form_valid(form)


class CourseEnrollmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing course enrollment."""

    model = CourseEnrollment
    form_class = CourseEnrollmentForm
    template_name = "academics/courseenrollment_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Course enrollment updated successfully!")
        return super().form_valid(form)


class CourseEnrollmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a course enrollment."""

    model = CourseEnrollment
    template_name = "academics/courseenrollment_confirm_delete.html"
    success_url = reverse_lazy("academics:courseenrollment_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Course enrollment deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
@require_http_methods(["GET"])
def filter_courses_by_student(request):
    """HTMX endpoint to filter courses by student's grade level."""
    student_id = request.GET.get("student")
    school_year_id = request.GET.get("school_year")

    # Get all courses for the user
    courses = Course.objects.filter(user=request.user).select_related(
        "grade_level",
    )

    # If both student and school year are provided, filter by grade level
    if student_id and school_year_id:
        try:
            student = Student.objects.get(pk=student_id, user=request.user)
            school_year = SchoolYear.objects.get(
                pk=school_year_id,
                user=request.user,
            )

            # Get the student's grade level for this school year
            student_grade = student.get_grade_for_year(school_year)

            if student_grade:
                # Filter: matching grade level or no grade level (universal)
                courses = courses.filter(
                    Q(grade_level=student_grade) | Q(grade_level__isnull=True),
                )
        except (Student.DoesNotExist, SchoolYear.DoesNotExist):
            pass

    # Render course options
    html = '<option value="">---------</option>'
    for course in courses.order_by("grade_level__order", "name"):
        grade_label = (
            f" ({course.grade_level.name})" if course.grade_level else " (Any)"
        )
        html += f'<option value="{course.pk}">{course.name}{grade_label}</option>'

    return HttpResponse(html)
