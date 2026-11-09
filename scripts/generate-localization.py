"""Generate native bundle resources from the reviewed translation table."""
from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
terms={}
for line in (root/'localization/zh-Hans.txt').read_text().splitlines():
 if line and not line.startswith('#') and '|' in line:
  key,value=line.split('|',1)
  if key in terms and terms[key]!=value:raise ValueError('Conflicting translation: '+key)
  tokens = lambda text: re.findall(r"%(?:lld|ld|d|@)", text)
  if tokens(key) != tokens(value): raise ValueError("Placeholder mismatch: "+key)
  terms[key]=value
for key,value in list(terms.items()):
 if not key.endswith('…'):terms.setdefault(key+'…',value+'…')
resources=root/'Compositor/Resources';locale=resources/'zh-Hans.lproj';locale.mkdir(parents=True,exist_ok=True)
quote=lambda s:json.dumps(s,ensure_ascii=False)
(locale/'Localizable.strings').write_text('\n'.join(f'{quote(k)} = {quote(v)};' for k,v in sorted(terms.items()))+'\n')
(resources/'ChineseTranslations.json').write_text(json.dumps(terms,ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(terms)} translations')
