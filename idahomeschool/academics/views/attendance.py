from datetime import date
from datetime import datetime
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from weasyprint import HTML

from idahomeschool.academics.forms import DailyLogForm
from idahomeschool.academics.models import AttendanceStatus
from idahomeschool.academics.models import ColorPalette
from idahomeschool.academics.models import CourseEnrollment
from idahomeschool.academics.models import CourseNote
from idahomeschool.academics.models import DailyLog
from idahomeschool.academics.models import SchoolYear
from idahomeschool.academics.models import Student


# DailyLog / Attendance Views
class DailyLogListView(LoginRequiredMixin, ListView):
    """List all daily logs for the current user."""

    model = DailyLog
    template_name = "academics/dailylog_list.html"
    context_object_name = "daily_logs"
    paginate_by = 20

    def get_queryset(self):
        queryset = DailyLog.objects.filter(user=self.request.user).select_related(
            "student",
        )

        # Filter by student if specified
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by date range
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["students"] = Student.objects.filter(user=self.request.user)
        return context


class DailyLogDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a daily log with course notes."""

    model = DailyLog
    template_name = "academics/dailylog_detail.html"
    context_object_name = "daily_log"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        daily_log = self.get_object()

        context["course_notes"] = daily_log.course_notes.select_related("course").all()

        return context


class DailyLogCreateView(LoginRequiredMixin, CreateView):
    """Create a new daily log."""

    model = DailyLog
    form_class = DailyLogForm
    template_name = "academics/dailylog_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["date"] = date.today()
        return initial

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Daily log for {form.instance.student.name} on {form.instance.date} created successfully!",
        )
        return super().form_valid(form)


class DailyLogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing daily log."""

    model = DailyLog
    form_class = DailyLogForm
    template_name = "academics/dailylog_form.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Daily log for {form.instance.student.name} on {form.instance.date} updated successfully!",
        )
        return super().form_valid(form)


class DailyLogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a daily log."""

    model = DailyLog
    template_name = "academics/dailylog_confirm_delete.html"
    success_url = reverse_lazy("academics:dailylog_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Daily log deleted successfully!")
        return super().delete(request, *args, **kwargs)


class DailyLogEntryView(LoginRequiredMixin, View):
    """View for entering daily log with course notes for all student's courses."""

    template_name = "academics/dailylog_entry.html"
    partial_template_name = "academics/partials/dailylog_entry_form.html"

    def get(self, request, student_pk=None, log_date=None):
        """Display the daily log entry form."""
        # Check for query parameters (HTMX requests)
        query_student_id = request.GET.get("student_id")
        query_date = request.GET.get("date")

        # Use query params if available, otherwise use URL params
        if query_student_id:
            student_pk = query_student_id
        if query_date:
            log_date = query_date

        # Get or set the date
        if log_date:
            try:
                entry_date = date.fromisoformat(log_date)
            except ValueError:
                entry_date = date.today()
        else:
            entry_date = date.today()

        # Get students
        students = Student.objects.filter(user=request.user)

        # Get selected student
        if student_pk:
            student = get_object_or_404(Student, pk=student_pk, user=request.user)
        else:
            student = students.first()

        if not student:
            messages.warning(request, "Please create a student first.")
            return redirect("academics:student_create")

        # Try to get existing daily log (but don't create one yet)
        try:
            daily_log = DailyLog.objects.get(student=student, date=entry_date)
        except DailyLog.DoesNotExist:
            daily_log = None

        # Get student's enrollments for the active school year
        active_year = SchoolYear.objects.filter(
            user=request.user,
            is_active=True,
        ).first()
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            student=student,
        ).select_related("course", "school_year")

        if active_year:
            enrollments = enrollments.filter(school_year=active_year)

        # Get existing course notes (if daily log exists)
        existing_notes = {}
        if daily_log:
            existing_notes = {
                note.course_enrollment_id: note for note in daily_log.course_notes.all()
            }

        # Prepare course notes data
        course_notes_data = []
        for enrollment in enrollments:
            note = existing_notes.get(enrollment.id)
            course_notes_data.append(
                {
                    "enrollment": enrollment,
                    "note": note,
                    "notes_text": note.notes if note else "",
                },
            )

        # Get user's custom attendance statuses
        attendance_statuses = AttendanceStatus.objects.filter(
            user=request.user,
        ).order_by("display_order")

        context = {
            "daily_log": daily_log,
            "student": student,
            "students": students,
            "entry_date": entry_date,
            "course_notes_data": course_notes_data,
            "attendance_statuses": attendance_statuses,
        }

        # If this is an HTMX request, return just the form partial
        if request.headers.get("HX-Request"):
            response = render(request, self.partial_template_name, context)
            # Set the proper URL for browser history
            from django.urls import reverse
            proper_url = reverse(
                "academics:dailylog_entry_date",
                kwargs={"student_pk": student.pk, "log_date": entry_date.isoformat()},
            )
            response["HX-Push-Url"] = proper_url
            return response

        return render(request, self.template_name, context)

    def post(self, request, student_pk=None, log_date=None):
        """Handle the daily log entry form submission."""
        # Get the date
        if log_date:
            try:
                entry_date = date.fromisoformat(log_date)
            except ValueError:
                entry_date = date.today()
        else:
            entry_date = date.today()

        # Get student
        if student_pk:
            student = get_object_or_404(Student, pk=student_pk, user=request.user)
        else:
            messages.error(request, "Student is required.")
            return redirect("academics:dailylog_entry")

        # Get or create daily log
        # Use the default attendance status for this user
        default_status = AttendanceStatus.objects.filter(
            user=request.user,
            is_default=True,
        ).first()

        # Fallback to first status if no default is set
        if not default_status:
            default_status = AttendanceStatus.objects.filter(
                user=request.user,
            ).order_by("display_order").first()

        daily_log, created = DailyLog.objects.get_or_create(
            student=student,
            date=entry_date,
            defaults={"user": request.user, "attendance_status": default_status},
        )

        # Update daily log fields
        status_code = request.POST.get("status")
        if status_code:
            # Get the AttendanceStatus object by code
            attendance_status = AttendanceStatus.objects.filter(
                user=request.user,
                code=status_code,
            ).first()
            if attendance_status:
                daily_log.attendance_status = attendance_status

        general_notes = request.POST.get("general_notes", "")
        daily_log.general_notes = general_notes
        daily_log.save()

        # Process course notes
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            student=student,
        )
        active_year = SchoolYear.objects.filter(
            user=request.user,
            is_active=True,
        ).first()
        if active_year:
            enrollments = enrollments.filter(school_year=active_year)

        for enrollment in enrollments:
            notes_text = request.POST.get(f"course_notes_{enrollment.id}", "").strip()
            if notes_text:
                # Create or update course note
                CourseNote.objects.update_or_create(
                    daily_log=daily_log,
                    course_enrollment=enrollment,
                    defaults={"notes": notes_text, "user": request.user},
                )
            else:
                # Delete course note if exists and notes are empty
                CourseNote.objects.filter(
                    daily_log=daily_log,
                    course_enrollment=enrollment,
                ).delete()

        messages.success(
            request,
            f"Daily log for {student.name} on {entry_date.strftime('%B %d, %Y')} saved successfully!",
        )

        # Redirect back to the entry form
        return redirect(
            "academics:dailylog_entry_date",
            student_pk=student.pk,
            log_date=entry_date.isoformat(),
        )


class AttendanceCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view showing attendance for the current week (mobile-optimized)."""

    template_name = "academics/attendance_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get date range (default to current week)
        view_type = self.request.GET.get("view", "week")  # week is now default

        # Get student filter
        selected_student_id = self.request.GET.get("student")
        if selected_student_id:
            try:
                selected_student_id = int(selected_student_id)
            except (ValueError, TypeError):
                selected_student_id = None

        # Get the reference date (default to today)
        ref_date_str = self.request.GET.get("date")
        if ref_date_str:
            try:
                ref_date = date.fromisoformat(ref_date_str)
            except ValueError:
                ref_date = date.today()
        else:
            ref_date = date.today()

        if view_type == "week":
            # Calculate the start of the week (Sunday)
            days_since_sunday = (ref_date.weekday() + 1) % 7
            start_date = ref_date - timedelta(days=days_since_sunday)
            end_date = start_date + timedelta(days=6)
            # Simple date range for week view
            date_range = [
                {"date": start_date + timedelta(days=i), "is_current_month": True}
                for i in range(7)
            ]
            calendar_start_date = start_date
            calendar_end_date = end_date
        else:  # month
            # Calculate the start and end of the month
            month_start = ref_date.replace(day=1)
            if ref_date.month == 12:
                month_end = ref_date.replace(
                    year=ref_date.year + 1, month=1, day=1,
                ) - timedelta(days=1)
            else:
                month_end = ref_date.replace(
                    month=ref_date.month + 1, day=1,
                ) - timedelta(days=1)

            # Calculate calendar grid boundaries (include prev/next month padding)
            # Start from the Sunday before (or on) the first of the month
            calendar_start_date = month_start - timedelta(days=month_start.weekday() + 1)
            if calendar_start_date > month_start:  # Adjust if month starts on Sunday
                calendar_start_date = month_start - timedelta(days=7)

            # End on the Saturday after (or on) the last of the month
            days_after = 6 - month_end.weekday()
            if days_after == 7:  # Month ends on Saturday
                days_after = 0
            calendar_end_date = month_end + timedelta(days=days_after)

            # Build date range with is_current_month flag
            date_range = []
            current = calendar_start_date
            while current <= calendar_end_date:
                date_range.append({
                    "date": current,
                    "is_current_month": current.month == ref_date.month and current.year == ref_date.year,
                })
                current += timedelta(days=1)

            start_date = month_start
            end_date = month_end

        # Get students (filtered if needed)
        students = Student.objects.filter(user=user).prefetch_related("daily_logs")
        if selected_student_id:
            students = students.filter(id=selected_student_id)

        # Get daily logs for the entire calendar date range
        daily_logs = (
            DailyLog.objects.filter(
                user=user,
                date__gte=calendar_start_date,
                date__lte=calendar_end_date,
            )
            .select_related("student", "attendance_status")
            .prefetch_related("course_notes")
        )

        # Filter logs by selected student if applicable
        if selected_student_id:
            daily_logs = daily_logs.filter(student_id=selected_student_id)

        # Organize logs by student and date, and track which logs have course notes
        logs_by_student_date = {}
        logs_with_notes = set()
        for log in daily_logs:
            if log.student_id not in logs_by_student_date:
                logs_by_student_date[log.student_id] = {}
            logs_by_student_date[log.student_id][log.date.isoformat()] = log

            # Check if this log has any course notes
            if log.course_notes.exists():
                logs_with_notes.add(log.id)

        # Build attendance grid
        attendance_grid = []
        for student in students:
            row = {"student": student, "dates": []}
            for date_info in date_range:
                d = date_info["date"] if isinstance(date_info, dict) else date_info
                log = logs_by_student_date.get(student.id, {}).get(d.isoformat())
                has_notes = log.id in logs_with_notes if log else False
                row["dates"].append({"date": d, "log": log, "has_notes": has_notes})
            attendance_grid.append(row)

        context["view_type"] = view_type
        context["ref_date"] = ref_date
        context["start_date"] = start_date
        context["end_date"] = end_date
        context["date_range"] = date_range
        context["attendance_grid"] = attendance_grid
        context["students"] = Student.objects.filter(user=user)  # All students for filter dropdown
        context["selected_student_id"] = selected_student_id
        context["today"] = date.today()
        context["prev_date"] = (
            start_date - timedelta(days=7 if view_type == "week" else 30)
        ).isoformat()
        context["next_date"] = (end_date + timedelta(days=1)).isoformat()

        # Get user's custom attendance statuses for legend
        context["attendance_statuses"] = AttendanceStatus.objects.filter(
            user=user,
        ).order_by("display_order")

        # If this is an HTMX request, return just the grid partial
        if self.request.headers.get("HX-Request"):
            self.template_name = "academics/partials/calendar_week_grid.html"

        return context


class AttendanceReportView(LoginRequiredMixin, TemplateView):
    """Report view for attendance statistics and compliance."""

    template_name = "academics/attendance_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get school year filter
        year_id = self.request.GET.get("year")
        if year_id:
            school_year = get_object_or_404(SchoolYear, pk=year_id, user=user)
        else:
            school_year = SchoolYear.objects.filter(user=user, is_active=True).first()

        # Get student filter
        student_id = self.request.GET.get("student")
        students_queryset = Student.objects.filter(user=user)
        if student_id:
            students_queryset = students_queryset.filter(pk=student_id)

        # Get user's custom attendance statuses
        attendance_statuses = AttendanceStatus.objects.filter(
            user=user,
        ).order_by("display_order")

        # Build report data
        report_data = []
        for student in students_queryset:
            # Get daily logs for this student in the school year
            logs_query = DailyLog.objects.filter(student=student).select_related("attendance_status")
            if school_year:
                logs_query = logs_query.filter(
                    date__gte=school_year.start_date, date__lte=school_year.end_date,
                )

            total_days = logs_query.count()

            # Calculate counts for each custom status
            status_counts = {}
            instructional_days = 0
            for status in attendance_statuses:
                count = logs_query.filter(attendance_status=status).count()
                status_counts[status.code] = {
                    "count": count,
                    "label": status.label,
                    "abbreviation": status.abbreviation,
                    "color": status.color,
                }
                if status.is_instructional:
                    instructional_days += count

            report_data.append(
                {
                    "student": student,
                    "total_days": total_days,
                    "instructional_days": instructional_days,
                    "status_counts": status_counts,
                },
            )

        context["school_year"] = school_year
        context["school_years"] = SchoolYear.objects.filter(user=user)
        context["students"] = Student.objects.filter(user=user)
        context["selected_student_id"] = int(student_id) if student_id else None
        context["report_data"] = report_data
        context["attendance_statuses"] = attendance_statuses

        return context


class AttendanceReportPDFView(LoginRequiredMixin, View):
    """PDF export view for attendance reports."""

    def get(self, request):
        """Generate and return PDF attendance report."""
        user = request.user

        # Get school year filter
        year_id = request.GET.get("year")
        if year_id:
            school_year = get_object_or_404(SchoolYear, pk=year_id, user=user)
        else:
            school_year = SchoolYear.objects.filter(user=user, is_active=True).first()

        # Get student filter
        student_id = request.GET.get("student")
        students_queryset = Student.objects.filter(user=user)
        if student_id:
            students_queryset = students_queryset.filter(pk=student_id)

        # Get user's custom attendance statuses
        attendance_statuses = AttendanceStatus.objects.filter(
            user=user,
        ).order_by("display_order")

        # Build report data (same logic as AttendanceReportView)
        report_data = []
        for student in students_queryset:
            logs_query = DailyLog.objects.filter(student=student).select_related("attendance_status")
            if school_year:
                logs_query = logs_query.filter(
                    date__gte=school_year.start_date, date__lte=school_year.end_date,
                )

            total_days = logs_query.count()

            # Calculate counts for each custom status
            status_counts = {}
            instructional_days = 0
            for status in attendance_statuses:
                count = logs_query.filter(attendance_status=status).count()
                status_counts[status.code] = {
                    "count": count,
                    "label": status.label,
                    "abbreviation": status.abbreviation,
                    "color": status.color,
                }
                if status.is_instructional:
                    instructional_days += count

            # Get enrollments for this student in the school year
            enrollments_query = (
                CourseEnrollment.objects.filter(
                    user=user,
                    student=student,
                )
                .select_related("course", "school_year")
                .prefetch_related("course__resources")
            )

            if school_year:
                enrollments_query = enrollments_query.filter(school_year=school_year)

            report_data.append(
                {
                    "student": student,
                    "total_days": total_days,
                    "instructional_days": instructional_days,
                    "status_counts": status_counts,
                    "enrollments": enrollments_query,
                },
            )

        # Chunk report_data into groups of 3 for table layout
        report_data_chunks = []
        for i in range(0, len(report_data), 3):
            report_data_chunks.append(report_data[i : i + 3])

        # Prepare context for PDF template
        context = {
            "school_year": school_year,
            "report_data": report_data,
            "report_data_chunks": report_data_chunks,
            "attendance_statuses": attendance_statuses,
            "user": user,
            "generated_date": date.today(),
        }

        # Render HTML template
        html_string = render_to_string("academics/attendance_report_pdf.html", context)

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # Return PDF response
        response = HttpResponse(pdf, content_type="application/pdf")
        filename = f"attendance_report_{school_year.name if school_year else 'all'}_{date.today().isoformat()}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


# =============================================================================
# HTMX Attendance Quick Actions
# =============================================================================


@require_http_methods(["GET"])
@login_required
def attendance_quick_toggle(request, student_pk, log_date):
    """
    HTMX endpoint: Show status selector dropdown for a specific student/date.
    Returns HTML fragment for status selection.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get existing log if any
    daily_log = DailyLog.objects.filter(student=student, date=date_obj).first()

    # Get user's custom attendance statuses
    attendance_statuses = AttendanceStatus.objects.filter(
        user=request.user,
    ).order_by("display_order")

    context = {
        "student": student,
        "date": date_obj,
        "date_str": log_date,
        "current_status": daily_log.attendance_status.code if (daily_log and daily_log.attendance_status) else None,
        "attendance_statuses": attendance_statuses,
    }

    return render(request, "academics/partials/status_selector.html", context)


@require_http_methods(["POST"])
@login_required
def attendance_quick_update(request, student_pk, log_date):
    """
    HTMX endpoint: Update attendance status for a specific student/date.
    Returns updated badge HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get new status from form
    new_status_code = request.POST.get("status")

    # Get the AttendanceStatus object for this user
    attendance_status = AttendanceStatus.objects.filter(
        user=request.user,
        code=new_status_code,
    ).first()

    if not attendance_status:
        return HttpResponse("Invalid status", status=400)

    # Update or create daily log
    daily_log, created = DailyLog.objects.update_or_create(
        student=student,
        date=date_obj,
        defaults={"attendance_status": attendance_status, "user": request.user},
    )

    # Check if there are any course notes for this log
    has_notes = CourseNote.objects.filter(daily_log=daily_log).exists()

    context = {
        "student": student,
        "date_str": log_date,
        "log": daily_log,
        "has_notes": has_notes,
    }

    # Return updated badge
    response = render(request, "academics/partials/status_badge.html", context)

    # Close the dropdown by also clearing the selector container
    response["HX-Trigger"] = "closeDropdown"

    return response


@require_http_methods(["DELETE"])
@login_required
def attendance_quick_delete(request, student_pk, log_date):
    """
    HTMX endpoint: Delete attendance log for a specific student/date.
    Returns empty badge HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Delete daily log if exists (cascade will delete course notes)
    DailyLog.objects.filter(student=student, date=date_obj, user=request.user).delete()

    context = {
        "student": student,
        "date_str": log_date,
        "log": None,
        "has_notes": False,
    }

    return render(request, "academics/partials/status_badge.html", context)


@require_http_methods(["GET"])
@login_required
def attendance_course_notes(request, student_pk, log_date):
    """
    HTMX endpoint: Show course notes modal for a specific student/date.
    Returns modal HTML fragment.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get existing log if any
    daily_log = DailyLog.objects.filter(student=student, date=date_obj).first()

    # Get active school year
    active_year = SchoolYear.objects.filter(user=request.user, is_active=True).first()

    # Get enrollments for this student
    enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        student=student,
    ).select_related("course", "school_year")

    if active_year:
        enrollments = enrollments.filter(school_year=active_year)

    enrollments = enrollments.order_by("course__name")

    # Get existing course notes if log exists
    course_notes = {}
    if daily_log:
        notes_qs = CourseNote.objects.filter(daily_log=daily_log).select_related(
            "course_enrollment",
        )
        course_notes = {note.course_enrollment.id: note.notes for note in notes_qs}

    context = {
        "student": student,
        "date": date_obj,
        "date_str": log_date,
        "daily_log": daily_log,
        "enrollments": enrollments,
        "course_notes": course_notes,
    }

    return render(request, "academics/partials/course_notes_modal.html", context)


@require_http_methods(["POST"])
@login_required
def attendance_save_course_notes(request, student_pk, log_date):
    """
    HTMX endpoint: Save course notes for a specific student/date.
    Returns success message or closes modal.
    """
    student = get_object_or_404(Student, pk=student_pk, user=request.user)

    # Parse date
    try:
        date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Get or create daily log
    # Use the default attendance status for this user
    default_status = AttendanceStatus.objects.filter(
        user=request.user,
        is_default=True,
    ).first()

    # Fallback to first status if no default is set
    if not default_status:
        default_status = AttendanceStatus.objects.filter(
            user=request.user,
        ).order_by("display_order").first()

    daily_log, created = DailyLog.objects.get_or_create(
        student=student,
        date=date_obj,
        defaults={"attendance_status": default_status, "user": request.user},
    )

    # Get active school year
    active_year = SchoolYear.objects.filter(user=request.user, is_active=True).first()

    # Get enrollments for this student
    enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        student=student,
    )

    if active_year:
        enrollments = enrollments.filter(school_year=active_year)

    # Save course notes
    saved_count = 0
    for enrollment in enrollments:
        note_text = request.POST.get(f"enrollment_{enrollment.id}", "").strip()

        if note_text:
            # Create or update course note
            CourseNote.objects.update_or_create(
                daily_log=daily_log,
                course_enrollment=enrollment,
                defaults={"notes": note_text, "user": request.user},
            )
            saved_count += 1
        else:
            # Delete course note if text is empty
            CourseNote.objects.filter(
                daily_log=daily_log, course_enrollment=enrollment,
            ).delete()

    # Check if there are any course notes for this log
    has_notes = CourseNote.objects.filter(daily_log=daily_log).exists()

    # Render updated badge with out-of-band swap to update the cell
    # The badge template already has the wrapper div with id, so we need to add hx-swap-oob to it
    badge_html = render_to_string(
        "academics/partials/status_badge.html",
        {
            "student": student,
            "date_str": log_date,
            "log": daily_log,
            "has_notes": has_notes,
        },
    )

    # Add hx-swap-oob attribute to the badge HTML
    # The badge template starts with <div id="cell-...">
    badge_html_with_oob = badge_html.replace(
        f'<div id="cell-{student_pk}-{log_date}"',
        f'<div id="cell-{student_pk}-{log_date}" hx-swap-oob="true"',
        1,
    )

    # Return updated badge HTML with OOB swap to update the badge, and closes modal
    return HttpResponse(badge_html_with_oob)


# =============================================================================
# Attendance Status Management Views
# =============================================================================


class AttendanceStatusListView(LoginRequiredMixin, ListView):
    """List all attendance statuses for the current user."""

    model = AttendanceStatus
    template_name = "academics/attendance_status_list.html"
    context_object_name = "statuses"

    def get_queryset(self):
        return AttendanceStatus.objects.filter(
            user=self.request.user,
        ).order_by("display_order")


class AttendanceStatusCreateView(LoginRequiredMixin, CreateView):
    """Create a new attendance status."""

    model = AttendanceStatus
    template_name = "academics/attendance_status_form.html"
    fields = [
        "code",
        "label",
        "abbreviation",
        "color",
        "is_instructional",
        "is_default",
    ]
    success_url = reverse_lazy("academics:attendance_status_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add help text and widgets
        form.fields["code"].widget.attrs["class"] = "form-control"
        form.fields["label"].widget.attrs["class"] = "form-control"
        form.fields["abbreviation"].widget.attrs["class"] = "form-control"
        form.fields["abbreviation"].widget.attrs["maxlength"] = "3"
        form.fields["color"].widget.attrs["class"] = "form-control"
        form.fields["color"].widget.attrs["type"] = "color"
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get colors from active palette
        active_palette = ColorPalette.objects.filter(
            user=self.request.user,
            is_active=True,
        ).first()
        if active_palette:
            context["palette_colors"] = active_palette.colors.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Set display_order to last
        max_order = AttendanceStatus.objects.filter(
            user=self.request.user,
        ).aggregate(max_order=Max("display_order"))["max_order"]
        form.instance.display_order = (max_order or 0) + 1
        messages.success(
            self.request,
            f"Attendance status '{form.instance.label}' created successfully!",
        )
        return super().form_valid(form)


class AttendanceStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing attendance status."""

    model = AttendanceStatus
    template_name = "academics/attendance_status_form.html"
    fields = [
        "code",
        "label",
        "abbreviation",
        "color",
        "is_instructional",
        "is_default",
    ]
    success_url = reverse_lazy("academics:attendance_status_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["code"].widget.attrs["class"] = "form-control"
        form.fields["label"].widget.attrs["class"] = "form-control"
        form.fields["abbreviation"].widget.attrs["class"] = "form-control"
        form.fields["abbreviation"].widget.attrs["maxlength"] = "3"
        form.fields["color"].widget.attrs["class"] = "form-control"
        form.fields["color"].widget.attrs["type"] = "color"
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get colors from active palette
        active_palette = ColorPalette.objects.filter(
            user=self.request.user,
            is_active=True,
        ).first()
        if active_palette:
            context["palette_colors"] = active_palette.colors.all()
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Attendance status '{form.instance.label}' updated successfully!",
        )
        return super().form_valid(form)


class AttendanceStatusDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete an attendance status."""

    model = AttendanceStatus
    template_name = "academics/attendance_status_confirm_delete.html"
    success_url = reverse_lazy("academics:attendance_status_list")

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        status = self.get_object()
        messages.success(
            self.request,
            f"Attendance status '{status.label}' deleted successfully!",
        )
        return super().delete(request, *args, **kwargs)
