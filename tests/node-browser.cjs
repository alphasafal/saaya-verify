const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({headless:true,channel:process.env.CHROME_CHANNEL||undefined});try{
 const base=(process.env.TEST_URL||'http://127.0.0.1:8765/').replace(/\/?$/,'/');
 for(const width of [1366,390]){const p=await b.newPage({viewport:{width,height:900}}),errors=[];p.on('pageerror',e=>errors.push(String(e)));
  await p.goto(base+'node.html');await p.waitForSelector('body[data-ready="1"]',{timeout:60000});
  for(const v of ['internals','front','bottom','assembly']){await p.click(`[data-view="${v}"]`);assert.equal(await p.locator(`[data-view="${v}"]`).getAttribute('aria-pressed'),'true')}
  const overflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert(overflow<=1,`overflow ${overflow}`);
  const r=await p.request.get(base+'downloads/SAAYA_Node_IoT_Design.pdf');assert.equal(r.status(),200);
  assert.deepEqual(errors,[]);await p.close()}
 console.log('PASS node: 3D model views, PDF download, mobile width, no JS errors');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
