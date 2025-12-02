import '@/sass/project.scss';
import '@/css/style.css';
import 'basecoat-css/all';
import Alpine from 'alpinejs'
import htmx from 'htmx.org';
import { createIcons, icons } from 'lucide';

window.Alpine = Alpine
window.htmx = htmx;

Alpine.start()

// Initialize Lucide icons
createIcons({ icons });

// Re-initialize Lucide icons after HTMX swaps content
document.body.addEventListener('htmx:afterSwap', function() {
  createIcons({ icons });
});