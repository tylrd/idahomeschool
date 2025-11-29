from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import ResourceForm
from idahomeschool.academics.forms import TagForm
from idahomeschool.academics.models import Resource
from idahomeschool.academics.models import Tag


# Resource Views
class ResourceListView(LoginRequiredMixin, ListView):
    """List all resources in the library for the current user."""

    model = Resource
    template_name = "academics/resource_list.html"
    context_object_name = "resources"
    paginate_by = 20

    def get_queryset(self):
        queryset = Resource.objects.filter(user=self.request.user).prefetch_related(
            "tags",
        )

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

        # Filter by tag
        tag_id = self.request.GET.get("tag", "")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)

        return queryset.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_resource_type"] = self.request.GET.get("resource_type", "")
        context["selected_tag"] = self.request.GET.get("tag", "")
        context["resource_types"] = Resource.RESOURCE_TYPE_CHOICES
        context["tags"] = Tag.objects.filter(user=self.request.user)
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


@login_required
def resource_search_htmx(request):
    """HTMX endpoint for searching resources."""
    search_query = request.GET.get("search", "")
    field_name = request.GET.get("field_name", "resources")
    selected_ids = request.GET.get("selected_ids", "")

    # Parse selected IDs
    selected_id_list = []
    if selected_ids:
        try:
            selected_id_list = [int(x) for x in selected_ids.split(",") if x]
        except ValueError:
            selected_id_list = []

    queryset = Resource.objects.filter(user=request.user).prefetch_related("tags")

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query)
            | Q(author__icontains=search_query)
            | Q(publisher__icontains=search_query),
        )

    # Limit results to 20
    resources = queryset[:20]

    return render(
        request,
        "academics/partials/resource_search_results.html",
        {
            "resources": resources,
            "field_name": field_name,
            "selected_ids": selected_id_list,
        },
    )


# Tag Views
class TagListView(LoginRequiredMixin, ListView):
    """List all tags for the current user."""

    model = Tag
    template_name = "academics/tag_list.html"
    context_object_name = "tags"
    paginate_by = 50

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).annotate(
            resource_count=Count("resources", distinct=True),
        )


class TagDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a tag."""

    model = Tag
    template_name = "academics/tag_detail.html"
    context_object_name = "tag"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        context["resources"] = tag.resources.all()
        return context


class TagCreateView(LoginRequiredMixin, CreateView):
    """Create a new tag."""

    model = Tag
    form_class = TagForm
    template_name = "academics/tag_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Tag '{form.instance.name}' created successfully!",
        )
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing tag."""

    model = Tag
    form_class = TagForm
    template_name = "academics/tag_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Tag '{form.instance.name}' updated successfully!",
        )
        return super().form_valid(form)


class TagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a tag."""

    model = Tag
    template_name = "academics/tag_confirm_delete.html"
    success_url = reverse_lazy("academics:tag_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tag deleted successfully!")
        return super().delete(request, *args, **kwargs)
