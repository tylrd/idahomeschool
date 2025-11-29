from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import SchoolYearForm
from idahomeschool.academics.models import SchoolYear


class SchoolYearListView(LoginRequiredMixin, ListView):
    """List all school years for the current user."""

    model = SchoolYear
    template_name = "academics/schoolyear_list.html"
    context_object_name = "school_years"
    paginate_by = 20

    def get_queryset(self):
        return SchoolYear.objects.filter(user=self.request.user).annotate(
            student_count=Count("students", distinct=True),
            course_count=Count("course_enrollments", distinct=True),
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
        context["enrollments"] = school_year.course_enrollments.select_related(
            "student",
            "course",
        ).all()

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
            self.request, f"School year '{form.instance.name}' created successfully!",
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
            self.request, f"School year '{form.instance.name}' updated successfully!",
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
