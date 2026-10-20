// Print docs/node/SAAYA_Node_IoT_Design.html to PDF with Chromium (Playwright).
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
const src=path.resolve(__dirname,'../docs/node/SAAYA_Node_IoT_Design.html');
await p.goto('file://'+src,{waitUntil:'networkidle'});
await p.pdf({path:src.replace('.html','.pdf'),format:'A4',landscape:true,printBackground:true,preferCSSPageSize:true});
await b.close();console.log('PDF written')})();
