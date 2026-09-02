(()=> {
'use strict';
const root=document.querySelector('#main');
if(!root)return;
let scheduled=false,lastAppliedSection='';

const slug=s=>String(s||'section').normalize('NFKD').toLowerCase()
  .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,72)||'section';

function uniqueId(base,el){
  let id=base,n=2;
  while(document.getElementById(id)&&document.getElementById(id)!==el)id=`${base}-${n++}`;
  return id;
}
function sectionUrl(id){
  const url=new URL(location.href);
  url.searchParams.set('section',id);
  url.hash=location.hash||'#home';
  return `${url.pathname}${url.search}${url.hash}`;
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
function formulaText(el){
  const clone=el.cloneNode(true);
  clone.querySelectorAll('.formula-copy').forEach(x=>x.remove());
  return clone.textContent.trim();
}
function enhanceFormula(el){
  if(el.dataset.readabilityEnhanced)return;
  el.dataset.readabilityEnhanced='formula';el.tabIndex=0;
  if(!el.getAttribute('aria-label'))el.setAttribute('aria-label','Formula or formal expression');
  const button=document.createElement('button');
  button.type='button';button.className='formula-copy';button.textContent='Copy';
  button.setAttribute('aria-label','Copy formula');
  button.addEventListener('click',e=>{e.stopPropagation();copyText(formulaText(el),button)});
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
function focusHeading(h,smooth=false){
  h.scrollIntoView({behavior:smooth&&!matchMedia('(prefers-reduced-motion: reduce)').matches?'smooth':'auto',block:'start'});
  h.focus({preventScroll:true});
}
function enhanceHeadings(){
  const route=(location.hash||'#home').replace(/^#/,'').split(':')[0]||'home';
  const heads=[...root.querySelectorAll('h2')].filter(h=>!h.closest('.tx-source'));
  heads.forEach((h,i)=>{
    const label=h.textContent.trim();
    if(!h.id)h.id=uniqueId(`${slug(route)}-${slug(label)}-${i+1}`,h);
    if(!h.hasAttribute('tabindex'))h.tabIndex=-1;
    if(!h.querySelector(':scope > .section-anchor')){
      const a=document.createElement('a');a.className='section-anchor';a.href=sectionUrl(h.id);a.textContent='#';
      a.setAttribute('aria-label',`Link to ${label}`);a.addEventListener('click',e=>{
        e.preventDefault();history.replaceState(null,'',sectionUrl(h.id));focusHeading(h,false);
      });h.appendChild(a);
    }
  });
  const eligible=heads.filter(h=>h.textContent.trim().length&&h.offsetParent!==null);
  const old=root.querySelector(':scope > .local-toc[data-generated="ui-002"]');
  if(eligible.length<3){old?.remove()}else{
    const sig=eligible.map(h=>`${h.id}:${h.textContent.replace('#','').trim()}`).join('|');
    if(old?.dataset.signature!==sig){
      const nav=document.createElement('nav');nav.className='local-toc';nav.dataset.generated='ui-002';nav.dataset.sticky='true';
      nav.dataset.signature=sig;nav.setAttribute('aria-label','On this page');
      const header=document.createElement('div');header.className='local-toc-header';
      header.innerHTML='<span class="local-toc-title">On this page</span><span class="readability-note">Jump without losing context</span>';
      const links=document.createElement('div');links.className='local-toc-links';
      eligible.forEach(h=>{const a=document.createElement('a');a.href=sectionUrl(h.id);a.textContent=h.textContent.replace('#','').trim();
        a.addEventListener('click',e=>{e.preventDefault();history.replaceState(null,'',sectionUrl(h.id));focusHeading(h,true)});links.appendChild(a)});
      nav.append(header,links);
      const intro=root.querySelector(':scope > .page-intro,:scope > .hero,:scope > .transmission-shell > .transmission-hero');
      if(intro?.parentNode===root)intro.insertAdjacentElement('afterend',nav);else root.prepend(nav);
      old?.remove();
    }
  }
  const requested=new URL(location.href).searchParams.get('section');
  if(requested&&requested!==lastAppliedSection){
    const target=document.getElementById(requested);
    if(target&&root.contains(target)){lastAppliedSection=requested;setTimeout(()=>focusHeading(target,false),0)}
  }
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
window.addEventListener('hashchange',()=>{lastAppliedSection='';setTimeout(schedule,0)},true);
schedule();
})();
