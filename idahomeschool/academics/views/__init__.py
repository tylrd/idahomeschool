"""
Academics views module.

This module provides all view classes and functions for the academics app,
organized into logical submodules for better maintainability.
"""

# Dashboard views
# Attendance and Daily Log views
from .attendance import AttendanceCalendarView
from .attendance import AttendanceReportPDFView
from .attendance import AttendanceReportView
from .attendance import DailyLogCreateView
from .attendance import DailyLogDeleteView
from .attendance import DailyLogDetailView
from .attendance import DailyLogEntryView
from .attendance import DailyLogListView
from .attendance import DailyLogUpdateView
from .attendance import attendance_course_notes
from .attendance import attendance_quick_delete
from .attendance import attendance_quick_toggle
from .attendance import attendance_quick_update
from .attendance import attendance_save_course_notes

# Course and Enrollment views
from .courses import CourseCreateView
from .courses import CourseDeleteView
from .courses import CourseDetailView
from .courses import CourseEnrollmentCreateView
from .courses import CourseEnrollmentDeleteView
from .courses import CourseEnrollmentDetailView
from .courses import CourseEnrollmentListView
from .courses import CourseEnrollmentUpdateView
from .courses import CourseListView
from .courses import CourseUpdateView
from .courses import filter_courses_by_student

# Curriculum views (CourseTemplates and CurriculumResources)
from .curriculum import CourseTemplateCreateView
from .curriculum import CourseTemplateDeleteView
from .curriculum import CourseTemplateDetailView
from .curriculum import CourseTemplateListView
from .curriculum import CourseTemplateUpdateView
from .curriculum import CurriculumResourceCreateView
from .curriculum import CurriculumResourceDeleteView
from .curriculum import CurriculumResourceUpdateView
from .dashboard import DashboardView
from .grades import GradeLevelCreateView
from .grades import GradeLevelDeleteView
from .grades import GradeLevelDetailView
from .grades import GradeLevelListView
from .grades import GradeLevelUpdateView

# Grade Level views
from .grades import create_pk12_grades

# Library views (Resources and Tags)
from .library import color_palette_import_csv
from .library import color_palette_preview_htmx
from .library import ColorCreateView
from .library import ColorDeleteView
from .library import ColorPaletteCreateView
from .library import ColorPaletteDeleteView
from .library import ColorPaletteListView
from .library import ColorPaletteUpdateView
from .library import ColorUpdateView
from .library import remove_color_from_palette
from .library import resource_create_modal_htmx
from .library import resource_search_htmx
from .library import ResourceCreateView
from .library import ResourceDeleteView
from .library import ResourceDetailView
from .library import ResourceListView
from .library import ResourceUpdateView
from .library import set_active_palette
from .library import tag_autocomplete_htmx
from .library import TagCreateView
from .library import TagDeleteView
from .library import TagDetailView
from .library import TagListView
from .library import TagUpdateView

# SchoolYear views
from .schoolyears import SchoolYearCreateView
from .schoolyears import SchoolYearDeleteView
from .schoolyears import SchoolYearDetailView
from .schoolyears import SchoolYearListView
from .schoolyears import SchoolYearUpdateView

# Student views
from .students import StudentCreateView
from .students import StudentDeleteView
from .students import StudentDetailView
from .students import StudentGradeYearCreateView
from .students import StudentGradeYearDeleteView
from .students import StudentGradeYearUpdateView
from .students import StudentListView
from .students import StudentUpdateView

__all__ = [
    "AttendanceCalendarView",
    "AttendanceReportPDFView",
    "AttendanceReportView",
    # Color Palette
    "color_palette_import_csv",
    "color_palette_preview_htmx",
    "ColorCreateView",
    "ColorDeleteView",
    "ColorPaletteCreateView",
    "ColorPaletteDeleteView",
    "ColorPaletteListView",
    "ColorPaletteUpdateView",
    "ColorUpdateView",
    "CourseCreateView",
    "CourseDeleteView",
    "CourseDetailView",
    "CourseEnrollmentCreateView",
    "CourseEnrollmentDeleteView",
    "CourseEnrollmentDetailView",
    # Course Enrollments
    "CourseEnrollmentListView",
    "CourseEnrollmentUpdateView",
    # Courses
    "CourseListView",
    "CourseTemplateCreateView",
    "CourseTemplateDeleteView",
    "CourseTemplateDetailView",
    # Course Templates
    "CourseTemplateListView",
    "CourseTemplateUpdateView",
    "CourseUpdateView",
    # Curriculum Resources
    "CurriculumResourceCreateView",
    "CurriculumResourceDeleteView",
    "CurriculumResourceUpdateView",
    "DailyLogCreateView",
    "DailyLogDeleteView",
    "DailyLogDetailView",
    "DailyLogEntryView",
    # Daily Logs / Attendance
    "DailyLogListView",
    "DailyLogUpdateView",
    # Dashboard
    "DashboardView",
    "GradeLevelCreateView",
    "GradeLevelDeleteView",
    "GradeLevelDetailView",
    # Grade Levels
    "GradeLevelListView",
    "GradeLevelUpdateView",
    "ResourceCreateView",
    "ResourceDeleteView",
    "ResourceDetailView",
    # Resources
    "ResourceListView",
    "ResourceUpdateView",
    "SchoolYearCreateView",
    "SchoolYearDeleteView",
    "SchoolYearDetailView",
    # SchoolYears
    "SchoolYearListView",
    "SchoolYearUpdateView",
    "StudentCreateView",
    "StudentDeleteView",
    "StudentDetailView",
    # Student Grade Years
    "StudentGradeYearCreateView",
    "StudentGradeYearDeleteView",
    "StudentGradeYearUpdateView",
    # Students
    "StudentListView",
    "StudentUpdateView",
    "TagCreateView",
    "TagDeleteView",
    "TagDetailView",
    # Tags
    "TagListView",
    "TagUpdateView",
    "attendance_course_notes",
    "attendance_quick_delete",
    # HTMX endpoints
    "attendance_quick_toggle",
    "attendance_quick_update",
    "attendance_save_course_notes",
    "create_pk12_grades",
    "filter_courses_by_student",
    "remove_color_from_palette",
    "resource_create_modal_htmx",
    "resource_search_htmx",
    "set_active_palette",
    "tag_autocomplete_htmx",
]
