# Attendance System Redesign Plan

## Overview
Redesign the attendance tracking system from scratch to deliver a mobile-first, quick-entry experience that meets Idaho homeschool compliance requirements while following existing project patterns.

## Objectives
1. **Mobile-First Design**: Optimize for quick, on-the-go logging with 1-2 tap interactions
2. **Visual Clarity**: Use distinct colors and icons for instant status recognition
3. **Fast Data Entry**: Auto-save on status changes, minimal form friction
4. **Compliance Ready**: Easy export for state documentation requirements
5. **Daily Journaling**: Support for course notes and general daily observations

## Current State Analysis

### What We're Keeping ✅
- **Models** (idahomeschool/academics/models.py):
  - `AttendanceStatus` - Customizable status types with colors (lines 315-458)
  - `DailyLog` - Per-student daily attendance (lines 799-870)
  - `CourseNote` - Course-specific daily notes (lines 872-921)
- **Backend Views** (idahomeschool/academics/views/attendance.py):
  - HTMX quick toggle endpoints (lines 630-887)
  - Attendance report generation (lines 450-622)
  - Status management CRUD (lines 894-1022)

### What We're Redesigning 🔄
- **Calendar View**: Create new mobile-optimized calendar interface
- **Status Selection UX**: Improve quick-toggle modal design
- **Daily Log Entry**: Redesign form for better course notes workflow
- **Navigation**: Add clear entry points from dashboard/student pages

## Implementation Plan

### Phase 1: Calendar View Redesign
**Goal**: Mobile-first calendar interface with visual attendance status overview

#### 1.1 Main Calendar Template
**File**: `idahomeschool/templates/academics/attendance_calendar.html` (CREATE NEW)

**Features**:
- Month view as default (easier on mobile than week view)
- Date picker for quick navigation to any date
- Student selector dropdown at top
- Color-coded status badges in calendar grid
- Tap any date to drill into daily details
- Legend showing all status types with colors

**Layout Structure**:
```
┌─────────────────────────────────────┐
│ ← December 2024 →       [Student ▼] │
├─────────────────────────────────────┤
│ Sun Mon Tue Wed Thu Fri Sat         │
│  1   2   3   4   5   6   7          │
│  P   P   -   P   P   -   -          │ ← Status abbreviations
│  8   9  10  11  12  13  14          │
│  P   A   P   P   P   -   -          │
│ ...                                 │
├─────────────────────────────────────┤
│ Legend:                             │
│ [P] Present [A] Absent [S] Sick ... │
└─────────────────────────────────────┘
```

**Technical Approach**:
- Alpine.js for month navigation
- HTMX for loading month data without full page reload
- Responsive grid: `grid-cols-7` (7 days)
- Each cell clickable to open daily entry modal

#### 1.2 Calendar View Backend
**File**: `idahomeschool/academics/views/attendance.py` (UPDATE)

**Updates needed to `AttendanceCalendarView` (lines 352-447)**:
- Change default view from "week" to "month"
- Add student filtering (currently shows all students)
- Return data optimized for month grid rendering
- Add HTMX endpoint for month data refresh

**New endpoint**: `attendance_month_data_htmx(request, year, month, student_id=None)`
- Returns partial HTML for calendar grid only
- Allows fast month switching without full page reload

### Phase 2: Quick Status Entry Modal
**Goal**: Fast, thumb-friendly status selection modal

#### 2.1 Daily Entry Modal
**File**: `idahomeschool/templates/academics/partials/daily_entry_modal.html` (CREATE NEW)

**Triggered when**:
- User taps a date in calendar
- User taps "Add Today" quick action button

**Modal Structure**:
```
┌─────────────────────────────────────┐
│ Student Name - December 5, 2024     │
│                                     │
│ Select Status:                      │
│ ┌─────────────────────────────────┐ │
│ │ [P] Present           ✓         │ │ ← Large tap targets
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ [T] Tardy                       │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ [A] Absent                      │ │
│ └─────────────────────────────────┘ │
│ ...                                 │
│                                     │
│ [+ Add Course Notes]                │ ← Expandable section
│                                     │
│ [Close]                   [Delete] │
└─────────────────────────────────────┘
```

**Features**:
- Auto-save on status selection (no "Save" button needed)
- Visual feedback (checkmark) for current status
- Optional course notes section (collapsed by default)
- Delete button only shown if log exists
- Follows dialog patterns from STYLE_GUIDE.md

**Technical Approach**:
- Native HTML5 `<dialog>` element
- HTMX POST to `attendance_quick_update` endpoint (already exists at line 664)
- Alpine.js for course notes expand/collapse
- Out-of-band swap to update calendar cell after save

#### 2.2 Course Notes Section (Within Modal)
**File**: `idahomeschool/templates/academics/partials/course_notes_section.html` (CREATE NEW)

**Expandable section showing**:
- General notes textarea
- List of enrolled courses with individual note fields
- Saved state indicator

**UX Flow**:
1. User taps "+ Add Course Notes"
2. Section expands with smooth animation (Alpine `x-collapse`)
3. Shows general notes + all active course enrollments
4. Auto-saves on blur of each field (debounced)

**Technical Approach**:
- HTMX POST to `attendance_save_course_notes` (already exists at line 797)
- Debounced auto-save using HTMX `hx-trigger="blur changed delay:500ms"`

### Phase 3: Enhanced Status Selector
**Goal**: Improve existing status selector partial

#### 3.1 Redesign Status Selector
**File**: `idahomeschool/templates/academics/partials/status_selector.html` (REDESIGN EXISTING)

**Current issues** (based on lines 1-109 of status_selector.html):
- Desktop-oriented modal layout
- Small tap targets
- Inline JavaScript (should use Alpine where possible)

**Improvements**:
- Larger button tap targets (min 44px height per accessibility guidelines)
- Color-coded buttons with status colors (already implemented)
- Move JavaScript to Alpine.js data attributes
- Add haptic feedback indication for mobile
- Simplified close behavior

**Button Design** (following Basecoat UI patterns):
```html
<button type="submit"
        name="status"
        value="{{ status.code }}"
        class="flex items-center gap-3 rounded-lg p-4 border-2 transition-all"
        :style="currentStatus === '{{ status.code }}'
                ? 'background-color: {{ status.color }}; border-color: {{ status.color }}'
                : 'border-color: {{ status.color }}; color: {{ status.color }}'">
  <span class="text-2xl font-bold">{{ status.abbreviation }}</span>
  <span class="flex-1 text-left">{{ status.label }}</span>
  <i x-show="currentStatus === '{{ status.code }}'"
     data-lucide="check"
     class="size-5"></i>
</button>
```

### Phase 4: Daily Log Entry Page
**Goal**: Comprehensive daily entry form (alternative to quick modal)

#### 4.1 Redesign Daily Log Entry
**File**: `idahomeschool/templates/academics/dailylog_entry.html` (REDESIGN EXISTING)

**Use cases**:
- User wants to enter detailed course notes
- User wants to see all courses for the day
- User wants to review/edit existing entry

**Current implementation** (lines 153-349 in attendance.py):
- Already has most functionality needed
- Backend logic is solid

**Frontend improvements needed**:
- Cleaner mobile layout
- Better visual hierarchy
- Quick date navigation (prev/next day buttons)
- Student switcher at top
- Collapsible course sections (if many courses)

**Layout Structure**:
```
┌─────────────────────────────────────┐
│ ← Dec 4  │  Dec 5, 2024  │  Dec 6 → │
│          │  [Student ▼]   │          │
├─────────────────────────────────────┤
│ Attendance Status:                  │
│ [P] [T] [A] [S] [H] [F]  ← Pill btns│
│                                     │
│ General Notes:                      │
│ ┌─────────────────────────────────┐ │
│ │ (textarea)                      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Course Notes:                       │
│ ▼ Math 101                          │
│ ┌─────────────────────────────────┐ │
│ │ (textarea for this course)      │ │
│ └─────────────────────────────────┘ │
│ ▼ English 201                       │
│ ...                                 │
│                                     │
│ [Save]                              │
└─────────────────────────────────────┘
```

**Features**:
- Status selector as horizontal pill buttons (faster than dropdown)
- Auto-save on status change
- Manual save for notes
- Toast notification on save
- Navigate to prev/next day without losing unsaved changes (Alpine confirmation)

### Phase 5: Dashboard Integration
**Goal**: Quick access to attendance from main dashboard

#### 5.1 Dashboard Attendance Widget
**File**: `idahomeschool/templates/academics/dashboard.html` (ADD WIDGET)

**Widget shows**:
- Today's date
- Quick status entry for each student
- "View Calendar" link
- "View Report" link

**Quick Add Today UI**:
```
┌─────────────────────────────────────┐
│ Today's Attendance - Dec 5, 2024    │
├─────────────────────────────────────┤
│ John Doe     [P] Present         ✓  │ ← Click to change
│ Jane Doe     [-] Not logged         │ ← Click to add
├─────────────────────────────────────┤
│ [View Calendar →]     [Report →]    │
└─────────────────────────────────────┘
```

**Technical Approach**:
- HTMX to load today's logs
- Same status toggle modal as calendar
- Live update when status changes

### Phase 6: Mobile Optimizations

#### 6.1 Touch Interactions
- All buttons minimum 44x44px tap targets
- Increased padding on form inputs (easier to tap)
- Swipe gestures for prev/next day navigation (Alpine.js)
- Pull-to-refresh for calendar (if desired)

#### 6.2 Performance
- Lazy load month data (only load visible month)
- Prefetch adjacent months in background
- Debounced auto-save (500ms delay)
- Optimistic UI updates (update UI before server confirms)

#### 6.3 Offline Considerations
- Use HTMX `hx-sync` to prevent duplicate saves
- Show loading states during saves
- Error handling with retry option

### Phase 7: Reporting Enhancements

#### 7.1 Attendance Report Page
**File**: `idahomeschool/templates/academics/attendance_report.html` (ENHANCE EXISTING)

**Current state** (lines 450-519 in attendance.py):
- Solid backend logic
- PDF export already works

**Frontend improvements**:
- Add date range picker for custom reports
- Add student multi-select filter
- Visual charts (simple bar chart showing status breakdown)
- Preview before export
- Export options: PDF, CSV, Print-friendly view

#### 7.2 Report Cards/Summaries
**New feature**: Monthly summary view
- Shows each student's attendance summary by month
- Highlights any concerning patterns (multiple absences)
- Instructional days count vs. required minimum

## URL Structure

```
/academics/attendance/
  ├── calendar/                          # Main calendar view
  │   └── ?student=<id>&date=<YYYY-MM>   # Filtered view
  ├── entry/                             # Today's quick entry
  ├── entry/<student_pk>/                # Specific student entry
  ├── entry/<student_pk>/<date>/         # Specific student + date
  ├── report/                            # Attendance report
  ├── report/pdf/                        # PDF export
  └── settings/
      └── statuses/                      # Manage attendance statuses
```

**HTMX Endpoints** (keep existing):
```
/academics/attendance/
  ├── quick-toggle/<student>/<date>/     # Show status selector
  ├── quick-update/<student>/<date>/     # Update status
  ├── quick-delete/<student>/<date>/     # Delete log
  ├── course-notes/<student>/<date>/     # Show course notes modal
  └── save-course-notes/<student>/<date>/# Save course notes
```

## Templates Structure

```
idahomeschool/templates/academics/
├── attendance_calendar.html              # NEW - Main calendar view
├── attendance_report.html                # ENHANCE - Reports page
├── attendance_report_pdf.html            # KEEP - PDF template
├── attendance_status_list.html           # KEEP - Status management
├── dailylog_entry.html                   # REDESIGN - Full entry form
└── partials/
    ├── attendance_dashboard_widget.html  # NEW - Dashboard widget
    ├── daily_entry_modal.html            # NEW - Quick entry modal
    ├── course_notes_section.html         # NEW - Expandable course notes
    ├── status_badge.html                 # KEEP - Existing badge
    ├── status_selector.html              # ENHANCE - Better mobile UX
    └── calendar_month_grid.html          # NEW - Month grid partial
```

## Components Breakdown

### 1. Calendar Month Grid
**Responsibility**: Display month grid with status badges
**State**: Selected month, selected student, logs data
**Interactions**: Click date → open daily entry modal
**HTMX**: Load month data on month change

### 2. Daily Entry Modal
**Responsibility**: Quick status + notes entry
**State**: Current status, course notes, form validity
**Interactions**: Tap status → auto-save, expand notes → manual save
**HTMX**: POST status update, POST course notes

### 3. Status Selector
**Responsibility**: Large tap targets for status selection
**State**: Current selected status
**Interactions**: Tap status button → submit form
**HTMX**: POST to update endpoint, close modal on success

### 4. Course Notes Section
**Responsibility**: General + per-course note entry
**State**: Notes text, save status
**Interactions**: Type → debounced auto-save
**HTMX**: POST individual note updates

### 5. Dashboard Widget
**Responsibility**: Today's quick status overview
**State**: Today's logs for all students
**Interactions**: Click student → open status modal
**HTMX**: Load today's data, update on status change

## Technical Requirements

### Backend (Python/Django)
- **Keep existing views**: AttendanceCalendarView, DailyLogEntryView, HTMX endpoints
- **Enhance**: Add month data endpoint, add dashboard widget endpoint
- **Keep models unchanged**: AttendanceStatus, DailyLog, CourseNote are well-designed

### Frontend Stack
- **Tailwind CSS + Basecoat UI**: Follow STYLE_GUIDE.md patterns exactly
- **HTMX**: For all AJAX interactions (status updates, month loading)
- **Alpine.js**: For client-side state (month navigation, modal control, collapsible sections)
- **Lucide Icons**: Via `data-lucide` attributes

### Mobile Considerations
- Viewport meta tag: `width=device-width, initial-scale=1`
- Touch-friendly tap targets (44px minimum)
- Fast tap response (no 300ms delay)
- Minimal scroll on forms
- Auto-focus management (don't auto-focus on mobile, causes keyboard pop-up)

## Design Patterns to Follow

### From STYLE_GUIDE.md
1. **Page Headers**: `<h1 class="text-3xl font-bold tracking-tight">`
2. **Dialogs**: Native HTML5 `<dialog>` with `.dialog` class
3. **Buttons**: `.btn`, `.btn-outline`, `.btn-icon-outline size-8`
4. **Forms**: `.form` class on container, auto-styled inputs
5. **Empty States**: Centered with icon, heading, description, CTA
6. **Tables**: `.table` class, action buttons right-aligned
7. **Icons**: Lucide via `data-lucide="icon-name"`

### Color Scheme
- Use `AttendanceStatus.color` for all status badges
- Maintain existing color contrast logic (light text on dark backgrounds)
- Use semantic colors: `text-muted-foreground`, `bg-destructive`, etc.

## Data Flow Examples

### Example 1: Quick Status Update from Calendar
1. User taps December 5 cell for John Doe
2. HTMX GET → `attendance_quick_toggle/john-pk/2024-12-05/`
3. Server returns status_selector.html modal
4. Modal opens with current status highlighted
5. User taps "Present" button
6. HTMX POST → `attendance_quick_update/john-pk/2024-12-05/`
7. Server creates/updates DailyLog with status="PRESENT"
8. Server returns updated status_badge.html
9. HTMX swaps badge in calendar cell
10. Modal closes (via HX-Trigger header)

### Example 2: Adding Course Notes
1. User opens daily entry modal for December 5
2. User taps "+ Add Course Notes"
3. Alpine.js expands course notes section (x-show toggle)
4. HTMX GET → `attendance_course_notes/john-pk/2024-12-05/`
5. Server returns course_notes_section.html with enrollments
6. User types notes in "Math 101" textarea
7. After 500ms delay, HTMX POST → `attendance_save_course_notes/...`
8. Server creates/updates CourseNote record
9. Server returns success indicator
10. UI shows "Saved" checkmark briefly

### Example 3: Dashboard Quick Entry
1. Dashboard loads with today's date
2. HTMX GET → `attendance_dashboard_widget/` (new endpoint)
3. Server returns today's logs for all students
4. User clicks "Jane Doe - Not logged"
5. Opens status selector modal (same as calendar flow)
6. User selects "Present"
7. HTMX updates backend
8. Dashboard widget updates to show "Jane Doe - Present ✓"

## Progressive Enhancement

### Core Functionality (No JS)
- Calendar view still works (server-side pagination)
- Form submission works (standard POST)
- Reports generate and download

### Enhanced with HTMX
- No page reloads on status updates
- Fast month switching
- Inline editing

### Enhanced with Alpine.js
- Smooth animations (modal open/close, section expand)
- Client-side state management (current month, expanded sections)
- Keyboard shortcuts (ESC to close modal)

## Success Metrics

1. **Mobile Performance**: Calendar loads in < 2 seconds on 3G
2. **Interaction Speed**: Status update completes in < 500ms
3. **User Experience**: Can log attendance for 3 students in < 30 seconds
4. **Accessibility**: All interactive elements keyboard navigable
5. **Compliance**: PDF report generates all required data

## Implementation Order

### Sprint 1: Core Calendar (Week 1)
1. Create attendance_calendar.html with month grid
2. Style calendar cells with status badges
3. Add month navigation (Alpine.js)
4. Test responsive layout on mobile devices

### Sprint 2: Quick Entry Modal (Week 1-2)
1. Create daily_entry_modal.html
2. Enhance status_selector.html for mobile
3. Wire up HTMX endpoints (already mostly exist)
4. Test auto-save and modal close behavior

### Sprint 3: Course Notes Integration (Week 2)
1. Create course_notes_section.html
2. Add debounced auto-save
3. Test multi-course scenarios
4. Add loading/saved indicators

### Sprint 4: Dashboard & Navigation (Week 2-3)
1. Create dashboard widget
2. Add calendar link to nav
3. Add "Today's Entry" quick action
4. Test cross-linking between views

### Sprint 5: Polish & Testing (Week 3)
1. Mobile testing on real devices
2. Accessibility audit (keyboard nav, screen readers)
3. Performance optimization
4. Bug fixes and edge cases

### Sprint 6: Reports Enhancement (Week 4)
1. Add date range picker
2. Add visual charts
3. Enhance PDF layout
4. Add CSV export option

## Files to Create

```
idahomeschool/templates/academics/
├── attendance_calendar.html                    # NEW
├── partials/
    ├── attendance_dashboard_widget.html        # NEW
    ├── daily_entry_modal.html                  # NEW
    ├── course_notes_section.html               # NEW
    └── calendar_month_grid.html                # NEW
```

## Files to Modify

```
idahomeschool/academics/views/attendance.py     # ENHANCE
  - AttendanceCalendarView (lines 352-447)
  - Add attendance_dashboard_widget_htmx endpoint
  - Add attendance_month_data_htmx endpoint

idahomeschool/templates/academics/
├── dailylog_entry.html                         # REDESIGN
├── attendance_report.html                      # ENHANCE
├── dashboard.html                              # ADD WIDGET
└── partials/
    └── status_selector.html                    # ENHANCE

idahomeschool/academics/urls.py                 # UPDATE
  - Add new dashboard widget endpoint
  - Add new month data HTMX endpoint
```

## Files to Keep (No Changes)

```
idahomeschool/academics/models.py
  - AttendanceStatus (lines 315-458)            # KEEP AS-IS
  - DailyLog (lines 799-870)                    # KEEP AS-IS
  - CourseNote (lines 872-921)                  # KEEP AS-IS

idahomeschool/templates/academics/
├── attendance_status_list.html                 # KEEP AS-IS
├── attendance_report_pdf.html                  # KEEP AS-IS
└── partials/
    └── status_badge.html                       # KEEP AS-IS

idahomeschool/academics/views/attendance.py
  - attendance_quick_toggle (lines 630-661)     # KEEP AS-IS
  - attendance_quick_update (lines 664-714)     # KEEP AS-IS
  - attendance_quick_delete (lines 717-742)     # KEEP AS-IS
  - attendance_course_notes (lines 745-794)     # KEEP AS-IS
  - attendance_save_course_notes (lines 797-886)# KEEP AS-IS
  - AttendanceStatusListView (lines 894-905)    # KEEP AS-IS
  - (All status CRUD views lines 907-1022)      # KEEP AS-IS
```

## Risk Mitigation

### Risk 1: Mobile browser compatibility
**Mitigation**: Test on iOS Safari, Android Chrome from start

### Risk 2: Complex state management
**Mitigation**: Keep Alpine.js state simple, rely on HTMX for server state

### Risk 3: Performance on slow connections
**Mitigation**: Optimize payloads, use pagination, show loading states

### Risk 4: User confusion with new UI
**Mitigation**: Add tooltips, include brief tutorial on first use

## Conclusion

This plan redesigns the attendance system to be:
- **Mobile-first**: Large tap targets, minimal scrolling, fast interactions
- **Modern**: HTMX + Alpine.js for smooth UX without SPA complexity
- **Compliant**: Maintains all reporting features for Idaho requirements
- **Maintainable**: Follows existing project patterns and style guide

The implementation can be completed in 3-4 weeks with focused development, and can be deployed incrementally without breaking existing functionality.
