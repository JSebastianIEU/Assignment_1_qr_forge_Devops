const grid = document.getElementById('grid');
const empty = document.getElementById('empty');
const form = document.getElementById('qr-form');
const exportBtn = document.getElementById('exportCsv');
const toastEl = document.getElementById('toast');

function toast(msg){
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(()=> toastEl.classList.remove('show'), 1800);
}

async function apiList(){
  const res = await fetch('/api/qr');
  if(!res.ok) throw new Error('Failed to fetch list');
  return await res.json();
}

function cardTemplate(item){
  // Image src points to download endpoint which serves the SVG
  const svgSrc = `/api/qr/${item.id}/download`;
  const created = new Date(item.created_at).toLocaleString();
  return `
    <article class="card qr" data-id="${item.id}">
      <div class="qr-title">${escapeHtml(item.title)}</div>
      <div class="qr-meta">Created: ${created}</div>
      <div class="qr-img">
        <img src="${svgSrc}" alt="QR for ${escapeHtml(item.title)}" loading="lazy">
      </div>
      <div class="row-actions">
        <a class="btn ghost" href="${svgSrc}" download>Download</a>
        <button class="btn danger del" data-id="${item.id}">Delete</button>
      </div>
    </article>
  `;
}

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, m => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[m]));
}

async function render(){
  const items = await apiList();
  grid.innerHTML = items.map(cardTemplate).join('');
  empty.classList.toggle('hidden', items.length > 0);

  // bind delete buttons
  grid.querySelectorAll('.del').forEach(btn=>{
    btn.addEventListener('click', async ()=>{
      const id = btn.dataset.id;
      const ok = confirm('Delete this QR?');
      if(!ok) return;
      const res = await fetch(`/api/qr/${id}`, { method: 'DELETE' });
      if(res.ok){
        toast('QR deleted');
        await render();
      }else{
        toast('Error deleting');
      }
    });
  });
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(form);
  const payload = {
    title: fd.get('title'),
    url: fd.get('url')
  };

  // Basic client validation for URL
  try{
    new URL(payload.url);
  }catch{
    toast('Please enter a valid URL');
    return;
  }

  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;

  const res = await fetch('/api/qr', {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify(payload)
  });

  btn.disabled = false;

  if(res.ok){
    form.reset();
    toast('QR created');
    await render();
  }else{
    const err = await res.text();
    toast('Error creating QR');
    console.error(err);
  }
});

exportBtn.addEventListener('click', ()=>{
  window.location.href = '/api/export/csv';
});

// initial render
render();
