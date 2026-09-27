using Water.Shared;
var passed=0;
void Test(string name,Action check){try{check();Console.WriteLine("PASS "+name);passed++;}catch(Exception e){Console.WriteLine("FAIL "+name+": "+e.Message);Environment.Exit(1);}}
void Reject(Action action,int status=400){try{action();}catch(DomainException e) when(e.Status==status){return;}throw new Exception("Expected rejection.");}
Test("Exact cents",()=>{if(Rules.Cents(123.45m)!=12345)throw new Exception();});
Test("Smallest payment",()=>{if(Rules.Cents(.01m)!=1)throw new Exception();});
Test("Reject zero",()=>Reject(()=>Rules.Cents(0)));
Test("Reject negative",()=>Reject(()=>Rules.Cents(-1)));
Test("Reject fractional cent",()=>Reject(()=>Rules.Cents(1.001m)));
Test("Reject maximum overflow",()=>Reject(()=>Rules.Cents(1000001)));
Test("Accept reference",()=>Rules.Reference("TEST-0001"));
Test("Reject empty reference",()=>Reject(()=>Rules.Reference(null)));
Test("Reject short reference",()=>Reject(()=>Rules.Reference("a")));
Test("Reject unsafe reference",()=>Reject(()=>Rules.Reference("<script>")));
var last=DateTimeOffset.UtcNow.AddDays(-1);var now=DateTimeOffset.UtcNow;
Test("Accept cumulative reading",()=>Rules.Reading(10,12.001m,last,now,now));
Test("Accept zero consumption",()=>Rules.Reading(10,10,last,now,now));
Test("Reject decreasing reading",()=>Reject(()=>Rules.Reading(10,9,last,now,now)));
Test("Reject old reading",()=>Reject(()=>Rules.Reading(10,12,last,last,now)));
Test("Reject future reading",()=>Reject(()=>Rules.Reading(10,12,last,now.AddDays(1),now)));
Test("Reject excess meter precision",()=>Reject(()=>Rules.Reading(10,12.0001m,last,now,now)));
Console.WriteLine($"RESULT {passed}/16 passed");
