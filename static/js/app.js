(() => {
  const input = document.getElementById('images');
  const drop = document.getElementById('dropzone');
  const previewArea = document.getElementById('preview-area');
  const previewGrid = document.getElementById('preview-grid');
  const count = document.getElementById('file-count');
  const clear = document.getElementById('clear-files');
  const form = document.getElementById('upload-form');
  const processing = document.getElementById('processing');
  const submit = document.getElementById('submit-button');

  function showFiles(files) {
    if (!input || !previewArea) return;
    const list = Array.from(files);
    previewGrid.innerHTML = '';
    count.textContent = `${list.length} ภาพที่เลือก`;
    previewArea.hidden = list.length === 0;
    list.forEach(file => {
      const card = document.createElement('div');
      card.className = 'preview-item';
      const img = document.createElement('img');
      const label = document.createElement('span');
      label.textContent = file.name;
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => { img.src = e.target.result; };
        reader.readAsDataURL(file);
      }
      card.append(img, label);
      previewGrid.append(card);
    });
  }
  input?.addEventListener('change', () => showFiles(input.files));
  clear?.addEventListener('click', () => { input.value = ''; showFiles([]); });
  ['dragenter','dragover'].forEach(event => drop?.addEventListener(event, e => {
    e.preventDefault(); drop.classList.add('dragover');
  }));
  ['dragleave','drop'].forEach(event => drop?.addEventListener(event, e => {
    e.preventDefault(); drop.classList.remove('dragover');
  }));
  drop?.addEventListener('drop', e => {
    if (!e.dataTransfer?.files?.length) return;
    input.files = e.dataTransfer.files;
    showFiles(input.files);
  });
  form?.addEventListener('submit', e => {
    if (!input.files || input.files.length < 3) {
      e.preventDefault();
      alert('กรุณาเลือกภาพอย่างน้อย 3 ภาพ');
      return;
    }
    processing.hidden = false;
    submit.disabled = true;
    submit.textContent = 'กำลังประมวลผล…';
  });
  const copy = document.getElementById('copy-url');
  copy?.addEventListener('click', async () => {
    const field = document.getElementById('share-url');
    try {
      await navigator.clipboard.writeText(field.value);
      copy.textContent = 'คัดลอกแล้ว ✓';
    } catch {
      field.select();
      document.execCommand('copy');
      copy.textContent = 'คัดลอกแล้ว ✓';
    }
  });
})();
