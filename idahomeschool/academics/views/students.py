from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import StudentForm
from idahomeschool.academics.forms import StudentGradeYearForm
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student
from idahomeschool.academics.models import StudentGradeYear


# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    """List all students for the current user."""

    model = Student
    template_name = "academics/student_list.html"
    context_object_name = "students"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Student.objects.filter(user=self.request.user)
            .annotate(
                course_count=Count("course_enrollments", distinct=True),
            )
            .prefetch_related("grade_years__grade_level", "grade_years__school_year")
        )

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active school year for grade display
        active_year = SchoolYear.objects.filter(
            user=self.request.user,
            is_active=True,
        ).first()
        context["active_year"] = active_year

        # Add current grade to each student for display
        if active_year:
            for student in context["students"]:
                student.current_grade = student.get_grade_for_year(active_year)

        return context


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

        context["enrollments"] = student.course_enrollments.select_related(
            "course",
            "school_year",
        ).all()
        context["school_years"] = student.school_years.all()
        context["grade_years"] = student.grade_years.select_related(
            "school_year",
            "grade_level",
        ).all()

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
            self.request, f"Student '{form.instance.name}' created successfully!",
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
            self.request, f"Student '{form.instance.name}' updated successfully!",
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


# StudentGradeYear Views
class StudentGradeYearCreateView(LoginRequiredMixin, CreateView):
    """Assign a student to a grade for a specific school year."""

    model = StudentGradeYear
    form_class = StudentGradeYearForm
    template_name = "academics/studentgradeyear_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        # If student_pk is in URL, pre-fill the student
        student_pk = self.kwargs.get("student_pk")
        if student_pk:
            student = get_object_or_404(
                Student,
                pk=student_pk,
                user=self.request.user,
            )
            kwargs["student"] = student

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_pk = self.kwargs.get("student_pk")
        if student_pk:
            context["student"] = get_object_or_404(
                Student,
                pk=student_pk,
                user=self.request.user,
            )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Grade assignment for {form.instance.student.name} created successfully!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.student.get_absolute_url()


class StudentGradeYearUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    """Update a student's grade assignment for a school year."""

    model = StudentGradeYear
    form_class = StudentGradeYearForm
    template_name = "academics/studentgradeyear_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["student"] = self.get_object().student
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_object().student
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Grade assignment for {form.instance.student.name} updated successfully!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.student.get_absolute_url()


class StudentGradeYearDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    """Delete a student's grade assignment."""

    model = StudentGradeYear
    template_name = "academics/studentgradeyear_confirm_delete.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Grade assignment deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.student.get_absolute_url()
