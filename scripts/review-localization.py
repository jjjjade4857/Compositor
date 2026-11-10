"""Check every English-bearing Swift literal against translations or an explicitly reviewed exception.
Compiler-extracted keys are checked separately; UI execution remains part of the release checklist.
"""
from pathlib import Path
import json,re,sys
from swift_strings import skip_string,end_group
ROOT=Path(__file__).resolve().parents[1]
TOKEN=re.compile(r'%(?:\d+\$)?[-+0 #]*\d*(?:\.\d+)?(?:ll|l)?[df@]')
def canonical(key):return TOKEN.sub('%@',key)
def literal_inventory():
 records={}
 for p in sorted((ROOT/'Compositor').rglob('*.swift')):
  if p.name=='UpdateDriver.swift':continue # Not built or instantiated in this fork.
  s=p.read_text();i=0
  while i<len(s):
   if s.startswith('//',i):
    end=s.find('\n',i);i=len(s) if end<0 else end;continue
   if s.startswith('/*',i):
    end=s.find('*/',i+2);i=len(s) if end<0 else end+2;continue
   if s[i]!='"':i+=1;continue
   end=skip_string(s,i)
   if s.startswith('"""',i) and p.parent.name=='Rendering':i=end;continue # Reviewed GPU shader source files; UI literals are scanned below.
   raw=s[i+1:end-1];key='';j=0
   while j<len(raw):
    if raw.startswith('\\(',j):j=end_group(raw,j+1)+1;key+='%@'
    else:key+=raw[j];j+=1
   key=key.replace('\\"','"').replace('\\n','\n')
   if re.search('[A-Za-z]{2}',key) and (key[:1].isupper() or ' ' in key):
    records.setdefault(key,[]).append({'file':str(p.relative_to(ROOT)),'line':s[:i].count('\n')+1})
   i=end
 return records

def boundary_gaps():
 gaps=[]
 for p in (ROOT/'Compositor').rglob('*.swift'):
  if p.name=='UpdateDriver.swift':continue
  s=p.read_text()
  patterns=[
   r'\b(?:setAccessibilityLabel|setAccessibilityHelp)\(\s*"[^"\n]*[A-Za-z]{3}',
   r'\.(?:message|messageText|informativeText|placeholderString|toolTip|prompt|title) = "[^"\n]*[A-Za-z]{3}',
   r'addButton\(withTitle: \"[^\"\n]*[A-Za-z]{3}',
   r'NSTextField\(labelWithString: (?!zh\()[^,\n]*\.rawValue',
   r'\b(?:Button|Text|Menu|Toggle|Picker|Label)\("[^"\n]*\\\([^"\n]*\.rawValue[^"\n]*"',
  ]
  for pattern in patterns:
   for m in re.finditer(pattern,s):
    if 'zh(' in m[0]:continue
    gaps.append({'file':str(p.relative_to(ROOT)),'line':s[:m.start()].count('\n')+1,'expression':m[0]})
 return gaps

def review():
 terms=dict(l.split('|',1) for l in (ROOT/'localization/zh-Hans.txt').read_text().splitlines() if l and not l.startswith('#') and '|' in l)
 normalized={canonical(k) for k in terms}
 exceptions=json.loads((ROOT/'localization/reviewed-exceptions.json').read_text())
 records=literal_inventory();missing={};reviewed={}
 for key,refs in records.items():
  if canonical(key) in normalized or (key.endswith('…') and canonical(key[:-1]) in normalized):continue
  approved=exceptions.get(key,{})
  uncovered=[r for r in refs if r['file'] not in approved.get('files',[]) or not approved.get('reason')]
  if uncovered:missing[key]=uncovered
  else:reviewed[key]=approved
 compiler_missing={}
 technical={'CMYK','RGB','sRGB','Compositor'}
 compiler_root=Path(sys.argv[sys.argv.index('--compiler-data')+1]) if '--compiler-data' in sys.argv else ROOT/'build/zh-Hans/localization'
 compiler_files=list(compiler_root.rglob('*.stringsdata'))
 if '--require-compiler-data' in sys.argv and not compiler_files: raise RuntimeError('Compiler localization extraction produced no data')
 for p in compiler_files:
  data=json.loads(p.read_text())
  for item in data.get('tables',{}).get('Localizable',[]):
   key=item['key']
   if not re.search('[A-Za-z]{3}',TOKEN.sub('',key)) or key in technical or canonical(key) in normalized:continue
   if key in exceptions and exceptions[key].get('reason'):continue
   compiler_missing[key]=data['source']
 gaps=boundary_gaps()
 report={'unlocalized_display_boundaries':gaps,'literal_count':len(records),'reviewed_exception_count':len(reviewed),'untranslated_literals':missing,'untranslated_compiler_keys':compiler_missing}
 (ROOT/'localization/full-audit-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'literal_count':len(records),'reviewed_exception_count':len(reviewed),'untranslated_literals':len(missing),'untranslated_compiler_keys':len(compiler_missing),'unlocalized_display_boundaries':len(gaps)}))
 return bool(missing or compiler_missing or gaps)
if __name__=='__main__':raise SystemExit(review())
