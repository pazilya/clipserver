async function pushClip() {
  const text = document.getElementById('pushText').value;
  if (!text.trim()) return;
  const res = await fetch('/clip', { method: 'POST', body: text, headers: { 'Content-Type': 'text/plain' } });
  if (res.ok) {
    document.getElementById('currentText').textContent = text;
    document.getElementById('pushText').value = '';
    showToast('Pushed ✓');
  }
}

async function toggleFavoriteCurrent() {
  const btn = document.getElementById('favoriteCurrentBtn');
  if (!btn || !btn.dataset.idx) return;
  const res = await fetch('/api/history/' + btn.dataset.idx + '/favorite', { method: 'POST' });
  if (res.ok) {
    const data = await res.json();
    btn.classList.toggle('active', data.favorite);
    showToast(data.favorite ? 'Favorited ✓' : 'Unfavorited');
  } else {
    showToast('Favorite failed');
  }
}

async function copyToClipboard() {
  const text = document.getElementById('currentText').textContent;
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied ✓');
  } catch {
    showToast('Copy failed — try manual select');
  }
}
