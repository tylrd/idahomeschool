"""Reading list views for tracking books students read."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import BookTagPreferenceForm
from idahomeschool.academics.forms import ReadingListForm
from idahomeschool.academics.models import BookTagPreference
from idahomeschool.academics.models import ReadingList
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student
from idahomeschool.academics.models import Tag


# Reading List Views
class ReadingListView(LoginRequiredMixin, ListView):
    """List all reading list entries for all students."""

    model = ReadingList
    template_name = "academics/reading_list.html"
    context_object_name = "reading_list_entries"
    paginate_by = 20

    def get_queryset(self):
        queryset = ReadingList.objects.filter(
            user=self.request.user,
        ).select_related("student", "resource", "school_year").prefetch_related(
            "resource__tags",
        )

        # Filter by student
        student_id = self.request.GET.get("student", "")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by status
        status = self.request.GET.get("status", "")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by school year
        school_year_id = self.request.GET.get("school_year", "")
        if school_year_id:
            queryset = queryset.filter(school_year_id=school_year_id)

        # Search by book title or author
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(resource__title__icontains=search_query)
                | Q(resource__author__icontains=search_query),
            )

        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["students"] = Student.objects.filter(user=self.request.user)
        context["school_years"] = SchoolYear.objects.filter(user=self.request.user)
        context["statuses"] = ReadingList.STATUS_CHOICES
        context["selected_student"] = self.request.GET.get("student", "")
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_school_year"] = self.request.GET.get("school_year", "")
        context["search_query"] = self.request.GET.get("search", "")

        # Get book tag preferences
        book_tags = BookTagPreference.get_book_tags_for_user(self.request.user)
        context["book_tags"] = book_tags
        context["has_book_tags"] = book_tags.exists()

        return context


class StudentReadingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List reading list entries for a specific student."""

    model = ReadingList
    template_name = "academics/student_reading_list.html"
    context_object_name = "reading_list_entries"
    paginate_by = 20

    def test_func(self):
        student = get_object_or_404(Student, pk=self.kwargs["pk"])
        return student.user == self.request.user

    def get_queryset(self):
        student_id = self.kwargs["pk"]
        queryset = ReadingList.objects.filter(
            student_id=student_id,
        ).select_related("resource", "school_year").prefetch_related(
            "resource__tags",
        )

        # Filter by status
        status = self.request.GET.get("status", "")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by school year
        school_year_id = self.request.GET.get("school_year", "")
        if school_year_id:
            queryset = queryset.filter(school_year_id=school_year_id)

        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, pk=self.kwargs["pk"])
        context["student"] = student
        context["school_years"] = SchoolYear.objects.filter(user=self.request.user)
        context["statuses"] = ReadingList.STATUS_CHOICES
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_school_year"] = self.request.GET.get("school_year", "")

        # Get counts by status
        all_entries = ReadingList.objects.filter(student=student)
        context["to_read_count"] = all_entries.filter(status="TO_READ").count()
        context["reading_count"] = all_entries.filter(status="READING").count()
        context["completed_count"] = all_entries.filter(status="COMPLETED").count()
        context["dnf_count"] = all_entries.filter(status="DID_NOT_FINISH").count()

        return context


class ReadingListCreateView(LoginRequiredMixin, CreateView):
    """Add a book to a student's reading list."""

    model = ReadingList
    form_class = ReadingListForm
    template_name = "academics/reading_list_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        # If coming from student detail page
        student_id = self.request.GET.get("student")
        if student_id:
            try:
                student = Student.objects.get(pk=student_id, user=self.request.user)
                kwargs["student"] = student
            except Student.DoesNotExist:
                pass
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user has configured book tags
        book_tags = BookTagPreference.get_book_tags_for_user(self.request.user)
        context["has_book_tags"] = book_tags.exists()
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f"'{form.instance.resource.title}' added to "
            f"{form.instance.student.name}'s reading list!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        # If student was pre-selected, return to student's reading list
        if self.object.student:
            return reverse(
                "academics:student_reading_list",
                kwargs={"pk": self.object.student.pk},
            )
        return reverse("academics:reading_list")


class ReadingListUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a reading list entry (progress, status, rating, notes)."""

    model = ReadingList
    form_class = ReadingListForm
    template_name = "academics/reading_list_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Reading list entry for '{form.instance.resource.title}' updated!",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "academics:student_reading_list",
            kwargs={"pk": self.object.student.pk},
        )


class ReadingListDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Remove a book from a student's reading list."""

    model = ReadingList
    template_name = "academics/reading_list_confirm_delete.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse(
            "academics:student_reading_list",
            kwargs={"pk": self.object.student.pk},
        )

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            self.request,
            f"'{obj.resource.title}' removed from {obj.student.name}'s reading list!",
        )
        return super().delete(request, *args, **kwargs)


class ReadingListDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a reading list entry."""

    model = ReadingList
    template_name = "academics/reading_list_detail.html"
    context_object_name = "entry"

    def test_func(self):
        return self.get_object().user == self.request.user


# Book Tag Preference Views
class BookTagPreferenceView(LoginRequiredMixin, UpdateView):
    """Configure which tags identify books for the reading list."""

    model = BookTagPreference
    form_class = BookTagPreferenceForm
    template_name = "academics/book_tag_preferences.html"
    success_url = reverse_lazy("academics:book_tag_preferences")

    def get_object(self, queryset=None):
        obj, _created = BookTagPreference.objects.get_or_create(
            user=self.request.user,
        )
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass color palette for tag selector (JSON-encoded for JavaScript)
        palette = Tag.get_palette_colors_for_user(self.request.user)
        context["palette_colors"] = json.dumps(palette)
        # Get all tags for display
        context["all_tags"] = Tag.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            "Book tag preferences saved successfully!",
        )
        return super().form_valid(form)


# HTMX endpoints
@login_required
def reading_list_quick_update_htmx(request, pk):
    """HTMX endpoint for quick status updates."""
    entry = get_object_or_404(ReadingList, pk=pk, user=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(ReadingList.STATUS_CHOICES):
            entry.status = new_status
            entry.save()
            return render(
                request,
                "academics/partials/reading_status_badge.html",
                {"entry": entry},
            )

    return HttpResponse(status=400)
