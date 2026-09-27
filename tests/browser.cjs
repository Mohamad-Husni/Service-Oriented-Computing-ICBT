const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});const results=[];const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const check=(name,value)=>{results.push({name,passed:!!value});if(!value)throw new Error(name);};
 await page.goto('http://127.0.0.1:'+(process.env.PORT_BASE||'5100'));
 await page.locator('#password').fill('wrong');await page.locator('#login-form button').click();await page.locator('#message.error').waitFor();check('Invalid login rejected',await page.locator('#login').isVisible());
 await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.locator('#dashboard').waitFor();await page.waitForFunction(()=>document.getElementById('balance').textContent!=='—');
 check('Customer dashboard loads',await page.locator('#account-label').textContent().then(t=>t.includes('Amani')));
 await page.locator('#amount').fill('25');await page.locator('#reference').fill('BROWSER-'+Date.now());await page.locator('#pay-button').click();await page.waitForFunction(()=>document.getElementById('message').textContent.includes('receipt'));await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 check('Browser payment produces receipt',(await page.locator('#message').textContent()).includes('25.00'));
 await page.locator('#message').evaluate(e=>e.classList.add('hidden'));
 await page.screenshot({path:'evidence/portal-desktop.png',fullPage:true});
 for(const width of [768,390]){await page.setViewportSize({width,height:1000});check('No horizontal overflow at '+width,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:`evidence/portal-${width}.png`,fullPage:true});}
 await page.locator('#logout').click();await page.locator('#login').waitFor();
 await page.locator('#username').selectOption('partner');await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.locator('#dashboard').waitFor();check('Partner lookup visible',await page.locator('#lookup').isVisible());check('Partner usage hidden',!await page.locator('#usage').isVisible());
 await page.locator('#logout').click();await page.locator('#login').waitFor();await page.locator('#username').selectOption('operator');await page.locator('#password').fill('WaterDemo2026!');await page.locator('#login-form button').click();await page.locator('#reading-form').waitFor();check('Operator meter form visible',await page.locator('#reading-form').isVisible());check('Operator payment form hidden',!await page.locator('#payment-panel').isVisible());
 check('No browser exceptions',errors.length===0);fs.writeFileSync('evidence/browser-results.json',JSON.stringify({tests:results,passed:results.length,total:results.length,errors},null,2));await browser.close();console.log(results);
})().catch(e=>{console.error(e);process.exit(1)});
