#!/usr/bin/env python3
"""Harden the data-driven Character and A-Z SPA surfaces.

This patch is deliberately marker-scoped. It changes rendering/navigation logic only:
no character record, source transmission, canon fact, Myth, or crossscale conclusion is
modified. Unknown fields remain unknown instead of being filled with invented defaults.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.js"

CHAR_START = "/* --- Character Encyclopedia & Dossier Subsystem --- */"
CHAR_END = "/* --- Causal Ontology Subsystem --- */"
INDEX_START = "/* --- INDEX-002: A-Z Site Index & Directory Subsystem --- */"
INDEX_END = "/* --- Route Not Found / 404 Recovery Subsystem (IA-F02) --- */"

CHAR_BLOCK = r'''/* --- Character Encyclopedia & Dossier Subsystem --- */
function nonEmpty(v){
  if(v === null || v === undefined) return false;
  if(Array.isArray(v)) return v.length > 0;
  if(typeof v === 'string') return v.trim().length > 0;
  if(typeof v === 'object') return Object.keys(v).length > 0;
  return true;
}

function renderRecordValue(v){
  if(!nonEmpty(v)) return '';
  if(Array.isArray(v)){
    const rows = v.filter(nonEmpty);
    if(!rows.length) return '';
    return `<ul style="margin:8px 0 0; padding-left:20px">${rows.map(x=>`<li>${renderRecordValue(x)}</li>`).join('')}</ul>`;
  }
  if(typeof v === 'object'){
    const rows = Object.entries(v).filter(([,value])=>nonEmpty(value));
    if(!rows.length) return '';
    return `<dl class="record-kv">${rows.map(([key,value])=>`<dt>${esc(key.replace(/_/g,' '))}</dt><dd>${renderRecordValue(value)}</dd>`).join('')}</dl>`;
  }
  return esc(v);
}

function safeCharacterLookup(chars, requested){
  const exact = chars.filter(c => c.slug === requested);
  if(exact.length === 1) return exact[0];
  if(exact.length > 1) return null;
  const q = slug(requested);
  if(!q) return null;
  const aliasMatches = chars.filter(c => Array.isArray(c.aliases) && c.aliases.some(a => slug(a) === q));
  return aliasMatches.length === 1 ? aliasMatches[0] : null;
}

function characterFactRow(label, value, badge=false){
  if(!nonEmpty(value)) return '';
  const rendered = Array.isArray(value) ? value.map(esc).join(' · ') : esc(value);
  return `<tr><th>${esc(label)}</th><td>${badge ? `<span class="canon-badge">◆ ${rendered}</span>` : rendered}</td></tr>`;
}

async function charactersHub(filterClan='all'){
  const d = await load('characters');
  const chars = d.characters || [];
  setBreadcrumbs([
    {label:'Sanctuary', href:'#home'},
    {label:'People & Entities'}
  ]);
  const clans = ['all', ...Array.from(new Set(chars.map(c => c.clan).filter(nonEmpty))).sort()];
  const filtered = (filterClan === 'all') ? chars : chars.filter(c => c.clan === filterClan);
  const getAvatar = c => c.model_art || 'assets/art/chibi-arthiteans.webp';

  main.innerHTML = pageIntro(
    `${chars.length} Published Character Records`,
    'Character Encyclopedia',
    'Structured dossiers from the current character registry. Missing properties remain explicitly unfilled rather than inferred.',
    'assets/art/chibi-arthiteans.webp'
  ) + `
  <div class="roster-filter-row">
    ${clans.map(clanName => `
      <button class="roster-pill ${filterClan === clanName ? 'is-active' : ''}" onclick="charactersHub('${esc(clanName)}')">
        ${esc(clanName === 'all' ? 'All Clans & Allegiances (' + chars.length + ')' : clanName)}
      </button>
    `).join('')}
  </div>
  <div class="character-roster-grid">
    ${filtered.map(c => `
      <a class="character-card" href="#character:${esc(c.slug)}">
        <img class="character-avatar" src="${esc(getAvatar(c))}" alt="${esc(c.name || c.slug || 'Character record')}">
        <div class="character-card-info">
          <h3>${esc(c.name || c.slug || 'Unnamed record')}</h3>
          <small>${esc(c.clan || c.species || c.classification || 'Published record')}${nonEmpty(c.status) ? ' · ' + esc(c.status) : ''}</small>
          ${nonEmpty(c.role || c.summary) ? `<p>${esc(c.role || c.summary)}</p>` : ''}
        </div>
      </a>
    `).join('')}
  </div>`;
}

async function characterView(cslug){
  const d = await load('characters');
  const chars = d.characters || [];
  const c = safeCharacterLookup(chars, cslug);
  if(!c) return routeNotFound(`character:${cslug}`);

  setBreadcrumbs([
    {label:'Sanctuary', href:'#home'},
    {label:'People & Entities', href:'#characters'},
    {label:c.name || c.slug}
  ]);

  const hasModelArt = nonEmpty(c.model_art);
  const avatar = hasModelArt ? c.model_art : 'assets/art/chibi-arthiteans.webp';
  const portraitLabel = hasModelArt
    ? (nonEmpty(c.model_note) ? c.model_note : 'Published model-art reference')
    : 'Generic site illustration — not a canonical portrait';

  const abilitiesHtml = Array.isArray(c.abilities) && c.abilities.length ? `
    <div class="section-head"><h2>Abilities & Mechanics</h2></div>
    <div class="grid two">
      ${c.abilities.filter(nonEmpty).map(a => {
        if(typeof a === 'string') return `<div class="card"><p>${esc(a)}</p></div>`;
        if(a && typeof a === 'object'){
          const title = a.name || a.title || '';
          const micro = a.type || a.class || '';
          const body = a.description || a.summary || a.text || '';
          return `<div class="card">${nonEmpty(micro) ? `<div class="micro">${esc(micro)}</div>` : ''}${nonEmpty(title) ? `<h3>${esc(title)}</h3>` : ''}${nonEmpty(body) ? `<p>${renderRecordValue(body)}</p>` : renderRecordValue(a)}</div>`;
        }
        return '';
      }).join('')}
    </div>` : '';

  const relsHtml = Array.isArray(c.relationships) && c.relationships.length ? `
    <div class="section-head"><h2>Documented Relationships</h2></div>
    <div class="grid two">
      ${c.relationships.filter(nonEmpty).map(r => {
        if(typeof r === 'string') return `<div class="card"><p>${esc(r)}</p></div>`;
        if(!r || typeof r !== 'object') return '';
        const relation = r.relation || r.type || '';
        const target = r.target || r.name || '';
        const notes = r.notes || r.summary || r.description || '';
        const targetSlug = r.target_slug;
        const canLink = nonEmpty(targetSlug) && chars.filter(x => x.slug === targetSlug).length === 1;
        const targetHtml = nonEmpty(target) ? (canLink ? `<a href="#character:${esc(targetSlug)}" style="color:#e4b76f; text-decoration:none">${esc(target)}</a>` : esc(target)) : '';
        return `<div class="card">${nonEmpty(relation) ? `<div class="micro">${esc(relation)}</div>` : ''}${targetHtml ? `<h3>${targetHtml}</h3>` : ''}${nonEmpty(notes) ? `<p>${renderRecordValue(notes)}</p>` : ''}</div>`;
      }).join('')}
    </div>` : '';

  const sourcesHtml = Array.isArray(c.source_threads) && c.source_threads.length ? `
    <div class="section-head"><h2>Preserved Source Occurrences & Threads</h2></div>
    <div class="card"><ul style="margin:0; padding-left:20px; color:#c3b9c8">
      ${c.source_threads.filter(nonEmpty).map(s => {
        const text = typeof s === 'string' ? s : JSON.stringify(s);
        const m = text.match(/([0-9a-f]{16})/i);
        const href = m ? `#transmission:${m[1]}` : '#stories';
        return `<li style="margin-bottom:6px"><a href="${href}" style="color:#e4b76f">${esc(text)}</a></li>`;
      }).join('')}
    </ul></div>` : '';

  const biographyParts = [];
  if(nonEmpty(c.history)) biographyParts.push(`<h3>History</h3>${renderRecordValue(c.history)}`);
  else if(nonEmpty(c.summary)) biographyParts.push(`<p>${esc(c.summary)}</p>`);
  if(nonEmpty(c.personality)) biographyParts.push(`<h3>Personality / Disposition</h3>${renderRecordValue(c.personality)}`);
  if(nonEmpty(c.appearance)) biographyParts.push(`<h3>Appearance</h3>${renderRecordValue(c.appearance)}`);
  if(Array.isArray(c.gaps) && c.gaps.length) biographyParts.push(`<h3>Information Not Yet Established</h3>${renderRecordValue(c.gaps)}`);

  main.innerHTML = `
  <section class="dossier-hero">
    <div>
      <div class="eyebrow">${esc(c.classification || 'Published Character Record')}${nonEmpty(c.clan) ? ' · ' + esc(c.clan) : ''}</div>
      <h1 class="page-title" style="margin:8px 0 14px">${esc(c.name || c.slug)}</h1>
      ${nonEmpty(c.summary || c.role) ? `<p class="lede">${esc(c.summary || c.role)}</p>` : ''}
      <table class="dossier-meta-table">
        ${characterFactRow('Role', c.role)}
        ${characterFactRow('Titles', c.titles)}
        ${characterFactRow('Clan', c.clan)}
        ${characterFactRow('Species', c.species)}
        ${characterFactRow('Sex', c.sex)}
        ${characterFactRow('Allegiance', c.allegiance)}
        ${characterFactRow('Canon Level', c.canon_level, true)}
        ${characterFactRow('Status', c.status)}
      </table>
    </div>
    <div class="dossier-portrait">
      <img src="${esc(avatar)}" alt="${esc(c.name || c.slug)}">
      <div style="padding:12px 14px; font-size:11px; color:#84788d; text-align:center">${esc(portraitLabel)}</div>
    </div>
  </section>
  ${biographyParts.length ? `<div class="section-head"><h2>Canonical Biography & Character Profile</h2></div><div class="card">${biographyParts.join('')}</div>` : ''}
  ${abilitiesHtml}
  ${relsHtml}
  ${sourcesHtml}
  <div class="concept-nav" style="margin-top:28px">
    <a href="#characters">← Back to Character Encyclopedia</a>
    <a href="#index">Browse A–Z Index</a>
    <a href="#masterpages">Masterpages Directory</a>
  </div>`;
}

'''

INDEX_BLOCK = r'''/* --- INDEX-002: A-Z Site Index & Directory Subsystem --- */
let siteIndexState = { activeLetter: '', activeDomain: 'all', query: '' };

async function siteIndexView(letter=''){
  siteIndexState.activeLetter = letter ? letter.toUpperCase() : '';
  const d = await load('siteIndex');
  const metrics = d.metadata?.metrics || {};
  const canonicalCount = Number(metrics.total_canonical_entries || 0);
  const aliasCount = Number(metrics.total_alias_mappings || 0);
  const termCount = Number(metrics.total_indexable_terms || (canonicalCount + aliasCount));
  const domainCount = Number(metrics.domains_count || Object.keys(d.domains_summary || {}).length);

  setBreadcrumbs([
    {label:'Sanctuary', href:'#home'},
    {label:'Discovery', href:'#search'},
    {label:'A–Z Site Index' + (siteIndexState.activeLetter ? ' (' + siteIndexState.activeLetter + ')' : '')}
  ]);

  const allLetters = ['ALL', ...(d.a_to_z ? Object.keys(d.a_to_z).sort() : [])];
  const allDomains = ['all', ...Object.keys(d.domains_summary || {})];
  main.innerHTML = pageIntro(
    `${canonicalCount} Canonical Entries · ${aliasCount} Aliases · ${domainCount} Domains`,
    'A–Z Codex Directory',
    'Search and browse the current generated index. Every “Open entity” target is validated against an implemented static or SPA destination by the architecture gate.',
    'assets/art/chibi-search.webp'
  ) + `
  <div class="index-toolbar">
    <div class="alphabet-jump-bar" id="azJumpBar">
      ${allLetters.map(l => {
        const isAct = (l === 'ALL' && !siteIndexState.activeLetter) || (l === siteIndexState.activeLetter);
        return `<button class="${isAct ? 'is-active' : ''}" onclick="filterIndexLetter('${l === 'ALL' ? '' : l}')">${esc(l)}</button>`;
      }).join('')}
    </div>
    <input class="index-search-input" id="indexSearchInput" type="search" placeholder="Type to filter ${termCount.toLocaleString()} indexed terms & aliases..." value="${esc(siteIndexState.query)}">
    <div class="domain-filter-row" id="domainFilterRow">
      ${allDomains.map(dom => {
        const isAct = dom === siteIndexState.activeDomain;
        const count = dom === 'all' ? canonicalCount : Number(d.domains_summary?.[dom] || 0);
        return `<button class="domain-pill ${isAct ? 'is-active' : ''}" data-domain="${esc(dom)}">${esc(dom)} (${count})</button>`;
      }).join('')}
    </div>
  </div>
  <div class="index-meta-strip" id="indexMetaStrip">Loading entries...</div>
  <div class="index-grid" id="indexCardsGrid"></div>`;

  const searchInput = $('#indexSearchInput');
  if(searchInput){
    searchInput.oninput = () => {
      siteIndexState.query = searchInput.value.trim().toLowerCase();
      renderIndexCards(d);
    };
  }
  document.querySelectorAll('#domainFilterRow button[data-domain]').forEach(btn => {
    btn.onclick = () => filterIndexDomain(btn.dataset.domain || 'all');
  });
  renderIndexCards(d);
}

function filterIndexLetter(l){
  siteIndexState.activeLetter = l;
  location.hash = l ? '#index:' + l.toLowerCase() : '#index';
}

function filterIndexDomain(dom){
  siteIndexState.activeDomain = dom;
  const d = state['siteIndex'];
  if(d) renderIndexCards(d);
}

function getDomainClass(domain){
  const name = String(domain || '');
  if(name.includes('Divine')) return 'index-domain-divine';
  if(name.includes('Zubaida')) return 'index-domain-zubaida';
  if(name.includes('Hypergendered')) return 'index-domain-hgl';
  if(name.includes('Concepts') || name.includes('Masterpages')) return 'index-domain-concepts';
  if(name.includes('Characters')) return 'index-domain-characters';
  if(name.includes('Chronology')) return 'index-domain-chronology';
  return 'index-domain-clans';
}

function renderIndexCards(d){
  const grid = $('#indexCardsGrid');
  const strip = $('#indexMetaStrip');
  if(!grid || !strip) return;

  const allEntries = [];
  Object.keys(d.a_to_z || {}).forEach(k => allEntries.push(...(d.a_to_z[k] || [])));
  const seen = new Set();
  let entries = allEntries.filter(e => {
    if(!e || !e.id || seen.has(e.id)) return false;
    seen.add(e.id);
    return true;
  });

  if(siteIndexState.activeLetter){
    entries = entries.filter(e => {
      const char = String(e.label || '').trim().charAt(0).toUpperCase();
      if(siteIndexState.activeLetter === '0-9') return /^[0-9]/.test(char);
      return char === siteIndexState.activeLetter;
    });
  }
  if(siteIndexState.activeDomain && siteIndexState.activeDomain !== 'all') entries = entries.filter(e => e.domain === siteIndexState.activeDomain);
  if(siteIndexState.query){
    const q = siteIndexState.query;
    entries = entries.filter(e => {
      const aliases = Array.isArray(e.aliases) ? e.aliases : [];
      return String(e.label || '').toLowerCase().includes(q) || String(e.description || '').toLowerCase().includes(q) || aliases.some(a => String(a).toLowerCase().includes(q));
    });
  }

  document.querySelectorAll('#azJumpBar button').forEach(b => {
    const txt = b.textContent;
    b.classList.toggle('is-active', (txt === 'ALL' && !siteIndexState.activeLetter) || txt === siteIndexState.activeLetter);
  });
  document.querySelectorAll('#domainFilterRow button[data-domain]').forEach(b => b.classList.toggle('is-active', (b.dataset.domain || 'all') === siteIndexState.activeDomain));

  strip.innerHTML = `Showing <b>${entries.length}</b> matching entities${siteIndexState.activeLetter ? ` (Letter ${esc(siteIndexState.activeLetter)})` : ''}${siteIndexState.activeDomain !== 'all' ? ` [Domain: ${esc(siteIndexState.activeDomain)}]` : ''}`;
  if(!entries.length){
    grid.innerHTML = `<div class="card" style="grid-column:1/-1;text-align:center;padding:32px"><h3>No matching index entries found</h3><p>Try clearing filters or searching a different term.</p><button class="primary" style="margin-top:14px" onclick="siteIndexState.query='';siteIndexState.activeLetter='';siteIndexState.activeDomain='all';renderIndexCards(state['siteIndex']);">Reset all filters</button></div>`;
    return;
  }

  grid.innerHTML = entries.map(e => {
    const badgeClass = getDomainClass(e.domain);
    const targetUrl = String(e.target_url || '').trim();
    const aliases = Array.isArray(e.aliases) ? e.aliases : [];
    return `<article class="index-card"><div><div class="index-card-head"><span class="index-domain-badge ${badgeClass}">${esc(e.domain || 'Index')}</span>${nonEmpty(e.status) ? `<span class="canon-badge" style="font-size:10px">◆ ${esc(e.status)}</span>` : ''}</div><h3>${esc(e.label || e.id)}</h3>${nonEmpty(e.description) ? `<p>${esc(e.description)}</p>` : ''}${aliases.length ? `<div class="index-alias-list">${aliases.slice(0,5).map(a=>`<span class="index-alias-tag">${esc(a)}</span>`).join('')}${aliases.length>5 ? `<span class="index-alias-tag">+${aliases.length-5} more</span>` : ''}</div>` : ''}</div><div class="index-card-foot"><small style="color:#7f738a">${esc(e.category || '')}</small>${targetUrl ? `<a class="concept-link" href="${esc(targetUrl)}" style="font-size:12px;font-weight:600;color:#e4b76f">Open entity →</a>` : `<span class="micro">No implemented target</span>`}</div></article>`;
  }).join('');
}

'''


def replace_marker_block(text: str, start: str, end: str, replacement: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError(f"Expected one marker pair: {start!r} / {end!r}")
    pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Failed to replace marker block starting {start}")
    return updated


def main() -> int:
    original = APP.read_text(encoding="utf-8")
    text = replace_marker_block(original, CHAR_START, CHAR_END, CHAR_BLOCK)
    text = replace_marker_block(text, INDEX_START, INDEX_END, INDEX_BLOCK)
    if text == original:
        print("SPA rendering already hardened.")
        return 0
    APP.write_text(text, encoding="utf-8", newline="")
    print("Hardened Character and A-Z SPA rendering without modifying canon data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
