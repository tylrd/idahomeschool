import json

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django import forms
from django.forms import modelformset_factory

from .models import ColorPalette
from .models import Course
from .models import CourseEnrollment
from .models import CourseNote
from .models import CourseTemplate
from .models import CurriculumResource
from .models import DailyLog
from .models import GradeLevel
from .models import Resource
from .models import SchoolYear
from .models import Student
from .models import StudentGradeYear
from .models import Tag


class SchoolYearForm(forms.ModelForm):
    """Form for creating and updating SchoolYear instances."""

    class Meta:
        model = SchoolYear
        fields = ["name", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            Row(
                Column("start_date", css_class="col-md-6"),
                Column("end_date", css_class="col-md-6"),
            ),
            "is_active",
            Submit("submit", "Save School Year", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class TagForm(forms.ModelForm):
    """Form for creating and updating Tag instances."""

    class Meta:
        model = Tag
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            "color",
            Submit("submit", "Save Tag", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class ResourceForm(forms.ModelForm):
    """Form for creating and updating Resource instances."""

    # Hidden field for tag data from tag selector component
    tags_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Resource
        fields = [
            "title",
            "author",
            "publisher",
            "isbn",
            "resource_type",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "publisher": forms.TextInput(attrs={"class": "form-control"}),
            "isbn": forms.TextInput(attrs={"class": "form-control"}),
            "resource_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Initialize tags_data with existing tags if editing
        if self.instance and self.instance.pk:
            existing_tags = [
                {"id": tag.id, "name": tag.name, "color": tag.color}
                for tag in self.instance.tags.all()
            ]
            self.initial["tags_data"] = json.dumps(existing_tags)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "title",
            Row(
                Column("author", css_class="col-md-6"),
                Column("publisher", css_class="col-md-6"),
            ),
            Row(
                Column("isbn", css_class="col-md-6"),
                Column("resource_type", css_class="col-md-6"),
            ),
            "description",
            # tags field will be rendered manually in template
            Submit("submit", "Save Resource", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()

            # Process tags from tag selector
            tags_data = self.cleaned_data.get("tags_data", "[]")
            try:
                tags_list = json.loads(tags_data)
            except (json.JSONDecodeError, TypeError):
                tags_list = []

            # Clear existing tags
            instance.tags.clear()

            # Process each tag
            for tag_data in tags_list:
                tag_id = tag_data.get("id")
                tag_name = tag_data.get("name", "").strip()

                if not tag_name:
                    continue

                # If ID is positive, it's an existing tag
                if tag_id and tag_id > 0:
                    try:
                        tag = Tag.objects.get(id=tag_id, user=self.user)
                        instance.tags.add(tag)
                    except Tag.DoesNotExist:
                        # Tag doesn't exist or doesn't belong to user, create new one
                        tag = Tag.objects.create(
                            user=self.user,
                            name=tag_name,
                            color=Tag.get_random_color_from_palette(self.user),
                        )
                        instance.tags.add(tag)
                else:
                    # Negative ID or no ID means it's a new tag
                    # Check if tag with this name already exists for this user
                    tag, _created = Tag.objects.get_or_create(
                        user=self.user,
                        name=tag_name,
                        defaults={
                            "color": Tag.get_random_color_from_palette(self.user),
                        },
                    )
                    instance.tags.add(tag)

        return instance


class StudentForm(forms.ModelForm):
    """Form for creating and updating Student instances."""

    class Meta:
        model = Student
        fields = [
            "name",
            "date_of_birth",
            "grade_level",
            "photo",
            "school_years",
            "paperless_tag_id",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter school_years to only show those belonging to the user
        if self.user:
            self.fields["school_years"].queryset = SchoolYear.objects.filter(
                user=self.user,
            )

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"  # Required for file uploads
        self.helper.layout = Layout(
            "name",
            Row(
                Column("date_of_birth", css_class="col-md-6"),
                Column("grade_level", css_class="col-md-6"),
            ),
            "photo",
            "school_years",
            "paperless_tag_id",
            Submit("submit", "Save Student", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
        return instance


class CourseTemplateForm(forms.ModelForm):
    """Form for creating and updating CourseTemplate instances."""

    class Meta:
        model = CourseTemplate
        fields = ["name", "description", "suggested_resources"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter resources to only show those belonging to the user
        if self.user:
            self.fields["suggested_resources"].queryset = Resource.objects.filter(
                user=self.user,
            )

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            "description",
            "suggested_resources",
            Submit("submit", "Save Course Template", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
        return instance


class CourseForm(forms.ModelForm):
    """Form for creating and updating Course instances."""

    class Meta:
        model = Course
        fields = ["name", "grade_level", "description", "course_template", "resources"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter grade_levels, course_templates, and resources to user's data
        if self.user:
            self.fields["grade_level"].queryset = GradeLevel.objects.filter(
                user=self.user,
            )
            self.fields["course_template"].queryset = CourseTemplate.objects.filter(
                user=self.user,
            ).prefetch_related("suggested_resources")
            self.fields["resources"].queryset = Resource.objects.filter(user=self.user)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="col-md-8"),
                Column("grade_level", css_class="col-md-4"),
            ),
            "course_template",
            "description",
            "resources",
            Submit("submit", "Save Course", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
        return instance


class CourseEnrollmentForm(forms.ModelForm):
    """Form for creating and updating CourseEnrollment instances."""

    class Meta:
        model = CourseEnrollment
        fields = [
            "student",
            "course",
            "school_year",
            "status",
            "started_date",
            "completed_date",
            "final_grade",
            "completion_percentage",
        ]
        widgets = {
            "started_date": forms.DateInput(attrs={"type": "date"}),
            "completed_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter students, courses, and school_years to only show those belonging to the user
        if self.user:
            self.fields["student"].queryset = Student.objects.filter(user=self.user)
            self.fields["course"].queryset = Course.objects.filter(
                user=self.user,
            ).select_related("grade_level")
            self.fields["school_year"].queryset = SchoolYear.objects.filter(
                user=self.user,
            )

        # Add HTMX attributes for dynamic course filtering
        self.fields["student"].widget.attrs.update(
            {
                "hx-get": "/academics/enrollments/filter-courses/",
                "hx-trigger": "change",
                "hx-target": "#id_course",
                "hx-swap": "innerHTML",
                "hx-include": "[name='student'], [name='school_year']",
            },
        )

        self.fields["school_year"].widget.attrs.update(
            {
                "hx-get": "/academics/enrollments/filter-courses/",
                "hx-trigger": "change",
                "hx-target": "#id_course",
                "hx-swap": "innerHTML",
                "hx-include": "[name='student'], [name='school_year']",
            },
        )

        # Update course field to show grade level in options
        course_choices = [("", "---------")]
        for course in self.fields["course"].queryset.order_by(
            "grade_level__order",
            "name",
        ):
            grade_label = (
                f" ({course.grade_level.name})" if course.grade_level else " (Any)"
            )
            label = f"{course.name}{grade_label}"
            course_choices.append((course.pk, label))

        self.fields["course"].choices = course_choices
        self.fields["course"].help_text = (
            "Courses are filtered by student's grade level. "
            "Select a student and school year to see relevant courses."
        )

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("student", css_class="col-md-6"),
                Column("course", css_class="col-md-6"),
            ),
            Row(
                Column("school_year", css_class="col-md-6"),
                Column("status", css_class="col-md-6"),
            ),
            Row(
                Column("started_date", css_class="col-md-6"),
                Column("completed_date", css_class="col-md-6"),
            ),
            Row(
                Column("final_grade", css_class="col-md-6"),
                Column("completion_percentage", css_class="col-md-6"),
            ),
            Submit("submit", "Save Enrollment", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class CurriculumResourceForm(forms.ModelForm):
    """Form for creating and updating CurriculumResource instances."""

    class Meta:
        model = CurriculumResource
        fields = ["title", "author", "publisher", "isbn", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "title",
            Row(
                Column("author", css_class="col-md-6"),
                Column("publisher", css_class="col-md-6"),
            ),
            "isbn",
            "notes",
            Submit("submit", "Save Resource", css_class="btn btn-primary"),
        )


class DailyLogForm(forms.ModelForm):
    """Form for creating and updating DailyLog instances."""

    class Meta:
        model = DailyLog
        fields = ["student", "date", "status", "general_notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "general_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter students to only show those belonging to the user
        if self.user:
            self.fields["student"].queryset = Student.objects.filter(user=self.user)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("student", css_class="col-md-6"),
                Column("date", css_class="col-md-6"),
            ),
            "status",
            "general_notes",
            Submit("submit", "Save Daily Log", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class CourseNoteForm(forms.ModelForm):
    """Form for creating and updating CourseNote instances."""

    class Meta:
        model = CourseNote
        fields = ["course", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 4, "placeholder": "What did the student work on today?"},
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

        # Filter courses to only show those for the specified student
        if self.student:
            self.fields["course"].queryset = Course.objects.filter(student=self.student)
        elif self.user:
            self.fields["course"].queryset = Course.objects.filter(
                student__user=self.user,
            )

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "course",
            "notes",
            Submit("submit", "Save Course Note", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


# Formset for managing multiple course notes at once
CourseNoteFormSet = modelformset_factory(
    CourseNote,
    fields=["course", "notes"],
    extra=0,
    can_delete=True,
    widgets={
        "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    },
)


class GradeLevelForm(forms.ModelForm):
    """Form for creating and updating GradeLevel instances."""

    class Meta:
        model = GradeLevel
        fields = ["name", "order", "description"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="col-md-8"),
                Column("order", css_class="col-md-4"),
            ),
            "description",
            Submit("submit", "Save Grade Level", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class StudentGradeYearForm(forms.ModelForm):
    """Form for creating and updating StudentGradeYear instances."""

    class Meta:
        model = StudentGradeYear
        fields = ["student", "school_year", "grade_level"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

        # Filter querysets to user's data
        if self.user:
            self.fields["student"].queryset = Student.objects.filter(
                user=self.user,
            )
            self.fields["school_year"].queryset = SchoolYear.objects.filter(
                user=self.user,
            )
            self.fields["grade_level"].queryset = GradeLevel.objects.filter(
                user=self.user,
            )

        # Pre-select student if provided
        if self.student:
            self.fields["student"].initial = self.student
            self.fields["student"].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_method = "post"

        if self.student:
            self.helper.layout = Layout(
                "student",
                Row(
                    Column("school_year", css_class="col-md-6"),
                    Column("grade_level", css_class="col-md-6"),
                ),
                Submit(
                    "submit",
                    "Assign Grade",
                    css_class="btn btn-primary",
                ),
            )
        else:
            self.helper.layout = Layout(
                "student",
                Row(
                    Column("school_year", css_class="col-md-6"),
                    Column("grade_level", css_class="col-md-6"),
                ),
                Submit(
                    "submit",
                    "Assign Grade",
                    css_class="btn btn-primary",
                ),
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class ColorPaletteImportForm(forms.Form):
    """Form for importing colors into a palette."""

    PALETTE_CHOICE_NEW = "new"

    csv_content = forms.CharField(
        label="Color Codes",
        help_text=(
            "Paste hex color codes "
            "(comma-separated or one per line, with or without # prefix)"
        ),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "27213c,5a352a,a33b20,a47963,a6a57a",
            },
        ),
    )
    palette_choice = forms.ChoiceField(
        label="Add to Palette",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    palette_name = forms.CharField(
        label="New Palette Name",
        required=False,
        help_text="Name for the new color palette (e.g., 'Ocean Blues', 'Earth Tones')",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    mark_as_active = forms.BooleanField(
        required=False,
        initial=False,
        label="Set as active palette",
        help_text="Use this palette for random tag colors (only for new palettes)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Build choices: existing palettes + "Create new"
            palette_choices = [(self.PALETTE_CHOICE_NEW, "Create new palette")]
            palette_choices.extend([
                (str(palette.id), palette.name)
                for palette in ColorPalette.objects.filter(user=user)
            ])

            self.fields["palette_choice"].choices = palette_choices

    def clean(self):
        cleaned_data = super().clean()
        palette_choice = cleaned_data.get("palette_choice")
        palette_name = cleaned_data.get("palette_name")

        if palette_choice == self.PALETTE_CHOICE_NEW and not palette_name:
            self.add_error(
                "palette_name",
                "Palette name is required when creating a new palette",
            )

        return cleaned_data
