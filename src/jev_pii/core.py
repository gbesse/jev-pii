# Purpose: Local detectors, seeded column sampling, payload controls and inventory diff.
import hashlib,json,random,re
PATTERNS={"email":re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)"),"phone":re.compile(r"(?<!\d)(?:\+?\d[ .-]?){8,15}(?!\d)"),"uuid":re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",re.I)}
def luhn(value):
 digits=[int(x) for x in re.sub(r"\D","",value)];return len(digits)>=12 and sum((n*2-9 if n*2>9 else n*2) if (len(digits)-i)%2==0 else n for i,n in enumerate(digits))%10==0
def iban(value):
 value=re.sub(r"\s","",value).upper()
 if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}",value):return False
 rearranged=value[4:]+value[:4];number=''.join(str(ord(c)-55) if c.isalpha() else c for c in rearranged);return int(number)%97==1
def detect(value):
 text=str(value);found=[name for name,pattern in PATTERNS.items() if pattern.search(text)]
 for match in re.findall(r"(?:\d[ -]?){12,19}",text):
  if luhn(match):found.append("payment_card")
 for match in re.findall(r"\b[A-Z]{2}\d{2}[A-Z0-9 ]{10,34}\b",text.upper()):
  if iban(match):found.append("iban")
 return sorted(set(found))
def assert_read_only(connection):
 if not getattr(connection,"read_only",False):raise PermissionError("Database connection is writable; read-only mode is required")
def sample_column(values,size=20,seed=7):
 values=[str(v) for v in values if v not in (None,'')];return random.Random(seed).sample(values,min(size,len(values)))
def mask_value(value):
 value=PATTERNS["email"].sub(lambda m:m.group(0)[0]+"***@"+m.group(0).split('@')[1],str(value));return re.sub(r"\d","#",value)
def payload_for(column,values,size=20,seed=7,mask=False):
 samples=sample_column(values,size,seed);samples=[mask_value(x) for x in samples] if mask else samples
 return json.dumps({"model":"jev-1.13.0","state":{"column":column,"samples":samples},"questions":{"personal":{"type":"noul"},"category":{"type":"choice","criteria":["identity","contact","financial","health","other"]},"special":{"type":"noul"},"subject":{"type":"choice","criteria":["employee","customer","prospect","patient","other"]},"free_text":{"type":"noul"}}},sort_keys=True,separators=(",",":")).encode()
class FakeJev:
 def __init__(self,answer=None):self.answer=answer or {"personal":.8,"category":"contact","special":.1,"subject":"customer","free_text":.2};self.calls=[]
 def send(self,payload):self.calls.append(payload);return self.answer
def scan_columns(columns,*,local_only=True,dry_run=False,mask=False,sample_size=20,seed=7,transport=None,row_counts=None):
 findings=[];payloads=[]
 for name,values in columns.items():
  local=sorted({kind for value in values for kind in detect(value)});entry={"column":name,"layers":["local"] if local else [],"detectors":local,"row_count":(row_counts or {}).get(name,len(values)),"confidence":1 if local else 0}
  if not local_only:
   payload=payload_for(name,values,sample_size,seed,mask);payloads.append(payload)
   if not dry_run:
    answer=transport.send(payload);entry.update({"semantic":answer,"confidence":answer.get("personal",0)});entry["layers"].append("semantic")
  findings.append(entry)
 return {"findings":findings,"payloads":payloads,"processing_record":[{"column":x["column"],"purpose":"","retention":"","row_count":x["row_count"]} for x in findings],"remediation":["Confirm purpose and retention","Restrict access","Review high-risk columns"]}
def diff(previous,current):
 old={x["column"]:x for x in previous["findings"]};new={x["column"]:x for x in current["findings"]}
 return {"added":sorted(new.keys()-old.keys()),"removed":sorted(old.keys()-new.keys()),"recategorized":sorted(k for k in old.keys()&new.keys() if old[k].get("detectors")!=new[k].get("detectors") or old[k].get("semantic")!=new[k].get("semantic"))}
def html_report(result):return '<!doctype html><meta charset=utf-8><title>PII inventory</title><style>body{font:16px system-ui;max-width:70rem;margin:auto}</style><h1>PII inventory</h1><pre>'+json.dumps(result,indent=2).replace('&','&amp;').replace('<','&lt;')+'</pre>'
