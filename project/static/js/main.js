/* ═══════════════════════════════════════
   NimbusVault — main.js
   • Dark mode persistence
   • Toast auto-init
   • Drag & drop file upload
   • File preview list
═══════════════════════════════════════ */

/* ── Dark Mode ── */
(function () {
  const saved = localStorage.getItem('nv-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', function () {

  /* ── Apply saved theme icon ── */
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon   = document.getElementById('themeIcon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('nv-theme', theme);
    if (themeIcon) {
      themeIcon.className = theme === 'dark'
        ? 'bi bi-sun-fill'
        : 'bi bi-moon-stars-fill';
    }
  }

  applyTheme(localStorage.getItem('nv-theme') || 'light');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  /* ── Bootstrap Toast auto-init ── */
  document.querySelectorAll('.toast').forEach(function (el) {
    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
  });

  /* ── Drag & Drop Upload ── */
  const dropZone      = document.getElementById('dropZone');
  const fileInput     = document.getElementById('fileInput');
  const previewList   = document.getElementById('filePreviewList');
  const submitBtn     = document.getElementById('submitBtn');

  if (!dropZone || !fileInput) return;

  // Prevent browser default drag behaviour on whole page
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (evt) {
    document.body.addEventListener(evt, function (e) { e.preventDefault(); });
  });

  // Highlight drop zone
  dropZone.addEventListener('dragenter', function () { dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragover',  function () { dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', function () { dropZone.classList.remove('drag-over'); });

  dropZone.addEventListener('drop', function (e) {
    dropZone.classList.remove('drag-over');
    const dt = e.dataTransfer;
    if (dt && dt.files.length) {
      // Transfer dragged files to the hidden input
      const dataTransfer = new DataTransfer();
      Array.from(dt.files).forEach(function (f) { dataTransfer.items.add(f); });
      fileInput.files = dataTransfer.files;
      renderPreview(fileInput.files);
    }
  });

  // Also handle browse-click selection
  fileInput.addEventListener('change', function () {
    renderPreview(fileInput.files);
  });

  /* ═══════════════════════════════════════
   NimbusVault — main.js
   • Dark mode persistence
   • Toast auto-init
   • Drag & drop file upload
   • File preview list
═══════════════════════════════════════ */

/* ── Dark Mode ── */
(function () {
  const saved = localStorage.getItem('nv-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', function () {

  /* ── Apply saved theme icon ── */
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon   = document.getElementById('themeIcon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('nv-theme', theme);
    if (themeIcon) {
      themeIcon.className = theme === 'dark'
        ? 'bi bi-sun-fill'
        : 'bi bi-moon-stars-fill';
    }
  }

  applyTheme(localStorage.getItem('nv-theme') || 'light');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  /* ── Bootstrap Toast auto-init ── */
  document.querySelectorAll('.toast').forEach(function (el) {
    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
  });

  /* ── Drag & Drop Upload ── */
  const dropZone      = document.getElementById('dropZone');
  const fileInput     = document.getElementById('fileInput');
  const previewList   = document.getElementById('filePreviewList');
  const submitBtn     = document.getElementById('submitBtn');

  if (!dropZone || !fileInput) return;

  // Prevent browser default drag behaviour on whole page
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (evt) {
    document.body.addEventListener(evt, function (e) { e.preventDefault(); });
  });

  // Highlight drop zone
  dropZone.addEventListener('dragenter', function () { dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragover',  function () { dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', function () { dropZone.classList.remove('drag-over'); });

  dropZone.addEventListener('drop', function (e) {
    dropZone.classList.remove('drag-over');
    const dt = e.dataTransfer;
    if (dt && dt.files.length) {
      // Transfer dragged files to the hidden input
      const dataTransfer = new DataTransfer();
      Array.from(dt.files).forEach(function (f) { dataTransfer.items.add(f); });
      fileInput.files = dataTransfer.files;
      renderPreview(fileInput.files);
    }
  });

  // Also handle browse-click selection
  fileInput.addEventListener('change', function () {
    renderPreview(fileInput.files);
  });

  function renderPreview(files) {
    previewList.innerHTML = '';
    if (!files || files.length === 0) {
      submitBtn.disabled = true;
      return;
    }

    submitBtn.disabled = false;

    Array.from(files).forEach(function (file) {
      const ext  = file.name.split('.').pop().toLowerCase();
      const size = formatBytes(file.size);

      const icons = {
        pdf: 'bi-file-earmark-pdf',
        docx: 'bi-file-earmark-word',
        txt: 'bi-file-earmark-text',
        jpg: 'bi-image', jpeg: 'bi-image',
        png: 'bi-image', gif: 'bi-image', webp: 'bi-image',
      };
      const iconClass = icons[ext] || 'bi-file-earmark';

      const item = document.createElement('div');
      item.className = 'fp-item';
      item.innerHTML =
        '<i class="bi ' + iconClass + ' fp-icon"></i>' +
        '<span class="fp-name" title="' + escapeHtml(file.name) + '">' + escapeHtml(file.name) + '</span>' +
        '<span class="fp-size">' + size + '</span>';
      previewList.appendChild(item);
    });
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

});


  function renderPreview(files) {
    previewList.innerHTML = '';
    if (!files || files.length === 0) {
      submitBtn.disabled = true;
      return;
    }

    submitBtn.disabled = false;

    Array.from(files).forEach(function (file) {
      const ext  = file.name.split('.').pop().toLowerCase();
      const size = formatBytes(file.size);

      const icons = {
        pdf: 'bi-file-earmark-pdf',
        docx: 'bi-file-earmark-word',
        txt: 'bi-file-earmark-text',
        jpg: 'bi-image', jpeg: 'bi-image',
        png: 'bi-image', gif: 'bi-image', webp: 'bi-image',
      };
      const iconClass = icons[ext] || 'bi-file-earmark';

      const item = document.createElement('div');
      item.className = 'fp-item';
      item.innerHTML =
        '<i class="bi ' + iconClass + ' fp-icon"></i>' +
        '<span class="fp-name" title="' + escapeHtml(file.name) + '">' + escapeHtml(file.name) + '</span>' +
        '<span class="fp-size">' + size + '</span>';
      previewList.appendChild(item);
    });
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

});
