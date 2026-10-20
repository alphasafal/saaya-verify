// node scripts/print_report.cjs in.html out.pdf  -- A4 print with CSS @page settings
const {chromium}=require('playwright');
(async()=>{const [src,out]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+src,{waitUntil:'networkidle'});await p.pdf({path:out,printBackground:true,preferCSSPageSize:true});await b.close()})();
