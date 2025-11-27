# OpenHomeSchool - Implementation Plan

This document tracks implementation progress and provides context for resuming work on the project.

## Project Overview

OpenHomeSchool is a self-hosted Django web application for managing homeschooling records in compliance with Idaho state recommendations. It serves as a "Metadata Layer" managing students, school years, courses, and attendance, while integrating with Paperless-NGX as the "Document Layer."

**Tech Stack:**
- Django 5.2 + Python 3.13
- PostgreSQL
- Bootstrap 5
- Docker Compose for local development
- uv for Python package management

## Implementation Status

**Current Progress:** Phase 1 & 2 Complete ✅ | Phase 3 & 4 Pending

- ✅ **Phase 1: Foundation** - Complete
- ✅ **Phase 2: Attendance System** - Complete (with course-specific notes)
- 🔜 **Phase 3: Paperless-NGX Integration** - Next up
- 📋 **Phase 4: Idaho Compliance Reporting** - Planned

---

### ✅ Phase 1: Foundation (COMPLETED)

**Models Created** (`idahomeschool/academics/models.py`):
- [x] **SchoolYear** - Academic year management with active year tracking
- [x] **Student** - Student records with grade level and age calculation
- [x] **Course** - Course management linked to students and school years
- [x] **CurriculumResource** - Textbooks/workbooks for courses

**Features Implemented:**
- [x] Full CRUD operations for all models
- [x] User authentication and authorization
- [x] User data isolation (users only see their own data)
- [x] Django Admin interface with inline editing
- [x] Dashboard with statistics and recent activity
- [x] Bootstrap 5 responsive templates
- [x] Crispy forms for user-friendly data entry
- [x] Search functionality for students
- [x] Filtering for courses (by school year and student)
- [x] Pagination (20 items per page)
- [x] Success/error messages on all operations
- [x] Navigation integrated into main site

**URL Structure:**
- `/academics/` - Dashboard
- `/academics/school-years/` - School year management
- `/academics/students/` - Student management
- `/academics/courses/` - Course management
- `/admin/academics/` - Django admin interface

### ✅ Phase 2: Attendance System (COMPLETED)

**Models Created** (`idahomeschool/academics/models.py`):
- [x] **DailyLog** - Daily attendance tracking for students
  - Fields: student, date, status (Present, Absent, Sick, Holiday, Field Trip), general_notes, user
  - Unique constraint: one log per student per day
  - `is_instructional_day` property for compliance reporting (Present + Field Trip)

- [x] **CourseNote** - Course-specific notes for each day
  - Fields: daily_log, course, notes, user
  - Allows tracking what was covered in each course each day
  - Unique constraint: one note per course per daily log

**Features Implemented:**
- [x] **Daily Log Entry View** - Comprehensive attendance entry with course notes
  - Select student and date (with prev/next navigation)
  - Mark attendance status
  - Add notes for ALL enrolled courses
  - Auto-save and retrieve existing entries

- [x] **Attendance Calendar View** - Visual grid of attendance
  - Week or month view toggle
  - All students displayed in grid format
  - Color-coded status badges (Present=green, Absent=red, Sick=yellow, etc.)
  - Click any date to quickly add/edit attendance

- [x] **Attendance Report View** - Compliance reporting
  - Filter by school year and student
  - Total instructional days calculation (Present + Field Trip)
  - Breakdown by status type (Present, Absent, Sick, Holiday, Field Trip)
  - Idaho homeschool compliance notes

- [x] **Daily Log List View** - Filterable list of all logs
  - Filter by student and date range
  - Pagination (20 items per page)
  - Quick actions (View, Edit, Delete)

- [x] **Daily Log Detail View** - Full log display
  - Shows attendance status and general notes
  - Displays all course notes for that day

- [x] **Dashboard Integration**
  - Instructional days counter for active year
  - Quick action buttons for attendance entry
  - Recent attendance logs widget

- [x] **Django Admin Integration**
  - Full admin interface for DailyLog and CourseNote
  - Inline course note editing within daily logs
  - Searchable and filterable

**URL Structure:**
- `/academics/attendance/` - Attendance calendar view
- `/academics/attendance/entry/` - Daily log entry (with course notes)
- `/academics/attendance/report/` - Compliance reports
- `/academics/daily-logs/` - List all daily logs
- `/academics/daily-logs/<pk>/` - Daily log detail view

**Technical Implementation:**
- Bootstrap 5 responsive design with color-coded badges
- User data isolation maintained throughout
- Crispy forms for all data entry
- Student and date navigation with JavaScript helpers
- Optimized queries with select_related and prefetch_related

### 📋 Phase 3: Paperless-NGX Integration (TODO)

**Models to Create:**
- [ ] **PaperlessLink** model (GenericForeignKey approach)
  - Fields: paperless_document_id, paperless_thumbnail_url
  - Generic relation to Course, Student, or other models

- [ ] **PaperlessConfig** model (settings)
  - Fields: api_url, api_token
  - Encrypted token storage

**Features to Implement:**
- [ ] Paperless API client class (`utils/paperless_client.py`)
- [ ] Settings page for Paperless URL and API token
- [ ] Document selector UI component (modal/search interface)
- [ ] Document linking from Student and Course detail pages
- [ ] Thumbnail display of linked documents
- [ ] Tag syncing to Paperless (apply tags when documents are linked)
- [ ] Work samples section (documents linked to courses)
- [ ] Correspondence section (documents linked to students)
- [ ] Standardized test results tracking

**API Endpoints to Integrate:**
- `/api/documents/` - List and search documents
- `/api/tags/` - Manage tags
- `/api/documents/{id}/` - Get document details

### 📊 Phase 4: Idaho Compliance Reporting (TODO)

**Features to Implement:**
- [ ] "End of Year Report" page
- [ ] Aggregate attendance by school year
- [ ] List all courses and curriculum resources
- [ ] Display thumbnails of work samples
- [ ] Printable view/PDF generation
- [ ] Export functionality (PDF/HTML)
- [ ] Portfolio view per student

## Project Structure

```
idahomeschool/
├── idahomeschool/
│   ├── academics/          # Phase 1 & 2 (COMPLETED)
│   │   ├── models.py       # SchoolYear, Student, Course, CurriculumResource
│   │   │                   # DailyLog, CourseNote (Phase 2)
│   │   ├── views.py        # All CRUD views + Dashboard
│   │   │                   # Attendance views (Phase 2)
│   │   ├── forms.py        # Crispy forms for all models
│   │   │                   # DailyLogForm, CourseNoteForm (Phase 2)
│   │   ├── admin.py        # Django admin configuration
│   │   ├── urls.py         # URL routing
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── 0002_dailylog_coursenote_and_more.py
│   │
│   ├── users/              # Custom user model (pre-existing)
│   │
│   ├── templates/
│   │   ├── academics/      # All academic templates
│   │   │   ├── base.html   # Base template with sidebar nav (updated)
│   │   │   ├── dashboard.html  # Updated with attendance widgets
│   │   │   ├── schoolyear_*.html
│   │   │   ├── student_*.html
│   │   │   ├── course_*.html
│   │   │   ├── curriculumresource_*.html
│   │   │   ├── attendance_calendar.html    # Phase 2
│   │   │   ├── attendance_report.html      # Phase 2
│   │   │   ├── dailylog_entry.html         # Phase 2 (main entry form)
│   │   │   ├── dailylog_list.html          # Phase 2
│   │   │   ├── dailylog_detail.html        # Phase 2
│   │   │   ├── dailylog_form.html          # Phase 2
│   │   │   └── dailylog_confirm_delete.html # Phase 2
│   │   └── base.html       # Main site template (navigation updated)
│   │
│   └── static/             # Static assets (JS, CSS, images)
│
├── config/
│   ├── settings/
│   │   ├── base.py         # Base settings (academics app added)
│   │   ├── local.py        # Local dev settings
│   │   └── production.py   # Production settings
│   └── urls.py             # Root URL config (academics included)
│
├── PRD.md                  # Product Requirements Document
├── PLAN.md                 # This file
└── CLAUDE.md               # Development guidelines
```

## Important Technical Details

### Model Relationships

```
User (1) ──────→ (N) SchoolYear
                     │
                     │ (N)
                     ↓
User (1) ──────→ (N) Student ←──────┐
                     │               │
                     │ (M:N)         │
                     │               │
                     ↓               │
                 SchoolYear          │
                     │               │
                     │ (1)           │ (1)
                     ↓               │
                  Course ────────────┘
                     │               │
                     │ (1)           │
                     ↓               │
              CurriculumResource (N) │
                                     │
                                     │
User (1) ──────→ (N) DailyLog ───────┘
                     │  (1)
                     │
                     │ (1)
                     ↓
                 CourseNote (N) ──→ Course (1)
```

**Phase 2 Models:**
- **DailyLog**: One entry per student per day, tracks attendance status
- **CourseNote**: Multiple notes per daily log, one per course
- CourseNote connects the daily log to specific courses, allowing detailed tracking

### User Data Isolation Pattern

All models include a `user` ForeignKey and views filter by `request.user`:
```python
queryset = Model.objects.filter(user=request.user)
# or for related objects:
queryset = Course.objects.filter(student__user=request.user)
```

### Active School Year Logic

Only one school year can be active per user. This is enforced in the `SchoolYear.save()` method:
```python
def save(self, *args, **kwargs):
    if self.is_active:
        SchoolYear.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
    super().save(*args, **kwargs)
```

## Development Commands

### Docker (via justfile)
```bash
just build          # Build Docker images
just up             # Start containers (Django on :8000, Webpack on :3000)
just down           # Stop containers
just logs           # View logs
just manage <cmd>   # Run Django management commands
```

### Common Management Commands
```bash
just manage makemigrations      # Create migrations
just manage migrate             # Apply migrations
just manage createsuperuser     # Create admin user
just manage shell               # Django shell
just manage check               # System check
just manage show_urls           # List all URLs
```

### Testing
```bash
uv run pytest                   # Run tests
uv run coverage run -m pytest   # Run with coverage
uv run coverage html            # Generate coverage report
```

## Known Issues / TODOs

### Phase 1 & 2 Items
- [ ] Add tests for models, views, and forms
- [ ] Add form validation (e.g., end_date must be after start_date)
- [ ] Consider adding "archived" status for old school years
- [ ] Add bulk delete confirmation with related object counts
- [ ] Add inline curriculum resource editing on course form
- [ ] Add PDF/CSV export for attendance reports (compliance)
- [ ] Consider HTMX for dynamic attendance toggling without page reloads
- [ ] Add bulk actions for marking multiple students/days

### Future Considerations
- [ ] Add data import capability (CSV upload)
- [ ] Add image upload for students (profile pictures)
- [ ] Consider adding "notes" field to Student and SchoolYear
- [ ] Add activity/audit log for compliance tracking
- [ ] Multi-year course support (for courses spanning multiple years)
- [ ] Grade/progress tracking within courses
- [ ] Email reminders for attendance logging
- [ ] Mobile app for quick attendance entry

## Getting Started (Next Session)

### 1. Start Development Environment
```bash
cd /Users/taylordaugherty/code/idahomeschool
just up
```

### 2. Verify Everything Works
```bash
just manage check
just manage showmigrations academics
```

### 3. Access the Application
- Main site: http://localhost:8000
- Admin: http://localhost:8000/admin
- Academic Records: http://localhost:8000/academics/
- **Attendance Entry**: http://localhost:8000/academics/attendance/entry/
- **Attendance Calendar**: http://localhost:8000/academics/attendance/
- **Attendance Reports**: http://localhost:8000/academics/attendance/report/

### 4. Create Test Data (if needed)
```bash
just manage shell
```
```python
from idahomeschool.users.models import User
from idahomeschool.academics.models import SchoolYear, Student, Course, DailyLog, CourseNote
from datetime import date

user = User.objects.first()  # or create one

# Create school year
year = SchoolYear.objects.create(
    name="2024-2025",
    start_date="2024-09-01",
    end_date="2025-06-15",
    is_active=True,
    user=user
)

# Create student
student = Student.objects.create(
    name="John Doe",
    date_of_birth="2015-03-15",
    grade_level="4",
    user=user
)
student.school_years.add(year)

# Create courses
math = Course.objects.create(
    name="Math 4",
    student=student,
    school_year=year,
    description="4th grade mathematics"
)

science = Course.objects.create(
    name="Science 4",
    student=student,
    school_year=year,
    description="4th grade science"
)

# Create daily log with course notes
daily_log = DailyLog.objects.create(
    student=student,
    date=date.today(),
    status="PRESENT",
    general_notes="Great day of learning!",
    user=user
)

# Add course notes
CourseNote.objects.create(
    daily_log=daily_log,
    course=math,
    notes="Completed chapter 5 on fractions. Student showed good understanding.",
    user=user
)

CourseNote.objects.create(
    daily_log=daily_log,
    course=science,
    notes="Studied the solar system. Built a model of planets.",
    user=user
)
```

## Next Immediate Steps (Phase 3)

Phase 3 will focus on **Paperless-NGX Integration** - the core feature that connects the Django app with Paperless-NGX for document management.

1. **Research & Planning**
   - Review Paperless-NGX API documentation
   - Plan GenericForeignKey implementation for PaperlessLink
   - Design document selector UI/UX

2. **Create Models**
   - Add `PaperlessConfig` model for API settings
   - Add `PaperlessLink` model with GenericForeignKey
   - Create migrations

3. **Build Paperless API Client**
   - Create `utils/paperless_client.py`
   - Implement document search/list functionality
   - Implement tag management
   - Add error handling and retry logic

4. **Create Settings Interface**
   - Settings page for Paperless URL and API token
   - Token validation
   - Connection testing

5. **Build Document Selector UI**
   - Modal/search interface for selecting documents
   - Thumbnail previews
   - Search and filter capabilities
   - Integration into Student and Course detail pages

6. **Implement Document Linking**
   - Link documents to students (correspondence, admin docs)
   - Link documents to courses (work samples, tests)
   - Display linked documents with thumbnails
   - Tag syncing to Paperless

## References

- **PRD**: See `PRD.md` for full product requirements
- **Django Docs**: https://docs.djangoproject.com/en/5.2/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **Crispy Forms**: https://django-crispy-forms.readthedocs.io/
- **Paperless-NGX API**: https://docs.paperless-ngx.com/api/

## Notes for AI Assistant

- All models must include `user` field for data isolation
- Use `LoginRequiredMixin` and `UserPassesTestMixin` for all views
- Follow existing code style (Ruff formatting, 4-space indent for Python)
- Use crispy forms with Bootstrap 5 for all forms
- Maintain consistency with existing template structure
- Add success messages for all create/update/delete operations
- Templates should extend `academics/base.html`
- Use `{% url %}` template tags instead of hardcoded URLs

## Contact & Support

For questions or issues during development, refer to:
- Project CLAUDE.md for coding guidelines
- PRD.md for feature requirements
- Django project documentation in config/
