// End-to-end test of site/simulator.html: drives the simulated hardware through every demo path.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({headless:true,channel:process.env.CHROME_CHANNEL||undefined});try{
 const base=(process.env.TEST_URL||'http://127.0.0.1:8765/').replace(/\/?$/,'/');
 for(const width of [1366,390]){
  const p=await b.newPage({viewport:{width,height:900}}),errors=[];
  p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(m.type()==='error'&&!/fonts\.(googleapis|gstatic)/.test(m.text()+' '+(m.location().url||'')))errors.push(m.text()+' '+(m.location().url||''))});
  await p.goto(base+'simulator.html');await p.waitForFunction(()=>window.saayaSim);await p.evaluate(()=>window.saayaSim.ready);
  assert.match(await p.textContent('#wasm-chip'),/WebAssembly ✓/);
  const S=()=>p.evaluate(()=>window.saayaSim.state()),adv=(ms)=>p.evaluate(m=>window.saayaSim.advance(m),ms);
  await p.evaluate(()=>{saayaSim.pause(true);saayaSim.build('field');saayaSim.set({seatT:33,outT:35.5,seatRH:50,outRH:45,roofT:41,waterLow:false})});
  await adv(6000);let s=await S();
  assert.equal(s.duty,50,'auto fan at 50 % above 32 °C');assert.ok(s.rpm>1000,`tach rpm ${s.rpm}`);assert.equal(s.oled[0],'SAAYA NODE / MEASURED');
  assert.equal(s.lastJson.quality,'valid');assert.ok(s.lastJson.watts>0.5&&s.lastJson.watts<4.5,`watts ${s.lastJson.watts}`);assert.equal(s.lastJson.duty,50);
  // heat cut-off at 39 C, manual still allowed
  await p.evaluate(()=>saayaSim.set({seatT:40}));await adv(3000);s=await S();
  assert.equal(s.duty,0,'auto stops at >= 39 °C');assert.equal(s.oled[4],'HOT: FAN MAY ADD HEAT');assert.equal(s.lastJson.fan_advice,'avoid');
  await p.evaluate(()=>saayaSim.press('MODE'));await adv(3000);s=await S();assert.ok(s.manual&&s.duty===70,'manual 70 % never blocked');
  await p.evaluate(()=>saayaSim.press('MODE'));await adv(500);
  await p.evaluate(()=>saayaSim.set({seatT:38.6}));await adv(3000);assert.equal((await S()).duty,0,'no restart above 38.5 °C');
  await p.evaluate(()=>saayaSim.set({seatT:38.2}));await adv(3000);assert.equal((await S()).duty,50,'restart below 38.5 °C');
  // stalled fan -> feedback fault
  await p.evaluate(()=>saayaSim.fault('fanBlocked',true));await adv(5000);s=await S();
  assert.ok(s.fanFault&&s.led,'fan feedback fault');assert.equal(s.oled[4],'FAN FEEDBACK FAULT');
  await p.evaluate(()=>saayaSim.fault('fanBlocked',false));await adv(5000);assert.ok(!(await S()).fanFault,'fault clears when tach returns');
  // tach wire cut also detected
  await p.evaluate(()=>saayaSim.fault('tachCut',true));await adv(5000);assert.ok((await S()).fanFault,'cut tach wire detected');
  await p.evaluate(()=>saayaSim.fault('tachCut',false));await adv(4000);
  // help latch survives a power cut, only ACK clears it
  await p.evaluate(()=>saayaSim.press('HELP'));await adv(1500);s=await S();
  assert.ok(s.help&&s.nvsHelp&&s.led);assert.equal(s.oled[4],'HELP REQUEST LATCHED');
  await p.evaluate(()=>saayaSim.powerCut());await adv(1000);assert.equal((await S()).powered,false);
  await adv(3000);s=await S();assert.ok(s.powered&&s.help,'help restored from flash after reboot');
  await p.evaluate(()=>saayaSim.press('ACK'));await adv(1500);s=await S();assert.ok(!s.help&&!s.nvsHelp,'ACK clears help');
  // sensor fault inhibits automatic fan and sends nulls
  await p.evaluate(()=>{saayaSim.set({seatT:34});saayaSim.fault('seatOff',true)});await adv(3000);s=await S();
  assert.ok(s.sensorFault&&s.duty===0);assert.equal(s.lastJson.temp,null);assert.equal(s.lastJson.quality,'invalid');assert.equal(s.oled[4],'SENSOR FAULT');
  await p.evaluate(()=>saayaSim.fault('seatOff',false));await adv(4000);s=await S();assert.ok(!s.sensorFault&&s.duty===50,'recovers after reconnection');
  // INA219 and water
  await p.evaluate(()=>{saayaSim.fault('inaOff',true);saayaSim.set({waterLow:true})});await adv(2000);s=await S();
  assert.equal(s.lastJson.watts,null);assert.equal(s.lastJson.water,'low');assert.equal(s.oled[3],'WATER LOW / CHECK');
  // default (bench) build has no automatic fan
  await p.evaluate(()=>{saayaSim.fault('inaOff',false);saayaSim.set({waterLow:false});saayaSim.build('bench')});await adv(3000);assert.equal((await S()).duty,0,'default build: no auto');
  // physical button on the SVG works with a real click
  await p.evaluate(()=>saayaSim.pause(false));
  const help=p.locator('#board .btn[aria-label="HELP button"]');await help.scrollIntoViewIfNeeded();await help.dispatchEvent('pointerdown');await p.waitForTimeout(250);await help.dispatchEvent('pointerup');
  await p.waitForFunction(()=>window.saayaSim.state().help,null,{timeout:5000});
  // scenario + day player run without errors
  await p.click('[data-scn="day"]');await p.waitForTimeout(1500);
  assert.ok((await p.textContent('#events')).includes('Playing a modelled Vellore May day'));
  assert.ok((await p.textContent('#serial')).includes('"schema_version":1'));
  const overflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert(overflow<=1,`overflow ${overflow}`);
  if(width===1366)await p.screenshot({path:process.env.SIM_SHOT||'/tmp/simulator.png',fullPage:false});
  assert.deepEqual(errors,[]);await p.close();
 }
 console.log('PASS simulator: auto band, 39 °C stop and 38.5 °C restart, manual never blocked, stall and cut-tach faults, help latch through power cut, ACK, sensor fault nulls, INA219/water, default build, SVG button, day player, mobile width');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
