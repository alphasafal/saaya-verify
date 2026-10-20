const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({headless:true,channel:process.env.CHROME_CHANNEL||undefined});try{
 const base=(process.env.TEST_URL||'http://127.0.0.1:8765/').replace(/\/?$/,'/');
 for(const width of [1366,390]){
  const p=await b.newPage({viewport:{width,height:900}}),errors=[];p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await p.goto(base+'defense.html');
  await p.locator('#design-table table tbody tr').first().waitFor();
  assert.equal(await p.locator('#design-table tbody tr').count(),7,'every roof option rendered');
  assert.match(await p.locator('#k-shade').textContent(),/^\d+\.\d K$/);
  assert.match(await p.locator('#cost-fullsize').textContent(),/₹/);
  assert.match(await p.locator('#aggregate-outcome').textContent(),/SIMULATED/);
  assert((await p.locator('#mrt-chart svg rect').count())>=7);
  assert((await p.locator('#adr details').count())>=10);
  assert((await p.locator('#qa details').count())>=8);
  assert(!(await p.content()).includes('RESEARCH-FILL'),'no unfilled sections');
  await p.locator('#adr summary').first().click();assert(await p.locator('#adr details').first().evaluate(d=>d.open));
  const overflow=await p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);assert(overflow<=1,`horizontal overflow ${overflow}px at ${width}`);
  assert.deepEqual(errors,[]);await p.close();
 }
 console.log('PASS defense: model tables, evidence chart, costs, decisions, questions, mobile width, no JS errors');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
