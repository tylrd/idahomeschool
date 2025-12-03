from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import GradeLevelForm
from idahomeschool.academics.models import GradeLevel
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student
from idahomeschool.academics.models import StudentGradeYear


# GradeLevel Views
class GradeLevelListView(LoginRequiredMixin, ListView):
    """List all grade levels for the current user."""

    model = GradeLevel
    template_name = "academics/gradelevel_list.html"
    context_object_name = "grade_levels"
    paginate_by = 20

    def get_queryset(self):
        return GradeLevel.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if there are any grade levels
        context["has_grades"] = context["grade_levels"].exists()
        return context


class GradeLevelDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a grade level."""

    model = GradeLevel
    template_name = "academics/gradelevel_detail.html"
    context_object_name = "grade_level"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade_level = self.get_object()

        # Get courses for this grade
        context["courses"] = grade_level.courses.all()

        # Get students currently in this grade (active year)
        active_year = SchoolYear.objects.filter(
            user=self.request.user,
            is_active=True,
        ).first()
        if active_year:
            context["current_students"] = Student.objects.filter(
                grade_years__grade_level=grade_level,
                grade_years__school_year=active_year,
            )

        # Get all student-year assignments for this grade
        context["student_assignments"] = StudentGradeYear.objects.filter(
            grade_level=grade_level,
        ).select_related("student", "school_year")

        return context


class GradeLevelCreateView(LoginRequiredMixin, CreateView):
    """Create a new grade level."""

    model = GradeLevel
    form_class = GradeLevelForm
    template_name = "academics/gradelevel_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Grade level '{form.instance.name}' created successfully!",
        )
        return super().form_valid(form)


class GradeLevelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing grade level."""

    model = GradeLevel
    form_class = GradeLevelForm
    template_name = "academics/gradelevel_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        # For HTMX requests, return the updated table row
        if self.request.htmx:
            return render(
                self.request,
                "academics/partials/gradelevel_row.html",
                {"grade_level": self.object},
            )

        messages.success(
            self.request,
            f"Grade level '{form.instance.name}' updated successfully!",
        )
        return response


class GradeLevelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a grade level."""

    model = GradeLevel
    template_name = "academics/gradelevel_confirm_delete.html"
    success_url = reverse_lazy("academics:gradelevel_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        # For HTMX requests, return empty content to trigger row removal
        if self.request.htmx:
            from django.http import HttpResponse
            return HttpResponse("")

        messages.success(self.request, "Grade level deleted successfully!")
        return response


@login_required
@require_http_methods(["POST"])
def create_pk12_grades(request):
    """Bulk create PK-12 grade levels for the user."""
    user = request.user

    # Check if user already has grades
    existing_count = GradeLevel.objects.filter(user=user).count()
    if existing_count > 0:
        messages.warning(
            request,
            "You already have grade levels defined. "
            "Delete them first if you want to recreate.",
        )
        return redirect("academics:gradelevel_list")

    # Define standard PK-12 grades
    grades = [
        ("Pre-Kindergarten", 0),
        ("Kindergarten", 1),
        ("1st Grade", 2),
        ("2nd Grade", 3),
        ("3rd Grade", 4),
        ("4th Grade", 5),
        ("5th Grade", 6),
        ("6th Grade", 7),
        ("7th Grade", 8),
        ("8th Grade", 9),
        ("9th Grade", 10),
        ("10th Grade", 11),
        ("11th Grade", 12),
        ("12th Grade", 13),
    ]

    # Bulk create all grades
    grade_objects = [
        GradeLevel(user=user, name=name, order=order)
        for name, order in grades
    ]
    GradeLevel.objects.bulk_create(grade_objects)

    messages.success(
        request,
        f"Successfully created {len(grades)} grade levels (PK-12)!",
    )
    return redirect("academics:gradelevel_list")
