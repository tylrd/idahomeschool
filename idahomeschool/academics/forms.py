from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from .models import Course, CurriculumResource, SchoolYear, Student


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


class StudentForm(forms.ModelForm):
    """Form for creating and updating Student instances."""

    class Meta:
        model = Student
        fields = ["name", "date_of_birth", "grade_level", "school_years", "paperless_tag_id"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter school_years to only show those belonging to the user
        if self.user:
            self.fields["school_years"].queryset = SchoolYear.objects.filter(user=self.user)

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


class CourseForm(forms.ModelForm):
    """Form for creating and updating Course instances."""

    class Meta:
        model = Course
        fields = ["student", "school_year", "name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Filter students and school_years to only show those belonging to the user
        if self.user:
            self.fields["student"].queryset = Student.objects.filter(user=self.user)
            self.fields["school_year"].queryset = SchoolYear.objects.filter(user=self.user)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("student", css_class="col-md-6"),
                Column("school_year", css_class="col-md-6"),
            ),
            "name",
            "description",
            Submit("submit", "Save Course", css_class="btn btn-primary"),
        )


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
