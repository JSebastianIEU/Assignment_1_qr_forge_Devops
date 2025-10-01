const storageKey = 'qrforge_token';
const authState = {
  token: localStorage.getItem(storageKey) || null,
};

const body = document.body;
const toastEl = document.getElementById('toast');

function toast(message, duration = 2200) {
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), duration);
}

function isAuthed() {
  return Boolean(authState.token);
}

function updateAuthStateUI() {
  const authed = isAuthed();
  body?.classList.toggle('authed', authed);
  document.querySelectorAll('[data-requires-auth]').forEach((el) => {
    el.classList.toggle('hidden', !authed);
  });
  document.querySelectorAll('[data-hide-when-authed]').forEach((el) => {
    el.classList.toggle('hidden', authed);
  });
}

function broadcastAuthState() {
  document.dispatchEvent(new CustomEvent('auth-change', { detail: { authed: isAuthed() } }));
}

function setToken(token) {
  if (token) {
    localStorage.setItem(storageKey, token);
    authState.token = token;
  } else {
    localStorage.removeItem(storageKey);
    authState.token = null;
  }
  updateAuthStateUI();
  broadcastAuthState();
}

updateAuthStateUI();
broadcastAuthState();

let unauthorizedNoticeShown = false;
function handleUnauthorized() {
  if (authState.token) setToken(null);
  if (!unauthorizedNoticeShown) {
    unauthorizedNoticeShown = true;
    toast('Please log in to continue');
    setTimeout(() => {
      unauthorizedNoticeShown = false;
      window.location.href = '/login';
    }, 400);
  }
  throw new Error('Unauthorized');
}

function authorizedFetch(url, options = {}) {
  if (!authState.token) throw new Error('Unauthorized');
  const opts = { ...options };
  const headers = new Headers(options.headers || {});
  headers.set('Authorization', `Bearer ${authState.token}`);
  opts.headers = headers;
  return fetch(url, opts).then((res) => {
    if (res.status === 401) handleUnauthorized();
    return res;
  });
}

function requireAuth() {
  if (isAuthed()) return true;
  toast('Please log in to continue');
  setTimeout(() => {
    window.location.href = '/login';
  }, 400);
  return false;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (match) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[match]);
}

function formatDate(value) {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleString();
  } catch (err) {
    return value;
  }
}

function sanitizeFilename(title, ext) {
  const safe = String(title || 'qr-code')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'qr-code';
  return `${safe}.${ext}`;
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function base64ToBlob(base64, type) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type });
}

const historyTargets = {
  drawer: document.getElementById('historyList'),
  page: document.getElementById('historyGrid'),
  empty: document.getElementById('historyEmpty'),
  guard: document.getElementById('historyGuard'),
  content: document.getElementById('historyContent'),
};

let historyCache = new Map();

function historyCardTemplate(item) {
  const created = formatDate(item.created_at);
  const title = escapeHtml(item.title || 'Untitled QR');
  return `
    <article class="history-card" data-id="${item.id}" data-title="${title}">
      <img data-id="${item.id}" alt="Preview for ${title}" loading="lazy" />
      <div class="history-card-body">
        <div class="history-card-title">${title}</div>
        <div class="history-card-meta">Created ${created}</div>
      </div>
      <div class="history-card-actions">
        <button class="btn ghost small" type="button" data-action="svg" data-id="${item.id}">SVG</button>
        <button class="btn small" type="button" data-action="png" data-id="${item.id}">PNG</button>
        <button class="btn danger small" type="button" data-action="delete" data-id="${item.id}">Delete</button>
      </div>
    </article>
  `;
}

function bindHistoryActions(container) {
  if (!container) return;
  container.querySelectorAll('[data-action]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      const id = btn.dataset.id;
      if (!id) return;
      const item = historyCache.get(id);
      if (!item) return;
      if (action === 'delete') {
        if (!requireAuth()) return;
        const confirmed = confirm('Delete this QR?');
        if (!confirmed) return;
        try {
          await authorizedFetch(`/api/qr/${id}`, { method: 'DELETE' });
          toast('QR deleted');
          await loadHistory();
        } catch (err) {
          if (err.message !== 'Unauthorized') {
            console.error(err);
            toast('Unable to delete QR');
          }
        }
      } else if (action === 'png' || action === 'svg') {
        if (!requireAuth()) return;
        downloadAsset(item, action);
      }
    });
  });
}

function updateHistoryUI(items) {
  historyCache = new Map(items.map((entry) => [String(entry.id), entry]));
  const hasItems = items.length > 0;
  historyTargets.empty?.classList.toggle('hidden', hasItems);
  function setThumb(img, item) {
    fetchAssetBlob(item.id, 'png').then(blob => {
      const url = URL.createObjectURL(blob);
      img.src = url;
    }).catch(() => {
      img.alt = 'Preview unavailable';
    });
  }
  function renderHistory(container, items) {
    container.innerHTML = hasItems ? items.map(historyCardTemplate).join('') : '';
    container.querySelectorAll('img[data-id]').forEach(img => {
      const id = img.getAttribute('data-id');
      const item = historyCache.get(id);
      if (item) setThumb(img, item);
    });
    bindHistoryActions(container);
  }
  if (historyTargets.page) {
    historyTargets.page.classList.toggle('empty', !hasItems);
    renderHistory(historyTargets.page, items);
  }
  if (historyTargets.drawer) {
    if (hasItems) {
      renderHistory(historyTargets.drawer, items.slice(0, 8));
    } else {
      historyTargets.drawer.innerHTML = '<div class="history-empty">No QR codes yet. Generate a new one to see it here.</div>';
    }
  }
}

async function loadHistory() {
  const authed = isAuthed();
  historyTargets.guard?.classList.toggle('hidden', authed);
  historyTargets.content?.classList.toggle('hidden', !authed);
  if (!authed) {
    if (historyTargets.drawer) {
      historyTargets.drawer.innerHTML = '<div class="history-empty">Login to see your saved QR codes.</div>';
    }
    historyCache.clear();
    return [];
  }
  try {
    const res = await authorizedFetch('/api/qr/history');
    if (!res.ok) throw new Error('Failed to load history');
    const items = await res.json();
    updateHistoryUI(items);
    return items;
  } catch (err) {
    if (err.message !== 'Unauthorized') {
      console.error(err);
      toast('Unable to load history');
    }
    return [];
  }
}

async function downloadCsv() {
  if (!requireAuth()) return;
  try {
    const res = await authorizedFetch('/api/export/csv');
    if (!res.ok) throw new Error('Failed to export history');
    const blob = await res.blob();
    triggerDownload(blob, 'qr-history.csv');
    toast('History exported');
  } catch (err) {
    if (err.message !== 'Unauthorized') {
      console.error(err);
      toast('Unable to export history');
    }
  }
}

async function downloadAsset(item, format) {
  try {
    const res = await authorizedFetch(`/api/qr/${item.id}/download?format=${format}`);
    if (!res.ok) throw new Error('Download failed');
    const blob = await res.blob();
    triggerDownload(blob, sanitizeFilename(item.title, format));
  } catch (err) {
    if (err.message !== 'Unauthorized') {
      console.error(err);
      toast('Unable to download file');
    }
  }
}

async function fetchAssetBlob(id, format) {
  const res = await authorizedFetch(`/api/qr/${id}/download?format=${format}`);
  if (!res.ok) throw new Error('Download failed');
  return res.blob();
}

function initHistory() {
  document.getElementById('refreshHistory')?.addEventListener('click', () => loadHistory());
  document.getElementById('exportCsv')?.addEventListener('click', () => downloadCsv());
  if (historyTargets.drawer || historyTargets.page || historyTargets.guard) {
    loadHistory();
    document.addEventListener('auth-change', () => loadHistory());
  }
}

function payloadFromForm(form) {
  const transparent = form.querySelector('#bgTransparent')?.checked;
  return {
    title: (form.querySelector('#title')?.value || '').trim(),
    url: form.querySelector('#url')?.value?.trim(),
    foreground_color: form.querySelector('#fgColor')?.value || '#000000',
    background_color: transparent ? 'transparent' : form.querySelector('#bgColor')?.value || '#ffffff',
    size: Number(form.querySelector('#sizeRange')?.value || 512),
    padding: Number(form.querySelector('#paddingRange')?.value || 16),
    border_radius: Number(form.querySelector('#radiusRange')?.value || 0),
  };
}

function payloadsMatch(a, b) {
  if (!a || !b) return false;
  return (
    a.title === b.title &&
    a.url === b.url &&
    a.foreground_color === b.foreground_color &&
    a.background_color === b.background_color &&
    a.size === b.size &&
    a.padding === b.padding &&
    a.border_radius === b.border_radius
  );
}

function initGenerator() {
  if (!body.classList.contains('page-generator')) return;

  const guard = document.getElementById('generatorGuard');
  const generatorNodes = document.querySelectorAll('[data-generator-auth]');
  const form = document.getElementById('qr-form');
  const qrBox = document.getElementById('qrBox');
  const previewImg = document.getElementById('qrPreview');
  const previewEmpty = document.getElementById('qrEmpty');
  const fgColor = document.getElementById('fgColor');
  const bgColor = document.getElementById('bgColor');
  const bgTransparent = document.getElementById('bgTransparent');
  const sizeRange = document.getElementById('sizeRange');
  const paddingRange = document.getElementById('paddingRange');
  const radiusRange = document.getElementById('radiusRange');
  const urlInput = document.getElementById('url');
  const sizeValue = document.getElementById('sizeValue');
  const paddingValue = document.getElementById('paddingValue');
  const previewBtn = document.getElementById('previewBtn');
  const saveBtn = document.getElementById('saveQr');
  const dlSvg = document.getElementById('dlSvg');
  const dlPng = document.getElementById('dlPng');
  const openHistoryBtn = document.getElementById('openHistory');
  const closeHistoryBtn = document.getElementById('closeHistory');
  const historyDrawer = document.getElementById('historyDrawer');

  const formElements = form ? Array.from(form.querySelectorAll('input, button')) : [];
  const controlInputs = [fgColor, bgColor, bgTransparent, sizeRange, paddingRange, radiusRange, urlInput];

  let lastPreview = null;
  let lastSaved = null;
  let previewDebounce = null;

  function setGeneratorAuthState(authed) {
    guard?.classList.toggle('hidden', authed);
    generatorNodes.forEach((node) => node.classList.toggle('hidden', !authed));
    formElements.forEach((el) => (el.disabled = !authed));
    controlInputs.forEach((el) => {
      if (el) el.disabled = !authed;
    });
    saveBtn.disabled = !authed;
    if (!authed) {
      historyDrawer?.classList.remove('open');
      lastPreview = null;
      lastSaved = null;
      previewImg?.setAttribute('style', 'display:none');
      previewImg?.removeAttribute('src');
      previewEmpty?.classList.remove('hidden');
      if (qrBox) {
        qrBox.style.backgroundColor = 'transparent';
        qrBox.style.borderRadius = '20px';
      }
    }
  }

  function applyControlLabels() {
    if (sizeValue && sizeRange) sizeValue.textContent = `${sizeRange.value} px`;
    if (paddingValue && paddingRange) paddingValue.textContent = `${paddingRange.value} px`;
  }

  function applyPreviewStyles(payload) {
    if (!qrBox || !previewImg) return;
    const bg = payload.background_color === 'transparent' ? 'transparent' : payload.background_color;
    qrBox.style.backgroundColor = bg;
    qrBox.style.borderRadius = `${payload.border_radius}px`;
    previewImg.style.borderRadius = `${Math.max(payload.border_radius - 4, 0)}px`;
    previewImg.style.padding = '0';
  }

  function setPreviewFromBase64(pngData, payload) {
    if (!pngData || !previewImg) return;
    const dataUrl = `data:image/png;base64,${pngData}`;
    previewImg.src = dataUrl;
    previewImg.style.display = 'block';
    previewEmpty?.classList.add('hidden');
    applyPreviewStyles(payload);
  }

  async function requestPreview(payload) {
    if (!isAuthed()) return null;
    if (!payload.url) return null;
    try {
      new URL(payload.url);
    } catch (err) {
      return null;
    }
    const res = await authorizedFetch('/api/qr/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function handlePreview(payload) {
    try {
      const preview = await requestPreview(payload);
      if (!preview) return;
      setPreviewFromBase64(preview.png_data, payload);
      lastPreview = {
        payload,
        pngData: preview.png_data,
        svg: preview.svg_data,
      };
      if (!lastSaved || !payloadsMatch(lastSaved.payload, payload)) {
        lastSaved = null;
      }
      saveBtn.disabled = false;
    } catch (err) {
      if (err.message !== 'Unauthorized') {
        console.error(err);
        toast('Unable to preview QR');
      }
    }
  }

  function schedulePreview(payload) {
    if (!isAuthed()) return;
    if (previewDebounce) clearTimeout(previewDebounce);
    previewDebounce = setTimeout(() => {
      handlePreview(payload);
    }, 250);
  }

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!requireAuth() || !form) return;
    const payload = payloadFromForm(form);
    if (!payload.url) {
      toast('Please enter a valid URL');
      return;
    }
    previewBtn.disabled = true;
    handlePreview(payload).finally(() => {
      previewBtn.disabled = false;
    });
  });

  saveBtn?.addEventListener('click', async () => {
    if (!lastPreview || !requireAuth()) return;
    saveBtn.disabled = true;
    try {
      const res = await authorizedFetch('/api/qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lastPreview.payload),
      });
      if (!res.ok) throw new Error(await res.text());
      const item = await res.json();
      lastSaved = { payload: lastPreview.payload, item };
      toast('QR saved to history');
      loadHistory();
    } catch (err) {
      if (err.message !== 'Unauthorized') {
        console.error(err);
        toast('Unable to save QR');
      }
    } finally {
      saveBtn.disabled = false;
    }
  });

  [fgColor, bgColor, bgTransparent, sizeRange, paddingRange, radiusRange, urlInput].forEach((input) => {
    input?.addEventListener('input', () => {
      applyControlLabels();
      if (!form) return;
      if (input === bgTransparent && bgTransparent.checked) {
        bgColor.disabled = true;
      } else if (input === bgTransparent && !bgTransparent.checked) {
        bgColor.disabled = false;
      }
      const payload = payloadFromForm(form);
      if (!payload.url) return;
      schedulePreview(payload);
    });
  });

  if (bgTransparent?.checked) {
    bgColor.disabled = true;
  }

  dlSvg?.addEventListener('click', () => {
    if (!lastPreview) {
      toast('Preview a QR code first');
      return;
    }
    if (lastSaved && payloadsMatch(lastSaved.payload, lastPreview.payload)) {
      if (!requireAuth()) return;
      downloadAsset(lastSaved.item, 'svg');
      return;
    }
    const blob = new Blob([lastPreview.svg], { type: 'image/svg+xml' });
    triggerDownload(blob, sanitizeFilename(lastPreview.payload.title, 'svg'));
  });

  dlPng?.addEventListener('click', () => {
    if (!lastPreview) {
      toast('Preview a QR code first');
      return;
    }
    if (lastSaved && payloadsMatch(lastSaved.payload, lastPreview.payload)) {
      if (!requireAuth()) return;
      downloadAsset(lastSaved.item, 'png');
      return;
    }
    const blob = base64ToBlob(lastPreview.pngData, 'image/png');
    triggerDownload(blob, sanitizeFilename(lastPreview.payload.title, 'png'));
  });

  openHistoryBtn?.addEventListener('click', () => {
    if (!requireAuth()) return;
    historyDrawer?.classList.add('open');
    loadHistory();
  });
  closeHistoryBtn?.addEventListener('click', () => historyDrawer?.classList.remove('open'));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') historyDrawer?.classList.remove('open');
  });

  applyControlLabels();
  setGeneratorAuthState(isAuthed());
  document.addEventListener('auth-change', (event) => {
    setGeneratorAuthState(Boolean(event.detail?.authed));
  });
}

function initAuthForms() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fd = new FormData(loginForm);
      const payload = { email: fd.get('email'), password: fd.get('password') };
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          let message = 'Unable to login';
          try {
            const error = await res.json();
            message = error.detail || message;
          } catch (err) {
            message = await res.text() || message;
          }
          toast(message);
          return;
        }
        const data = await res.json();
        setToken(data.access_token);
        toast('Welcome back!');
        window.location.href = '/generator';
      } catch (err) {
        console.error(err);
        toast('Unable to login');
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const fd = new FormData(signupForm);
      const payload = {
        full_name: fd.get('full_name'),
        email: fd.get('email'),
        password: fd.get('password'),
      };
      const submitBtn = signupForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
      try {
        const res = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          let message = 'Unable to sign up';
          try {
            const error = await res.json();
            message = error.detail || message;
          } catch (err) {
            message = await res.text() || message;
          }
          toast(message);
          return;
        }
        toast('Account created!');
        const loginRes = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: payload.email, password: payload.password }),
        });
        if (!loginRes.ok) {
          toast('Account created. Please login.');
          window.location.href = '/login';
          return;
        }
        const data = await loginRes.json();
        setToken(data.access_token);
        toast('Welcome to QR Forge!');
        window.location.href = '/generator';
      } catch (err) {
        console.error(err);
        toast('Unable to sign up');
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }
}

function initProfile() {
  const nameEl = document.getElementById('profileName');
  if (!nameEl) return;
  const emailEl = document.getElementById('profileEmail');
  const sinceEl = document.getElementById('profileSince');
  const guard = document.getElementById('profileGuard');
  const content = document.getElementById('profileContent');
  const logoutBtn = document.getElementById('logoutBtn');
  const passwordForm = document.getElementById('passwordForm');
  const editProfileBtn = document.getElementById('editProfile');
  const deleteAccountBtn = document.getElementById('deleteAccount');

  async function syncProfile() {
    if (!isAuthed()) {
      guard?.classList.remove('hidden');
      content?.classList.add('hidden');
      return;
    }
    guard?.classList.add('hidden');
    content?.classList.remove('hidden');
    try {
      const res = await authorizedFetch('/api/user/me');
      if (!res.ok) throw new Error('Failed to load profile');
      const user = await res.json();
      nameEl.textContent = user.full_name || '—';
      emailEl.textContent = user.email || '—';
      sinceEl.textContent = formatDate(user.created_at);
    } catch (err) {
      if (err.message !== 'Unauthorized') {
        console.error(err);
        toast('Unable to load profile');
      }
    }
  }

  logoutBtn?.addEventListener('click', async () => {
    if (!requireAuth()) return;
    try {
      await authorizedFetch('/api/auth/logout', { method: 'POST' });
    } catch (err) {
      if (err.message !== 'Unauthorized') console.warn(err);
    } finally {
      setToken(null);
      toast('Logged out');
      window.location.href = '/login';
    }
  });

  deleteAccountBtn?.addEventListener('click', async () => {
    if (!requireAuth()) return;
    const confirmed = confirm('Delete your account and all saved QR codes? This cannot be undone.');
    if (!confirmed) return;
    try {
      const res = await authorizedFetch('/api/user/me', { method: 'DELETE' });
      if (!res.ok) throw new Error(await res.text());
      setToken(null);
      toast('Account deleted');
      window.location.href = '/signup';
    } catch (err) {
      if (err.message !== 'Unauthorized') {
        console.error(err);
        toast('Unable to delete account');
      }
    }
  });

  passwordForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    toast('Password updates are coming soon.');
  });

  editProfileBtn?.addEventListener('click', () => {
    toast('Profile editing will be available in the next update.');
  });

  syncProfile();
  document.addEventListener('auth-change', () => syncProfile());
}

initAuthForms();
initProfile();
initHistory();
initGenerator();
