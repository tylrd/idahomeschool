import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from idahomeschool.academics.forms import ColorPaletteImportForm
from idahomeschool.academics.forms import ResourceForm
from idahomeschool.academics.forms import TagForm
from idahomeschool.academics.models import Color
from idahomeschool.academics.models import ColorPalette
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass color palette for tag selector (JSON-encoded for JavaScript)
        palette = Tag.get_palette_colors_for_user(self.request.user)
        context["palette_colors"] = json.dumps(palette)
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass color palette for tag selector (JSON-encoded for JavaScript)
        palette = Tag.get_palette_colors_for_user(self.request.user)
        context["palette_colors"] = json.dumps(palette)
        return context

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
    tag_ids = request.GET.getlist("tag_ids[]", [])

    # Parse selected IDs
    selected_id_list = []
    if selected_ids:
        try:
            selected_id_list = [int(x) for x in selected_ids.split(",") if x]
        except ValueError:
            selected_id_list = []

    queryset = Resource.objects.filter(user=request.user).prefetch_related("tags")

    # Filter by tag IDs (AND logic - resource must have ALL selected tags)
    if tag_ids:
        for tag_id in tag_ids:
            queryset = queryset.filter(tags__id=tag_id)
        queryset = queryset.distinct()

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


@login_required
def tag_autocomplete_htmx(request):
    """HTMX endpoint for tag autocomplete."""
    search_query = request.GET.get("search", "").strip()

    # If no search query, return all tags (useful for showing full list on focus)
    # Otherwise, filter by search query and limit results
    if search_query:
        tags = Tag.objects.filter(
            user=request.user,
            name__icontains=search_query,
        ).values("id", "name", "color").order_by("name")[:10]
    else:
        # Return all tags when no search (browsing mode)
        tags = Tag.objects.filter(
            user=request.user,
        ).values("id", "name", "color").order_by("name")

    return JsonResponse({"tags": list(tags)})


@login_required
def resource_create_modal_htmx(request):
    """HTMX endpoint for creating a resource in a modal."""
    field_name = request.GET.get("field_name", "resources")
    selected_ids = request.GET.get("selected_ids", "")

    if request.method == "POST":
        form = ResourceForm(request.POST, user=request.user)
        if form.is_valid():
            resource = form.save()

            # Parse selected IDs and add the new resource
            selected_id_list = []
            if selected_ids:
                try:
                    selected_id_list = [int(x) for x in selected_ids.split(",") if x]
                except ValueError:
                    selected_id_list = []

            # Add new resource to selected list
            selected_id_list.append(resource.id)

            # Get all resources for the search results
            # Order by created_at descending to show newest first
            # This ensures the newly created resource appears at the top
            resources = Resource.objects.filter(
                user=request.user,
            ).prefetch_related("tags").order_by("-created_at")[:20]

            # Return updated search results with success message
            context = {
                "resources": resources,
                "field_name": field_name,
                "selected_ids": selected_id_list,
                "modal_success": True,
                "new_resource_title": resource.title,
            }

            return render(
                request,
                "academics/partials/resource_search_results.html",
                context,
            )
    else:
        form = ResourceForm(user=request.user)

    palette = Tag.get_palette_colors_for_user(request.user)
    return render(
        request,
        "academics/partials/resource_create_modal.html",
        {
            "form": form,
            "field_name": field_name,
            "selected_ids": selected_ids,
            "palette_colors": json.dumps(palette),
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get colors from active palette for color picker
        palette_colors = Tag.get_palette_colors_for_user(self.request.user)
        context["palette_colors"] = Color.objects.filter(
            user=self.request.user,
            color__in=palette_colors,
        )
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get colors from active palette for color picker
        palette_colors = Tag.get_palette_colors_for_user(self.request.user)
        context["palette_colors"] = Color.objects.filter(
            user=self.request.user,
            color__in=palette_colors,
        )
        return context

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


# Color Palette Views
class ColorPaletteListView(LoginRequiredMixin, ListView):
    """List all color palettes (collections) for the current user."""

    model = ColorPalette
    template_name = "academics/color_palette_list.html"
    context_object_name = "palettes"
    paginate_by = 50

    def get_queryset(self):
        return ColorPalette.objects.filter(
            user=self.request.user,
        ).prefetch_related("colors")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all user's colors for showing in the "All Colors" tab
        context["all_colors"] = Color.objects.filter(user=self.request.user)
        context["all_colors_count"] = context["all_colors"].count()
        return context


class ColorPaletteCreateView(LoginRequiredMixin, CreateView):
    """Create a new color palette (collection)."""

    model = ColorPalette
    template_name = "academics/color_palette_form.html"
    fields = ["name", "is_active"]
    success_url = reverse_lazy("academics:color_palette_list")

    def form_valid(self, form):
        form.instance.user = self.request.user

        # If marking as active, deactivate all other palettes
        if form.cleaned_data.get("is_active"):
            ColorPalette.objects.filter(user=self.request.user).update(is_active=False)

        messages.success(
            self.request,
            f"Palette '{form.instance.name}' created successfully!",
        )
        return super().form_valid(form)


class ColorPaletteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a color palette."""

    model = ColorPalette
    template_name = "academics/color_palette_form.html"
    fields = ["name", "is_active"]
    success_url = reverse_lazy("academics:color_palette_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        # If marking as active, deactivate all other palettes
        if form.cleaned_data.get("is_active"):
            ColorPalette.objects.filter(
                user=self.request.user,
            ).exclude(pk=form.instance.pk).update(is_active=False)

        messages.success(
            self.request,
            f"Palette '{form.instance.name}' updated successfully!",
        )
        return super().form_valid(form)


class ColorPaletteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a color palette."""

    model = ColorPalette
    template_name = "academics/color_palette_confirm_delete.html"
    success_url = reverse_lazy("academics:color_palette_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        palette_name = self.get_object().name
        messages.success(
            self.request,
            f"Palette '{palette_name}' deleted successfully!",
        )
        return super().delete(request, *args, **kwargs)


# Color Views (individual colors)
class ColorCreateView(LoginRequiredMixin, CreateView):
    """Create a new color."""

    model = Color
    template_name = "academics/color_form.html"
    fields = ["name", "color", "palettes"]
    success_url = reverse_lazy("academics:color_palette_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show user's palettes in the dropdown
        form.fields["palettes"].queryset = ColorPalette.objects.filter(
            user=self.request.user,
        )
        form.fields["palettes"].required = False
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request,
            f"Color {form.instance.color} created successfully!",
        )
        return super().form_valid(form)


class ColorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing color."""

    model = Color
    template_name = "academics/color_form.html"
    fields = ["name", "color", "palettes"]
    success_url = reverse_lazy("academics:color_palette_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show user's palettes in the dropdown
        form.fields["palettes"].queryset = ColorPalette.objects.filter(
            user=self.request.user,
        )
        form.fields["palettes"].required = False
        return form

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Color {form.instance.color} updated successfully!",
        )
        return super().form_valid(form)


class ColorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a color."""

    model = Color
    template_name = "academics/color_confirm_delete.html"
    success_url = reverse_lazy("academics:color_palette_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        color = self.get_object()
        messages.success(
            self.request,
            f"Color {color.color} deleted successfully!",
        )
        return super().delete(request, *args, **kwargs)


def _process_hex_code(hex_code, line_num):
    """Process and validate a hex code from CSV import."""
    hex_code = hex_code.strip()

    # Skip empty lines
    if not hex_code:
        return None, None

    # Add # prefix if missing
    if not hex_code.startswith("#"):
        hex_code = f"#{hex_code}"

    # Validate hex code pattern
    if not re.match(r"^#[0-9A-Fa-f]{6}$", hex_code):
        return None, f"Line {line_num}: Invalid hex code '{hex_code}'"

    return hex_code.upper(), None


def _import_colors_from_lines(lines, user, *, palette=None):
    """Import colors from CSV lines and return counts and errors."""
    imported_count = 0
    skipped_count = 0
    errors = []

    for line_num, line in enumerate(lines, start=1):
        hex_code, error = _process_hex_code(line, line_num)

        if error:
            errors.append(error)
            skipped_count += 1
            continue

        if hex_code is None:
            continue

        # Check if color already exists for this user
        color, created = Color.objects.get_or_create(
            user=user,
            color=hex_code,
            defaults={"name": ""},
        )

        if not created:
            skipped_count += 1
        else:
            imported_count += 1

        # Add color to palette if specified
        if palette:
            color.palettes.add(palette)

    return imported_count, skipped_count, errors


def _display_import_results(request, imported_count, skipped_count, errors):
    """Display import result messages to user."""
    if imported_count > 0:
        messages.success(request, f"Successfully imported {imported_count} color(s)!")
    if skipped_count > 0:
        messages.info(
            request,
            f"Skipped {skipped_count} color(s) (duplicates or invalid)",
        )
    for error in errors[:5]:
        messages.warning(request, error)




@login_required
def color_palette_preview_htmx(request):
    """HTMX endpoint for live color preview."""
    csv_content = request.POST.get("csv_content", "").strip()

    if not csv_content:
        return render(
            request,
            "academics/partials/color_palette_preview.html",
            {"preview_colors": [], "preview_errors": []},
        )

    preview_colors = []
    preview_errors = []

    # Split by both newlines and commas
    lines = csv_content.replace(",", "\n").split("\n")

    for line_num, line in enumerate(lines, start=1):
        hex_code, error = _process_hex_code(line, line_num)

        if error:
            preview_errors.append(error)
            continue

        if hex_code is None:
            continue

        exists = Color.objects.filter(
            user=request.user,
            color=hex_code,
        ).exists()

        preview_colors.append(
            {
                "hex_code": hex_code,
                "line_num": line_num,
                "exists": exists,
            },
        )

    new_count = sum(1 for c in preview_colors if not c["exists"])
    existing_count = sum(1 for c in preview_colors if c["exists"])

    return render(
        request,
        "academics/partials/color_palette_preview.html",
        {
            "preview_colors": preview_colors,
            "preview_errors": preview_errors[:5],
            "new_count": new_count,
            "existing_count": existing_count,
        },
    )


@login_required
def color_palette_import_csv(request):
    """Import colors into a new or existing palette."""
    if request.method == "POST":
        form = ColorPaletteImportForm(request.POST, user=request.user)
        if form.is_valid():
            csv_content = form.cleaned_data["csv_content"]
            palette_choice = form.cleaned_data["palette_choice"]
            palette_name = form.cleaned_data.get("palette_name")
            mark_as_active = form.cleaned_data.get("mark_as_active", False)

            # Get or create palette
            if palette_choice == ColorPaletteImportForm.PALETTE_CHOICE_NEW:
                # Create new palette
                if mark_as_active:
                    ColorPalette.objects.filter(user=request.user).update(
                        is_active=False,
                    )

                palette = ColorPalette.objects.create(
                    user=request.user,
                    name=palette_name,
                    is_active=mark_as_active,
                )
                action_msg = f"Created palette '{palette_name}'"
            else:
                # Use existing palette
                palette = ColorPalette.objects.get(
                    pk=palette_choice,
                    user=request.user,
                )
                action_msg = f"Added colors to '{palette.name}'"

            # Split by both newlines and commas
            lines = csv_content.strip().replace(",", "\n").split("\n")

            # Import colors and add to palette
            imported, skipped, errors = _import_colors_from_lines(
                lines,
                request.user,
                palette=palette,
            )
            _display_import_results(request, imported, skipped, errors)

            messages.success(
                request,
                f"{action_msg} - imported {imported} color(s)!",
            )

            return redirect("academics:color_palette_list")
    else:
        form = ColorPaletteImportForm(user=request.user)

    return render(
        request,
        "academics/color_palette_import.html",
        {"form": form},
    )


@login_required
def set_active_palette(request, pk):
    """Set a color palette as the active palette."""
    palette = ColorPalette.objects.filter(pk=pk, user=request.user).first()

    if not palette:
        messages.error(request, "Palette not found")
        return redirect("academics:color_palette_list")

    # Deactivate all other palettes
    ColorPalette.objects.filter(user=request.user).update(is_active=False)

    # Activate this palette
    palette.is_active = True
    palette.save()

    messages.success(request, f"'{palette.name}' is now your active palette!")
    return redirect("academics:color_palette_list")


@login_required
def remove_color_from_palette(request, palette_pk, color_pk):
    """Remove a color from a palette (without deleting the color)."""
    palette = ColorPalette.objects.filter(pk=palette_pk, user=request.user).first()
    color = Color.objects.filter(pk=color_pk, user=request.user).first()

    if not palette or not color:
        messages.error(request, "Palette or color not found")
        return redirect("academics:color_palette_list")

    # Remove the color from this palette
    palette.colors.remove(color)

    messages.success(
        request,
        f"Removed {color.color} from palette '{palette.name}'",
    )
    return redirect("academics:color_palette_list")
