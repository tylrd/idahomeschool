from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CourseForm, CurriculumResourceForm, SchoolYearForm, StudentForm
from .models import Course, CurriculumResource, SchoolYear, Student


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard showing overview of all academic records."""

    template_name = "academics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get active school year
        active_year = SchoolYear.objects.filter(user=user, is_active=True).first()

        context["active_year"] = active_year
        context["total_students"] = Student.objects.filter(user=user).count()
        context["total_school_years"] = SchoolYear.objects.filter(user=user).count()

        if active_year:
            context["active_courses"] = Course.objects.filter(
                school_year=active_year,
                student__user=user,
            ).select_related("student", "school_year")

        context["recent_students"] = Student.objects.filter(user=user).order_by("-created_at")[:5]
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
        messages.success(self.request, f"School year '{form.instance.name}' created successfully!")
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
        messages.success(self.request, f"School year '{form.instance.name}' updated successfully!")
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
        messages.success(self.request, f"Student '{form.instance.name}' created successfully!")
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
        messages.success(self.request, f"Student '{form.instance.name}' updated successfully!")
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
        queryset = Course.objects.filter(student__user=self.request.user).select_related(
            "student", "school_year"
        )

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
        messages.success(self.request, f"Course '{form.instance.name}' created successfully!")
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
        messages.success(self.request, f"Course '{form.instance.name}' updated successfully!")
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
        messages.success(self.request, f"Resource '{form.instance.title}' added successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("academics:course_detail", kwargs={"pk": self.kwargs["course_pk"]})

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
        messages.success(self.request, f"Resource '{form.instance.title}' updated successfully!")
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
