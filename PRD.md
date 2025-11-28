Product Requirements Document (PRD)
Project Name: OpenHomeSchool (Integration with Paperless-NGX) Target Platform: Web Application (Django) Version: 1.0 (MVP)

1. Executive Summary
The goal is to build a self-hosted web application to manage homeschooling records in compliance with Idaho state recommendations. The application will serve as the "Metadata Layer," managing students, school years, courses, and attendance, while utilizing a running instance of Paperless-NGX as the "Document Layer."

The system must allow the user to easily link scanned documents (work samples, correspondence, test results) stored in Paperless to specific students and academic contexts within the application.

Shutterstock
Explore

2. User Personas
The Administrator/Parent: The primary user. They need quick entry for daily attendance, easy setup for new school years, and a seamless flow to associate a scanned piece of paper with a child's academic record.

3. Functional Requirements
3.1. Core Configuration & Management
School Year Management:

Create/Edit School Years (e.g., "2024-2025").

Define Start Date and End Date.

Set a "Current Active Year" toggle.

Student Management:

Add/Edit Students (Name, Date of Birth, Grade Level).

Assign Students to a School Year.

3.2. Course & Curriculum Tracking
Course Creation:

Ability to create courses (e.g., "Math 5", "Idaho History") linked to a specific Student and School Year.

Curriculum Resources:

Ability to log textbooks and workbooks used for a course.

Fields: Title, Author, Publisher, ISBN (optional).

3.3. Attendance System
Daily Log:

A dashboard view showing the current week.

Ability to toggle status for each student per day: Present, Absent, Sick, Holiday, Field Trip.

Reporting:

Calculate total instructional days per School Year.

Generate a simple PDF or CSV export of attendance for state compliance.

3.4. Paperless-NGX Integration (The Core Feature)
The application must communicate with the Paperless-NGX REST API.

API Configuration: Settings page to input Paperless URL and API Token.

Document Linking:

Users should be able to view a list of documents from Paperless inside the Django app.

Search/Filter: Ability to search Paperless documents by query or tag.

Contextual Linking: When viewing a Student or Course, the user can "Attach Document."

Tag Syncing (Optional but Recommended):

When a document is linked in Django, the app should call the Paperless API to apply a specific tag (e.g., homeschool, student:john) to the document in Paperless for consistency.

3.5. Portfolio & Records (The "Idaho Requirements")
Work Samples: Ability to link a Paperless document to a specific Course (e.g., "Math Test Chapter 1").

Correspondence: A dedicated section to link "Administrative" documents (Withdrawal letters, district emails) not tied to a specific course but tied to the Student.

Standardized Tests: A section to record test scores and link the physical result PDF from Paperless.

4. Technical Specifications
4.1. Tech Stack
Backend: Python / Django 5.x.

Database: PostgreSQL (Recommended to match Paperless) or SQLite for simplicity.

Frontend: Django Templates with HTMX (for dynamic attendance toggling/searching) and Bootstrap/Tailwind.

Integration: requests library to hit Paperless-NGX endpoints (/api/documents/, /api/tags/).

4.2. Data Models (Implemented)

**Core Academic Models:**

```python
class SchoolYear(models.Model):
    """Academic year with start/end dates and active year tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)  # Only one active per user

class Student(models.Model):
    """Student records with grade level and M2M to school years"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    grade_level = models.CharField(max_length=20)
    school_years = models.ManyToManyField(SchoolYear, related_name='students')
    # Future: paperless_tag_id for document linking
```

**Resource & Tag Models:**

```python
class Tag(models.Model):
    """Colored tags for organizing curriculum resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)  # Hex color code

    class Meta:
        unique_together = [['user', 'name']]

class Resource(models.Model):
    """Curriculum materials (textbooks, workbooks, online resources)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    resource_type = models.CharField(max_length=20, choices=[
        ('TEXTBOOK', 'Textbook'),
        ('WORKBOOK', 'Workbook'),
        ('ONLINE', 'Online Resource'),
        ('VIDEO', 'Video Course'),
        ('SOFTWARE', 'Software'),
        ('OTHER', 'Other'),
    ])
    url = models.URLField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='resources', blank=True)
```

**Course Models (Multi-Year Support):**

```python
class CourseTemplate(models.Model):
    """Optional template for creating standardized courses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)  # "Algebra 1"
    description = models.TextField(blank=True)
    suggested_resources = models.ManyToManyField(Resource, blank=True)

class Course(models.Model):
    """User-owned course definition (reusable across students/years)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course_template = models.ForeignKey(CourseTemplate, null=True, blank=True)
    resources = models.ManyToManyField(Resource, related_name='courses', blank=True)

class CourseEnrollment(models.Model):
    """Links student to course for specific school year with progress tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
    ])
    started_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    final_grade = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = [['student', 'course', 'school_year']]
```

**Attendance Models:**

```python
class DailyLog(models.Model):
    """Daily attendance record per student"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('SICK', 'Sick'),
        ('HOLIDAY', 'Holiday'),
        ('FIELD_TRIP', 'Field Trip'),
    ])
    general_notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['student', 'date']]

class CourseNote(models.Model):
    """Course-specific notes for each day (linked to enrollment)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)
    course_enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE)
    notes = models.TextField()

    class Meta:
        unique_together = [['daily_log', 'course_enrollment']]
```

**Future Paperless Integration:**

```python
class PaperlessLink(models.Model):
    """
    Links Paperless-NGX documents to any object in the system
    (Course, Student, DailyLog, etc.)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paperless_document_id = models.IntegerField()
    paperless_thumbnail_url = models.URLField()  # Cache thumbnail

    # Generic FK to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = models.GenericForeignKey('content_type', 'object_id')
```
5. UI/UX Workflow Example: "Adding a Math Test"
Physical World: Parent scans the graded Math Test. Paperless-NGX ingests it.

Django App: Parent logs in and goes to Students > John > Math 5.

Action: Clicks "Add Work Sample".

Modal: A modal opens displaying recent documents fetched from Paperless API. Parent types "Math" in the search box.

Selection: Parent selects the correct PDF.

Save: The system saves a PaperlessLink connecting that document ID to the "Math 5" course object.

Result: When viewing the "Math 5" course later, the thumbnail of the test appears under "Work Samples."

6. Non-Functional Requirements
Privacy: Data must be self-hosted. No external cloud calls.

Responsiveness: Must work well on mobile/tablet (parents often update records on an iPad).

Backups: The database should be easily dump-able (e.g., standard django-admin dumpdata).

7. Implementation Roadmap

**✅ Phase 1: The Foundation (COMPLETED)**
- ✅ Set up Django Project with user authentication
- ✅ Build SchoolYear, Student, Course models
- ✅ Build full CRUD views for all models
- ✅ Dashboard with statistics and recent activity

**✅ Phase 2: Attendance System (COMPLETED)**
- ✅ Build DailyLog and CourseNote models
- ✅ Create attendance calendar view with week/month toggle
- ✅ Build daily log entry form with course-specific notes
- ✅ Generate PDF attendance reports for compliance

**✅ Phase 2.5: HTMX Dynamic Attendance (COMPLETED)**
- ✅ Quick status toggle with inline dropdown (no page reload)
- ✅ Batch operations for marking multiple cells at once
- ✅ Keyboard navigation and shortcuts (arrow keys, number keys)
- ✅ Inline course notes modal

**✅ Phase 2.6: Multi-Year Course Support (COMPLETED)**
- ✅ Created Tag and Resource models with M2M relationships
- ✅ Created CourseTemplate for standardized course definitions
- ✅ Refactored Course to be user-owned (removed student/school_year FKs)
- ✅ Created CourseEnrollment to link student+course+school_year
- ✅ Updated CourseNote to reference enrollments instead of courses
- ✅ HTMX-powered resource search for course/template forms
- ✅ Auto-populate resources when selecting course templates
- ✅ Updated all views, templates, and reports to use new architecture
- ✅ Data migration from old Course structure completed successfully

**✅ Phase 2.7: Navigation & UX Restructuring (COMPLETED)**
- ✅ Removed top header navigation
- ✅ Persistent collapsible sidebar with expandable sections
- ✅ Mobile-responsive with hamburger menu
- ✅ Root URL redirects directly to dashboard

**🔜 Phase 3: Paperless-NGX Integration (NEXT)**
- Implement the Paperless API client class in Python
- Build settings page for API URL and token
- Build the "Document Selector" UI component
- Create the "PaperlessLink" logic to attach docs to Students and Courses
- Tag syncing between OpenHomeSchool and Paperless
- Work samples and correspondence sections

**📋 Phase 4: Idaho Compliance Reporting (PLANNED)**
- Create "End of Year Report" page
- Aggregate attendance count, textbook list, and work samples
- Printable view with Paperless document thumbnails
- Portfolio view per student for compliance