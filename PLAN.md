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

### 🚧 Phase 2: Attendance System (TODO)

**Models to Create:**
- [ ] **Attendance** model
  - Fields: student, date, status (Present, Absent, Sick, Holiday, Field Trip)
  - Link to SchoolYear for reporting

**Features to Implement:**
- [ ] Calendar view dashboard for the current week
- [ ] Quick toggle for attendance status per student per day
- [ ] Daily log view
- [ ] Attendance statistics per school year
- [ ] Total instructional days calculation
- [ ] PDF/CSV export for state compliance reporting
- [ ] Monthly/yearly attendance reports

**Technical Considerations:**
- Consider using HTMX for dynamic attendance toggling without page reloads
- Calendar widget selection (FullCalendar.js or Bootstrap calendar)
- Bulk actions for marking multiple students/days

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
│   ├── academics/          # Phase 1 app (COMPLETED)
│   │   ├── models.py       # SchoolYear, Student, Course, CurriculumResource
│   │   ├── views.py        # All CRUD views + Dashboard
│   │   ├── forms.py        # Crispy forms for all models
│   │   ├── admin.py        # Django admin configuration
│   │   ├── urls.py         # URL routing
│   │   └── migrations/
│   │
│   ├── users/              # Custom user model (pre-existing)
│   │
│   ├── templates/
│   │   ├── academics/      # All academic templates
│   │   │   ├── base.html   # Base template with sidebar nav
│   │   │   ├── dashboard.html
│   │   │   ├── schoolyear_*.html
│   │   │   ├── student_*.html
│   │   │   ├── course_*.html
│   │   │   └── curriculumresource_*.html
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
                     │
                     │ (1)
                     ↓
              CurriculumResource (N)
```

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

### Current Phase 1 Items
- [ ] Add tests for models, views, and forms
- [ ] Add form validation (e.g., end_date must be after start_date)
- [ ] Consider adding "archived" status for old school years
- [ ] Add bulk delete confirmation with related object counts
- [ ] Add inline curriculum resource editing on course form

### Future Considerations
- [ ] Add export functionality (CSV/PDF) for all models
- [ ] Add data import capability (CSV upload)
- [ ] Add image upload for students (profile pictures)
- [ ] Consider adding "notes" field to Student and SchoolYear
- [ ] Add activity/audit log for compliance tracking
- [ ] Multi-year course support (for courses spanning multiple years)
- [ ] Grade/progress tracking within courses

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

### 4. Create Test Data (if needed)
```bash
just manage shell
```
```python
from idahomeschool.users.models import User
from idahomeschool.academics.models import SchoolYear, Student, Course

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

# Create course
course = Course.objects.create(
    name="Math 4",
    student=student,
    school_year=year,
    description="4th grade mathematics"
)
```

## Next Immediate Steps (Phase 2)

1. **Create Attendance Model**
   - Add to `idahomeschool/academics/models.py`
   - Create migration
   - Add to admin.py

2. **Create Attendance Views**
   - Calendar view for week/month
   - Quick toggle interface
   - Attendance report view

3. **Update Dashboard**
   - Add attendance summary
   - Show today's attendance status
   - Link to attendance entry

4. **Create Templates**
   - `attendance_calendar.html` - Main calendar view
   - `attendance_report.html` - Reporting view
   - Update dashboard with attendance widgets

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
