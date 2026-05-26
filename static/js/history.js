function copyEntry(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied ✓');
  }).catch(() => {
    showToast('Copy failed');
  });
}
