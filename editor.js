(() => {
  'use strict';

  const EDITS_URL = 'data/site-edits.json';
  const CONFIG_URL = 'data/editor-config.json';
  const DEFAULT_REPOSITORY = 'micminemx/arthratan-mythology-site';
  const DEFAULT_BRANCH = 'main';
  const KDF_ITERATIONS = 600000;
  const DEVICE_DB = 'arthratan-wiki-device';
  const DEVICE_STORE = 'credentials';
  const DEVICE_RECORD = 'editor-access';
  const ALLOWED_INLINE = new Set(['B', 'STRONG', 'EM', 'I', 'BR', 'SUP', 'SUB', 'CODE']);
  const EDIT_SELECTORS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'pre', 'td', 'summary',
    '.eyebrow', '.micro', '.canon-badge', '.quote', '.filetype', '.formula',
    '.node > strong', '.node > span', '.stat > b', '.stat > span',
    '.art-caption > b', '.art-caption > span', '.rung > b', '.rung > small',
    '.seal > .num', '.operator > .symbol', '.operator > b', '.source-note',
    '.warning', '.cell', '.arrow', '.pill', '.bar > span', '.art-action > span',
    '.archive-link', '.toc-tree button'
  ];
  const EDIT_SELECTOR = EDIT_SELECTORS.map(selector => `#main ${selector}`).join(',');

  let editorConfig = null;
  let siteEdits = emptyEdits();
  let token = '';
  let editorName = localStorage.getItem('arthratanEditorName') || sessionStorage.getItem('arthratanEditorName') || '';
  let deviceRemembered = false;
  let editing = false;
  let dirty = false;
  let saving = false;
  let baselinePage = {};
  let baselineChrome = {};
  let loadedPageSlots = {};
  let loadedChromeSlots = {};
  let observer = null;
  let hydrateQueued = false;

  function emptyEdits() {
    return {version: 1, revision: 0, updatedAt: null, updatedBy: null, pages: {}, chrome: {slots: {}, updatedAt: null, updatedBy: null}};
  }

  function routeKey() {
    return (location.hash || '#home').slice(1) || 'home';
  }

  function cacheBust(url) {
    return `${url}${url.includes('?') ? '&' : '?'}v=${Date.now()}`;
  }

  async function fetchJson(url, fallback) {
    try {
      const response = await fetch(cacheBust(url), {cache: 'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn(`Unable to load ${url}`, error);
      return fallback;
    }
  }

  function safeInlineHtml(html) {
    const template = document.createElement('template');
    template.innerHTML = String(html ?? '');
    [...template.content.querySelectorAll('*')].forEach(element => {
      if (!ALLOWED_INLINE.has(element.tagName)) {
        element.replaceWith(...element.childNodes);
        return;
      }
      [...element.attributes].forEach(attribute => element.removeAttribute(attribute.name));
    });
    return template.innerHTML;
  }

  function pageNodes() {
    return [...document.querySelectorAll(EDIT_SELECTOR)]
      .filter(node => !node.closest('#searchResults'));
  }

  function chromeNodes() {
    return [
      ['brand-title', document.querySelector('.brand strong')],
      ['brand-subtitle', document.querySelector('.brand small')],
      ...[...document.querySelectorAll('#nav .nav-label')].map((node, index) => [`nav-group-${index}`, node]),
      ...[...document.querySelectorAll('#nav a[data-route] span')].map(node => [`nav-${node.closest('a').dataset.route}`, node]),
      ['sidebar-status', document.querySelector('.sidebar-foot span:last-child')],
      ...[...document.querySelectorAll('footer span')].map((node, index) => [`footer-${index}`, node])
    ].filter(([, node]) => node);
  }

  function annotate() {
    pageNodes().forEach((node, index) => {
      node.dataset.editSlot = `${index}:${node.tagName.toLowerCase()}`;
    });
    chromeNodes().forEach(([key, node]) => {
      node.dataset.chromeSlot = key;
    });
  }

  function applyEdits() {
    annotate();
    if (editing) return;
    const page = siteEdits.pages?.[routeKey()]?.slots || {};
    pageNodes().forEach(node => {
      const value = page[node.dataset.editSlot];
      if (typeof value === 'string' && node.innerHTML !== value) node.innerHTML = safeInlineHtml(value);
    });
    const chrome = siteEdits.chrome?.slots || {};
    chromeNodes().forEach(([key, node]) => {
      const value = chrome[key];
      if (typeof value === 'string' && node.innerHTML !== value) node.innerHTML = safeInlineHtml(value);
    });
    const title = document.querySelector('#main h1');
    if (title) document.title = `${title.textContent.trim()} · The Arthitean Codex`;
  }

  function queueHydrate() {
    if (hydrateQueued) return;
    hydrateQueued = true;
    requestAnimationFrame(() => {
      hydrateQueued = false;
      applyEdits();
    });
  }

  function snapshotPage() {
    annotate();
    return Object.fromEntries(pageNodes().map(node => [node.dataset.editSlot, safeInlineHtml(node.innerHTML)]));
  }

  function snapshotChrome() {
    annotate();
    return Object.fromEntries(chromeNodes().map(([key, node]) => [key, safeInlineHtml(node.innerHTML)]));
  }

  function changedSlots(before, after) {
    return Object.fromEntries(Object.entries(after).filter(([key, value]) => before[key] !== value));
  }

  function setEditable(enabled) {
    annotate();
    [...pageNodes(), ...chromeNodes().map(([, node]) => node)].forEach(node => {
      if (enabled) {
        node.setAttribute('contenteditable', 'true');
        node.setAttribute('spellcheck', 'true');
      } else {
        node.removeAttribute('contenteditable');
        node.removeAttribute('spellcheck');
      }
    });
  }

  function startEditing() {
    applyEdits();
    editing = true;
    dirty = false;
    baselinePage = snapshotPage();
    baselineChrome = snapshotChrome();
    loadedPageSlots = {...(siteEdits.pages?.[routeKey()]?.slots || {})};
    loadedChromeSlots = {...(siteEdits.chrome?.slots || {})};
    setEditable(true);
    document.body.classList.add('wiki-editing');
    document.getElementById('wikiToolbar').hidden = false;
    updateToolbar('Editing this page', 'Select any highlighted text and type.');
  }

  function stopEditing({restore = false} = {}) {
    if (restore) {
      const currentPage = siteEdits.pages?.[routeKey()]?.slots || {};
      pageNodes().forEach(node => {
        const key = node.dataset.editSlot;
        const value = currentPage[key] ?? baselinePage[key];
        if (typeof value === 'string') node.innerHTML = safeInlineHtml(value);
      });
      const currentChrome = siteEdits.chrome?.slots || {};
      chromeNodes().forEach(([key, node]) => {
        const value = currentChrome[key] ?? baselineChrome[key];
        if (typeof value === 'string') node.innerHTML = safeInlineHtml(value);
      });
    }
    editing = false;
    dirty = false;
    setEditable(false);
    document.body.classList.remove('wiki-editing');
    document.getElementById('wikiToolbar').hidden = true;
    applyEdits();
  }

  function updateToolbar(title, detail) {
    const toolbar = document.getElementById('wikiToolbar');
    toolbar.querySelector('b').textContent = title;
    toolbar.querySelector('span').textContent = detail;
  }

  function markDirty() {
    if (!editing || saving) return;
    dirty = true;
    updateToolbar('Unsaved changes', 'Save and publish when this page is ready.');
  }

  function bytesToBase64(bytes) {
    let binary = '';
    for (let i = 0; i < bytes.length; i += 0x8000) {
      binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    }
    return btoa(binary);
  }

  function base64ToBytes(value) {
    const binary = atob(value);
    return Uint8Array.from(binary, character => character.charCodeAt(0));
  }

  function utf8ToBase64(value) {
    return bytesToBase64(new TextEncoder().encode(value));
  }

  function base64ToUtf8(value) {
    return new TextDecoder().decode(base64ToBytes(value.replace(/\n/g, '')));
  }

  function cryptoContext(config) {
    return new TextEncoder().encode(`arthratan-editor:v1:${config.repository}:${config.branch}`);
  }

  function deviceContext(config = editorConfig) {
    return new TextEncoder().encode(`arthratan-device:v1:${config.repository}:${config.branch}:${config.cipher?.data || 'unconfigured'}`);
  }

  function openDeviceDb() {
    return new Promise((resolve, reject) => {
      if (!('indexedDB' in window)) return reject(new Error('Remembering this device is not supported by this browser.'));
      const request = indexedDB.open(DEVICE_DB, 1);
      request.onupgradeneeded = () => request.result.createObjectStore(DEVICE_STORE, {keyPath: 'id'});
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function deviceRecord(mode, value) {
    const db = await openDeviceDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(DEVICE_STORE, mode === 'get' ? 'readonly' : 'readwrite');
      const store = transaction.objectStore(DEVICE_STORE);
      const request = mode === 'get' ? store.get(DEVICE_RECORD) : mode === 'delete' ? store.delete(DEVICE_RECORD) : store.put(value);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
      transaction.oncomplete = () => db.close();
    });
  }

  async function rememberDeviceToken(rawToken) {
    const key = await crypto.subtle.generateKey({name: 'AES-GCM', length: 256}, false, ['encrypt', 'decrypt']);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      {name: 'AES-GCM', iv, additionalData: deviceContext()},
      key,
      new TextEncoder().encode(rawToken)
    );
    await deviceRecord('put', {
      id: DEVICE_RECORD,
      key,
      iv: bytesToBase64(iv),
      data: bytesToBase64(new Uint8Array(encrypted)),
      context: bytesToBase64(deviceContext()),
      editorName
    });
    deviceRemembered = true;
  }

  async function recoverDeviceToken() {
    const record = await deviceRecord('get');
    if (!record || record.context !== bytesToBase64(deviceContext())) return '';
    const decrypted = await crypto.subtle.decrypt(
      {name: 'AES-GCM', iv: base64ToBytes(record.iv), additionalData: deviceContext()},
      record.key,
      base64ToBytes(record.data)
    );
    editorName = record.editorName || editorName;
    return new TextDecoder().decode(decrypted);
  }

  async function forgetDeviceToken() {
    try { await deviceRecord('delete'); } catch (error) { console.warn('Unable to forget device access', error); }
    deviceRemembered = false;
  }

  async function detectRememberedDevice() {
    try {
      const record = await deviceRecord('get');
      deviceRemembered = Boolean(record && record.context === bytesToBase64(deviceContext()));
    } catch {
      deviceRemembered = false;
    }
  }

  async function deriveKey(passphrase, salt, iterations) {
    const material = await crypto.subtle.importKey('raw', new TextEncoder().encode(passphrase), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey(
      {name: 'PBKDF2', salt, iterations, hash: 'SHA-256'},
      material,
      {name: 'AES-GCM', length: 256},
      false,
      ['encrypt', 'decrypt']
    );
  }

  async function encryptToken(rawToken, passphrase, baseConfig) {
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(passphrase, salt, KDF_ITERATIONS);
    const encrypted = await crypto.subtle.encrypt(
      {name: 'AES-GCM', iv, additionalData: cryptoContext(baseConfig)},
      key,
      new TextEncoder().encode(rawToken.trim())
    );
    return {
      version: 1,
      configured: true,
      repository: baseConfig.repository,
      branch: baseConfig.branch,
      kdf: {name: 'PBKDF2', hash: 'SHA-256', iterations: KDF_ITERATIONS, salt: bytesToBase64(salt)},
      cipher: {name: 'AES-GCM', iv: bytesToBase64(iv), data: bytesToBase64(new Uint8Array(encrypted))}
    };
  }

  async function decryptToken(passphrase, config) {
    const key = await deriveKey(passphrase, base64ToBytes(config.kdf.salt), config.kdf.iterations);
    const decrypted = await crypto.subtle.decrypt(
      {name: 'AES-GCM', iv: base64ToBytes(config.cipher.iv), additionalData: cryptoContext(config)},
      key,
      base64ToBytes(config.cipher.data)
    );
    return new TextDecoder().decode(decrypted);
  }

  function githubHeaders(rawToken) {
    return {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${rawToken}`,
      'X-GitHub-Api-Version': '2022-11-28'
    };
  }

  function repoParts(config = editorConfig) {
    const [owner, repository] = (config.repository || DEFAULT_REPOSITORY).split('/');
    return {owner, repository, branch: config.branch || DEFAULT_BRANCH};
  }

  async function githubFile(path, rawToken, config = editorConfig) {
    const {owner, repository, branch} = repoParts(config);
    const response = await fetch(`https://api.github.com/repos/${owner}/${repository}/contents/${path}?ref=${encodeURIComponent(branch)}`, {
      headers: githubHeaders(rawToken), cache: 'no-store'
    });
    if (!response.ok) throw new Error(await githubError(response));
    const payload = await response.json();
    return {sha: payload.sha, json: JSON.parse(base64ToUtf8(payload.content))};
  }

  async function githubPut(path, value, sha, message, rawToken, config = editorConfig) {
    const {owner, repository, branch} = repoParts(config);
    const response = await fetch(`https://api.github.com/repos/${owner}/${repository}/contents/${path}`, {
      method: 'PUT',
      headers: {...githubHeaders(rawToken), 'Content-Type': 'application/json'},
      body: JSON.stringify({message, content: utf8ToBase64(`${JSON.stringify(value, null, 2)}\n`), sha, branch})
    });
    if (!response.ok) throw new Error(await githubError(response));
    return response.json();
  }

  async function githubError(response) {
    try {
      const payload = await response.json();
      return payload.message || `GitHub returned ${response.status}`;
    } catch {
      return `GitHub returned ${response.status}`;
    }
  }

  async function verifyRepositoryAccess(rawToken, config) {
    const {owner, repository} = repoParts(config);
    const response = await fetch(`https://api.github.com/repos/${owner}/${repository}`, {headers: githubHeaders(rawToken)});
    if (!response.ok) throw new Error(await githubError(response));
    const repositoryInfo = await response.json();
    if (repositoryInfo.permissions && !repositoryInfo.permissions.push) {
      throw new Error('This token can read the repository but cannot publish changes. Give it Contents: Read and write permission.');
    }
  }

  function slotsConflict(changed, loaded, remote) {
    return Object.keys(changed).some(key => {
      const remoteValue = remote[key];
      const loadedValue = loaded[key];
      return remoteValue !== loadedValue && remoteValue !== changed[key];
    });
  }

  async function savePage() {
    if (saving) return;
    const currentPage = snapshotPage();
    const currentChrome = snapshotChrome();
    const pageChanges = changedSlots(baselinePage, currentPage);
    const chromeChanges = changedSlots(baselineChrome, currentChrome);
    if (!Object.keys(pageChanges).length && !Object.keys(chromeChanges).length) {
      dirty = false;
      updateToolbar('Nothing to publish', 'No text has changed on this page.');
      return;
    }

    saving = true;
    const saveButton = document.getElementById('wikiSave');
    saveButton.disabled = true;
    saveButton.classList.add('wiki-saving');
    updateToolbar('Publishing changes', 'Checking the newest version and creating a revision…');
    try {
      const remoteFile = await githubFile('data/site-edits.json', token);
      const remote = remoteFile.json || emptyEdits();
      const remotePageSlots = remote.pages?.[routeKey()]?.slots || {};
      const remoteChromeSlots = remote.chrome?.slots || {};
      if (slotsConflict(pageChanges, loadedPageSlots, remotePageSlots) || slotsConflict(chromeChanges, loadedChromeSlots, remoteChromeSlots)) {
        throw new Error('Someone changed the same text after this page was opened. Cancel, reload the page, and combine the newest wording before saving.');
      }

      const now = new Date().toISOString();
      const next = {
        ...emptyEdits(),
        ...remote,
        version: 1,
        revision: Number(remote.revision || 0) + 1,
        updatedAt: now,
        updatedBy: editorName,
        pages: {...(remote.pages || {})},
        chrome: {...(remote.chrome || {slots: {}})}
      };
      if (Object.keys(pageChanges).length) {
        next.pages[routeKey()] = {
          ...(remote.pages?.[routeKey()] || {}),
          slots: {...remotePageSlots, ...pageChanges},
          updatedAt: now,
          updatedBy: editorName
        };
      }
      if (Object.keys(chromeChanges).length) {
        next.chrome = {slots: {...remoteChromeSlots, ...chromeChanges}, updatedAt: now, updatedBy: editorName};
      }
      await githubPut('data/site-edits.json', next, remoteFile.sha, `Wiki edit: ${routeKey()} by ${editorName}`, token);
      siteEdits = next;
      baselinePage = currentPage;
      baselineChrome = currentChrome;
      loadedPageSlots = {...(next.pages?.[routeKey()]?.slots || {})};
      loadedChromeSlots = {...(next.chrome?.slots || {})};
      dirty = false;
      updateToolbar('Published successfully', 'The live site normally refreshes within one or two minutes.');
      if (typeof window.toast === 'function') window.toast('Wiki changes published');
      setTimeout(() => stopEditing(), 1500);
    } catch (error) {
      console.error(error);
      updateToolbar('Could not publish', error.message);
    } finally {
      saving = false;
      saveButton.disabled = false;
      saveButton.classList.remove('wiki-saving');
    }
  }

  function buildUi() {
    const editButton = document.createElement('button');
    editButton.id = 'wikiEditButton';
    editButton.className = 'ghost wiki-edit-button';
    editButton.type = 'button';
    editButton.textContent = 'Edit page';
    document.querySelector('.top-actions')?.prepend(editButton);

    const overlay = document.createElement('div');
    overlay.id = 'wikiOverlay';
    overlay.className = 'wiki-overlay';
    overlay.hidden = true;
    overlay.innerHTML = '<section class="wiki-dialog" role="dialog" aria-modal="true" aria-labelledby="wikiDialogTitle"><button class="wiki-dialog-close" type="button" aria-label="Close">×</button><div id="wikiDialogBody"></div></section>';
    document.body.appendChild(overlay);

    const toolbar = document.createElement('div');
    toolbar.id = 'wikiToolbar';
    toolbar.className = 'wiki-toolbar';
    toolbar.hidden = true;
    toolbar.innerHTML = '<div class="wiki-toolbar-status"><b>Editing this page</b><span>Select highlighted text and type.</span></div><button id="wikiCancel" class="wiki-secondary" type="button">Cancel</button><button id="wikiLock" class="wiki-secondary" type="button">Lock & forget</button><button id="wikiSave" class="wiki-primary" type="button">Save & publish</button>';
    document.body.appendChild(toolbar);

    editButton.addEventListener('click', openEditor);
    overlay.querySelector('.wiki-dialog-close').addEventListener('click', closeDialog);
    overlay.addEventListener('click', event => { if (event.target === overlay) closeDialog(); });
    document.getElementById('wikiCancel').addEventListener('click', () => {
      if (!dirty || confirm('Discard the unsaved changes on this page?')) stopEditing({restore: true});
    });
    document.getElementById('wikiLock').addEventListener('click', async () => {
      if (dirty && !confirm('Discard the unsaved changes and lock the editor?')) return;
      stopEditing({restore: true});
      token = '';
      await forgetDeviceToken();
      editButton.classList.remove('is-unlocked');
      editButton.textContent = 'Edit page';
    });
    document.getElementById('wikiSave').addEventListener('click', savePage);

    document.addEventListener('input', event => {
      if (editing && event.target.closest?.('[data-edit-slot],[data-chrome-slot]')) markDirty();
    });
    document.addEventListener('paste', event => {
      if (!editing || !event.target.closest?.('[data-edit-slot],[data-chrome-slot]')) return;
      event.preventDefault();
      document.execCommand('insertText', false, event.clipboardData.getData('text/plain'));
    });
    document.addEventListener('click', event => {
      if (!editing) return;
      if (event.target.closest?.('a,[onclick]') && event.target.closest?.('[data-edit-slot],[data-chrome-slot]')) {
        event.preventDefault();
        event.stopPropagation();
      }
    }, true);
    window.addEventListener('beforeunload', event => {
      if (!dirty) return;
      event.preventDefault();
      event.returnValue = '';
    });
  }

  async function openEditor() {
    if (editing) return;
    if (token) {
      startEditing();
      return;
    }
    if (deviceRemembered && editorConfig?.configured) {
      const editButton = document.getElementById('wikiEditButton');
      editButton.disabled = true;
      editButton.textContent = 'Unlocking…';
      try {
        token = await recoverDeviceToken();
        if (!token) throw new Error('Saved device access is no longer current.');
        await verifyRepositoryAccess(token, editorConfig);
        editButton.classList.add('is-unlocked');
        editButton.textContent = `Edit as ${editorName}`;
        startEditing();
        return;
      } catch (error) {
        console.warn(error);
        token = '';
        await forgetDeviceToken();
      } finally {
        editButton.disabled = false;
        if (!token) editButton.textContent = 'Edit page';
      }
    }
    if (!editorConfig?.configured) showSetup();
    else showUnlock();
  }

  function closeDialog() {
    document.getElementById('wikiOverlay').hidden = true;
    document.getElementById('wikiDialogBody').innerHTML = '';
  }

  function openDialog(html) {
    const overlay = document.getElementById('wikiOverlay');
    document.getElementById('wikiDialogBody').innerHTML = html;
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.querySelector('input')?.focus());
  }

  function showUnlock() {
    openDialog(`
      <h2 id="wikiDialogTitle">Unlock wiki editing</h2>
      <p>Enter your editor name and the shared passphrase. The passphrase stays in this browser tab and is never published.</p>
      <form id="wikiUnlockForm">
        <label class="wiki-field"><span>Editor name</span><input id="wikiEditorName" autocomplete="name" value="${escapeAttribute(editorName)}" required></label>
        <label class="wiki-field"><span>Shared editor passphrase</span><input id="wikiPassphrase" type="password" autocomplete="current-password" required></label>
        <label class="wiki-check"><input id="wikiRememberDevice" type="checkbox" checked><span>Remember this private device<small>Future visits will open editing with one press. Leave this off on a shared phone or computer.</small></span></label>
        <div class="wiki-error" id="wikiFormError" role="alert"></div>
        <div class="wiki-dialog-actions"><button class="wiki-primary" type="submit">Unlock editor</button><button class="wiki-secondary" id="wikiUnlockCancel" type="button">Cancel</button></div>
      </form>`);
    document.getElementById('wikiUnlockCancel').onclick = closeDialog;
    document.getElementById('wikiUnlockForm').onsubmit = async event => {
      event.preventDefault();
      const button = event.submitter;
      const error = document.getElementById('wikiFormError');
      button.disabled = true;
      error.textContent = 'Decrypting editor access…';
      try {
        const name = document.getElementById('wikiEditorName').value.trim();
        const passphrase = document.getElementById('wikiPassphrase').value;
        if (!name) throw new Error('Enter the editor name that should appear in the revision history.');
        token = await decryptToken(passphrase, editorConfig);
        await verifyRepositoryAccess(token, editorConfig);
        editorName = name;
        sessionStorage.setItem('arthratanEditorName', editorName);
        localStorage.setItem('arthratanEditorName', editorName);
        if (document.getElementById('wikiRememberDevice').checked) {
          try { await rememberDeviceToken(token); } catch (rememberError) { console.warn('This browser could not remember editor access', rememberError); }
        }
        document.getElementById('wikiEditButton').classList.add('is-unlocked');
        document.getElementById('wikiEditButton').textContent = `Edit as ${editorName}`;
        closeDialog();
        startEditing();
      } catch (unlockError) {
        token = '';
        error.textContent = unlockError.name === 'OperationError' ? 'That passphrase is incorrect.' : unlockError.message;
      } finally {
        button.disabled = false;
      }
    };
  }

  function escapeAttribute(value) {
    return String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  }

  function randomPassphrase() {
    const bytes = crypto.getRandomValues(new Uint8Array(24));
    return `arth-${bytesToBase64(bytes).replace(/[+/=]/g, '').match(/.{1,6}/g).join('-')}`;
  }

  function showSetup() {
    openDialog(`
      <h2 id="wikiDialogTitle">Set up wiki editing</h2>
      <p>This one-time owner setup encrypts a repository-scoped publishing token with your shared passphrase. No account database is created.</p>
      <div class="wiki-help">
        <b>Create a fine-grained GitHub token:</b>
        <ol>
          <li>Open <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">GitHub’s token page</a>.</li>
          <li>Select only <code>arthratan-mythology-site</code>.</li>
          <li>Set repository permission <code>Contents</code> to <code>Read and write</code>.</li>
          <li>Choose an expiry date, create the token and paste it below.</li>
        </ol>
      </div>
      <form id="wikiSetupForm">
        <label class="wiki-field"><span>Your editor name</span><input id="wikiSetupName" autocomplete="name" value="${escapeAttribute(editorName)}" required></label>
        <label class="wiki-field"><span>Fine-grained GitHub token</span><input id="wikiSetupToken" type="password" autocomplete="off" placeholder="github_pat_…" required></label>
        <div class="wiki-generated">
          <label class="wiki-field"><span>Shared passphrase — minimum 20 characters</span><input id="wikiSetupPass" type="password" autocomplete="new-password" minlength="20" required></label>
          <button class="wiki-secondary" id="wikiGeneratePass" type="button">Generate</button>
        </div>
        <label class="wiki-field"><span>Confirm shared passphrase</span><input id="wikiSetupPassConfirm" type="password" autocomplete="new-password" minlength="20" required></label>
        <label class="wiki-check"><input id="wikiSetupRemember" type="checkbox" checked><span>Remember this private device<small>Future visits will open editing with one press.</small></span></label>
        <div class="wiki-error" id="wikiFormError" role="alert"></div>
        <div class="wiki-dialog-actions"><button class="wiki-primary" type="submit">Encrypt & activate editor</button><button class="wiki-secondary" id="wikiSetupCancel" type="button">Cancel</button></div>
      </form>`);
    document.getElementById('wikiSetupCancel').onclick = closeDialog;
    document.getElementById('wikiGeneratePass').onclick = () => {
      const generated = randomPassphrase();
      const first = document.getElementById('wikiSetupPass');
      const second = document.getElementById('wikiSetupPassConfirm');
      first.type = second.type = 'text';
      first.value = second.value = generated;
      first.focus();
      first.select();
    };
    document.getElementById('wikiSetupForm').onsubmit = async event => {
      event.preventDefault();
      const button = event.submitter;
      const error = document.getElementById('wikiFormError');
      const name = document.getElementById('wikiSetupName').value.trim();
      const rawToken = document.getElementById('wikiSetupToken').value.trim();
      const passphrase = document.getElementById('wikiSetupPass').value;
      const confirmation = document.getElementById('wikiSetupPassConfirm').value;
      button.disabled = true;
      error.textContent = 'Verifying access and encrypting the publishing key…';
      try {
        if (!name) throw new Error('Enter your editor name.');
        if (passphrase.length < 20) throw new Error('Use at least 20 characters for the shared passphrase.');
        if (passphrase !== confirmation) throw new Error('The two passphrases do not match.');
        const baseConfig = {repository: editorConfig?.repository || DEFAULT_REPOSITORY, branch: editorConfig?.branch || DEFAULT_BRANCH};
        await verifyRepositoryAccess(rawToken, baseConfig);
        const currentConfigFile = await githubFile('data/editor-config.json', rawToken, baseConfig);
        const encryptedConfig = await encryptToken(rawToken, passphrase, baseConfig);
        await githubPut('data/editor-config.json', encryptedConfig, currentConfigFile.sha, 'Activate encrypted wiki editor', rawToken, baseConfig);
        editorConfig = encryptedConfig;
        token = rawToken;
        editorName = name;
        sessionStorage.setItem('arthratanEditorName', editorName);
        localStorage.setItem('arthratanEditorName', editorName);
        if (document.getElementById('wikiSetupRemember').checked) {
          try { await rememberDeviceToken(token); } catch (rememberError) { console.warn('This browser could not remember editor access', rememberError); }
        }
        document.getElementById('wikiEditButton').classList.add('is-unlocked');
        document.getElementById('wikiEditButton').textContent = `Edit as ${editorName}`;
        document.getElementById('wikiSetupToken').value = '';
        closeDialog();
        startEditing();
      } catch (setupError) {
        token = '';
        error.textContent = setupError.message;
      } finally {
        button.disabled = false;
      }
    };
  }

  async function init() {
    buildUi();
    [editorConfig, siteEdits] = await Promise.all([
      fetchJson(CONFIG_URL, {version: 1, configured: false, repository: DEFAULT_REPOSITORY, branch: DEFAULT_BRANCH}),
      fetchJson(EDITS_URL, emptyEdits())
    ]);
    siteEdits = {...emptyEdits(), ...siteEdits, pages: siteEdits.pages || {}, chrome: siteEdits.chrome || {slots: {}}};
    if (editorConfig?.configured) await detectRememberedDevice();
    applyEdits();
    observer = new MutationObserver(queueHydrate);
    observer.observe(document.getElementById('main'), {childList: true, subtree: true});
    window.addEventListener('hashchange', () => {
      if (editing) stopEditing({restore: false});
      queueHydrate();
    });
  }

  init().catch(error => console.error('Wiki editor failed to initialize', error));
})();
