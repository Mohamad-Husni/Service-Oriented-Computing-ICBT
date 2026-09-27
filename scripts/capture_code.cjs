const {chromium}=require('playwright');
const fs=require('fs');const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 let page=await browser.newPage();
 const dest='evidence/report-v2';
 const manifest=JSON.parse(fs.readFileSync(dest+'/manifest.json','utf8')).filter(x=>x.type==='ui');
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
 fs.writeFileSync(dest+'/manifest.json',JSON.stringify(manifest,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
