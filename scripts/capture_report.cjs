const {chromium}=require('playwright');
const fs=require('fs');const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 let page=await browser.newPage({viewport:{width:390,height:950},deviceScaleFactor:3});
 const dest='evidence/report-v2';fs.mkdirSync(dest,{recursive:true});const manifest=[];
 async function shot(selector,name,caption){const el=page.locator(selector);await el.scrollIntoViewIfNeeded();const text=await el.evaluate(node=>{
 const words=[];
 function walk(n){
  if(n.nodeType===3){if(n.textContent.trim())words.push(n.textContent.trim());return;}
  if(n.nodeType!==1||getComputedStyle(n).display==='none')return;
  if(n.tagName==='SELECT'){words.push(n.selectedOptions[0]?.textContent||'');return;}
  if(n.tagName==='INPUT'){words.push(n.type==='password'?'':n.value||(n.type==='datetime-local'?'yyyy-mm-dd, --:-- --':''));return;}
  for(const child of n.childNodes)walk(child);
 }
 walk(node);return words.filter(Boolean).join(' ');
});await el.screenshot({path:`${dest}/${name}.png`});manifest.push({name,path:`${dest}/${name}.png`,text,caption,type:'ui'});}
 await page.goto('http://127.0.0.1:5200');
 await shot('#login-form','ui-login','Account role and sign in form');
 await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.waitForFunction(()=>document.getElementById('balance').textContent!=='—');
 await shot('.card.balance','ui-balance','Current balance returned by the payment service');
 await page.locator('#amount').fill('12.50');await page.locator('#reference').fill('REPORT-'+Date.now());
 await shot('#payment-form','ui-payment','Customer payment form with amount and reference');
 await page.locator('#pay-button').click();await page.waitForFunction(()=>document.getElementById('message').textContent.includes('New receipt'));await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 await shot('#message','ui-receipt','Receipt returned after the demonstration payment');
 await shot('.card.balance','ui-updated-balance','Updated balance after the payment');
 await page.locator('#logout').click();await page.locator('#login').waitFor();await page.locator('#username').selectOption('operator');await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.locator('#reading-form').waitFor();await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 await shot('#reading-form','ui-operator','Operator form for a cumulative meter reading');
 await shot('#meter-history','ui-meter','Latest recorded meter values and timestamps');
 await page.locator('#logout').click();await page.locator('#login').waitFor();await page.locator('#username').selectOption('partner');await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.locator('#lookup').waitFor();
 await shot('#lookup','ui-partner','Partner account lookup uses the same service');
 // These are screenshots of a source viewer, with exact source text and real line numbers.
 const extracts=[
 {name:'code-validation',file:'src/Water.Shared/Domain.cs',start:12,end:18,caption:'Money validation in the shared library'},
 {name:'code-retry',file:'src/Water.Payments/PaymentRepository.cs',start:49,end:55,caption:'Returning a receipt when a request is repeated'},
 {name:'code-endpoint',file:'src/Water.Payments/Program.cs',start:23,end:28,caption:'Payment endpoint checks access before recording'},
 {name:'code-client',file:'src/Water.Desktop/PaymentClient.cs',start:14,end:15,caption:'The desktop client calls the shared HTTP service'}];
 await page.close(); page=await browser.newPage({viewport:{width:720,height:1200},deviceScaleFactor:3});
 const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
 for(const item of extracts){const lines=fs.readFileSync(item.file,'utf8').split('\n').slice(item.start-1,item.end);const text=lines.join('\n');
 await page.setContent(`<html><head><style>*{box-sizing:border-box}body{margin:0;background:white;color:#172f3b;font-family:'Times New Roman';}article{width:720px;border:1px solid #becdd2;border-radius:8px;overflow:hidden;}header{padding:18px 22px;background:#edf3f5;font-size:22px;font-weight:bold;}main{padding:14px 12px;}section{display:grid;grid-template-columns:42px 1fr;gap:10px;line-height:1.3;font-size:24px;}b{font-weight:normal;text-align:right;color:#697e86;}pre{margin:0;font:inherit;white-space:pre-wrap;overflow-wrap:anywhere;}footer{font-size:22px;padding:12px 22px;border-top:1px solid #dbe4e7;}</style></head><body><article><header>${esc(path.basename(path.dirname(item.file))+'/'+path.basename(item.file))}</header><main>${lines.map((l,i)=>`<section><b>${i+item.start}</b><pre>${esc(l)}</pre></section>`).join('')}</main><footer>Exact source lines ${item.start} to ${item.end}</footer></article></body></html>`);
 await page.locator('article').screenshot({path:`${dest}/${item.name}.png`});manifest.push({...item,path:`${dest}/${item.name}.png`,text:await page.locator('article').innerText(),rawSource:text,type:'code'});
 }
 const build=fs.readFileSync('evidence/build.log','utf8').split('\n').filter(x=>/Build succeeded|Warning\(s\)|Error\(s\)/.test(x)).join('\n');
 await page.setContent(`<html><body style="margin:0"><pre style="margin:0;padding:24px;border:1px solid #bacbd0;background:#f3f6f7;font:28px/1.5 'Times New Roman';width:700px">${esc(build)}</pre></body></html>`);await page.locator('pre').screenshot({path:`${dest}/build-output.png`});manifest.push({name:'build-output',path:`${dest}/build-output.png`,text:build,caption:'Recorded solution build output',type:'output'});
 fs.writeFileSync(`${dest}/manifest.json`,JSON.stringify(manifest,null,2));await browser.close();console.log('Captured',manifest.length,'source and application images.');
})().catch(e=>{console.error(e);process.exit(1)});
