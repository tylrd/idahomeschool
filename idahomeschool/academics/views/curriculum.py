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

from idahomeschool.academics.forms import CourseTemplateForm
from idahomeschool.academics.forms import CurriculumResourceForm
from idahomeschool.academics.models import Course
from idahomeschool.academics.models import CourseTemplate
from idahomeschool.academics.models import CurriculumResource


# CourseTemplate Views
class CourseTemplateListView(LoginRequiredMixin, ListView):
    """List all course templates for the current user."""

    model = CourseTemplate
    template_name = "academics/coursetemplate_list.html"
    context_object_name = "course_templates"
    paginate_by = 20

    def get_queryset(self):
        queryset = CourseTemplate.objects.filter(user=self.request.user).annotate(
            course_count=Count("courses", distinct=True),
        )

        # Search functionality
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class CourseTemplateDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a course template."""

    model = CourseTemplate
    template_name = "academics/coursetemplate_detail.html"
    context_object_name = "course_template"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.get_object()
        context["courses"] = template.courses.all()
        context["suggested_resources"] = template.suggested_resources.all()
        return context


class CourseTemplateCreateView(LoginRequiredMixin, CreateView):
    """Create a new course template."""

    model = CourseTemplate
    form_class = CourseTemplateForm
    template_name = "academics/coursetemplate_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Course template '{form.instance.name}' created successfully!",
        )
        return super().form_valid(form)


class CourseTemplateUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing course template."""

    model = CourseTemplate
    form_class = CourseTemplateForm
    template_name = "academics/coursetemplate_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Course template '{form.instance.name}' updated successfully!",
        )
        return super().form_valid(form)


class CourseTemplateDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a course template."""

    model = CourseTemplate
    template_name = "academics/coursetemplate_confirm_delete.html"
    success_url = reverse_lazy("academics:coursetemplate_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Course template deleted successfully!")
        return super().delete(request, *args, **kwargs)


# CurriculumResource Views
class CurriculumResourceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new curriculum resource for a course."""

    model = CurriculumResource
    form_class = CurriculumResourceForm
    template_name = "academics/curriculumresource_form.html"

    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return course.user == self.request.user

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        form.instance.course = course
        messages.success(
            self.request, f"Resource '{form.instance.title}' added successfully!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "academics:course_detail", kwargs={"pk": self.kwargs["course_pk"]},
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
        return self.get_object().course.user == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request, f"Resource '{form.instance.title}' updated successfully!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CurriculumResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a curriculum resource."""

    model = CurriculumResource
    template_name = "academics/curriculumresource_confirm_delete.html"

    def test_func(self):
        return self.get_object().course.user == self.request.user

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Resource deleted successfully!")
        return super().delete(request, *args, **kwargs)
