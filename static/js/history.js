function copyEntry(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied ✓');
  }).catch(() => {
    showToast('Copy failed');
  });
}

async function deleteEntry(idx) {
  if (!confirm('Delete this entry?')) return;
  const res = await fetch('/api/history/' + idx, { method: 'DELETE' });
  if (res.ok) {
    location.reload();
  } else {
    showToast('Delete failed');
  }
}
