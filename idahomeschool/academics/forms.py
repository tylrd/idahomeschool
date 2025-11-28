from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.forms import modelformset_factory

from .models import (
    Course,
    CourseEnrollment,
    CourseNote,
    CourseTemplate,
    CurriculumResource,
    DailyLog,
    Resource,
    SchoolYear,
    Student,
)


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


class ResourceForm(forms.ModelForm):
    """Form for creating and updating Resource instances."""

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
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
            Submit("submit", "Save Resource", css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class StudentForm(forms.ModelForm):
    """Form for creating and updating Student instances."""

    class Meta:
        model = Student
        fields = [
            "name",
            "date_of_birth",
            "grade_level",
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
                user=self.user
            )

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            Row(
                Column("date_of_birth", css_class="col-md-6"),
                Column("grade_level", css_class="col-md-6"),
            ),
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
                user=self.user
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
        fields = ["name", "description", "course_template", "resources"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter course_templates and resources to only show those belonging to the user
        if self.user:
            self.fields["course_template"].queryset = CourseTemplate.objects.filter(
                user=self.user
            )
            self.fields["resources"].queryset = Resource.objects.filter(user=self.user)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
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
            self.fields["course"].queryset = Course.objects.filter(user=self.user)
            self.fields["school_year"].queryset = SchoolYear.objects.filter(
                user=self.user
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
                attrs={"rows": 4, "placeholder": "What did the student work on today?"}
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
                student__user=self.user
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
