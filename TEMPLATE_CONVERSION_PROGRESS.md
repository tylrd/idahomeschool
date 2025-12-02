# Template Conversion Progress: Bootstrap → Tailwind/Basecoat UI

## Project Context

**Objective**: Convert all smaller academic templates from Bootstrap to Tailwind CSS using Basecoat UI components, following the shadcn theme.

**Tech Stack**:
- Django 5.2
- Python 3.13
- Tailwind CSS (already installed)
- Basecoat UI components
- crispy-tailwind (already configured in settings: `CRISPY_TEMPLATE_PACK = "tailwind"`)

**Basecoat UI Reference**: Kitchen sink available at https://basecoatui.com/kitchen-sink/

## Completed Work (64 templates) ✅ ALL DONE!

### ✅ All Confirm Delete Templates (16 files)
All converted to Basecoat UI with proper card structure, alerts, and buttons:

1. ✅ schoolyear_confirm_delete.html
2. ✅ student_confirm_delete.html
3. ✅ course_confirm_delete.html
4. ✅ coursetemplate_confirm_delete.html
5. ✅ courseenrollment_confirm_delete.html
6. ✅ curriculumresource_confirm_delete.html
7. ✅ gradelevel_confirm_delete.html
8. ✅ studentgradeyear_confirm_delete.html
9. ✅ tag_confirm_delete.html
10. ✅ resource_confirm_delete.html
11. ✅ color_confirm_delete.html
12. ✅ color_palette_confirm_delete.html
13. ✅ color_palette_group_confirm_delete.html
14. ✅ attendance_status_confirm_delete.html
15. ✅ dailylog_confirm_delete.html
16. ✅ reading_list_confirm_delete.html

### ✅ ALL Partial Templates (11 files) - COMPLETED!
All partial templates converted to Tailwind/Basecoat UI:

1. ✅ tag_badge.html - Simple badge conversion
2. ✅ reading_status_badge.html - Badge color mapping
3. ✅ status_badge.html - Complex with HTMX and inline styles
4. ✅ color_palette_preview.html - Grid layout with badges and alerts
5. ✅ reading_list_entry.html - Card with image, body, and footer
6. ✅ resource_search_results.html - List group with checkboxes
7. ✅ dailylog_entry_form.html - Form with Basecoat components (was already converted)
8. ✅ course_notes_modal.html - Modal with HTMX form submission
9. ✅ resource_create_modal.html - Modal with multi-field form
10. ✅ status_selector.html - **Complex**: Modal with custom-colored status buttons, HTMX
11. ✅ tag_selector.html - **Complex**: Autocomplete component with JavaScript (~345 lines)

## Remaining Work (0 templates) - PROJECT COMPLETE! 🎉

### Partial Templates
✅ **ALL COMPLETED!** (11/11 files)

### List Templates
✅ **ALL COMPLETED!** (11/11 files)
All list templates converted to Tailwind/Basecoat UI with responsive tables, search/filter forms, and pagination:

1. ✅ schoolyear_list.html - Table with badge, pagination
2. ✅ student_list.html - Card grid with search, photos
3. ✅ course_list.html - **Complex**: Collapsible sections grouped by grade level with JavaScript
4. ✅ coursetemplate_list.html - Card grid with search, pagination
5. ✅ courseenrollment_list.html - Table with multi-select filters, pagination
6. ✅ gradelevel_list.html - Simple table
7. ✅ tag_list.html - Table with custom color badges
8. ✅ color_palette_list.html - Already converted (tabbed interface with HTMX)
9. ✅ resource_list.html - Table with image thumbnails, multi-filter, pagination
10. ✅ dailylog_list.html - Table with date filters, status badges, pagination
11. ✅ attendance_status_list.html - Table with color previews

### Detail Templates
✅ **ALL COMPLETED!** (10/10 files)
All detail templates converted with Tailwind grid layouts, description lists, and Basecoat cards:

1. ✅ schoolyear_detail.html - Details card, statistics, enrolled students grid, enrollments table
2. ✅ student_detail.html - Photo/avatar, student info, enrollment cards, grade assignments, course enrollments, recent books
3. ✅ course_detail.html - Course info card, enrollments table with status badges, resources list
4. ✅ coursetemplate_detail.html - Template info, suggested resources list, courses created from template
5. ✅ courseenrollment_detail.html - Enrollment details with progress bar and status badges
6. ✅ gradelevel_detail.html - Grade info, current students table, courses table, student assignments
7. ✅ tag_detail.html - Tag badge display, resources with tag table
8. ✅ reading_list_detail.html - Book info card, reading progress with star ratings, notes section
9. ✅ resource_detail.html - Resource info card with tags display
10. ✅ dailylog_detail.html - Daily log info with status badges, course notes section, metadata

### Form Templates
✅ **ALL COMPLETED!** (16/16 files)
All form templates converted with crispy-forms integration, HTMX interactions, and JavaScript preserved:

1. ✅ student_form.html - Uses {% crispy form %}
2. ✅ schoolyear_form.html - Uses {% crispy form %}
3. ✅ gradelevel_form.html - Uses {% crispy form %}
4. ✅ courseenrollment_form.html - Uses {% crispy form %}
5. ✅ curriculumresource_form.html - Uses {% crispy form %} with conditional cancel links
6. ✅ studentgradeyear_form.html - Uses {% crispy form %} with conditional header
7. ✅ color_palette_form.html - Manual form with checkboxes for colors
8. ✅ color_palette_group_form.html - Simple form with description field
9. ✅ attendance_status_form.html - Two-column layout with sidebar tips
10. ✅ coursetemplate_form.html - **Complex**: ~360 lines, HTMX resource search with tag filters
11. ✅ tag_form.html - Color picker with palette selection
12. ✅ color_form.html - Individual color creation with preview
13. ✅ reading_list_form.html - Book entry form with status tracking
14. ✅ resource_form.html - Resource form with image upload support
15. ✅ dailylog_form.html - Daily log entry with course selection
16. ✅ course_form.html - **Very Complex**: ~440 lines, HTMX, resource search, tag filters, template selection

## Conversion Reference Guide

### Key Principles
1. **Preserve Django template logic**: Keep all `{% %}` and `{{ }}` syntax intact
2. **Preserve HTMX attributes**: Keep all `hx-*` attributes unchanged
3. **Preserve JavaScript**: Keep all `<script>` blocks and event handlers
4. **Preserve accessibility**: Maintain ARIA attributes and semantic HTML
5. **Custom colors**: Use inline styles for custom colors (like tag colors)
6. **Bootstrap Icons**: Can remain (`bi bi-*` classes work with Tailwind)

### Card Components

**Bootstrap:**
```html
<div class="card">
  <div class="card-header">
    <h3 class="mb-0">Title</h3>
  </div>
  <div class="card-body">
    Content
  </div>
</div>
```

**Basecoat:**
```html
<div class="card max-w-2xl">
  <header>
    <h2>Title</h2>
    <p>Optional description</p>
  </header>
  <section>
    Content
  </section>
  <footer>
    Optional footer
  </footer>
</div>
```

### Buttons

| Bootstrap | Basecoat |
|-----------|----------|
| `btn btn-primary` | `btn-primary` |
| `btn btn-secondary` | `btn-secondary` |
| `btn btn-success` | `btn-primary` (no success variant) |
| `btn btn-danger` | `btn-destructive` |
| `btn btn-outline-primary` | `btn-outline` |
| `btn btn-outline-secondary` | `btn-secondary` |
| `btn btn-outline-danger` | `btn-outline` + destructive styling |
| `btn btn-sm` | `btn-sm-primary`, `btn-sm-outline`, etc. |
| `btn btn-link` | `btn-link` |

### Forms

**Bootstrap:**
```html
<div class="mb-3">
  <label for="id" class="form-label">Label</label>
  <input type="text" class="form-control" id="id">
  <small class="form-text text-muted">Help text</small>
  <div class="invalid-feedback">Error</div>
</div>
```

**Basecoat:**
```html
<form class="form grid gap-6">
  <div class="grid gap-2">
    <label for="id">Label</label>
    <input type="text" id="id">
    <p class="text-muted-foreground text-sm">Help text</p>
    <p class="text-destructive text-sm">Error</p>
  </div>
</form>
```

**Form Class Changes:**
- Remove `form-control` class (inputs styled automatically)
- Remove `form-label` class from labels
- Remove `form-select` class (use `select` directly)
- `form-text text-muted` → `text-muted-foreground text-sm`
- `is-invalid` → `aria-invalid="true"`
- `invalid-feedback` → Standard paragraph with error styling

### Tables

**Bootstrap:**
```html
<div class="table-responsive">
  <table class="table table-striped">
    <thead>...</thead>
    <tbody>...</tbody>
  </table>
</div>
```

**Basecoat:**
```html
<div class="relative w-full overflow-x-auto">
  <table class="table">
    <thead>...</thead>
    <tbody>...</tbody>
  </table>
</div>
```

### Badges

| Bootstrap | Basecoat |
|-----------|----------|
| `badge bg-success` | `badge` or custom `bg-green-600 text-white` |
| `badge bg-secondary` | `badge-secondary` |
| `badge bg-primary` | `badge` |
| `badge bg-warning` | `badge-outline` + custom yellow styling |
| `badge bg-danger` | `badge-destructive` |
| `badge bg-info` | `badge` |

### Alerts

**Bootstrap:**
```html
<div class="alert alert-info">
  <h4>Title</h4>
  <p>Message</p>
</div>
```

**Basecoat:**
```html
<div class="alert">
  <svg>...</svg>
  <h2>Title</h2>
  <section>Message</section>
</div>
```

**Alert Types:**
- Standard alert: `alert`
- Destructive/Error: `alert-destructive`
- Include appropriate SVG icon

**SVG Icons for Alerts:**

Warning/Alert Icon:
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
  <path d="M12 9v4" />
  <path d="M12 17h.01" />
</svg>
```

Circle Alert Icon:
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10" />
  <line x1="12" x2="12" y1="8" y2="12" />
  <line x1="12" x2="12.01" y1="16" y2="16" />
</svg>
```

### Layout Classes

| Bootstrap | Tailwind |
|-----------|----------|
| `d-flex` | `flex` |
| `d-inline-block` | `inline-block` |
| `d-grid` | `grid` |
| `justify-content-between` | `justify-between` |
| `justify-content-center` | `justify-center` |
| `align-items-center` | `items-center` |
| `mb-3`, `mb-4` | `mb-3`, `mb-4` |
| `mt-3`, `mt-4` | `mt-3`, `mt-4` |
| `gap-2`, `gap-3` | `gap-2`, `gap-3` |
| `row` | `grid` or `flex` |
| `col-md-6` | `grid grid-cols-1 md:grid-cols-2` |
| `text-muted` | `text-muted-foreground` |
| `text-success` | `text-green-600` |
| `text-danger` | `text-destructive` |
| `w-100` | `w-full` |
| `text-decoration-none` | `no-underline` |
| `ms-1`, `ms-2` | `ml-1`, `ml-2` |
| `me-1`, `me-2` | `mr-1`, `mr-2` |
| `position-relative` | `relative` |
| `position-absolute` | `absolute` |
| `visually-hidden` | `sr-only` |

### Pagination

**Bootstrap:**
```html
<ul class="pagination">
  <li class="page-item"><a class="page-link" href="#">Previous</a></li>
  <li class="page-item active"><span class="page-link">1</span></li>
</ul>
```

**Basecoat:**
```html
<nav role="navigation" aria-label="pagination" class="mx-auto flex w-full justify-center">
  <ul class="flex flex-row items-center gap-1">
    <li><a href="#" class="btn-ghost">Previous</a></li>
    <li><a href="#" class="btn-outline size-9">1</a></li>
  </ul>
</nav>
```

### Modals

**Bootstrap Modal** (from status_selector.html):
```html
<div class="modal fade show d-block" tabindex="-1" role="dialog" style="background-color: rgba(0,0,0,0.5);">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Title</h5>
        <button type="button" class="btn-close"></button>
      </div>
      <div class="modal-body">Content</div>
    </div>
  </div>
</div>
```

**Basecoat/Tailwind Modal Pattern** (needs to be defined):
- Use Tailwind utility classes for modal overlay and positioning
- Keep HTMX swap patterns intact
- Preserve JavaScript for modal open/close

### Description Lists

**Bootstrap:**
```html
<dl class="row">
  <dt class="col-sm-4">Label:</dt>
  <dd class="col-sm-8">Value</dd>
</dl>
```

**Tailwind:**
```html
<dl class="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-2">
  <dt class="font-medium">Label:</dt>
  <dd class="sm:col-span-2">Value</dd>
</dl>
```

## Special Cases & Notes

### 1. Crispy Forms Templates
Templates using `{% crispy form %}` (like student_form.html) will automatically use Tailwind styling because crispy-tailwind is configured in settings.

### 2. Custom Colors (Tags, Attendance Status)
Preserve inline styles for custom colors:
```html
<span class="badge" style="background-color: {{ tag.color }}; color: {{ text_color }};">
  {{ tag.name }}
</span>
```

### 3. HTMX Attributes
Always preserve:
- `hx-get`, `hx-post`, `hx-delete`
- `hx-target`, `hx-swap`
- `hx-trigger`, `hx-include`
- `hx-confirm`, `hx-headers`

### 4. JavaScript Functions
Keep all JavaScript intact, including:
- Event listeners
- HTMX event handlers (`htmx:afterSwap`, etc.)
- Custom functions
- State management

### 5. Complex Templates to Watch

**course_form.html** (~440 lines):
- HTMX resource search
- Tag filter system
- Template selection with auto-populate
- Modal for creating resources
- Extensive JavaScript

**tag_selector.html** (~345 lines):
- Autocomplete dropdown
- Tag creation
- Color palette integration
- Complex JavaScript state management

**status_selector.html** (~109 lines):
- Bootstrap modal structure
- HTMX form submission
- Dynamic button generation
- JavaScript for modal interactions

## Implementation Strategy

### Completed Order:
1. ✅ **Confirm delete templates** (16/16) - COMPLETED
2. ✅ **Partial templates** (11/11) - COMPLETED
3. ✅ **List templates** (11/11) - COMPLETED
4. ✅ **Detail templates** (10/10) - COMPLETED
5. ✅ **Form templates** (16/16) - COMPLETED

### Summary:
All 64 academic templates have been successfully converted from Bootstrap to Tailwind CSS/Basecoat UI. Complex modals, HTMX interactions, JavaScript functionality, and custom color systems have all been preserved during the conversion.

## Files Not Included

These larger/complex templates are handled separately:
- dashboard.html (already being worked on)
- dailylog_entry.html (already being worked on)
- attendance_calendar.html
- attendance_report.html
- attendance_report_pdf.html
- student_reading_list.html
- reading_list.html
- book_tag_preferences.html
- color_palette_import.html

## Project Complete! 🎉

All 64 academic templates have been successfully converted from Bootstrap to Tailwind CSS/Basecoat UI:

- ✅ 16 Confirm delete templates
- ✅ 11 Partial templates (including complex modals and autocomplete)
- ✅ 11 List templates (with tables, pagination, and filters)
- ✅ 10 Detail templates (with description lists and card layouts)
- ✅ 16 Form templates (including very complex forms with HTMX and JavaScript)

All Django template logic, HTMX attributes, JavaScript functionality, and custom color systems have been preserved.

## Testing Checklist

After each template conversion, verify:
- [ ] Forms render correctly with proper spacing
- [ ] Form validation errors display properly
- [ ] Tables are responsive and scrollable
- [ ] Buttons have correct variants and sizes
- [ ] Badges display with appropriate colors
- [ ] Cards have proper structure (header, section, footer)
- [ ] HTMX interactions still work
- [ ] JavaScript functions still execute
- [ ] Accessibility attributes preserved
- [ ] Mobile responsiveness maintained
- [ ] Custom colors (tags, attendance) display correctly

## Quick Reference: File Locations

- Templates: `/Users/taylordaugherty/code/idahomeschool/idahomeschool/templates/academics/`
- Partials: `/Users/taylordaugherty/code/idahomeschool/idahomeschool/templates/academics/partials/`
- Settings: `/Users/taylordaugherty/code/idahomeschool/config/settings/base.py`
- Basecoat Examples: Downloaded to `/tmp/basecoat-examples.html` (may need to re-fetch)
