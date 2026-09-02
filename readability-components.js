(()=> {
'use strict';
const root=document.querySelector('#main');
if(!root)return;
let scheduled=false;

const slug=s=>String(s||'section').normalize('NFKD').toLowerCase()
  .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,72)||'section';

function uniqueId(base,el){
  let id=base,n=2;
  while(document.getElementById(id)&&document.getElementById(id)!==el)id=`${base}-${n++}`;
  return id;
}

function copyText(text,button){
  const done=()=>{const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,1200)};
  if(navigator.clipboard?.writeText)return navigator.clipboard.writeText(text).then(done).catch(()=>fallback());
  fallback();
  function fallback(){
    const ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';
    document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch{}ta.remove();
  }
}

function enhanceFormula(el){
  if(el.dataset.readabilityEnhanced)return;
  el.dataset.readabilityEnhanced='formula';el.tabIndex=0;
  if(!el.getAttribute('aria-label'))el.setAttribute('aria-label','Formula or formal expression');
  const button=document.createElement('button');
  button.type='button';button.className='formula-copy';button.textContent='Copy';
  button.setAttribute('aria-label','Copy formula');
  button.addEventListener('click',e=>{e.stopPropagation();copyText(el.textContent.replace(/^Copy/,'').trim(),button)});
  el.appendChild(button);
}

function enhanceTable(table){
  if(table.closest('.readability-table-wrap'))return;
  const wrap=document.createElement('div');wrap.className='readability-table-wrap';wrap.tabIndex=0;
  wrap.setAttribute('role','region');
  const caption=table.querySelector('caption')?.textContent?.trim();
  wrap.setAttribute('aria-label',caption?`Scrollable table: ${caption}`:'Scrollable table');
  table.parentNode.insertBefore(wrap,table);wrap.appendChild(table);
}

function enhanceDiagram(el){
  if(el.dataset.readabilityEnhanced)return;
  el.dataset.readabilityEnhanced='diagram';el.tabIndex=0;
  if(!el.getAttribute('role'))el.setAttribute('role','group');
  if(!el.getAttribute('aria-label'))el.setAttribute('aria-label','Scrollable concept diagram');
}
function enhanceLadder(el){
  if(el.dataset.readabilityEnhanced)return;
  el.dataset.readabilityEnhanced='ladder';el.setAttribute('role','list');
  [...el.children].filter(x=>x.classList.contains('rung')).forEach(x=>x.setAttribute('role','listitem'));
}

function enhanceHeadings(){
  const route=(location.hash||'#home').replace(/^#/,'').split(':')[0]||'home';
  const heads=[...root.querySelectorAll('h2')].filter(h=>!h.closest('.tx-source'));
  heads.forEach((h,i)=>{
    if(!h.id)h.id=uniqueId(`${slug(route)}-${slug(h.textContent)}-${i+1}`,h);
    if(!h.querySelector(':scope > .section-anchor')){
      const a=document.createElement('a');a.className='section-anchor';a.href=`#${h.id}`;a.textContent='#';
      a.setAttribute('aria-label',`Link to ${h.textContent.trim()}`);a.addEventListener('click',e=>{
        e.preventDefault();history.replaceState(null,'',`${location.pathname}${location.search}#${h.id}`);
        h.scrollIntoView({block:'start'});h.focus?.({preventScroll:true});
      });h.appendChild(a);
    }
  });
  const eligible=heads.filter(h=>h.textContent.trim().length&&h.offsetParent!==null);
  const old=root.querySelector(':scope > .local-toc[data-generated="ui-002"]');
  if(eligible.length<3){old?.remove();return}
  const sig=eligible.map(h=>`${h.id}:${h.textContent.replace('#','').trim()}`).join('|');
  if(old?.dataset.signature===sig)return;
  const nav=document.createElement('nav');nav.className='local-toc';nav.dataset.generated='ui-002';nav.dataset.sticky='true';
  nav.dataset.signature=sig;nav.setAttribute('aria-label','On this page');
  const header=document.createElement('div');header.className='local-toc-header';
  header.innerHTML='<span class="local-toc-title">On this page</span><span class="readability-note">Jump without losing context</span>';
  const links=document.createElement('div');links.className='local-toc-links';
  eligible.forEach(h=>{const a=document.createElement('a');a.href=`#${h.id}`;a.textContent=h.textContent.replace('#','').trim();
    a.addEventListener('click',e=>{e.preventDefault();h.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});history.replaceState(null,'',`${location.pathname}${location.search}#${h.id}`)});links.appendChild(a)});
  nav.append(header,links);
  const intro=root.querySelector(':scope > .page-intro,:scope > .hero,:scope > .transmission-shell > .transmission-hero');
  if(intro?.parentNode===root)intro.insertAdjacentElement('afterend',nav);else root.prepend(nav);
  old?.remove();
}

function enhance(){
  root.querySelectorAll('.formula,.readability-formula').forEach(enhanceFormula);
  root.querySelectorAll('table').forEach(enhanceTable);
  root.querySelectorAll('.diagram').forEach(enhanceDiagram);
  root.querySelectorAll('.ladder').forEach(enhanceLadder);
  root.querySelectorAll('details.readability-derivation,details.derivation').forEach(d=>{
    if(!d.hasAttribute('aria-label'))d.setAttribute('aria-label','Expandable derivation or detail');
  });
  enhanceHeadings();
}

function schedule(){
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{scheduled=false;enhance()});
}
new MutationObserver(schedule).observe(root,{childList:true,subtree:true});
window.addEventListener('hashchange',()=>setTimeout(schedule,0),true);
schedule();
})();
