document.querySelectorAll('.entry .btn-copy').forEach(btn => {
  btn.addEventListener('click', () => {
    const text = btn.parentElement.querySelector('.entry-text').textContent;
    navigator.clipboard.writeText(text)
      .then(() => showToast('Copied ✓'))
      .catch(() => showToast('Copy failed'));
  });
});

document.querySelectorAll('.entry .btn-favorite').forEach(btn => {
  btn.addEventListener('click', async () => {
    const res = await fetch('/api/history/' + btn.dataset.idx + '/favorite', { method: 'POST' });
    if (res.ok) location.reload();
    else showToast('Favorite failed');
  });
});

document.querySelectorAll('.entry .btn-delete').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (!confirm('Delete this entry?')) return;
    const res = await fetch('/api/history/' + btn.dataset.idx, { method: 'DELETE' });
    if (res.ok) location.reload();
    else showToast('Delete failed');
  });
});
