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
  setTimeout(() => {
    toastEl.classList.remove('show');
  }, duration);
}

function isAuthed() {
  return Boolean(authState.token);
}

function updateAuthStateUI() {
  const authed = isAuthed();
  if (body) {
    body.classList.toggle('authed', authed);
  }
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
  if (authState.token) {
    setToken(null);
  }
  if (!unauthorizedNoticeShown) {
    unauthorizedNoticeShown = true;
    toast('Please log in to continue');
    setTimeout(() => {
      unauthorizedNoticeShown = false;
    }, 2500);
    setTimeout(() => {
      window.location.href = '/login';
    }, 500);
  }
  throw new Error('Unauthorized');
}

function authorizedFetch(url, options = {}) {
  if (!authState.token) {
    throw new Error('Unauthorized');
  }
  const opts = { ...options };
  const headers = new Headers(options.headers || {});
  headers.set('Authorization', `Bearer ${authState.token}`);
  opts.headers = headers;
  return fetch(url, opts).then((res) => {
    if (res.status === 401) {
      handleUnauthorized();
    }
    return res;
  });
}

function requireAuth() {
  if (isAuthed()) return true;
  toast('Please log in to continue');
  setTimeout(() => {
    window.location.href = '/login';
  }, 500);
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

const historyTargets = {
  drawer: document.getElementById('historyList'),
  page: document.getElementById('historyGrid'),
  empty: document.getElementById('historyEmpty'),
  guard: document.getElementById('historyGuard'),
  content: document.getElementById('historyContent'),
};

let historyCache = new Map();
const thumbnailCache = new Map();

function clearThumbnailCache() {
  thumbnailCache.forEach((url) => URL.revokeObjectURL(url));
  thumbnailCache.clear();
}

function historyCardTemplate(item) {
  const created = formatDate(item.created_at);
  const title = escapeHtml(item.title || 'Untitled QR');
  return `
    <article class="history-card" data-id="${item.id}" data-title="${title}">
      <img data-thumb-id="${item.id}" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==" alt="Preview for ${title}" loading="lazy" />
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
      const parent = btn.closest('.history-card');
      const itemId = parent?.dataset.id || id;
      const item = historyCache.get(itemId) || { id: itemId, title: parent?.dataset.title || 'qr-code' };
      if (action === 'delete') {
        if (!requireAuth()) return;
        const confirmed = confirm('Delete this QR?');
        if (!confirmed) return;
        try {
          await authorizedFetch(`/api/qr/${itemId}`, { method: 'DELETE' });
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

function renderThumbnails(container) {
  if (!container) return;
  container.querySelectorAll('[data-thumb-id]').forEach((img) => {
    const id = img.dataset.thumbId;
    if (!id) return;
    resolveThumbnail(id)
      .then((url) => {
        if (url) {
          img.src = url;
        }
      })
      .catch((err) => {
        if (err.message !== 'Unauthorized') {
          console.error(err);
        }
      });
  });
}

async function resolveThumbnail(id) {
  if (!thumbnailCache.has(id)) {
    const blob = await fetchAssetBlob(id, 'png');
    const url = URL.createObjectURL(blob);
    thumbnailCache.set(id, url);
  }
  return thumbnailCache.get(id);
}

function updateHistoryUI(items) {
  historyCache = new Map(items.map((entry) => [String(entry.id), entry]));
  clearThumbnailCache();
  const hasItems = items.length > 0;
  if (historyTargets.empty) {
    historyTargets.empty.classList.toggle('hidden', hasItems);
  }
  if (historyTargets.page) {
    historyTargets.page.classList.toggle('empty', !hasItems);
    historyTargets.page.innerHTML = hasItems ? items.map(historyCardTemplate).join('') : '';
    bindHistoryActions(historyTargets.page);
    renderThumbnails(historyTargets.page);
  }
  if (historyTargets.drawer) {
    if (!hasItems) {
      historyTargets.drawer.innerHTML = '<div class="history-empty">No QR codes yet. Generate a new one to see it here.</div>';
    } else {
      const sample = items.slice(0, 8).map(historyCardTemplate).join('');
      historyTargets.drawer.innerHTML = sample;
      bindHistoryActions(historyTargets.drawer);
      renderThumbnails(historyTargets.drawer);
    }
  }
}

async function loadHistory() {
  const authed = isAuthed();
  if (historyTargets.guard) {
    historyTargets.guard.classList.toggle('hidden', authed);
  }
  if (historyTargets.content) {
    historyTargets.content.classList.toggle('hidden', !authed);
  }
  if (!authed) {
    if (historyTargets.drawer) {
      historyTargets.drawer.innerHTML = '<div class="history-empty">Login to see your saved QR codes.</div>';
    }
    historyCache.clear();
    clearThumbnailCache();
    return [];
  }
  try {
    const res = await authorizedFetch('/api/qr/history');
    if (!res.ok) {
      throw new Error('Failed to load history');
    }
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
    if (!res.ok) {
      throw new Error('Failed to export history');
    }
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
    if (!res.ok) {
      throw new Error('Download failed');
    }
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
  if (!res.ok) {
    throw new Error('Download failed');
  }
  return await res.blob();
}

function initHistory() {
  const refreshBtn = document.getElementById('refreshHistory');
  refreshBtn?.addEventListener('click', () => loadHistory());
  const exportBtn = document.getElementById('exportCsv');
  exportBtn?.addEventListener('click', () => downloadCsv());

  if (historyTargets.drawer || historyTargets.page || historyTargets.guard) {
    loadHistory();
    document.addEventListener('auth-change', () => loadHistory());
  }
}

function initGenerator() {
  if (!body.classList.contains('page-generator')) return;

  const guard = document.getElementById('generatorGuard');
  const generatorNodes = document.querySelectorAll('[data-generator-auth]');
  const form = document.getElementById('qr-form');
  const editInputs = document.getElementById('editInputs');
  const fgColor = document.getElementById('fgColor');
  const bgColor = document.getElementById('bgColor');
  const sizeRange = document.getElementById('sizeRange');
  const paddingRange = document.getElementById('paddingRange');
  const radiusRange = document.getElementById('radiusRange');
  const overlayInput = document.getElementById('overlayText');
  const overlayToggle = document.getElementById('toggleOverlay');
  const overlayEl = document.getElementById('qrOverlay');
  const previewBox = document.getElementById('qrBox');
  const previewImg = document.getElementById('qrPreview');
  const previewEmpty = document.getElementById('qrEmpty');
  const sizeValue = document.getElementById('sizeValue');
  const paddingValue = document.getElementById('paddingValue');
  const dlSvg = document.getElementById('dlSvg');
  const dlPng = document.getElementById('dlPng');
  const openHistoryBtn = document.getElementById('openHistory');
  const closeHistoryBtn = document.getElementById('closeHistory');
  const historyDrawer = document.getElementById('historyDrawer');

  const formElements = form ? Array.from(form.querySelectorAll('input, button')) : [];
  const controlInputs = [fgColor, bgColor, sizeRange, paddingRange, radiusRange, overlayInput, overlayToggle, dlSvg, dlPng, openHistoryBtn, editInputs];

  let overlayVisible = false;
  let currentItem = null;
  let previewObjectUrl = null;

  function setOverlayVisibility(visible) {
    overlayVisible = visible;
    if (overlayEl) {
      overlayEl.classList.toggle('hidden', !visible);
      if (visible) {
        overlayEl.textContent = overlayInput?.value?.trim() || 'QR';
        overlayEl.style.color = fgColor?.value || '#0a0a0a';
      }
    }
    if (overlayToggle) {
      overlayToggle.textContent = visible ? 'Hide' : 'Show';
    }
  }

  function applyControlStyles() {
    if (!isAuthed()) return;
    if (previewBox) {
      previewBox.style.backgroundColor = bgColor?.value || '#ffffff';
      previewBox.style.padding = `${paddingRange?.value || 16}px`;
      previewBox.style.borderRadius = `${radiusRange?.value || 0}px`;
    }
    if (previewImg && sizeRange) {
      const numeric = Number(sizeRange.value) || 512;
      const previewSize = Math.max(140, Math.min(320, Math.round(numeric / 1.6)));
      previewImg.style.width = `${previewSize}px`;
      previewImg.style.height = `${previewSize}px`;
    }
    if (sizeValue && sizeRange) {
      sizeValue.textContent = `${sizeRange.value} px`;
    }
    if (paddingValue && paddingRange) {
      paddingValue.textContent = `${paddingRange.value} px`;
    }
    if (overlayVisible && overlayEl) {
      overlayEl.textContent = overlayInput?.value?.trim() || 'QR';
      overlayEl.style.color = fgColor?.value || '#0a0a0a';
    }
  }

  function resetPreview() {
    currentItem = null;
    if (previewObjectUrl) {
      URL.revokeObjectURL(previewObjectUrl);
      previewObjectUrl = null;
    }
    if (previewImg) {
      previewImg.removeAttribute('src');
      previewImg.style.display = 'none';
    }
    previewEmpty?.classList.remove('hidden');
    setOverlayVisibility(false);
  }

  function setGeneratorAuthState(authed) {
    guard?.classList.toggle('hidden', authed);
    generatorNodes.forEach((node) => node.classList.toggle('hidden', !authed));
    formElements.forEach((el) => {
      el.disabled = !authed;
    });
    controlInputs.forEach((el) => {
      if (el) el.disabled = !authed;
    });
    if (!authed) {
      historyDrawer?.classList.remove('open');
      resetPreview();
    } else {
      applyControlStyles();
      loadHistory();
    }
  }

  [fgColor, bgColor, sizeRange, paddingRange, radiusRange].forEach((input) => {
    input?.addEventListener('input', () => applyControlStyles());
  });

  overlayInput?.addEventListener('input', () => {
    if (!overlayVisible || !overlayEl) return;
    overlayEl.textContent = overlayInput.value.trim() || 'QR';
  });

  overlayToggle?.addEventListener('click', () => {
    setOverlayVisibility(!overlayVisible);
  });

  openHistoryBtn?.addEventListener('click', () => {
    if (!requireAuth()) return;
    historyDrawer?.classList.add('open');
    loadHistory();
  });

  closeHistoryBtn?.addEventListener('click', () => {
    historyDrawer?.classList.remove('open');
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      historyDrawer?.classList.remove('open');
    }
  });

  dlSvg?.addEventListener('click', () => {
    if (!currentItem) {
      toast('Generate a QR code first');
      return;
    }
    if (!requireAuth()) return;
    downloadAsset(currentItem, 'svg');
  });

  dlPng?.addEventListener('click', () => {
    if (!currentItem) {
      toast('Generate a QR code first');
      return;
    }
    if (!requireAuth()) return;
    downloadAsset(currentItem, 'png');
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!requireAuth() || !form) return;
    const fd = new FormData(form);
    const payload = {
      title: (fd.get('title') || '').toString(),
      url: fd.get('url'),
      foreground_color: fgColor?.value || '#000000',
      background_color: bgColor?.value || '#ffffff',
      size: Number(sizeRange?.value || 512),
      padding: Number(paddingRange?.value || 16),
      border_radius: Number(radiusRange?.value || 0),
      overlay_text: overlayVisible ? (overlayInput?.value?.trim() || null) : null,
    };
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    try {
      const res = await authorizedFetch('/api/qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const item = await res.json();
      currentItem = item;
      const pngBlob = await fetchAssetBlob(item.id, 'png');
      if (previewObjectUrl) {
        URL.revokeObjectURL(previewObjectUrl);
      }
      previewObjectUrl = URL.createObjectURL(pngBlob);
      if (previewImg) {
        previewImg.src = previewObjectUrl;
        previewImg.style.display = 'block';
      }
      previewEmpty?.classList.add('hidden');
      setOverlayVisibility(false);
      toast('QR created');
      form.reset();
      applyControlStyles();
      loadHistory();
    } catch (err) {
      if (err.message !== 'Unauthorized') {
        console.error(err);
        toast('Unable to create QR');
      }
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  resetPreview();
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
      const payload = {
        email: fd.get('email'),
        password: fd.get('password'),
      };
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
      if (!res.ok) {
        throw new Error('Failed to load profile');
      }
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
      if (err.message !== 'Unauthorized') {
        console.warn(err);
      }
    } finally {
      setToken(null);
      toast('Logged out');
      window.location.href = '/login';
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
