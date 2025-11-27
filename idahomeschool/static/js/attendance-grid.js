/**
 * Attendance Grid Advanced Features
 * - Batch operations (multi-select and bulk update)
 * - Keyboard shortcuts (Space for batch mode, Esc to close modals)
 */

class AttendanceGrid {
  constructor() {
    this.selectedCells = new Set();
    this.lastSelectedCell = null;
    this.batchMode = false;

    this.init();
  }

  init() {
    this.setupBatchMode();
    this.setupCellSelection();
    this.setupEscapeKey();
  }

  /**
   * Setup batch selection mode
   */
  setupBatchMode() {
    // Add batch mode toggle button
    const calendarCard = document.querySelector('.card.mb-4 .card-body .row');
    if (!calendarCard) return;

    // Create batch mode controls
    const batchControls = document.createElement('div');
    batchControls.className = 'col-md-12 mt-3';
    batchControls.id = 'batch-controls';
    batchControls.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <button type="button" class="btn btn-sm btn-outline-secondary" id="toggle-batch-mode">
          <i class="bi bi-check2-square"></i> Batch Mode
        </button>
        <div id="batch-actions" class="d-none">
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-success batch-action" data-status="PRESENT">
              Mark Present
            </button>
            <button type="button" class="btn btn-danger batch-action" data-status="ABSENT">
              Mark Absent
            </button>
            <button type="button" class="btn btn-warning batch-action" data-status="SICK">
              Mark Sick
            </button>
            <button type="button" class="btn btn-info batch-action" data-status="HOLIDAY">
              Mark Holiday
            </button>
            <button type="button" class="btn btn-primary batch-action" data-status="FIELD_TRIP">
              Mark Field Trip
            </button>
          </div>
          <button type="button" class="btn btn-sm btn-outline-secondary ms-2" id="clear-selection">
            Clear (<span id="selected-count">0</span>)
          </button>
        </div>
      </div>
    `;

    calendarCard.appendChild(batchControls);

    // Toggle batch mode
    document.getElementById('toggle-batch-mode').addEventListener('click', () => {
      this.batchMode = !this.batchMode;
      this.toggleBatchMode();
    });

    // Clear selection
    document.getElementById('clear-selection')?.addEventListener('click', () => {
      this.clearSelection();
    });

    // Batch actions
    document.querySelectorAll('.batch-action').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const status = e.target.dataset.status;
        this.batchUpdateStatus(status);
      });
    });
  }

  /**
   * Toggle batch mode UI
   */
  toggleBatchMode() {
    const batchActions = document.getElementById('batch-actions');
    const toggleBtn = document.getElementById('toggle-batch-mode');

    if (this.batchMode) {
      batchActions.classList.remove('d-none');
      toggleBtn.classList.add('active');
      toggleBtn.innerHTML = '<i class="bi bi-x-square"></i> Exit Batch Mode';
      document.body.classList.add('batch-mode');
    } else {
      batchActions.classList.add('d-none');
      toggleBtn.classList.remove('active');
      toggleBtn.innerHTML = '<i class="bi bi-check2-square"></i> Batch Mode';
      document.body.classList.remove('batch-mode');
      this.clearSelection();
    }
  }

  /**
   * Setup cell selection (click, shift-click, ctrl-click)
   */
  setupCellSelection() {
    document.addEventListener('click', (e) => {
      if (!this.batchMode) return;

      const cell = e.target.closest('.attendance-cell');
      if (!cell) return;

      // Prevent default badge action in batch mode
      if (e.target.closest('[hx-get]')) {
        e.preventDefault();
        e.stopPropagation();
      }

      // Prevent text selection when shift-clicking in batch mode
      if (e.shiftKey) {
        e.preventDefault();
      }

      const cellKey = `${cell.dataset.studentId}-${cell.dataset.date}`;

      if (e.shiftKey && this.lastSelectedCell) {
        // Shift-click: select range
        this.selectRange(this.lastSelectedCell, cell);
      } else if (e.ctrlKey || e.metaKey) {
        // Ctrl/Cmd-click: toggle selection
        this.toggleCell(cellKey, cell);
      } else {
        // Regular click: select only this cell
        if (!e.ctrlKey && !e.metaKey) {
          this.clearSelection();
        }
        this.toggleCell(cellKey, cell);
      }

      this.lastSelectedCell = cell;
      this.updateSelectionCount();
    });
  }

  /**
   * Toggle cell selection
   */
  toggleCell(cellKey, cellElement) {
    if (this.selectedCells.has(cellKey)) {
      this.selectedCells.delete(cellKey);
      cellElement.classList.remove('selected');
    } else {
      this.selectedCells.add(cellKey);
      cellElement.classList.add('selected');
    }
  }

  /**
   * Select range of cells (for shift-click)
   */
  selectRange(startCell, endCell) {
    const allCells = Array.from(document.querySelectorAll('.attendance-cell'));
    const startIndex = allCells.indexOf(startCell);
    const endIndex = allCells.indexOf(endCell);

    const [minIndex, maxIndex] = [Math.min(startIndex, endIndex), Math.max(startIndex, endIndex)];

    for (let i = minIndex; i <= maxIndex; i++) {
      const cell = allCells[i];
      const cellKey = `${cell.dataset.studentId}-${cell.dataset.date}`;
      this.selectedCells.add(cellKey);
      cell.classList.add('selected');
    }
  }

  /**
   * Clear all selections
   */
  clearSelection() {
    this.selectedCells.clear();
    document.querySelectorAll('.attendance-cell.selected').forEach(cell => {
      cell.classList.remove('selected');
    });
    this.updateSelectionCount();
  }

  /**
   * Update selection count display
   */
  updateSelectionCount() {
    const countSpan = document.getElementById('selected-count');
    if (countSpan) {
      countSpan.textContent = this.selectedCells.size;
    }
  }

  /**
   * Batch update selected cells to a new status
   */
  async batchUpdateStatus(status) {
    if (this.selectedCells.size === 0) {
      alert('No cells selected');
      return;
    }

    const confirmMsg = `Mark ${this.selectedCells.size} cell(s) as ${status.replace('_', ' ')}?`;
    if (!confirm(confirmMsg)) return;

    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content ||
                      document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                      getCookie('csrftoken');

    // Update each selected cell
    const updates = Array.from(this.selectedCells).map(async (cellKey) => {
      // Split cellKey properly: "3-2025-11-27" -> studentId="3", dateStr="2025-11-27"
      const parts = cellKey.split('-');
      const studentId = parts[0];
      const dateStr = parts.slice(1).join('-');
      const url = `/academics/attendance/quick-update/${studentId}/${dateStr}/`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
          },
          body: `status=${status}`,
        });

        if (response.ok) {
          const html = await response.text();
          const cell = document.querySelector(`[data-student-id="${studentId}"][data-date="${dateStr}"]`);
          if (cell) {
            // Update the cell content
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            const newBadge = tempDiv.querySelector('[id^="cell-"]');
            if (newBadge) {
              const oldBadge = cell.querySelector('[id^="cell-"]');
              if (oldBadge) {
                oldBadge.replaceWith(newBadge);
                // Tell HTMX to process the new element so hx-* attributes work
                if (typeof htmx !== 'undefined') {
                  htmx.process(newBadge);
                }
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error updating ${cellKey}:`, error);
      }
    });

    await Promise.all(updates);

    // Exit batch mode after successful batch update
    this.batchMode = false;
    this.toggleBatchMode();
  }

  /**
   * Setup escape key to close modals
   */
  setupEscapeKey() {
    document.addEventListener('keydown', (e) => {
      // Escape to close modals
      if (e.key === 'Escape') {
        document.getElementById('status-selector-container').innerHTML = '';
        document.getElementById('course-notes-modal-container').innerHTML = '';
      }

      // Space to toggle batch mode
      if (e.key === ' ' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        const toggleBtn = document.getElementById('toggle-batch-mode');
        if (toggleBtn) toggleBtn.click();
      }
    });
  }
}

/**
 * Helper function to get CSRF token from cookies
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.attendance-cell')) {
      new AttendanceGrid();
    }
  });
} else {
  if (document.querySelector('.attendance-cell')) {
    new AttendanceGrid();
  }
}
