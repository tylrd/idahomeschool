# Idaho Homeschool UI Style Guide

This document outlines the UI design patterns and preferences for the Idaho Homeschool application. All new pages and components should follow these patterns for consistency.

## Design System

- **Framework**: Basecoat UI + Tailwind CSS
- **JavaScript**: Alpine.js for interactivity, HTMX for dynamic updates
- **Icons**: Lucide icons via `data-lucide` attributes
- **Principles**: Follow shadcn/ui and Basecoat UI patterns - minimal containers, clean typography, consistent spacing

## Typography

### Page Titles
```html
<h1 class="text-3xl font-bold tracking-tight">Page Title</h1>
```

### Section Headers
```html
<h2 class="text-xl font-semibold tracking-tight">Section Title</h2>
```

### Dialog/Modal Titles
```html
<h2 class="text-lg font-semibold">Dialog Title</h2>
```

### Form Labels
```html
<label for="field-id" class="text-sm font-medium">Field Label</label>
```

### Helper Text
```html
<p class="text-muted-foreground text-sm">Helper text here</p>
```

### Error Messages
```html
<p class="text-destructive text-sm">Error message here</p>
```

## Layout Patterns

### Page Header
```html
<div class="flex justify-between items-center mb-6">
  <h1 class="text-3xl font-bold tracking-tight">Page Title</h1>
  <div class="flex gap-2">
    <a href="..." class="btn-outline">
      <i data-lucide="icon-name"></i> Action
    </a>
  </div>
</div>
```

### Section Header (Simple)
```html
<div class="mb-6">
  <h1 class="text-3xl font-bold tracking-tight">Section Title</h1>
</div>
```

### Filter Section
```html
<div class="mb-6 pb-4 border-b">
  <form method="get" class="form grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Filter fields -->
  </form>
</div>
```

## Forms

### Form Container
```html
<form method="post" class="form space-y-6">
  {% csrf_token %}
  <!-- Form fields -->
</form>
```

**IMPORTANT:** Basecoat UI automatically styles all inputs inside a `.form` container. Do NOT add custom classes to inputs - they will be styled automatically via CSS selectors like `:is(.form, .field) input[type='text']`. Only add classes for error states (e.g., `border-destructive`).

### Form Field Pattern
```html
<div class="grid gap-2">
  <label for="field-id" class="text-sm font-medium">Field Label</label>
  <input type="text" name="field_name" class="{% if form.field.errors %}border-destructive{% endif %}"
         id="field-id" value="{{ form.field.value|default:'' }}">
  {% if form.field.errors %}
    <p class="text-destructive text-sm">{{ form.field.errors.0 }}</p>
  {% endif %}
  {% if form.field.help_text %}
    <p class="text-muted-foreground text-sm">{{ form.field.help_text }}</p>
  {% endif %}
</div>
```

### Textarea Field
```html
<div class="grid gap-2">
  <label for="description" class="text-sm font-medium">Description</label>
  <textarea name="description" class="{% if form.description.errors %}border-destructive{% endif %}"
            id="description" rows="3">{{ form.description.value|default:'' }}</textarea>
  {% if form.description.errors %}
    <p class="text-destructive text-sm">{{ form.description.errors.0 }}</p>
  {% endif %}
</div>
```

### Select Field
```html
<div class="grid gap-2">
  <label for="select-id" class="text-sm font-medium">Select Label</label>
  <select name="field_name" id="select-id" class="w-full">
    <option value="">All Options</option>
    {% for option in options %}
      <option value="{{ option.id }}" {% if selected == option.id|stringformat:"s" %}selected{% endif %}>
        {{ option.name }}
      </option>
    {% endfor %}
  </select>
</div>
```

### Form Actions
```html
<div class="flex gap-2">
  <button type="submit" class="btn">
    <i data-lucide="save"></i> Save
  </button>
  <a href="{% url 'cancel_url' %}" class="btn-outline">
    <i data-lucide="x"></i> Cancel
  </a>
</div>
```

## Buttons

### Primary Button
```html
<button class="btn">
  <i data-lucide="icon-name"></i> Button Text
</button>
```

### Secondary/Outline Button
```html
<a href="..." class="btn-outline">
  <i data-lucide="icon-name"></i> Button Text
</a>
```

### Icon-Only Button (Size 8)
```html
<a href="..." class="btn-icon-outline size-8">
  <i data-lucide="pencil"></i>
</a>
```

### Destructive Action Button
```html
<a href="..." class="btn-icon-outline size-8 text-destructive hover:bg-destructive/10">
  <i data-lucide="trash-2"></i>
</a>
```

### Ghost Button (for toggles)
```html
<button class="btn-icon-ghost size-8">
  <i data-lucide="icon-name"></i>
</button>
```

## Tables

### Table Structure
```html
<div class="relative w-full overflow-x-auto">
  <table class="table">
    <thead>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
        <th class="text-right">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td>
          <a href="..." class="link font-medium">{{ item.name }}</a>
        </td>
        <td class="text-muted-foreground">{{ item.description }}</td>
        <td>
          <div class="flex gap-1 justify-end">
            <a href="..." class="btn-icon-outline size-8">
              <i data-lucide="pencil"></i>
            </a>
            <a href="..." class="btn-icon-outline size-8 text-destructive hover:bg-destructive/10">
              <i data-lucide="trash-2"></i>
            </a>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

### Table Link Patterns
- **Primary data**: `<a href="..." class="link font-medium">Text</a>`
- **Secondary data/metadata**: `<a href="..." class="link text-sm">Text</a>`
- **Muted text**: `<span class="text-muted-foreground">Text</span>`
- **Placeholder**: `<span class="text-muted-foreground/50">-</span>`

## Pagination

```html
{% if is_paginated %}
<nav role="navigation" aria-label="pagination" class="mx-auto flex w-full justify-center mt-6">
  <ul class="flex flex-row items-center gap-1">
    {% if page_obj.has_previous %}
      <li>
        <a href="?page=1" class="btn-ghost btn-sm">First</a>
      </li>
      <li>
        <a href="?page={{ page_obj.previous_page_number }}" class="btn-ghost btn-sm">Previous</a>
      </li>
    {% endif %}

    <li>
      <span class="btn-outline btn-sm">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
    </li>

    {% if page_obj.has_next %}
      <li>
        <a href="?page={{ page_obj.next_page_number }}" class="btn-ghost btn-sm">Next</a>
      </li>
      <li>
        <a href="?page={{ page_obj.paginator.num_pages }}" class="btn-ghost btn-sm">Last</a>
      </li>
    {% endif %}
  </ul>
</nav>
{% endif %}
```

## Empty States

```html
<div class="p-12 text-center">
  <div class="mx-auto flex max-w-md flex-col items-center gap-2">
    <div class="flex size-12 items-center justify-center rounded-full bg-muted">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-muted-foreground">
        <!-- Icon path -->
      </svg>
    </div>
    <h2 class="text-xl font-semibold">No items found</h2>
    <p class="text-sm text-muted-foreground mb-2">Description of empty state</p>
    <a href="..." class="btn">
      <i data-lucide="plus-circle"></i> Create First Item
    </a>
  </div>
</div>
```

## Alerts/Banners

### Warning Banner
```html
<div class="mb-6 p-4 border-l-4 border-yellow-600 bg-yellow-50 dark:bg-yellow-900/20">
  <div class="flex items-start gap-3">
    <i data-lucide="alert-triangle" class="size-5 text-yellow-600 shrink-0 mt-0.5"></i>
    <div>
      <h4 class="font-semibold text-yellow-900 dark:text-yellow-200">Warning Title</h4>
      <p class="text-sm text-yellow-800 dark:text-yellow-300 mt-1">
        Warning message content.
      </p>
    </div>
  </div>
</div>
```

## Dialogs/Modals

Use native HTML5 `<dialog>` element (not Bootstrap modals).

### Dialog Structure
```html
<dialog id="dialog-id" class="dialog w-full sm:max-w-2xl max-h-[90vh]"
        aria-labelledby="dialog-title"
        onclick="if (event.target === this) this.close()">
  <div id="dialog-content">
    <header>
      <h2 id="dialog-title" class="text-lg font-semibold">Dialog Title</h2>
      <p id="dialog-description" class="text-sm text-muted-foreground">Dialog description</p>
    </header>

    <form class="form">
      <section class="space-y-4">
        <!-- Form fields -->
      </section>

      <footer>
        <button type="button" class="btn-outline" onclick="this.closest('dialog').close()">
          <i data-lucide="x"></i> Cancel
        </button>
        <button type="submit" class="btn">
          <i data-lucide="save"></i> Save
        </button>
      </footer>
    </form>

    <button type="button" class="dialog-close" aria-label="Close dialog" onclick="this.closest('dialog').close()">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 6 6 18"/>
        <path d="m6 6 12 12"/>
      </svg>
    </button>
  </div>
</dialog>

<script>
  const dialog = document.getElementById('dialog-id');

  document.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'dialog-content') {
      dialog.showModal();
    }
  });
</script>
```

### IMPORTANT: Dialog Placement

**❌ NEVER nest dialogs inside tables or other structural elements:**

```html
<!-- WRONG - Dialog inside table body -->
<table>
  <tbody>
    <tr>...</tr>
    <dialog>...</dialog>  <!-- This breaks CSS! -->
  </tbody>
</table>
```

**✅ ALWAYS place dialogs outside table structures:**

```html
<!-- CORRECT - Dialogs outside table -->
<table>
  <tbody>
    <tr>...</tr>
  </tbody>
</table>

<!-- Dialogs here, outside the table -->
{% for item in items %}
  <dialog id="dialog-edit-{{ item.pk }}">...</dialog>
  <dialog id="dialog-delete-{{ item.pk }}">...</dialog>
{% endfor %}
```

**Why this matters:**
1. Nesting dialogs inside `<tbody>`, `<tr>`, or other table elements is **invalid HTML**
2. Browsers will try to "fix" the invalid structure, which **breaks CSS inheritance and scoping**
3. This prevents Basecoat UI's form styles from applying correctly to inputs inside dialogs
4. Form inputs will appear unstyled or incorrectly styled

**Rule:** Dialogs should always be direct children of the content area, never nested inside structural elements like tables, lists, or grids.

## View Toggles (Cards/Table)

```html
<div x-data="{ viewMode: localStorage.getItem('viewKey') || 'cards' }"
     x-init="$watch('viewMode', value => localStorage.setItem('viewKey', value))">

  <!-- View Toggle -->
  <div class="flex justify-end mb-6">
    <div class="inline-flex rounded-lg border p-1 gap-1">
      <button @click="viewMode = 'cards'"
              :class="viewMode === 'cards' ? 'bg-primary text-primary-foreground' : 'bg-transparent'"
              class="btn-icon-ghost size-8">
        <i data-lucide="layout-grid"></i>
      </button>
      <button @click="viewMode = 'table'"
              :class="viewMode === 'table' ? 'bg-primary text-primary-foreground' : 'bg-transparent'"
              class="btn-icon-ghost size-8">
        <i data-lucide="table"></i>
      </button>
    </div>
  </div>

  <!-- Cards View -->
  <div x-show="viewMode === 'cards'" x-cloak class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Cards -->
  </div>

  <!-- Table View -->
  <div x-show="viewMode === 'table'" x-cloak style="display: none;" class="relative w-full overflow-x-auto">
    <!-- Table -->
  </div>
</div>
```

## Collapsible Sections

```html
<div x-data="{ open: true }">
  <!-- Section Header -->
  <div class="flex items-center justify-between pb-2 border-b">
    <button @click="open = !open" class="flex items-center gap-2 text-left group">
      <i data-lucide="chevron-down"
         class="size-5 text-muted-foreground transition-transform"
         :class="{ '-rotate-90': !open }"></i>
      <h2 class="text-xl font-semibold tracking-tight">Section Title</h2>
      <span class="badge badge-sm ml-2">{{ count }}</span>
    </button>
  </div>

  <!-- Collapsible Content -->
  <div x-show="open" x-collapse>
    <!-- Content -->
  </div>
</div>
```

## Responsive Grid Layouts

### Filter Grids
- **4-column**: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4`
- **5-column**: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4`
- **With span**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-5` + `md:col-span-2` for search fields

### Content Grids
- **Cards**: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- **Form 2-column**: `grid grid-cols-1 md:grid-cols-2 gap-4`

## Badge Styles

```html
<!-- Default badge -->
<span class="badge">Text</span>

<!-- Small badge -->
<span class="badge badge-sm">Text</span>

<!-- Colored badge -->
<span class="badge badge-sm bg-green-600 text-white">Completed</span>
<span class="badge badge-sm bg-yellow-600 text-white">Paused</span>
```

## Icons

Always use Lucide icons via `data-lucide` attributes:

```html
<i data-lucide="icon-name"></i>
```

Common icons:
- `plus-circle` - Create/Add
- `pencil` - Edit
- `trash-2` - Delete
- `eye` - View
- `save` - Save
- `x` - Cancel/Close
- `x-circle` - Clear
- `filter` - Filter
- `layout-grid` - Card view
- `table` - Table view
- `chevron-down` - Collapse indicator
- `alert-triangle` - Warning
- `settings` - Settings
- `tags` - Tags

## What to Avoid

❌ **Don't use**:
- Bootstrap modal classes (`modal`, `modal-dialog`, etc.)
- Bootstrap button classes (`btn-primary`, `btn-secondary`)
- Bootstrap icon classes (`bi`, `bi-*`)
- Heavy card wrappers on form pages
- Inconsistent spacing (use `space-y-6` on forms, `gap-4` on grids)
- `mt-4` or manual margin classes (use container spacing instead)
- `aria-invalid` (use `border-destructive` instead)
- **Dialogs nested inside tables, lists, or other structural elements** (breaks CSS!)
- Custom classes on form inputs inside `.form` containers (Basecoat styles them automatically)

✅ **Do use**:
- Native HTML5 `<dialog>` elements **placed outside table structures**
- Basecoat UI button classes (`btn`, `btn-outline`, `btn-icon-outline`)
- Lucide icons via `data-lucide`
- Minimal containers and clean spacing
- Consistent form patterns
- `text-muted-foreground` for secondary text
- `link` class for text links
- `tracking-tight` on headings
- Clean input elements without extra classes (let Basecoat CSS handle styling)

## Common Patterns Reference

### Student/User Avatar
```html
{% if student.photo %}
  <img src="{{ student.photo.url }}" alt="{{ student.name }}" class="rounded-full size-10 object-cover shrink-0">
{% else %}
  <div class="rounded-full bg-secondary text-secondary-foreground flex items-center justify-center size-10 text-sm font-bold shrink-0">
    {{ student.name.0 }}
  </div>
{% endif %}
```

### Resource/Book Thumbnail
```html
{% if resource.image %}
  <img src="{{ resource.image.url }}" alt="{{ resource.title }}" class="rounded border size-12 object-cover">
{% else %}
  <div class="bg-muted border rounded flex items-center justify-center size-12">
    <i data-lucide="book" class="size-5 text-muted-foreground"></i>
  </div>
{% endif %}
```

### Filter with Clear Button
```html
<div class="flex items-end gap-2">
  <button type="submit" class="btn flex-1">
    <i data-lucide="filter"></i> Filter
  </button>
  {% if has_filters %}
  <a href="{% url 'list_url' %}" class="btn-outline flex-1">
    <i data-lucide="x-circle"></i> Clear
  </a>
  {% endif %}
</div>
```

## Notes

- All forms should use `class="form space-y-6"`
- All form fields should be wrapped in `<div class="grid gap-2">`
- **Form inputs inside `.form` containers need NO classes** - Basecoat CSS styles them automatically
- **NEVER nest dialogs inside table structures** - always place them outside `<table>`, `<tbody>`, etc.
- Use `w-full` on select elements in filter grids
- Use `flex gap-2` for button groups
- Use `flex gap-1` for icon button groups
- Always include both icon and text in primary buttons
- Use `shrink-0` on avatars to prevent squishing
- Use `text-right` on action columns in tables
- Maintain consistent `size-8` for icon buttons
- Use Alpine.js `x-cloak` to prevent flash of unstyled content
- Use `onclick="if (event.target === this) this.close()"` on dialogs for backdrop close
