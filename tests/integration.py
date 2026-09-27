"""Real HTTP tests against freshly seeded services. Run once before the browser demo."""
import os, json, urllib.request, urllib.error, concurrent.futures, datetime, uuid
results=[]
tokens={'customer':'demo-customer-token-change-me-001','customer2':'demo-customer-token-change-me-002','partner':'demo-partner-token-change-me-001','operator':'demo-operator-token-change-me-001'}
def call(port,path,role='customer',body=None):
 port += int(os.environ.get('PORT_BASE','5100'))-5100
 headers={'Content-Type':'application/json'}
 if role: headers['Authorization']='Bearer '+tokens[role]
 r=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
 try:
  with urllib.request.urlopen(r,timeout=20) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def check(name,condition,detail=''):
 results.append({'name':name,'passed':bool(condition),'detail':detail});print(('PASS ' if condition else 'FAIL ')+name,detail)
a='/api/v1/accounts/100000001';b='/api/v1/accounts/100000002'
check('Unauthenticated denied',call(5102,a+'/balance',None)[0]==401)
check('Customer reads own balance',call(5102,a+'/balance')[0]==200)
check('Cross-account balance denied',call(5102,b+'/balance')[0]==403)
check('Cross-account usage denied',call(5101,b+'/usage')[0]==403)
check('Partner cannot read personal usage',call(5101,a+'/usage','partner')[0]==403)
check('Partner can lookup balance',call(5102,a+'/balance','partner')[0]==200)
check('Missing account returns 404',call(5102,'/api/v1/accounts/999999999/balance','partner')[0]==404)
def payment(amount,ref,account='100000001'):return {'accountId':account,'amount':amount,'reference':ref}
base=call(5102,a+'/balance')[1]['outstanding'];ref='TEST-'+uuid.uuid4().hex
code,first=call(5102,'/api/v1/payments',body=payment(100,ref))
check('Valid payment creates receipt',code==201)
code,replay=call(5102,'/api/v1/payments',body=payment(100,ref))
check('Retry returns same receipt',code==200 and replay.get('receipt',{}).get('id')==first.get('receipt',{}).get('id'))
check('Balance reduced once',call(5102,a+'/balance')[1]['outstanding']==base-100)
check('Reference payload conflict',call(5102,'/api/v1/payments',body=payment(101,ref))[0]==409)
check('Zero amount rejected',call(5102,'/api/v1/payments',body=payment(0,'ZERO-0001'))[0]==400)
check('Fractional cents rejected',call(5102,'/api/v1/payments',body=payment(1.001,'FRAC-0001'))[0]==400)
check('Overpayment rejected',call(5102,'/api/v1/payments',body=payment(base+1,'OVER-0001'))[0]==409)
check('Operator payment denied',call(5102,'/api/v1/payments','operator',payment(1,'OPER-0001'))[0]==403)
check('Payment against another account denied',call(5102,'/api/v1/payments',body=payment(1,'CROSS-001','100000002'))[0]==403)
remaining=call(5102,b+'/balance','customer2')[1]['outstanding']
with concurrent.futures.ThreadPoolExecutor(2) as executor:
 futures=[executor.submit(call,5102,'/api/v1/payments','partner',payment(remaining,f'RACE-{uuid.uuid4().hex}','100000002')) for _ in range(2)]
 codes=[f.result()[0] for f in futures]
check('Concurrent overpayment prevented',sorted(codes)==[201,409],str(codes))
check('Concurrent settlement leaves zero balance',call(5102,b+'/balance','partner')[1]['outstanding']==0)
ref='DUP-'+uuid.uuid4().hex
with concurrent.futures.ThreadPoolExecutor(2) as executor:
 pairs=list(executor.map(lambda _:call(5102,'/api/v1/payments','partner',payment(10,ref)),range(2)))
check('Concurrent duplicate stored once',sorted(p[0] for p in pairs)==[200,201] and pairs[0][1]['receipt']['id']==pairs[1][1]['receipt']['id'])
history=call(5102,a+'/payments','partner')[1]
check('Partner sees only its own receipts',len(history)>0 and all(p['channel']=='partner' for p in history))
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); reading={'meterValue':1260,'recordedAt':now}
check('Customer cannot submit readings',call(5101,a+'/readings',body=reading)[0]==403)
check('Decreasing meter rejected',call(5101,a+'/readings','operator',{'meterValue':1,'recordedAt':now})[0]==400)
check('Future meter timestamp rejected',call(5101,a+'/readings','operator',{'meterValue':1260,'recordedAt':'2099-01-01T00:00:00Z'})[0]==400)
check('Operator reading accepted',call(5101,a+'/readings','operator',reading)[0]==201)
check('Consumption refresh reflects new reading',call(5101,a+'/usage')[1]['consumption']==2)
check('Duplicate timestamp rejected',call(5101,a+'/readings','operator',reading)[0]==400)
with open('evidence/integration-results.json','w') as f:json.dump({'tests':results,'passed':sum(x['passed'] for x in results),'total':len(results),'recordedAt':now},f,indent=2)
assert all(x['passed'] for x in results),'Integration failure'
