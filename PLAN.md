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

**Current Progress:** Phases 1, 2, 2.5, 2.6, 2.7, 2.8 & Student Photos Complete ✅ | Phase 3 & 4 Pending

- ✅ **Phase 1: Foundation** - Complete
- ✅ **Phase 2: Attendance System** - Complete (with course-specific notes)
- ✅ **Phase 2.5: HTMX Dynamic Attendance** - Complete
- ✅ **Phase 2.6: Multi-Year Course Support** - Complete (with tagging and HTMX search)
- ✅ **Phase 2.7: Navigation & UX Restructuring** - Complete
- ✅ **Phase 2.8: Color Palette System** - Complete (tag color management with named palettes)
- ✅ **Student Photo Uploads** - Complete (filesystem-based, cloud-ready)
- 🔜 **Phase 3: Paperless-NGX Integration** - Planned (next up)
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

**Authentication & Template Structure:**
- [x] Django-allauth integration with MFA support
- [x] Custom template structure with separate blocks for authenticated/unauthenticated users
  - `base.html` uses `{% block content %}` for authenticated users (with sidebar)
  - `base.html` uses `{% block unauthenticated_content %}` for login/signup pages
- [x] Allauth templates created:
  - `account/login.html` - Bootstrap 5 styled login form
  - `account/signup.html` - User registration form
  - `account/logout.html` - Sign out confirmation
  - `account/password_reset.html` - Password reset request form
- [x] Fixed duplicate content block issue in base template
- [x] LOGIN_URL configured to 'account_login'
- [x] LOGIN_REDIRECT_URL configured to 'users:redirect'

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
  - PDF export functionality with professional formatting
    - Flipped table structure (statuses as rows, max 3 students per table)
    - Detailed course and curriculum information section
    - WeasyPrint integration for PDF generation

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
- `/academics/attendance/report/pdf/` - PDF export of attendance report
- `/academics/daily-logs/` - List all daily logs
- `/academics/daily-logs/<pk>/` - Daily log detail view

**Technical Implementation:**
- Bootstrap 5 responsive design with color-coded badges
- User data isolation maintained throughout
- Crispy forms for all data entry
- Student and date navigation with JavaScript helpers
- Optimized queries with select_related and prefetch_related
- WeasyPrint for PDF generation
  - Added system dependencies to Dockerfile (libpango, libgdk-pixbuf, etc.)
  - Professional PDF formatting with page breaks and styled tables
  - Report data chunked into groups of 3 students per table for readability

### ✅ Phase 2.5: HTMX Dynamic Attendance (COMPLETED)

**Overview:**
Enhanced the attendance calendar with HTMX for dynamic, real-time updates without page reloads. This dramatically improves the user experience for daily attendance logging.

**Dependencies Added:**
- [x] `django-htmx==1.26.0` - Django middleware for HTMX integration
- [x] `htmx.org` (via npm) - Frontend HTMX library bundled with Webpack
- [x] Bootstrap Icons CDN - For UI icons

**Features Implemented:**

- [x] **Quick Status Toggle**
  - Click any attendance badge to show inline dropdown
  - Status options appear instantly without page reload
  - Auto-closes after selection
  - Supports: Present, Absent, Sick, Holiday, Field Trip

- [x] **Inline Course Notes Modal**
  - Click note icon to open modal with all course notes
  - Edit multiple course notes in one place
  - Modal closes dropdown automatically
  - Shows general notes and course-specific notes

- [x] **Batch Operations**
  - Toggle batch mode with dedicated button or Space key
  - Single-click to select individual cells
  - Shift+Click to select range of cells
  - Ctrl/Cmd+Click to toggle individual cells
  - Visual selection indicators (blue highlight + checkmark)
  - Apply status to all selected cells at once
  - Auto-exits batch mode after applying changes

- [x] **Keyboard Navigation**
  - Arrow keys (↑↓←→) to navigate grid
  - Number keys (1-5) for quick status setting
    - 1 = Present, 2 = Absent, 3 = Sick, 4 = Holiday, 5 = Field Trip
  - Space bar to toggle batch mode
  - Escape to close dropdowns/modals
  - Visual keyboard focus indicator (only shown when using keyboard)
  - Help card with keyboard shortcuts displayed on calendar

- [x] **Delete Attendance Log**
  - Delete button in status dropdown
  - Confirmation prompt before deletion
  - Returns cell to empty state after deletion

**Technical Implementation:**

**Backend (Django):**
- Added 5 new HTMX endpoint views in `views.py`:
  - `attendance_quick_toggle()` - Returns status selector dropdown HTML
  - `attendance_quick_update()` - Updates status and returns new badge HTML
  - `attendance_quick_delete()` - Deletes log and returns empty badge HTML
  - `attendance_course_notes()` - Returns course notes modal HTML
  - `attendance_save_course_notes()` - Saves notes and closes modal
- Added URL patterns for HTMX endpoints in `urls.py`
- CSRF token handling via `X-CSRFToken` header and meta tag
- Partial template rendering for dynamic updates

**Frontend (JavaScript/CSS):**
- Created `attendance-grid.js` (445 lines) - Batch operations & keyboard navigation
  - AttendanceGrid class with full state management
  - Batch mode with multi-select and bulk update
  - Keyboard navigation with arrow keys and shortcuts
  - CSRF token integration for fetch requests
  - HTMX.process() integration for dynamically inserted elements
- Created `attendance-grid.scss` - Styling for dynamic features
  - Batch mode visual indicators
  - Keyboard focus styling
  - Selection highlights and animations
  - User-select prevention in batch mode
- Updated `project.js` to expose HTMX globally for script access

**Partial Templates Created:**
- `partials/status_badge.html` - Reusable badge component with HTMX attributes
- `partials/status_selector.html` - Dropdown status selector
- `partials/course_notes_modal.html` - Modal for course notes editing

**Template Tags Created:**
- `academics/templatetags/academics_extras.py`
  - `get_item` filter for dictionary access in templates

**URL Structure:**
- `/academics/attendance/quick-toggle/<student_pk>/<date>/` - Get status dropdown
- `/academics/attendance/quick-update/<student_pk>/<date>/` - Update status
- `/academics/attendance/quick-delete/<student_pk>/<date>/` - Delete log
- `/academics/attendance/course-notes/<student_pk>/<date>/` - Get course notes modal
- `/academics/attendance/save-course-notes/<student_pk>/<date>/` - Save course notes

**Configuration:**
- HTMX middleware added to `MIDDLEWARE` in `config/settings/base.py`
- CSRF token meta tag added to `templates/base.html`
- HTMX global event listener for automatic CSRF token injection
- Bootstrap Icons CDN for note and UI icons

**Bug Fixes Applied:**
- Fixed duplicate note icons by wrapping badge and button in container div
- Fixed delete button not working by adding explicit CSRF header
- Fixed dropdown not closing when modal opens
- Fixed text selection during shift-click by preventing default and CSS user-select
- Fixed keyboard focus showing on page load by tracking `keyboardActive` state
- Fixed keyboard shortcuts (1-5) not working by setting initial focus cell
- Fixed batch update breaking HTMX by calling `htmx.process()` on new elements
- Fixed date parsing in batch mode (split on `-` correctly for YYYY-MM-DD format)

**Performance Optimizations:**
- Attendance grid view uses `prefetch_related('course_notes')` to check for notes
- Batch operations use concurrent async fetch requests
- Dropdown positioning calculated dynamically based on click position

**User Experience Improvements:**
- Reduced attendance logging from 3-4 page loads to instant updates
- Batch mode enables marking entire week in seconds
- Keyboard shortcuts for power users
- Visual feedback for all interactions (animations, highlights, badges)
- Progressive enhancement - links still work without JavaScript

### ✅ Phase 2.6: Multi-Year Course Support (COMPLETED)

**Overview:**
Implemented comprehensive multi-year course support using the Course Template Model. Courses like "Algebra 1" or "Latin" that span multiple school years can now be tracked as a single educational unit while maintaining year-by-year enrollment and progress tracking. Also implemented resource tagging system and HTMX-powered resource search for improved UX.

**Models Implemented:**

1. **CourseTemplate** - Defines a course independent of school year
   - Fields: user, name, description, suggested_resources (M2M to Resource), created_at, updated_at
   - Replaces the old Course model's role as the course definition
   - Resources are suggested at template level and can be added to specific courses

2. **Course** - Refactored from student-specific to user-owned
   - **REMOVED**: student, school_year foreign keys (these are now in CourseEnrollment)
   - Fields: user, name, description, course_template (optional FK), resources (M2M), created_at, updated_at
   - A Course now belongs to a user and can be reused across multiple students/years
   - Students enroll in courses via CourseEnrollment

3. **CourseEnrollment** - Links student to course for specific school year
   - Fields: user, student, course, school_year, status, started_date, completed_date, final_grade
   - Status choices: IN_PROGRESS, COMPLETED, PAUSED
   - Unique constraint: one enrollment per student+course+school_year
   - This is the new way to track "which student is taking which course in which year"

4. **Tag** - NEW model for organizing resources
   - Fields: user, name, color (hex color code), created_at, updated_at
   - Unique constraint: unique tag names per user
   - Used for filtering and organizing curriculum resources

5. **Resource** - NEW model replacing CurriculumResource
   - Fields: user, title, author, publisher, isbn, resource_type, url, tags (M2M), created_at, updated_at
   - Resource types: TEXTBOOK, WORKBOOK, ONLINE, VIDEO, SOFTWARE, OTHER
   - Tags enable flexible categorization and filtering
   - Resources are shared across courses via M2M relationship

6. **CourseNote** - Updated to reference CourseEnrollment
   - **CHANGED**: course_enrollment FK (was course FK)
   - Now connects daily logs to specific enrollment (student+course+year combination)
   - This allows proper tracking of notes across multi-year courses

**Migration Strategy (Completed):**

- ✅ Created Tag and Resource models
- ✅ Created CourseTemplate model with suggested_resources M2M to Resource
- ✅ Created CourseEnrollment model linking student+course+school_year
- ✅ Removed student and school_year FKs from Course model (Course.user is now the owner)
- ✅ Updated CourseNote to reference course_enrollment instead of course
- ✅ Created data migration (0005_migrate_course_data.py) to:
  - Create Course from old Course records (one per user+name)
  - Create CourseEnrollment for each old Course record
  - Update CourseNote foreign keys to point to enrollments
- ✅ Removed old CurriculumResource model (replaced by Resource)

**Features Implemented:**

**1. Course Template Management**
- ✅ Full CRUD views for course templates
- ✅ List view showing all templates with enrollment count
- ✅ Detail view showing all enrollments using this template
- ✅ Suggested resources management (M2M to Resource)
- ✅ Auto-populate resources when selecting a template for a course

**2. Course Management (Refactored)**
- ✅ CRUD views for courses (user-owned, not student-specific)
- ✅ Course can be created from template or standalone
- ✅ Resources are M2M (can attach multiple resources to a course)
- ✅ HTMX-powered resource search with live filtering
- ✅ Resource checkboxes with search-as-you-type
- ✅ Auto-selection of template resources when choosing a template

**3. Course Enrollment Management**
- ✅ Full CRUD views for enrollments
- ✅ Enrollment workflow:
  - Select student and school year
  - Select course
  - Set status (IN_PROGRESS, COMPLETED, PAUSED)
  - Track start/end dates and final grades
- ✅ Unique constraint prevents duplicate enrollments
- ✅ List view with filtering by student and school year

**4. Tag & Resource System**
- ✅ Tag CRUD operations with color coding
- ✅ Resource CRUD operations with tag assignment
- ✅ Tag filtering in resource list view
- ✅ HTMX search for resources in course/template forms
- ✅ Visual tag badges with custom colors
- ✅ Search by title, author, or publisher

**5. Updated Attendance & Reporting**
- ✅ Daily log entry updated to use enrollments
- ✅ Calendar view modal updated to show enrollment-based notes
- ✅ PDF export updated to show enrollments with school year
- ✅ Dashboard updated to show active enrollments
- ✅ All views updated to query by enrollment instead of course

**6. Dashboard Integration**
- ✅ Active enrollments widget (shows current year enrollments)
- ✅ Recent courses widget
- ✅ Enrollment status indicators (badges for IN_PROGRESS, COMPLETED)

**URL Structure (Implemented):**
```
# Course Templates
/academics/course-templates/                    # List all templates
/academics/course-templates/create/             # Create new template
/academics/course-templates/<pk>/               # Template detail (shows all courses using it)
/academics/course-templates/<pk>/update/        # Edit template
/academics/course-templates/<pk>/delete/        # Delete template

# Courses (Refactored - user-owned)
/academics/courses/                             # List all courses
/academics/courses/create/                      # Create new course
/academics/courses/<pk>/                        # Course detail (shows enrollments)
/academics/courses/<pk>/update/                 # Edit course
/academics/courses/<pk>/delete/                 # Delete course

# Enrollments
/academics/enrollments/                         # List all enrollments
/academics/enrollments/create/                  # New enrollment
/academics/enrollments/<pk>/                    # Enrollment detail
/academics/enrollments/<pk>/update/             # Edit enrollment
/academics/enrollments/<pk>/delete/             # Delete enrollment

# Tags & Resources
/academics/tags/                                # List all tags
/academics/tags/create/                         # Create new tag
/academics/tags/<pk>/update/                    # Edit tag
/academics/tags/<pk>/delete/                    # Delete tag

/academics/resources/                           # List all resources (with tag filtering)
/academics/resources/create/                    # Create new resource
/academics/resources/<pk>/                      # Resource detail
/academics/resources/<pk>/update/               # Edit resource
/academics/resources/<pk>/delete/               # Delete resource

# HTMX Endpoints
/academics/resources/search/                    # HTMX resource search endpoint
```

**Updated Model Relationships:**
```
User (1) ──────→ (N) ColorPalette (is_active)
                     │
                     │ (M:N)
                     ↓
User (1) ──────→ (N) Color (hex codes)
                     │
                     │ (used by)
                     ↓
User (1) ──────→ (N) Tag
                     │
                     │ (M:N)
                     ↓
User (1) ──────→ (N) Resource ←────┐
                     │              │ (M:N)
                     │              │
                     │ (M:N)        │
                     ↓              │
User (1) ──────→ (N) Course ←──────┤
                     │              │
                     │ (M:N)        │ (M:N)
                     ↓              │
User (1) ──────→ (N) CourseTemplate┘

User (1) ──────→ (N) CourseEnrollment
                     │
                     ├──→ (1) Student
                     ├──→ (1) SchoolYear
                     └──→ (1) Course

User (1) ──────→ (N) DailyLog ←────┐
                     │              │ (1)
                     │ (1)          │
                     ↓              │
                 CourseNote (N) ────┘
                     │
                     └──→ (1) CourseEnrollment
```

**Key Architecture Benefits:**
- ✅ Courses are user-owned and reusable across multiple students/years
- ✅ CourseEnrollment tracks which student takes which course in which year
- ✅ CourseTemplate provides optional standardization and resource suggestions
- ✅ Resources are tagged and searchable with HTMX for better UX
- ✅ CourseNote properly tracks notes per enrollment (student+course+year)
- ✅ Multi-year courses supported through multiple enrollments of the same course
- ✅ Shared resources across courses via M2M relationship
- ✅ Flexible tagging system for organizing curriculum materials

**Migration Completed Successfully:**
- ✅ All existing Course records migrated to new structure
- ✅ CourseEnrollments created for all old student+course+year combinations
- ✅ CourseNotes updated to reference enrollments instead of courses
- ✅ No data loss during migration
- ✅ All views, templates, and reports updated to use new architecture

### ✅ Phase 2.7: Navigation & UX Restructuring (COMPLETED)

**Overview:**
Based on customer feedback, restructure the navigation to provide a cleaner, more focused user experience with a persistent sidebar and direct access to the dashboard.

**UX Requirements:**
- ✅ Remove top header navigation completely
- ✅ Remove Home/About pages - root URL redirects directly to dashboard
- ✅ Persistent collapsible sidebar pinned to left side across all pages
- ✅ Expandable main sections in sidebar with subsections
- ✅ Clean, focused interface for homeschooling parents

**Navigation Structure:**
```
Desktop/Tablet Sidebar:
├─ 📊 Dashboard
├─ 🏫 School Management (expandable)
│  ├─ 📅 School Years
│  ├─ 👥 Students
│  └─ 📚 Courses
├─ 📅 Attendance (expandable)
│  ├─ ✏️ Daily Log Entry
│  ├─ 📆 Calendar View
│  ├─ 📄 Reports
│  └─ 📋 All Logs
└─ 👤 User Settings (expandable)
   ├─ 👤 My Profile
   └─ 🚪 Sign Out

Mobile: ☰ Hamburger → Slide-out menu (same structure)
```

**Technical Implementation:**

**Frontend Changes:**
- [x] Update `templates/base.html` - Remove navbar, add sidebar layout
- [x] Create `static/sass/sidebar.scss` - Responsive sidebar styles
- [x] Add sidebar JavaScript to `static/js/project.js` - Collapse/expand functionality
- [x] Update `academics/base.html` - Remove duplicate sidebar
- [x] Sidebar state persists using localStorage (desktop only)
- [x] Add Bootstrap Icons for all navigation items
- [x] Mobile header bar with hamburger button
- [x] X close button on mobile sidebar
- [x] Fixed CSS specificity issues for mobile collapse

**Backend Changes:**
- [x] Update `config/urls.py` - Root URL goes directly to DashboardView
- [x] Remove Home and About template views
- [x] Dashboard already has LoginRequiredMixin

**Responsive Design:**
- **Desktop (>768px):**
  - Sidebar always visible (280px width)
  - Click "Collapse" button → Icon-only mode (70px width)
  - Icons remain visible and clickable when collapsed
  - State saved in localStorage

- **Tablet (769-992px):**
  - Sidebar visible by default (240px width)
  - Can be collapsed to icon-only mode

- **Mobile (≤768px):**
  - Fixed header bar with app title
  - Hamburger menu (☰) button in top-left
  - Sidebar hidden by default
  - Tap hamburger → Slide-in sidebar (90% width, max 500px)
  - Full text + icons always visible on mobile
  - X button to close sidebar
  - Dark overlay when open
  - Tap overlay or X to close

**Key Technical Challenges Solved:**
1. **CSS Specificity Conflict:** Desktop `#wrapper.toggled` (collapsed) conflicted with mobile `#wrapper.toggled` (open). Fixed by wrapping desktop collapsed styles in `@media (min-width: 769px)`.
2. **Bootstrap Collapse on Mobile:** Desktop was hiding all `.collapse` divs. Fixed by scoping desktop rules to prevent interference.
3. **Icon Visibility:** Ensured icons display properly in both collapsed (desktop) and mobile modes.
4. **Chevron Rotation:** Added JavaScript listeners for Bootstrap collapse events to rotate chevron arrows.

**Files Modified:**
- `templates/base.html` - New sidebar structure with mobile header, separate content blocks for auth/unauth
- `templates/account/login.html` - Bootstrap 5 styled login page
- `templates/account/signup.html` - User registration page
- `templates/account/logout.html` - Sign out confirmation page
- `templates/account/password_reset.html` - Password reset request page
- `static/sass/sidebar.scss` - Complete responsive sidebar styles
- `static/js/project.js` - Toggle logic and chevron rotation
- `templates/academics/base.html` - Simplified (removed old sidebar)
- `config/urls.py` - Direct dashboard routing

**Future Enhancements:**
- Consider adding tooltips to collapsed sidebar icons on desktop
- Add keyboard shortcuts (Cmd+B to toggle sidebar)
- Add smooth scroll to active nav item on mobile
- Consider adding breadcrumbs for deep navigation


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
│   │   │   ├── attendance_report_pdf.html  # Phase 2 (PDF export)
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

### Model Relationships (Updated Phase 2.8)

```
User (1) ──────→ (N) SchoolYear
                     │
                     │ (M:N)
                     ↓
User (1) ──────→ (N) Student

User (1) ──────→ (N) ColorPalette (is_active)
                     │
                     │ (M:N)
                     ↓
User (1) ──────→ (N) Color (hex codes)
                     │
                     │ (used by)
                     ↓
User (1) ──────→ (N) Tag
                     │
                     │ (M:N)
                     ↓
User (1) ──────→ (N) Resource
                     │
                     │ (M:N - suggested)
                     ↓
User (1) ──────→ (N) CourseTemplate
                     │
                     │ (0..1 - optional)
                     ↓
User (1) ──────→ (N) Course ←──────────┐
                     │                  │ (M:N)
                     │                  │
                     │ (M:N)            │
                     └──────────────────┘ Resource
                     │
                     │ (1)
                     ↓
User (1) ──────→ (N) CourseEnrollment
                     │
                     ├──→ (1) Student
                     ├──→ (1) SchoolYear
                     └──→ (1) Course

User (1) ──────→ (N) DailyLog
                     │
                     ├──→ (1) Student
                     │
                     │ (1)
                     ↓
                 CourseNote (N)
                     │
                     └──→ (1) CourseEnrollment
```

**Key Models:**
- **SchoolYear**: Academic years with start/end dates, active year tracking
- **Student**: Student records with M2M to school years
- **ColorPalette**: Named collections of colors (e.g., "Ocean Blues"), only one active per user
- **Color**: Individual hex color codes, can belong to multiple palettes via M2M
- **Tag**: Colored tags for organizing resources, colors selected from active palette
- **Resource**: Curriculum materials (textbooks, workbooks, etc.) with M2M tags
- **CourseTemplate**: Optional template for creating standardized courses with suggested resources
- **Course**: User-owned course definitions with optional template and M2M resources
- **CourseEnrollment**: Links student+course+school_year, tracks progress and completion
- **DailyLog**: Daily attendance records per student
- **CourseNote**: Course-specific notes for each day, linked to enrollment

### User Data Isolation Pattern

All models include a `user` ForeignKey and views filter by `request.user`:
```python
queryset = Model.objects.filter(user=request.user)

# Examples with new architecture:
# Get enrollments for user's students
enrollments = CourseEnrollment.objects.filter(user=request.user)

# Get courses for user
courses = Course.objects.filter(user=request.user)

# Get resources with tags
resources = Resource.objects.filter(user=request.user).prefetch_related('tags')

# Get course notes via enrollments
notes = CourseNote.objects.filter(course_enrollment__user=request.user)
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
- [ ] Add additional allauth templates as needed:
  - [ ] `account/email_confirm.html` - Email verification page (important since email verification is mandatory)
  - [ ] `account/email.html` - Email management page
  - [ ] `account/password_reset_from_key.html` - Password reset form (after clicking email link)
  - [ ] `account/password_reset_done.html` - Confirmation after requesting password reset
  - [ ] `account/password_change.html` - Change password when logged in
  - [ ] `account/verification_sent.html` - Shown after signup
- [x] Add PDF export for attendance reports (compliance) - ✅ COMPLETED
  - Implemented with WeasyPrint
  - Includes flipped table structure (statuses as rows, max 3 students per table)
  - Includes detailed course and curriculum information
- [ ] Add CSV export for attendance reports (optional)
- [x] HTMX for dynamic attendance toggling without page reloads - ✅ COMPLETED (Phase 2.5)
  - Quick status toggle with inline dropdown
  - Batch operations for multi-cell updates
  - Keyboard navigation and shortcuts
  - Inline course notes modal
  - Delete attendance logs

### Phase 2.6 Items (Multi-Year Courses) - ✅ ALL COMPLETED
- [x] Create CourseTemplate and CourseEnrollment models - ✅ COMPLETED
- [x] Create Tag and Resource models with M2M relationships - ✅ COMPLETED
- [x] Refactor Course model to be user-owned (removed student/school_year FKs) - ✅ COMPLETED
- [x] Create data migration for existing Course records - ✅ COMPLETED
- [x] Implement course template management views (CRUD) - ✅ COMPLETED
- [x] Implement course enrollment management views (CRUD) - ✅ COMPLETED
- [x] Implement tag and resource management views (CRUD) - ✅ COMPLETED
- [x] Update dashboard with active enrollments widget - ✅ COMPLETED
- [x] Update attendance calendar modal to use enrollments - ✅ COMPLETED
- [x] Update daily log entry to use enrollments - ✅ COMPLETED
- [x] Update PDF export to show enrollments with school year - ✅ COMPLETED
- [x] Implement HTMX resource search for course/template forms - ✅ COMPLETED
- [x] Auto-populate resources when selecting course template - ✅ COMPLETED

### ✅ Phase 2.8: Color Palette System for Tag Management (COMPLETED)

**Overview:**
Implemented a comprehensive color palette system allowing users to create named collections of colors (e.g., "Ocean Blues", "Earth Tones") for organizing and generating tag colors. Only one palette can be active at a time, and its colors are used for random tag color generation.

**Models Implemented:**

1. **ColorPalette** - Named collection of colors
   - Fields: user, name, is_active, created_at, updated_at
   - Only one palette can be active per user
   - Active palette colors are used for tag generation
   - Ordering: Active palette first, then alphabetical

2. **Color** - Individual hex color codes
   - Fields: user, name, color (hex code), palettes (M2M to ColorPalette)
   - Colors can belong to multiple palettes
   - M2M relationship allows flexible organization
   - Can exist without being in any palette

**Features Implemented:**

**1. Color Palette Management**
- ✅ Full CRUD views for color palettes
- ✅ List view with Bootstrap tabs showing:
  - Individual palette tabs with all colors in that palette
  - "All Colors" tab showing every color user has created
- ✅ Active/inactive palette toggle
- ✅ Visual badges for active palette
- ✅ Color count displayed on each palette tab

**2. Color Management**
- ✅ Full CRUD operations for individual colors
- ✅ Create color with optional palette assignment
- ✅ Edit/delete colors from any view (palette tab or "All Colors")
- ✅ Checkbox-based palette assignment (replaced clunky multiselect)
- ✅ Remove color from palette (M2M delete) without deleting color
- ✅ Live color preview when creating/editing

**3. Color Import Feature**
- ✅ Import multiple colors from hex codes (comma or newline separated)
- ✅ Dropdown to select existing palette or create new one
- ✅ Optional "mark as active" checkbox for new palettes
- ✅ Bulk color creation with automatic palette assignment

**4. Tag Integration**
- ✅ Tag creation/edit forms show only active palette colors
- ✅ `Tag.get_palette_colors_for_user()` filters by active palette
- ✅ Random tag color selection from active palette
- ✅ Visual color picker with active palette colors

**5. Tag Filters for Resource Search**
- ✅ Tag filter UI on course form
- ✅ Colored tag badges for visual filtering
- ✅ Click to toggle tag filters
- ✅ "Clear Filters" button
- ✅ Integration with HTMX resource search
- ✅ Tag autocomplete fixed to return all tags when no search query

**URL Structure (Implemented):**
```
/academics/settings/color-palettes/                              # List all palettes (tabbed view)
/academics/settings/color-palettes/create/                       # Create new palette
/academics/settings/color-palettes/<pk>/update/                  # Edit palette
/academics/settings/color-palettes/<pk>/delete/                  # Delete palette
/academics/settings/color-palettes/import/                       # Import colors to palette

/academics/settings/colors/add/                                  # Create color
/academics/settings/colors/<pk>/update/                          # Edit color
/academics/settings/colors/<pk>/delete/                          # Delete color
/academics/settings/color-palette/<palette_pk>/remove-color/<color_pk>/  # Remove from palette
```

**Technical Implementation:**

**Backend (Django):**
- ColorPalette and Color models in `models.py`
- Full CRUD views in `views/library.py`:
  - ColorPaletteListView - Tabbed interface with all palettes
  - ColorPaletteCreateView, ColorPaletteUpdateView, ColorPaletteDeleteView
  - ColorPaletteImportView - Bulk import with palette selection
  - ColorCreateView, ColorUpdateView, ColorDeleteView
  - remove_color_from_palette() - M2M removal without delete
- ColorPaletteImportForm with dynamic palette choices
- ColorForm with checkbox palette assignment
- Tag autocomplete fixed to return all tags for filters

**Frontend (Templates):**
- `color_palette_list.html` - Bootstrap tabs for palette management
- `color_palette_form.html` - Create/edit palette
- `color_palette_import.html` - Bulk import interface
- `color_form.html` - Create/edit color with checkboxes
- `partials/color_palette_preview.html` - Live preview component
- Tag forms updated to filter by active palette
- Course form updated with tag filter buttons

**Model Relationships:**
```
User (1) ──────→ (N) ColorPalette (is_active field)
                     │
                     │ (M2M)
                     ↓
                 (N) Color (name, hex)
                     │
                     │ (used by)
                     ↓
                 (N) Tag (gets random color from active palette)
```

**Migration Strategy (Completed):**
- ✅ 0009_add_color_palette.py - Initial Color model
- ✅ 0010_add_color_palette_groups.py - ColorPalette model with M2M
- ✅ 0011_rename_color_models.py - Renamed models to correct architecture
  - ColorPalette → Color (individual colors)
  - ColorPaletteGroup → ColorPalette (named collections)
  - Updated all foreign keys and related names

**Key Architecture Benefits:**
- ✅ Flexible color organization with named palettes
- ✅ Colors can belong to multiple palettes (M2M)
- ✅ Active palette controls tag color generation
- ✅ Easy to switch color themes by changing active palette
- ✅ Import colors in bulk with palette assignment
- ✅ Remove vs delete distinction for color management
- ✅ Tag filtering for resource search

**Bug Fixes Applied:**
- Fixed tag creation showing all colors instead of active palette colors
- Fixed multiselect UI by replacing with checkboxes
- Fixed tag autocomplete returning empty array for tag filters
- Fixed tag filter buttons not rendering on course form

### ✅ Student Photo Uploads (COMPLETED)

**Overview:**
Implemented photo upload functionality for students with thumbnail displays throughout the application. Photos are stored on the filesystem with an architecture that makes future cloud storage migration seamless.

**Features Implemented:**
- ✅ Photo field added to Student model with custom upload path
- ✅ File upload handling in StudentForm with multipart/form-data support
- ✅ Thumbnail generation utilities using Pillow
- ✅ Graceful fallbacks - displays student's initial in colored circle when no photo
- ✅ Photo display in student list (60px circular thumbnails)
- ✅ Photo display in student detail page (80px header image)
- ✅ Photo display in attendance calendar (40px thumbnails)
- ✅ Photo display in enrollment lists (32px thumbnails)
- ✅ Photo display in dashboard widgets (28-40px thumbnails)
- ✅ Cloud storage ready - easy migration to S3/Azure/GCS in future

**Technical Implementation:**
- Upload path: `media/students/<user_id>/<student_id>_<filename>`
- Image processing with PIL/Pillow for format conversion
- Responsive circular thumbnails with object-fit: cover
- Consistent visual design across all views
- User data isolation maintained in upload paths

**Migration:**
- Migration 0008_add_student_photo applied successfully
- No data loss, backward compatible

**Files Modified:**
- `idahomeschool/academics/models.py` - Added photo field and upload path function
- `idahomeschool/academics/forms.py` - Updated StudentForm with file upload support
- `idahomeschool/academics/utils.py` - NEW: Thumbnail generation utilities
- `idahomeschool/templates/academics/student_list.html` - Added thumbnails
- `idahomeschool/templates/academics/student_detail.html` - Added header photo
- `idahomeschool/templates/academics/attendance_calendar.html` - Added thumbnails
- `idahomeschool/templates/academics/courseenrollment_list.html` - Added thumbnails
- `idahomeschool/templates/academics/dashboard.html` - Added thumbnails to all widgets

### Future Considerations
- [ ] Add data import capability (CSV upload)
- [x] Add image upload for students (profile pictures) - ✅ COMPLETED
- [ ] Consider adding "notes" field to Student and SchoolYear
- [ ] Add activity/audit log for compliance tracking
- [ ] Grade/progress tracking within courses
- [ ] Email reminders for attendance logging
- [ ] Mobile app for quick attendance entry
- [ ] Assignment tracking and grading
- [ ] Batch photo upload/management tool
- [ ] Photo cropping/editing in the UI
- [ ] Photo compression for optimized storage

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
from idahomeschool.academics.models import (
    SchoolYear, Student, Course, CourseEnrollment,
    Tag, Resource, DailyLog, CourseNote
)
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

# Create tags
math_tag = Tag.objects.create(
    name="Mathematics",
    color="#007bff",
    user=user
)

science_tag = Tag.objects.create(
    name="Science",
    color="#28a745",
    user=user
)

# Create resources
math_book = Resource.objects.create(
    title="Saxon Math 4",
    author="Stephen Hake",
    publisher="Saxon Publishers",
    resource_type="TEXTBOOK",
    user=user
)
math_book.tags.add(math_tag)

science_book = Resource.objects.create(
    title="Apologia Science",
    author="Dr. Jay Wile",
    publisher="Apologia",
    resource_type="TEXTBOOK",
    user=user
)
science_book.tags.add(science_tag)

# Create courses (user-owned, reusable)
math_course = Course.objects.create(
    name="Math 4",
    description="4th grade mathematics",
    user=user
)
math_course.resources.add(math_book)

science_course = Course.objects.create(
    name="Science 4",
    description="4th grade science",
    user=user
)
science_course.resources.add(science_book)

# Enroll student in courses for this school year
math_enrollment = CourseEnrollment.objects.create(
    student=student,
    course=math_course,
    school_year=year,
    status="IN_PROGRESS",
    user=user
)

science_enrollment = CourseEnrollment.objects.create(
    student=student,
    course=science_course,
    school_year=year,
    status="IN_PROGRESS",
    user=user
)

# Create daily log with course notes
daily_log = DailyLog.objects.create(
    student=student,
    date=date.today(),
    status="PRESENT",
    general_notes="Great day of learning!",
    user=user
)

# Add course notes (linked to enrollments)
CourseNote.objects.create(
    daily_log=daily_log,
    course_enrollment=math_enrollment,
    notes="Completed chapter 5 on fractions. Student showed good understanding.",
    user=user
)

CourseNote.objects.create(
    daily_log=daily_log,
    course_enrollment=science_enrollment,
    notes="Studied the solar system. Built a model of planets.",
    user=user
)
```

## Next Immediate Steps (Phase 3)

Phase 3 will focus on **Paperless-NGX Integration** - connecting the application to a running Paperless-NGX instance for document management and work sample tracking.

1. **Create Paperless Models**
   - Create `PaperlessConfig` model for API settings (URL, token)
   - Create `PaperlessLink` model with GenericForeignKey
   - Create migration for new tables

2. **Build Paperless API Client**
   - Create `utils/paperless_client.py` with API wrapper
   - Implement document fetching and searching
   - Implement tag syncing functionality
   - Add error handling and connection testing

3. **Settings Interface**
   - Create settings page for Paperless URL and API token configuration
   - Add connection test button
   - Implement secure token storage (encryption)

4. **Document Selector UI**
   - Create modal component for document selection
   - Implement search and filtering
   - Display document thumbnails from Paperless API
   - Add document metadata display

5. **Document Linking Features**
   - Add "Attach Document" button to Student detail pages
   - Add "Attach Document" button to Course detail pages
   - Implement document linking workflow
   - Display linked documents with thumbnails
   - Add ability to remove document links

6. **Tag Syncing**
   - Auto-apply tags to documents when linked (e.g., "homeschool", "student:john")
   - Sync tags from OpenHomeSchool to Paperless
   - Add tag management interface

7. **Work Samples & Portfolio**
   - Create work samples section on course detail pages
   - Create correspondence section on student detail pages
   - Add filtering by document type or date
   - Create portfolio view for compliance reporting

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
