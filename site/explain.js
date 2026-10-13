let pendingSelection=null;
const frame=document.querySelector('iframe[name="cad-viewer"]');
document.querySelectorAll('.diagram a').forEach(a=>a.addEventListener('click',event=>{const href=a.getAttribute('xlink:href')||a.getAttribute('href');const id=new URL(href,location.href).searchParams.get('part');if(!id)return;event.preventDefault();pendingSelection=id;frame.contentWindow.postMessage({type:'saaya-select',id},location.origin);document.querySelector('#cad').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}));
window.addEventListener('message',e=>{if(e.origin===location.origin&&e.source===frame.contentWindow&&e.data?.type==='saaya-height'&&Number.isFinite(e.data.height))frame.style.height=Math.max(700,Math.min(6000,e.data.height))+'px';});

window.addEventListener('message',e=>{if(e.origin===location.origin&&e.source===frame.contentWindow&&e.data?.type==='saaya-ready'&&pendingSelection)frame.contentWindow.postMessage({type:'saaya-select',id:pendingSelection},location.origin);});
