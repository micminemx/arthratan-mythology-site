
const state={manifest:null,canon:null,divine:null,hglPages:null,hglToc:null};
const $=s=>document.querySelector(s); const main=$('#main');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug=s=>String(s).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
async function load(name){ if(state[name]) return state[name]; const map={manifest:'manifest.json',canon:'new-canon.json',divine:'divine.json',hglPages:'hgl-pages.json',hglToc:'hgl-toc.json',masterpages:'masterpages.json',characters:'characters.json',causalOntology:'causal-ontology.json',siteIndex:'site-index.json'}; const file=map[name]||(name.endsWith('.json')?name:name+'.json'); const r=await fetch('data/'+file); state[name]=await r.json(); return state[name]; }
function toast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1800)}
function setBreadcrumbs(crumbs){
  const el=$('#crumbs'); if(!el)return;
  if(typeof crumbs==='string'){
    if(crumbs==='Sanctuary'){ crumbs=[{label:'Sanctuary',href:'#home'}]; }
    else { crumbs=[{label:'Sanctuary',href:'#home'},{label:crumbs}]; }
  }
  if(!Array.isArray(crumbs)||!crumbs.length) crumbs=[{label:'Sanctuary',href:'#home'}];
  const last=crumbs[crumbs.length-1];
  document.title=(last.label||'Sanctuary')+' · The Arthitean Codex';
  el.innerHTML=crumbs.map((c,i)=>{
    const isLast=(i===crumbs.length-1);
    if(isLast||!c.href){ return `<span class="crumb-current" aria-current="page">${esc(c.label)}</span>`; }
    return `<a href="${esc(c.href)}">${esc(c.label)}</a><span class="crumb-sep">/</span>`;
  }).join('');
  const currentHash=location.hash||'#home';
  document.querySelectorAll('#nav a').forEach(a=>{
    const href=a.getAttribute('href')||'';
    const active=(href===currentHash)||(href!=='#home'&&href!=='/'&&currentHash.startsWith(href));
    a.classList.toggle('active',active);
  });
}
function setCrumb(x){ setBreadcrumbs(x); }
function routeTo(hash){location.hash=hash;}
function card(title,micro,text,href){return `<article class="card ${href?'clickable':''}" ${href?`onclick="routeTo('${href}')"`:''}><div class="micro">${esc(micro)}</div><h3>${esc(title)}</h3><p>${esc(text)}</p></article>`}
function pageIntro(kicker,title,lede,img){return `<section class="page-intro"><div><div class="eyebrow">${esc(kicker)}</div><h1 class="page-title">${esc(title)}</h1><p class="lede">${esc(lede)}</p><div class="canon-badge">◆ Living canon · source-preserving</div></div>${img?`<img src="${img}" alt="">`:''}</section>`}
function artCard(src,title,caption,contain=false){return `<div class="art-card ${contain?'contain':''}"><img src="${src}" alt="${esc(title)}"><div class="art-caption"><b>${esc(title)}</b><span>${esc(caption)}</span></div></div>`}
function artBanner(src,title,caption){return `<div class="art-banner"><img src="${src}" alt="${esc(title)}"><div class="art-caption"><b>${esc(title)}</b><span>${esc(caption)}</span></div></div>`}
function gatewayCard(title,micro,text,href,img){return `<article class="card gateway-card clickable" onclick="routeTo('${href}')"><img class="gateway-chibi" src="${img}" alt=""><div class="gateway-copy"><div class="micro">${esc(micro)}</div><h3>${esc(title)}</h3><p>${esc(text)}</p></div></article>`}
function artAction(label,href,img,cls='primary'){return `<a class="${cls} art-action" href="${href}"><img src="${img}" alt=""><span>${esc(label)}</span></a>`}

async function home(){const m=await load('manifest');setCrumb('Sanctuary');main.innerHTML=`
<section class="hero"><img src="assets/art/arthratan-twilight-citadel.webp" alt="Arthratan mythology citadel populated by black-phoenix-winged Arthiteans"><div class="hero-content"><div class="eyebrow">Living visual world-canon · Arthratan mythology</div><h1>The Arthitean Codex</h1><p>A navigable sanctuary for <b>Divine v144</b>, <b>Hypergendered Logic</b>, and the newest living canon—converted from document-mass into visual systems, character architecture, searchable source-pages and formal substructures.</p><div class="hero-actions">${artAction('Enter the Visual Atlas','#atlas','assets/art/chibi-sources.webp')}${artAction('Search all canon','#search','assets/art/chibi-search.webp','secondary')}</div></div></section>
<div class="stats-strip"><div class="stat"><b>${m.stats.divine_sections}</b><span>Divine sections</span></div><div class="stat"><b>${m.stats.hgl_pages}</b><span>HGL source pages</span></div><div class="stat"><b>${m.stats.hgl_toc_entries}</b><span>HGL indexed headings</span></div><div class="stat"><b>${m.stats.conversation_canon_sections}</b><span>Newest canon nodes</span></div></div>
<div class="section-head"><h2>Enter by system, not by document</h2><p>The site keeps the complete source material accessible, but the default experience is concept-first: diagrams, ladders, operator maps, character arcs and crosslinked subpages.</p></div>
<div class="grid three gateway-grid">${gatewayCard('Metagovernance & Ultraarsayne','Scaling','Rules → Metarules → Antipossibility → Lydrextent → Arsayne-family totality recursion.','#scaling','assets/art/chibi-scaling.webp')}${gatewayCard('Rhayhara','Goddess of Arthiteans','Sealed legacy, beginningless past, Negative Rewrite growth and the tension between former war-goddess power and present protector-rulership.','#rhayhara','assets/art/chibi-rhayhara.webp')}${gatewayCard('Hypergendered Logic','Formal biology','PA, IH, PH, Γ, Suprafemale/Supramale recursion, Archwomanhood/Archmanhood and transordinal inheritance.','#hgl','assets/art/chibi-hgl.webp')}</div>
<div class="section-head"><h2>Arthitean visual identity</h2><p>The site’s original artwork follows the canon: reddish-brown skin, dark-red hair, purple eyes, and black phoenix-like wings—not angelic or demonic wings.</p></div><div class="phenotype-art"><img src="assets/art/arthitean-royal-pair.webp" alt="Arthitean man and woman with reddish-brown skin, dark-red hair, purple eyes and black phoenix-like wings"></div><div class="section-head"><h2>Arthitean living portraiture</h2><p>Generated character art now replaces the former abstract decorative figures throughout the living-canon pages.</p></div><div class="art-gallery">${artCard('assets/art/rhayhara-crowned.webp','Rhayhara','Goddess of Arthiteans · phoenix-crowned ruler',true)}${artCard('assets/art/arthitean-male-warrior.webp','Arthitean male','Extremely masculine divine warrior',true)}${artCard('assets/art/arthitean-female-goddess.webp','Arthitean female','Goddessly, strongly feminine Arthitean',true)}</div><div class="section-head"><h2>Arthratan mythology panoramas</h2><p>World-art is used as page architecture: civilization, rulership, warfare, archives, gates and metaphysical ascent.</p></div><div class="arthratan-mosaic">${artCard('assets/art/arthratan-palace.webp','The Celestial Palace','Arthitean imperial-metaphysical architecture')}${artCard('assets/art/arthratan-phoenix-throne.webp','Phoenix Throne','Divine sovereignty at monumental scale')}${artCard('assets/art/arthratan-gates.webp','Celestial Gates','Thresholds between higher Arthratan structures')}${artCard('assets/art/arthratan-archive-scholars.webp','Living Archive','Arthitean scholarship within the mythology')}</div>`}

async function atlas(){setCrumb('Visual Atlas');main.innerHTML=pageIntro('Codex cartography','Visual Atlas','A concept-first map of the major systems. Each panel is a compressed visual gateway into the full source canon.','assets/art/chibi-sources.webp')+`
<div class="grid two gateway-grid">${gatewayCard('Governance recursion','Ontology','Rules govern states; Metarules govern rules; higher Metarules recursively govern prior governance.','#scaling','assets/art/chibi-scaling.webp')}${gatewayCard('Negative Rewrite','Causality','Effect generation followed by self-erasure of the rewrite’s causal provenance while the effect persists.','#negative-rewrite','assets/art/chibi-negative-rewrite.webp')}${gatewayCard('Arthitean ontostates','Inheritance','Arthitean → Archarthitean → Deity of Arthiteans, with higher states inheriting prior-state properties.','#arthiteans','assets/art/chibi-arthiteans.webp')}${gatewayCard('Rhayhara seal architecture','Character system','Recovered former strength, non-restored growth dynamics, escalating seal factors and legacy-overhang.','#rhayhara','assets/art/chibi-rhayhara.webp')}${gatewayCard('HGL operator stack','Formal logic','PA developmental causation, IH provenance-bearing inheritance, PH whole-profile possession, Γ global stage metaexpression.','#hgl','assets/art/chibi-hgl.webp')}${gatewayCard('Full-source archives','Provenance','Every Divine section and every HGL page remains reachable and searchable.','#sources','assets/art/chibi-sources.webp')}</div>
${artBanner('assets/art/arthratan-gates.webp','The Arthratan Atlas','A mythology-map rendered as thresholds, citadels and divine beings rather than abstract geometry alone.')}<div class="art-gallery">${artCard('assets/art/arthratan-procession.webp','Ascension procession','Arthiteans traversing a higher-order path')}${artCard('assets/art/arthratan-twilight-citadel.webp','Twilight Citadel','Civilization-scale Arthratan mythology')}${artCard('assets/art/arthratan-palace.webp','Golden-wing palace','A visual anchor for the world-canon')}</div><div class="section-head"><h2>Crosssystem map</h2><p>Arthitean canon repeatedly separates state, source, governance, inheritance, effect and growth-dynamics instead of collapsing them into one scalar “power” variable.</p></div><div class="diagram"><div class="flow"><div class="node"><strong>Governance</strong><span>what may classify</span></div><span class="arrow">→</span><div class="node"><strong>State</strong><span>what presently is</span></div><span class="arrow">→</span><div class="node"><strong>Effect</strong><span>what changes</span></div><span class="arrow">→</span><div class="node"><strong>Inheritance</strong><span>what persists from source</span></div><span class="arrow">→</span><div class="node"><strong>Meta-growth</strong><span>how change-rate itself changes</span></div></div></div>`}

async function scaling(){const c=await load('canon');setCrumb('Metagovernance & Scaling');const get=id=>c.sections.find(x=>x.id===id);main.innerHTML=pageIntro('Post-impossibility scaling','Metagovernance & Scaling','The core ladder is not “bigger numbers.” It repeatedly changes the governance-order by which possibility, impossibility, whole families, and entire Metarule-indexed totalities can be classified.','assets/art/chibi-scaling.webp')+`
<div class="section-head"><h2>Rules → Metarules</h2><p>Governance-depth recursively turns the previous governance layer into the next governed object.</p></div><div class="diagram"><div class="flow"><div class="node"><strong>Rules</strong><span>depth 0</span></div><span class="arrow">→</span><div class="node"><strong>Metarules</strong><span>depth 1</span></div><span class="arrow">→</span><div class="node"><strong>Metarules²</strong><span>depth 2</span></div><span class="arrow">→</span><div class="node"><strong>Metarules³</strong><span>depth 3</span></div><span class="arrow">→</span><div class="node"><strong>…</strong><span>no terminal order</span></div></div></div>
<div class="section-head"><h2>Antipossibility coordinate-space</h2><p>Family order is the outer recursion; intrafamily order is the inner recursion. Lydrextent walks their diagonal A(n,n).</p></div><div class="grid two"><div class="diagram"><div class="matrix">${Array.from({length:36},(_,i)=>{const r=Math.floor(i/6)+1,cl=i%6+1;return `<div class="cell ${r===cl?'diag':''}">${r===cl?'L'+r:`A(${r},${cl})`}</div>`}).join('')}</div></div><div class="card"><div class="micro">Biordinality</div><h3>Lydrextent n = A(n,n)</h3><p>Each Lydrextent step raises both the Antipossibility-family coordinate and the intrafamily Metarule order. A higher family outranks every state of the lower family regardless of inner order.</p><div class="formula">Lₙ ↔ A(n,n)</div></div></div>
${artBanner('assets/art/arthratan-procession.webp','The scale behind the empire','The ascending procession mirrors the canon’s movement from one recursive governance-order into a higher one.')}<div class="section-head"><h2>Post-Lydrextent totality recursion</h2><p>Each new Arsayne family begins by surpassing a complete possible-and-impossible Metarule-indexed totality built from the preceding scale.</p></div><div class="ladder"><div class="rung"><b>Lydrextent</b><small>biordinal Antipossibility diagonal</small></div><div class="rung"><b>Arsayne</b><small>beyond Metarule^Lydrextent totality</small></div><div class="rung"><b>Supraarsayne</b><small>beyond Metarule^Arsayne totality</small></div><div class="rung"><b>Hyperarsayne</b><small>beyond Metarule^Supraarsayne totality</small></div><div class="rung"><b>Ultraarsayne</b><small>beyond Metarule^Hyperarsayne totality</small></div></div>
<div class="section-head"><h2>Canonical text</h2></div><div class="grid two">${['metagovernance','antipossibility','lydrextent','arsayne'].map(id=>{const s=get(id);return `<article class="card"><div class="micro">${esc(s.kicker)}</div><h3>${esc(s.title)}</h3>${s.body.map(p=>`<p style="margin-top:10px">${esc(p)}</p>`).join('')}</article>`}).join('')}</div>`}

async function negativeRewrite(){const c=await load('canon');const s=c.sections.find(x=>x.id==='negative-rewrite');setCrumb('Negative Rewrite');main.innerHTML=pageIntro('Causal-provenance nullification','Negative Rewrite','A rewrite can produce a real effect and then make its own occurrence and causal role never have been true—without undoing the effect.','assets/art/chibi-negative-rewrite.webp')+`
${artBanner('assets/art/arthratan-shattered-divide.webp','Negative Rewrite · visual metaphor','One reality-side is destroyed while the restored side persists—visualizing effect persistence after causal-provenance erasure.')}${artBanner('assets/art/arthratan-ruin-rebirth.webp','Ruin → restoration without surviving origin','The changed state remains even when the rewrite that produced it no longer survives as historical truth.')}<div class="diagram"><div class="flow"><div class="node"><strong>1 · Generate effect</strong><span>reality changes</span></div><span class="arrow">→</span><div class="node"><strong>2 · Erase origin</strong><span>rewrite self-nullifies</span></div><span class="arrow">→</span><div class="node"><strong>3 · Persist</strong><span>effect remains real</span></div></div></div>
<div class="section-head"><h2>Persistence invariant</h2><p>Negative Rewrite changes causal provenance, not merely the visible state.</p></div><div class="formula">effect-generation → causal-origin erasure → effect persistence</div>
<div class="section-head"><h2>Four worked examples</h2></div><div class="grid two">${s.examples.map(([a,b])=>card(a,'Negative Rewrite example',b)).join('')}</div>
<div class="section-head"><h2>Canonical definition</h2></div><div class="card">${s.body.map(p=>`<p style="margin:0 0 12px">${esc(p)}</p>`).join('')}</div>`}

async function arthiteans(){const c=await load('canon');const s=c.sections.find(x=>x.id==='arthitean-states');setCrumb('Arthitean Ontostates');main.innerHTML=pageIntro('Inheritance-state hierarchy','Arthitean Ontostates','Higher Arthitean states do not replace the lower state; they inherit it and add a higher property-set.','assets/art/chibi-arthiteans.webp')+`${artBanner('assets/art/arthratan-throne-guardians.webp','Arthitean ontostates · mythology embodiment','The hierarchy is shown as inherited divinity within an Arthratan throne-civilization.')}<div class="figure-pair">${artCard('assets/art/arthitean-male-warrior.webp','Arthitean male embodiment','Extremely masculine, godly, unfeminine; black phoenix wings.',true)}${artCard('assets/art/arthitean-female-goddess.webp','Arthitean female embodiment','Extremely feminine, goddessly, unmasculine; black phoenix wings.',true)}</div>
<div class="diagram"><div class="flow"><div class="node"><strong>ARTHITEAN</strong><span>base Arthitean property-set</span></div><span class="arrow">⊂</span><div class="node"><strong>ARCHARTHITEAN</strong><span>inherits Arthitean + higher state</span></div><span class="arrow">⊂</span><div class="node"><strong>DEITY OF ARTHITEANS</strong><span>inherits both prior states + deity-state</span></div></div></div>
<div class="grid two" style="margin-top:18px"><article class="card"><div class="micro">Ontoinheritance</div><h3>A → (A+B) → (A+B+C)</h3><p>State advancement is additive inheritance, not type replacement. A Deity of Arthiteans remains Archarthitean and Arthitean by inherited property possession.</p></article><article class="card"><div class="micro">Rhayhara</div><h3>Goddess-state</h3><p>Rhayhara’s present ontology can therefore be read simultaneously as Arthitean, Archarthitean and Goddess/Deity of Arthiteans.</p></article></div>
<div class="arthratan-mosaic">${artCard('assets/art/arthratan-imperial-royalty.webp','Imperial darkwing royalty','Arthitean masculine/feminine divine pairing',true)}${artCard('assets/art/arthratan-regal-warrior.webp','Arthitean war-god form','Masculine divine-warrior embodiment',true)}${artCard('assets/art/arthratan-phoenix-goddess.webp','Arthitean goddess form','Feminine phoenix-divinity embodiment',true)}</div><div class="section-head"><h2>Canonical text</h2></div><div class="card">${s.body.map(p=>`<p>${esc(p)}</p>`).join('')}</div>`}

async function rhayhara(){const c=await load('canon');const seals=c.sections.find(x=>x.id==='rhayhara-seals');const legacy=c.sections.find(x=>x.id==='rhayhara-legacy');setCrumb('Rhayhara');main.innerHTML=pageIntro('Goddess · ruler · warrior · living legacy','Rhayhara','Her seal system is not a simple hidden-power bank. It restores pieces of former strength while leaving open whether the former growth-rate and acceleration-rate that once produced that strength can ever be recovered.','assets/art/chibi-rhayhara.webp')+`
${artBanner('assets/art/arthratan-memory-empress.webp','Rhayhara · memory and legacy','Her seals tie present recovery to increasingly distant emotional memories from a beginningless past.')}<div class="figure-pair">${artCard('assets/art/arthratan-astral-queen.webp','Present Rhayhara','Compassionate ruler looking toward what she can become rather than merely reproducing what she was.')}${artCard('assets/art/arthratan-crimson-sorceress.webp','War-goddess inheritance','The older, more ruthless warrior-self remains part of her identity rather than a self she simply rejects.',true)}</div><div class="section-head"><h2>The four Seal Factors</h2><p>Each factor operates at a different metalevel: restored strength, increase of restoration, interseal meta-ratio, and Negative-Rewrite-driven retroincrease of that ratio.</p></div><div class="seal-stack">
<div class="seal"><span class="num">01</span><h3>Recovered former strength</h3><p>Ultraarsayne increase in previously possessed bloodline-blessing strength per seal removed, keyed to an equivalent former acceleration-of-growth measure. Former growth dynamics are not guaranteed to return.</p></div>
<div class="seal"><span class="num">02</span><h3>Restoration acceleration</h3><p>Ultraarsayne increase in Seal Factor One per seal removed: later seal-removals can restore increasingly greater former strength.</p></div>
<div class="seal"><span class="num">03</span><h3>Interseal metadifferential</h3><p>Ultraarsayne of Seal Factor Two of the second-next seal per extent of Seal Factor Two of the next seal.</p></div>
<div class="seal"><span class="num">04</span><h3>Negative retroincrease</h3><p>Peak hardship and exertion negatively rewrite an Ultraarsayne increase in Seal Factor Three into the past while the increase persists after its causal origin is erased.</p></div></div>
<div class="section-head"><h2>Power ascent ↔ memory descent</h2><p>Every recovered seal requires a key emotional memory from deeper into Rhayhara’s beginningless past. Greater present recovery therefore requires deeper self-recovery.</p></div><div class="diagram"><div class="flow"><div class="node"><strong>Deeper lost memory</strong><span>further into beginningless past</span></div><span class="arrow">→</span><div class="node"><strong>One seal removed</strong><span>never all at once</span></div><span class="arrow">→</span><div class="node"><strong>Former strength restored</strong><span>Ultraarsayne-scale</span></div><span class="arrow">≠</span><div class="node"><strong>Former growth dynamics</strong><span>not necessarily restored</span></div></div></div>
<div class="section-head"><h2>Her deepest conflict is not “become stronger”</h2><p>Her past can remain a standard she may never fully reproduce. Her present project is to become a superior person even if she cannot simply recreate the trajectory of her old power.</p></div><div class="timeline"><div class="timeline-item"><h3>Far-past Rhayhara · War Goddess</h3><p>More ruthless, more executioner-oriented, fighting evil principally to punish it. Her old power and growth-dynamics cast a monumental legacy-overhang.</p></div><div class="timeline-item"><h3>Sealed Rhayhara · Legacy burden</h3><p>Her former strength is hidden behind memory-linked seals. Every restoration proves how extraordinary she was while simultaneously reminding her that former growth machinery may be gone.</p></div><div class="timeline-item"><h3>Present Rhayhara · Protector-ruler</h3><p>She still embraces warriorhood, but repurposes it: fighting to save rather than merely to execute evil. Compassion and rulership become dimensions on which her present self can surpass her stronger former self.</p></div></div>
<div class="quote">“Recover her strength without surrendering to her purpose.”</div>
<div class="section-head"><h2>Canonical seal text</h2></div><div class="card">${seals.body.map(p=>`<p style="margin:0 0 12px">${esc(p)}</p>`).join('')}</div>
<div class="section-head"><h2>Legacy-overhang canon</h2></div><div class="card">${legacy.body.map(p=>`<p style="margin:0 0 12px">${esc(p)}</p>`).join('')}</div>`}

async function hgl(){setCrumb('Hypergendered Logic');main.innerHTML=pageIntro('Fictional formal biology','Hypergendered Logic','A typed developmental-inheritance-phenotype-metaexpression modal logic. The website preserves the treatise’s explicit status as a fictional formal system rather than a real-world medical theory.','assets/art/chibi-hgl.webp')+`
<div class="warning"><b>Scope notice:</b> HGL’s chromosome predicates and biological examples are internal to a fictional formal system; the source explicitly distinguishes them from real human sex development.</div>
<div class="section-head"><h2>Four non-collapsible layers</h2><p>The operators answer different questions. The site keeps them visually separate to prevent the exact collapse-errors the treatise warns against.</p></div><div class="operator-grid"><div class="operator"><div class="symbol">PA</div><b>Developmental cause</b><p>Due to what designated condition is physiology/anatomy necessarily developable?</p></div><div class="operator"><div class="symbol">IH</div><b>Inheritance provenance</b><p>Which logical/state properties are inherited, and from which source did they come?</p></div><div class="operator"><div class="symbol">PH</div><b>Whole-profile possession</b><p>Which complete Hypergendered phenotype-profile is irreducibly possessed as a whole-source profile?</p></div><div class="operator"><div class="symbol">Γ</div><b>Global metaexpression</b><p>What stage-level rule-function governs how actual physical phenotypes may, must or cannot express?</p></div></div>
<div class="section-head"><h2>Core anti-collapse laws</h2></div><div class="grid two"><div class="formula">PA(¬φ) ≢ ¬PA(φ)</div><div class="formula">PA(A ∧ B) ≢ PA(A) ∧ PA(B)</div><div class="formula">IH(Z) ⇒ Z, but Z ⇏ IH(Z)</div><div class="formula">PH(¬Z) ≢ ¬PH(Z)</div><div class="formula">PH(Z) ≢ PA(Z)</div><div class="formula">PH(Z) ≢ IH(Z)</div></div>
${artBanner('assets/art/arthratan-archive-scholars.webp','Embodied formal biology · living archive','Arthitean scholars visually anchor the formal system while the logical operators retain their exact source roles.')}<div class="section-head"><h2>Major category ascent</h2><p>Current authoritative category order in the source is Supra → Hyper → Ultra → Apex; category boundaries are strict constructions rather than endpoint identities.</p></div><div class="flow diagram"><div class="node"><strong>SUPRA</strong><span>recursive minor-category foundation</span></div><span class="arrow">→</span><div class="node"><strong>HYPER</strong><span>higher dimensional strata</span></div><span class="arrow">→</span><div class="node"><strong>ULTRA</strong><span>higher category family</span></div><span class="arrow">→</span><div class="node"><strong>APEX</strong><span>higher category family</span></div></div>
<div class="section-head"><h2>Read the complete treatise</h2><p>The full 293-page source is converted into searchable webpage text with TOC-linked parts and subheadings.</p></div>${artAction('Open HGL Archive','#hgl-archive','assets/art/chibi-hgl.webp')}`}

async function divine(){const d=await load('divine');setCrumb('Divine v144 Archive');renderDivineArchive(d.sections[0].id)}
async function renderDivineArchive(id){const d=await load('divine');const secs=d.sections;const selected=secs.find(s=>s.id===id)||secs[0];const nav=secs.filter(s=>s.level<=2||/Rhayhara|Arthitean|Lydrextent|Hyperfunction|Antilobe|crossfunction|Divinity|Causal/i.test(s.title));main.innerHTML=`<div class="archive-layout"><aside class="archive-nav"><input id="divineFilter" placeholder="Filter Divine headings…" aria-label="Filter Divine headings"><div id="divineLinks">${nav.map(s=>`<button class="archive-link ${s.id===selected.id?'active':''}" data-id="${s.id}" style="padding-left:${8+Math.max(0,s.level-1)*12}px">${esc(s.title.slice(0,130))}</button>`).join('')}</div></aside><section class="archive-content"><div class="archive-art-head"><img src="assets/art/arthratan-phoenix-throne.webp" alt="Arthratan phoenix throne"><div><div class="eyebrow">Divine v144 · source-preserving web conversion</div><h1>${esc(selected.title)}</h1></div></div><div class="source-note">Heading level ${selected.level} · ${selected.blocks.length} content blocks · source text preserved</div>${selected.blocks.length?selected.blocks.map(renderBlock).join(''):'<div class="card"><p>This heading is primarily structural. Select a child or neighboring section for its source content.</p></div>'}${selected.children?.length?`<div class="section-head"><h2>Subsections</h2></div><div class="grid two">${selected.children.map(cid=>{const x=secs.find(q=>q.id===cid);return x?card(x.title,'Subsection',`${x.blocks.length} source blocks`,`#divine-section:${x.id}`):''}).join('')}</div>`:''}</section></div>`;document.querySelectorAll('.archive-link').forEach(b=>b.onclick=()=>routeTo('#divine-section:'+b.dataset.id));const inp=$('#divineFilter');inp.oninput=()=>{const q=inp.value.toLowerCase();$('#divineLinks').innerHTML=nav.filter(s=>s.title.toLowerCase().includes(q)).slice(0,180).map(s=>`<button class="archive-link" data-id="${s.id}">${esc(s.title.slice(0,130))}</button>`).join('');document.querySelectorAll('.archive-link').forEach(b=>b.onclick=()=>routeTo('#divine-section:'+b.dataset.id));};}
function renderBlock(b){if(b.type==='p') return `<div class="prose-block"><p>${esc(b.text)}</p></div>`;return `<div class="prose-block"><div style="overflow:auto"><table class="source-table">${b.rows.map(r=>`<tr>${r.map(c=>`<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div></div>`}

async function hglArchive(partId='hgl-part-0'){const t=await load('hglToc');const p=await load('hglPages');setCrumb('HGL Archive');const part=t.parts.find(x=>x.id===partId)||t.parts[0];const pages=p.pages.filter(x=>x.page>=part.start_page&&x.page<=part.end_page);main.innerHTML=`<div class="archive-layout"><aside class="archive-nav"><input id="hglFilter" placeholder="Filter HGL parts…" aria-label="Filter HGL parts"><div id="hglLinks">${t.parts.map(x=>`<button class="archive-link ${x.id===part.id?'active':''}" data-id="${x.id}">${esc(x.title)}</button>`).join('')}</div></aside><section class="archive-content"><div class="archive-art-head"><img src="assets/art/arthratan-archive-scholars.webp" alt="Arthitean scholars in a magical archive"><div><div class="eyebrow">Hypergendered Logic · 17 Aug 2026</div><h1>${esc(part.title)}</h1></div></div><div class="source-note">Source pages ${part.start_page}–${part.end_page} · ${part.subheads.length} indexed subheadings</div>${part.subheads.length?`<details class="page-card"><summary>Subsection index</summary><div class="toc-tree">${part.subheads.map(s=>`<button class="l${s.level}" onclick="document.getElementById('hgl-page-${s.page}')?.scrollIntoView({behavior:'smooth'})">${esc(s.title)} · p.${s.page}</button>`).join('')}</div></details>`:''}${pages.map(x=>`<details class="page-card" id="hgl-page-${x.page}" ${pages.length<=4?'open':''}><summary>Source page ${x.page}</summary><pre>${esc(x.text)}</pre></details>`).join('')}</section></div>`;document.querySelectorAll('#hglLinks .archive-link').forEach(b=>b.onclick=()=>routeTo('#hgl-part:'+b.dataset.id));const inp=$('#hglFilter');inp.oninput=()=>{const q=inp.value.toLowerCase();$('#hglLinks').innerHTML=t.parts.filter(x=>x.title.toLowerCase().includes(q)).map(x=>`<button class="archive-link" data-id="${x.id}">${esc(x.title)}</button>`).join('');document.querySelectorAll('#hglLinks .archive-link').forEach(b=>b.onclick=()=>routeTo('#hgl-part:'+b.dataset.id));};}

async function searchPage(){setCrumb('Search the Codex');main.innerHTML=pageIntro('Cross-source discovery','Search the Codex','Search across Divine v144 sections, all 293 HGL pages, and the newest conversation canon.','assets/art/chibi-search.webp')+`<div class="search-wrap"><input id="globalSearch" class="search-box" placeholder="Try Rhayhara, Hyperfunction, PA irreducibility, Lydrextent, Rosha…" autofocus><div id="searchResults" class="search-results"></div></div>`;const input=$('#globalSearch');let timer;input.oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>doSearch(input.value),120)};}
async function doSearch(q){const out=$('#searchResults');if(!q||q.trim().length<2){out.innerHTML='';return}out.innerHTML='<div class="card">Searching complete canon…</div>';const [d,h,c]=await Promise.all([load('divine'),load('hglPages'),load('canon')]);const needle=q.toLowerCase();let results=[];for(const s of d.sections){const text=s.blocks.map(b=>b.type==='p'?b.text:b.rows.flat().join(' ')).join(' ');let idx=(s.title+' '+text).toLowerCase().indexOf(needle);if(idx>=0){const sn=text.slice(Math.max(0,idx-100),idx+260);results.push({score:s.title.toLowerCase().includes(needle)?3:1,type:'Divine v144',title:s.title,sn,href:'#divine-section:'+s.id});}}for(const pg of h.pages){let idx=pg.text.toLowerCase().indexOf(needle);if(idx>=0)results.push({score:1,type:'HGL page '+pg.page,title:'Hypergendered Logic · page '+pg.page,sn:pg.text.slice(Math.max(0,idx-100),idx+260),href:'#hgl-page-direct:'+pg.page});}for(const s of c.sections){const text=s.body.join(' ');let idx=(s.title+' '+text).toLowerCase().indexOf(needle);if(idx>=0)results.push({score:4,type:'Living canon',title:s.title,sn:text.slice(Math.max(0,idx-80),idx+260),href:s.id==='negative-rewrite'?'#negative-rewrite':s.id.startsWith('rhayhara')?'#rhayhara':s.id==='arthitean-states'?'#arthiteans':'#scaling'});}results.sort((a,b)=>b.score-a.score);out.innerHTML=results.slice(0,60).map(r=>`<a class="result" href="${r.href}"><b>${esc(r.title)}</b><small>${esc(r.type)}</small><p>${esc(r.sn)}…</p></a>`).join('')||'<div class="card"><p>No exact text match. Try a shorter root term.</p></div>';}

async function hglDirect(page){const t=await load('hglToc');const part=t.parts.find(x=>page>=x.start_page&&page<=x.end_page);if(part){await hglArchive(part.id);setTimeout(()=>document.getElementById('hgl-page-'+page)?.scrollIntoView(),50)}else await hglArchive();}

async function sources(){const m=await load('manifest');setCrumb('Sources & Provenance');main.innerHTML=pageIntro('Source-preserving architecture','Sources & Provenance','The visual pages are an interface layer, not a replacement for the canon. Complete source documents and complete source-text conversions remain accessible.','assets/art/chibi-sources.webp')+`
${artBanner('assets/art/arthratan-golden-ruins.webp','Arthratan provenance','The mythology remains visually present even on source/provenance pages; the documents remain the canonical evidentiary layer.')}<div class="grid three source-grid"><a href="https://docs.google.com/document/d/1qW4UR7CGTLLW1JqfrOrN1uRHQOnRoVKE/edit" target="_blank" rel="noopener"><article class="card source-card"><div class="filetype">DOCX</div><h3>Divine v144</h3><p>Drive-resident 306-page source document preserved beside the website project.</p></article></a><a href="https://drive.google.com/file/d/1G49E65Epg-nPMmNF4F9geP_qckKeOGjF/view" target="_blank" rel="noopener"><article class="card source-card"><div class="filetype">PDF</div><h3>Hypergendered Logic</h3><p>Drive-resident 293-page formal treatise preserved beside the website project.</p></article></a><a href="https://drive.google.com/drive/folders/1k6fpEF3Zi_tBhtWRUR7wCs8NbKojkCpq" target="_blank" rel="noopener"><article class="card source-card"><div class="filetype">DRIVE</div><h3>Editable project source</h3><p>HTML, CSS, JavaScript, structured canon data, artwork and a complete ZIP are stored in the Arthitean Codex Website folder.</p></article></a></div>
<div class="section-head"><h2>Completeness</h2></div><div class="stats-strip"><div class="stat"><b>${m.stats.divine_paragraphs}</b><span>Divine paragraphs</span></div><div class="stat"><b>${m.stats.divine_tables}</b><span>Divine tables</span></div><div class="stat"><b>${m.stats.hgl_pages}</b><span>HGL pages</span></div><div class="stat"><b>${m.stats.hgl_toc_entries}</b><span>HGL TOC nodes</span></div></div>
<div class="warning">This site is deliberately marked <b>noindex / nofollow</b>. It is intended to be accessed through its direct link rather than public search discovery.</div>
<div class="section-head"><h2>Visual provenance</h2><p>The Drive source package preserves the two original comparison plates embedded in Divine v144. The live site uses new vector artwork so every living-canon depiction can include the specified black phoenix wings and monumental Arthitean visual language.</p></div><a class="secondary art-action" href="https://drive.google.com/drive/folders/1k6fpEF3Zi_tBhtWRUR7wCs8NbKojkCpq" target="_blank" rel="noopener"><img src="assets/art/chibi-sources.webp" alt=""><span>Open the Drive project</span></a>`}


// MP-009: MASTERPAGE HUB & DYNAMIC MASTERPAGE RENDERER
async function masterpagesHub(){
  const d = await load('masterpages');
  setCrumb('Masterpages Directory');
  const domains = {};
  d.masterpages.forEach(m => {
    if(!domains[m.domain_name]) domains[m.domain_name] = [];
    domains[m.domain_name].push(m);
  });

  let domainHtml = '';
  for(const [dName, mList] of Object.entries(domains)){
    domainHtml += `<div class="section-head"><h2>${esc(dName)}</h2><p>${mList.length} canonical masterpages</p></div>
    <div class="grid two concept-grid">
      ${mList.map(m => `
        <a class="card concept-card" href="#masterpage:${m.id}">
          <div class="micro">${esc(m.class)}</div>
          <h3>${esc(m.title)}</h3>
          <p>${esc(m.summary)}</p>
          <span class="concept-link">Open masterpage entry →</span>
        </a>
      `).join('')}
    </div>`;
  }

  main.innerHTML = pageIntro('Canonical concept atlas · Source vs explanation · Formal ontology','Masterpages Directory','Authoritative masterpages unifying verbatim source canon, explanatory analysis, mathematical formalization, and character links.','assets/art/chibi-scaling.webp') + `
  <div class="warning"><b>Source-vs-Explanation Invariant:</b> Masterpages enforce strict visual and structural separation between verbatim source canon (gold panels) and non-canonical explanatory commentary (teal panels).</div>
  ${domainHtml}
  `;
}

async function masterpageView(id){
  const d = await load('masterpages');
  const m = d.masterpages.find(x => x.id === id);
  if(!m) return masterpagesHub();
  setCrumb(m.title);

  const canonHtml = (m.source_canon || []).map(p => `<p style="margin-bottom:12px">${esc(p)}</p>`).join('');
  const formalHtml = m.formalization && m.formalization.length ? `
    <div class="section-head"><h2>Formal Compression & Logic</h2></div>
    <div class="formula-stack">
      ${m.formalization.map(f => `<div class="formula">${esc(f)}</div>`).join('')}
    </div>
  ` : '';

  const relatedHtml = m.related_concepts && m.related_concepts.length ? `
    <div class="section-head"><h2>Related Masterpages</h2></div>
    <div class="concept-nav">
      ${m.related_concepts.map(cid => `<a href="#masterpage:${cid}">${esc(cid)}</a>`).join('')}
    </div>
  ` : '';

  const charsHtml = m.related_characters && m.related_characters.length ? `
    <div class="section-head"><h2>Embodied & Associated Characters</h2></div>
    <div class="grid three">
      ${m.related_characters.map(cslug => {
        const canonical = {
          'empress-rhayhara':'rhayhara',
          'asmouth':'asmouth-varvadeil',
          'annaris':'annaris-deyhamora',
          'orotus':'holy-black-phoenix',
          'qai\'lyth':'qailyth'
        }[cslug] || cslug;
        const href = canonical === 'rhayhara' ? '#rhayhara' : `#character:${canonical}`;
        return `
        <a class="card clickable" href="${href}">
          <div class="micro">CANONICAL EMBODIMENT</div>
          <h3>${esc(canonical.replace(/-/g, ' ').toUpperCase())}</h3>
          <span class="concept-link">View character dossier →</span>
        </a>`;
      }).join('')}
    </div>
  ` : '';

  main.innerHTML = pageIntro(m.class, m.title, m.summary, 'assets/art/chibi-scaling.webp') + `
    <div class="concept-nav"><a href="#masterpages">← Masterpages directory</a><a href="#masterpages">${esc(m.domain_name)}</a></div>

    <div class="section-head"><h2 style="color:#FFD700">Verbatim Source Canon</h2><p>Primary authoritative text, normalized only for typography.</p></div>
    <div class="card" style="border-left:4px solid #FFD700; background:rgba(255,215,0,0.04)">${canonHtml || '<p>No verbatim fragment recorded.</p>'}</div>

    <div class="section-head"><h2 style="color:#00FFCC">Explanatory & Causal Analysis</h2><p>Non-canonical interpretive analysis to make the underlying mechanics inspectable.</p></div>
    <div class="card" style="border-left:4px solid #00FFCC; background:rgba(0,255,204,0.04)">
      <div class="micro">INTERPRETIVE LAYER · EXPLANATION ONLY</div>
      <p>${esc(m.explanation || 'No secondary analysis recorded.')}</p>
    </div>

    ${formalHtml}

    ${m.commonly_confused_with ? `
    <div class="section-head"><h2>Commonly Confused With</h2><p>Semantic boundary disambiguation to prevent category errors.</p></div>
    <div class="card" style="border-left:4px solid #FF3366; background:rgba(255,51,102,0.04)">
      <div class="micro">ANTI-CONFLATION BOUNDARY</div>
      <p>${esc(m.commonly_confused_with)}</p>
    </div>` : ''}

    ${charsHtml}
    ${relatedHtml}

    <div class="section-head"><h2>Documented Source Occurrences</h2></div>
    <div class="card">
      <ul style="margin:0; padding-left:20px; color:#C0C0D0">
        ${(m.source_occurrences || []).map(s => `<li>${esc(s)}</li>`).join('')}
      </ul>
    </div>
  `;
}

/* --- Character Encyclopedia & Dossier Subsystem --- */
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

/* --- Causal Ontology Subsystem --- */
async function causalOntologyView(){
  const d = await load('causalOntology');
  setBreadcrumbs([
    {label:'Sanctuary', href:'#home'},
    {label:'Concepts & Systems', href:'#masterpages'},
    {label:'Causal Ontology'}
  ]);
  
  const ladder = d.hierarchy_ladder || [];
  const concepts = d.concepts || [];
  
  main.innerHTML = pageIntro(
    'Formal Metaphysical Order · Causal & Ontic Precedence',
    'Causal Ontology & Hierarchy',
    d.editorial_note || 'Exhaustive classification of Arthratan causal structures, establishing rigorous precedence between physical causality, paraconceptual rewrites, and ultimate trans-ontic absolutes.',
    'assets/art/chibi-negative-rewrite.webp'
  ) + `
  <div class="section-head"><h2>The 7-Tier Causal Hierarchy Ladder</h2><p>Ascending levels of ontological authority and resistance to retrospective alteration.</p></div>
  <div class="ontology-ladder-grid">
    ${ladder.map((rung, i) => `
      <div class="ontology-rung-card" style="border-top: 3px solid ${['#4fd1c5','#63b3ed','#9f7aea','#b794f4','#d6bcfa','#f6ad55','#e4b76f'][i % 7]}">
        <div class="micro">LEVEL ${rung.level || i + 1}</div>
        <b>${esc(rung.tier || rung.name)}</b>
        <p>${esc(rung.description || rung.scope)}</p>
      </div>
    `).join('')}
  </div>
  
  <div class="section-head"><h2 style="color:#FFD700">Core Causal Concepts & Formalisms</h2></div>
  <div class="grid two">
    ${concepts.map(c => `
      <div class="card" style="border-left: 4px solid #00FFCC; background:rgba(0,255,204,0.03)">
        <div class="micro">${esc(c.class || 'CAUSAL OPERATOR')}</div>
        <h3>${esc(c.name)}</h3>
        <p style="margin-bottom:10px">${esc(c.canon_definition || c.clarification)}</p>
        ${c.formal_logic ? `<div class="formula" style="font-size:12px; margin:8px 0">${esc(c.formal_logic)}</div>` : ''}
        ${c.commonly_confused_with ? `<small style="color:#ff88a3; display:block; margin-top:8px"><b>Anti-Conflation:</b> ${esc(c.commonly_confused_with)}</small>` : ''}
      </div>
    `).join('')}
  </div>
  
  <div class="concept-nav" style="margin-top:28px">
    <a href="#scaling">Metagovernance &amp; Scaling →</a>
    <a href="#negative-rewrite">Negative Rewrite →</a>
    <a href="#masterpages">Masterpages Directory →</a>
  </div>
  `;
}

/* --- INDEX-002: A-Z Site Index & Directory Subsystem --- */
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

/* --- Route Not Found / 404 Recovery Subsystem (IA-F02) --- */
function routeNotFound(hash){
  setBreadcrumbs([
    {label:'Sanctuary', href:'#home'},
    {label:'Route Not Found'}
  ]);
  
  main.innerHTML = `
  <section class="not-found-card">
    <div class="micro" style="color:#ff88a3; letter-spacing:0.18em">INFORMATION ARCHITECTURE · NAVIGATION RECOVERY</div>
    <h2>Codex Route Not Found</h2>
    <p>The requested route destination <span class="not-found-code">#${esc(hash)}</span> was not found in the canonical route registry or may have been renamed during living-canon consolidation.</p>
    
    <div style="max-width:480px; margin:0 auto 20px">
      <form action="/search/" method="get" role="search">
        <div class="hero-actions" style="display:flex; gap:8px">
          <input name="q" value="${esc(hash.replace(/[^a-zA-Z0-9\s]/g, ' '))}" type="search" placeholder="Search the Codex for this term..." style="flex:1; border:1px solid #4a3b63; background:#09080c; color:#eee; border-radius:10px; padding:10px 14px">
          <button type="submit" class="primary">Search</button>
        </div>
      </form>
    </div>
    
    <div class="recovery-actions">
      <a class="primary art-action" href="#home"><img src="assets/art/chibi-codex.webp" alt=""><span>Return to Sanctuary</span></a>
      <a class="art-action" href="#index" style="background:#1e172a; border:1px solid #4a3b63; color:#e2e8f0"><img src="assets/art/chibi-search.webp" alt=""><span>Browse A–Z Site Index</span></a>
      <a class="art-action" href="#masterpages" style="background:#1e172a; border:1px solid #4a3b63; color:#e2e8f0"><img src="assets/art/chibi-scaling.webp" alt=""><span>Masterpages Directory</span></a>
      <a class="art-action" href="#characters" style="background:#1e172a; border:1px solid #4a3b63; color:#e2e8f0"><img src="assets/art/chibi-arthiteans.webp" alt=""><span>Character Encyclopedia</span></a>
      <a class="art-action" href="#stories" style="background:#1e172a; border:1px solid #4a3b63; color:#e2e8f0"><img src="assets/art/chibi-sources.webp" alt=""><span>Story &amp; Thread Archive</span></a>
    </div>
  </section>
  `;
}

async function router(){
  window.scrollTo(0,0);
  const rawHash = (location.hash||'#home').slice(1);
  const h = rawHash.trim();
  try{
    if(h==='stories'||h.startsWith('transmission:')||h.startsWith('session:')||h.startsWith('unit:'))return;
    if(h.startsWith('masterpage:'))return masterpageView(h.slice(11));
    if(h==='masterpages')return masterpagesHub();
    if(h.startsWith('character:'))return characterView(h.slice(10));
    if(h==='characters')return charactersHub();
    if(h.startsWith('index:'))return siteIndexView(h.slice(6));
    if(h==='index'||h==='glossary')return siteIndexView('');
    if(h==='ontology'||h==='causal-ontology'||h==='causality')return causalOntologyView();
    if(h==='home'||h==='')return home();
    if(h==='atlas')return atlas();
    if(h==='scaling')return scaling();
    if(h==='negative-rewrite')return negativeRewrite();
    if(h==='arthiteans')return arthiteans();
    if(h==='rhayhara')return rhayhara();
    if(h==='hgl')return hgl();
    if(h==='divine')return divine();
    if(h==='hgl-archive')return hglArchive();
    if(h==='search')return searchPage();
    if(h==='sources')return sources();
    if(h.startsWith('divine-section:')){
      setBreadcrumbs([{label:'Sanctuary',href:'#home'},{label:'Divine v144 Archive',href:'#divine'},{label:'Section '+h.split(':')[1]}]);
      return renderDivineArchive(h.split(':')[1]);
    }
    if(h.startsWith('hgl-part:'))return hglArchive(h.split(':')[1]);
    if(h.startsWith('hgl-page-direct:'))return hglDirect(Number(h.split(':')[1]));
    return routeNotFound(rawHash);
  }catch(e){
    console.error(e);
    main.innerHTML=`<div class="card"><h3>Codex rendering error</h3><p>${esc(e.message)}</p></div>`;
  }
}
window.addEventListener('hashchange',router);
$('#shareBtn').onclick=async()=>{try{await navigator.clipboard.writeText(location.href);toast('Current view link copied')}catch{toast('Copy unavailable — use browser share')}};
$('#openNav').onclick=()=>$('#sidebar').classList.add('open');
$('#closeNav').onclick=()=>$('#sidebar').classList.remove('open');
document.querySelectorAll('#nav a').forEach(a=>a.addEventListener('click',()=>$('#sidebar').classList.remove('open')));
router();

