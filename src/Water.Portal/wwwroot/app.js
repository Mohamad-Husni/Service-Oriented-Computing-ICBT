const $ = id => document.getElementById(id);
let session, account, loading = false;
const money = n => new Intl.NumberFormat('en-LK',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n);
const date = s => new Date(s).toLocaleString('en-GB',{timeZone:'Asia/Colombo',dateStyle:'medium',timeStyle:'short'});
function notify(text,error=false){$('message').textContent=text;$('message').classList.remove('hidden');$('message').classList.toggle('error',error);}
async function api(path,body){
 const response=await fetch(path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json','X-WaterLink':'1'},body:body?JSON.stringify(body):undefined});
 const data=await response.json().catch(()=>({}));
 if(!response.ok)throw new Error(data.title || (response.status===401?'Please sign in with valid credentials.':'The request could not be completed.'));
 return data;
}
function newReference(){ $('reference').value='WEB-'+crypto.randomUUID().slice(0,18); }
function row(values){const tr=document.createElement('tr');values.forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});return tr;}
async function refresh(){
 if(loading)return;loading=true;$('refresh').disabled=true;
 const base=`/api/v1/accounts/${encodeURIComponent(account)}`;
 $('balance').textContent='—';$('paid').textContent='—';$('consumption').textContent='—';$('due').textContent='';$('as-of').textContent='';$('payments').replaceChildren();$('meter-history').replaceChildren();$('empty').classList.add('hidden');
 const results=await Promise.allSettled([api('/gateway/payments'+base+'/balance'),api('/gateway/payments'+base+'/payments'),session.role==='partner'?Promise.resolve(null):api('/gateway/usage'+base+'/usage')]);
 if(results[0].status==='fulfilled'){const b=results[0].value;$('balance').textContent=money(b.outstanding);$('paid').textContent=money(b.paid);$('due').textContent=`Due ${b.dueDate}`;$('as-of').textContent='Checked '+date(b.asOf);$('amount').max=b.outstanding;}
 if(results[1].status==='fulfilled'){const payments=results[1].value;payments.forEach(p=>$('payments').append(row([date(p.recordedAt),p.reference,p.channel,money(p.amount)])));$('empty').classList.toggle('hidden',payments.length>0);}
 if(results[2].status==='fulfilled'&&results[2].value){const u=results[2].value;$('consumption').textContent=u.consumption.toFixed(3);$('read-at').textContent='Last reading '+date(u.readings[0].recordedAt);$('account-label').textContent=`${u.customerName} · Account ${account} · ${u.address}`;u.readings.forEach(r=>{const item=document.createElement('div');item.className='meter-item';const value=document.createElement('strong');value.textContent=r.meterValue.toFixed(3)+' m³';item.append(value,document.createTextNode(date(r.recordedAt)));$('meter-history').append(item);});}
 if(session.role==='partner'){$('read-at').textContent='Usage is private to the customer';$('account-label').textContent='Partner collection · Account '+account;}
 const errors=results.filter(r=>r.status==='rejected');if(errors.length)notify(errors.map(r=>r.reason.message).join(' '),true);
 loading=false;$('refresh').disabled=false;
}
async function enter(s){session=s;account=s.account||$('account').value;$('login').classList.add('hidden');$('dashboard').classList.remove('hidden');$('logout').classList.remove('hidden');$('identity').textContent=s.name+' · '+s.role;$('greeting').textContent=s.role==='customer'?'Your water account':s.role==='partner'?'Partner collections':'Meter operations';$('lookup').classList.toggle('hidden',s.role==='customer');$('payment-panel').classList.toggle('hidden',s.role==='operator');$('reading-form').classList.toggle('hidden',s.role!=='operator');$('usage').classList.toggle('hidden',s.role==='partner');newReference();await refresh();}
$('login-form').addEventListener('submit',async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{await enter(await api('/session',{username:$('username').value,password:$('password').value}));$('password').value='';$('message').classList.add('hidden');}catch(err){notify(err.message,true);}finally{button.disabled=false;}});
$('logout').addEventListener('click',async()=>{await api('/logout',{});location.reload();});
$('refresh').addEventListener('click',refresh);
$('lookup').addEventListener('submit',async e=>{e.preventDefault();account=$('account').value;await refresh();});
$('payment-form').addEventListener('submit',async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{const result=await api('/gateway/payments/api/v1/payments',{accountId:account,amount:Number($('amount').value),reference:$('reference').value});notify(`${result.replay?'Existing':'New'} receipt ${result.receipt.id} · LKR ${money(result.receipt.amount)}`);$('amount').value='';newReference();await refresh();}catch(err){notify(err.message,true);}finally{button.disabled=false;}});
$('reading-form').addEventListener('submit',async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{await api(`/gateway/usage/api/v1/accounts/${encodeURIComponent(account)}/readings`,{meterValue:Number($('meter').value),recordedAt:new Date($('recorded-at').value).toISOString()});notify('Meter reading saved.');await refresh();}catch(err){notify(err.message,true);}finally{button.disabled=false;}});
api('/session').then(enter).catch(()=>{});
