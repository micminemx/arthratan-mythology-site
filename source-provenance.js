(()=>{
const EXACT_SOURCES={
  divine:{
    id:'1qW4UR7CGTLLW1JqfrOrN1uRHQOnRoVKE',
    url:'https://docs.google.com/document/d/1qW4UR7CGTLLW1JqfrOrN1uRHQOnRoVKE/edit',
    title:'Divine v144 · exact DOCX',
    filename:'Divine_v144.docx',
    description:'Exact Drive source: Divine_v144.docx · 306-page authoritative Divine v144 edition.',
    linkLabel:'Open exact Divine_v144.docx source'
  },
  hgl:{
    id:'1G49E65Epg-nPMmNF4F9geP_qckKeOGjF',
    url:'https://drive.google.com/file/d/1G49E65Epg-nPMmNF4F9geP_qckKeOGjF/view',
    title:'Hypergendered Logic · 17 Aug 2026',
    filename:'Hypergendered_Logic_17_Aug_2026.pdf',
    description:'Exact Drive source: Hypergendered_Logic_17_Aug_2026.pdf · 293-page authoritative HGL edition dated 17 August 2026.',
    linkLabel:'Open exact HGL 17 Aug 2026 PDF source'
  }
};

function exactSourceLink(source,key){
  const a=document.createElement('a');
  a.className='tx-source-link';
  a.href=source.url;
  a.target='_blank';
  a.rel='noopener';
  a.dataset.exactSource=key;
  a.textContent=source.linkLabel;
  a.setAttribute('aria-label',`${source.linkLabel} (opens in a new tab)`);
  return a;
}

function enhanceSourceCards(main){
  main.querySelectorAll('.source-grid > a').forEach(anchor=>{
    const source=Object.values(EXACT_SOURCES).find(x=>anchor.href.includes(x.id));
    if(!source||anchor.dataset.exactSourceVerified==='true')return;
    const heading=anchor.querySelector('h3');
    const copy=anchor.querySelector('p');
    if(heading)heading.textContent=source.title;
    if(copy)copy.textContent=source.description;
    anchor.title=`Open exact source: ${source.filename}`;
    anchor.dataset.exactSourceVerified='true';
  });
}

function enhanceArchiveHeader(main){
  const eyebrow=main.querySelector('.archive-art-head .eyebrow');
  if(!eyebrow)return;
  const text=eyebrow.textContent||'';
  const key=text.includes('Divine v144')?'divine':text.includes('Hypergendered Logic')?'hgl':null;
  if(!key)return;
  const source=EXACT_SOURCES[key];
  const header=eyebrow.closest('.archive-art-head');
  const note=header?.nextElementSibling;
  if(!note?.classList?.contains('source-note')||note.querySelector(`[data-exact-source="${key}"]`))return;
  note.append(document.createTextNode(' · '),exactSourceLink(source,key));
}

function enhance(){
  const main=document.getElementById('main');
  if(!main)return;
  enhanceSourceCards(main);
  enhanceArchiveHeader(main);
}

const main=document.getElementById('main');
if(!main)return;
let queued=false;
const schedule=()=>{
  if(queued)return;
  queued=true;
  requestAnimationFrame(()=>{queued=false;enhance()});
};
new MutationObserver(schedule).observe(main,{childList:true,subtree:true});
window.addEventListener('hashchange',schedule);
enhance();
})();
