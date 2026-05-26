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

async function copyToClipboard() {
  const text = document.getElementById('currentText').textContent;
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied ✓');
  } catch {
    showToast('Copy failed — try manual select');
  }
}
