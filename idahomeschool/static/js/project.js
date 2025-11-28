import '../sass/project.scss';
import htmx from 'htmx.org';

/* Expose HTMX globally so it can be used by other scripts */
window.htmx = htmx;

/* Project specific Javascript goes here. */

// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileMenuToggle = document.getElementById('sidebarMenuToggle');
  const mobileCloseButton = document.getElementById('sidebarClose');
  const wrapper = document.getElementById('wrapper');

  const isMobile = () => window.innerWidth <= 768;

  if (wrapper) {
    // Only restore collapsed state on desktop
    if (!isMobile()) {
      const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
      if (sidebarCollapsed) {
        wrapper.classList.add('toggled');
        if (sidebarToggle) updateToggleButton(true);
      }
    }

    // Desktop toggle button
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', function() {
        if (!isMobile()) {
          wrapper.classList.toggle('toggled');
          const isCollapsed = wrapper.classList.contains('toggled');
          localStorage.setItem('sidebarCollapsed', isCollapsed);
          updateToggleButton(isCollapsed);
        }
      });
    }

    // Mobile hamburger button - opens sidebar
    if (mobileMenuToggle) {
      mobileMenuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        if (isMobile()) {
          wrapper.classList.add('toggled');
        }
      });
    }

    // Mobile close button - closes sidebar
    if (mobileCloseButton) {
      mobileCloseButton.addEventListener('click', function(e) {
        e.stopPropagation();
        if (isMobile()) {
          wrapper.classList.remove('toggled');
        }
      });
    }

    // Close sidebar when clicking overlay (only the dark overlay, not the sidebar itself)
    if (isMobile()) {
      document.addEventListener('click', function(e) {
        if (wrapper.classList.contains('toggled')) {
          const sidebar = document.getElementById('sidebar-wrapper');
          const mobileHeader = document.querySelector('.mobile-header');

          // Check if click is inside sidebar or mobile header
          const isClickInSidebar = sidebar && sidebar.contains(e.target);
          const isClickInHeader = mobileHeader && mobileHeader.contains(e.target);

          // Only close if clicking outside both sidebar and header (on the overlay)
          if (!isClickInSidebar && !isClickInHeader) {
            wrapper.classList.remove('toggled');
          }
        }
      });
    }
  }

  function updateToggleButton(isCollapsed) {
    if (!sidebarToggle) return;

    const icon = sidebarToggle.querySelector('i');
    const textSpan = sidebarToggle.querySelector('span');

    if (isCollapsed) {
      icon.className = 'bi bi-chevron-right';
      if (textSpan) textSpan.textContent = ' Expand';
    } else {
      icon.className = 'bi bi-chevron-left';
      if (textSpan) textSpan.textContent = ' Collapse';
    }
  }

  // Handle chevron rotation for expandable sections
  const collapsibleElements = document.querySelectorAll('.sidebar-section-toggle');

  collapsibleElements.forEach(function(element) {
    const targetId = element.getAttribute('href').substring(1);
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
      // Set initial state based on whether section is shown
      if (targetElement.classList.contains('show')) {
        element.classList.remove('collapsed');
        element.setAttribute('aria-expanded', 'true');
      }

      // Listen for Bootstrap collapse events
      targetElement.addEventListener('show.bs.collapse', function() {
        element.classList.remove('collapsed');
        element.setAttribute('aria-expanded', 'true');
      });

      targetElement.addEventListener('hide.bs.collapse', function() {
        element.classList.add('collapsed');
        element.setAttribute('aria-expanded', 'false');
      });
    }
  });
});
