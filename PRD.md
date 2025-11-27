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

4.2. Proposed Data Models (High Level)
Python

# Conceptual Models for Developers

class SchoolYear(models.Model):
    name = models.CharField(max_length=50) # "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()

class Student(models.Model):
    name = models.CharField(max_length=100)
    # Link to Paperless Tag ID for this student
    paperless_tag_id = models.IntegerField(null=True, blank=True) 

class Course(models.Model):
    student = models.ForeignKey(Student)
    school_year = models.ForeignKey(SchoolYear)
    name = models.CharField(max_length=100) # "Science 4"
    # Resources (Textbooks) can be a JSONField or separate model

class Attendance(models.Model):
    student = models.ForeignKey(Student)
    date = models.DateField()
    status = models.CharField(choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent')...])

class PaperlessLink(models.Model):
    """
    Polymorphic link or GenericForeignKey to connect a paperless document 
    to any object in the system (Course, Student, TestResult).
    """
    paperless_document_id = models.IntegerField()
    paperless_thumbnail_url = models.URLField() # Cache the thumbnail link
    
    # Generic FK to link to Course, Student, or Attendance
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = models.GenericForeignKey('content_type', 'object_id')
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
Phase 1: The Foundation
Set up Django Project & Authentication.

Build Student, Year, and Course Models.

Build Basic CRUD views for these models.

Phase 2: Attendance
Build the Attendance model.

Create a "Calendar View" dashboard for quick toggling.

Phase 3: The Paperless Bridge
Implement the Paperless API client class in Python.

Build the "Document Selector" UI component.

Create the "PaperlessLink" logic to attach docs to Courses.

Phase 4: Idaho Compliance View
Create a "End of Year Report" page that aggregates the attendance count, textbook list, and thumbnails of attached work samples into a single printable view.