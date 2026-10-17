(() => {
  'use strict';
  document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-copy-target]');
    if (!button) return;
    const field = document.getElementById(button.dataset.copyTarget);
    const status = document.getElementById('copy-status');
    if (!field) return;
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(field.value);
      const original = button.textContent;
      button.textContent = 'Copied';
      status.textContent = 'Copied. Paste it into the matching Vinted field.';
      setTimeout(() => { button.textContent = original; }, 1800);
    } catch (_) {
      field.focus();
      field.select();
      field.setSelectionRange(0, field.value.length);
      status.textContent = 'Copy manually: the text is selected. Use Copy from your device menu, or Ctrl+C / Command+C.';
    }
  });
})();
