# coding: utf-8
"""Report uncovered literal UI labels. Dynamic and system-provided text still needs visual review."""
from pathlib import Path
import re, json
ROOT=Path(__file__).resolve().parents[1]
terms=dict(l.split('|',1) for l in (ROOT/'localization/zh-Hans.txt').read_text().splitlines() if l and not l.startswith('#') and '|' in l)
# Hardware product names remain unchanged.
allowed={'RGB','CMYK','iPhone 18 Pro','iPhone 18 Pro Max','MacBook Pro 14\\\"','MacBook Pro 16\\\"','Studio Display'}
pattern=re.compile(r'(?:\b(?:Button|Menu|Text|Toggle|Picker|Label|TextField|ColorPicker)|\.(?:help|accessibilityLabel|alert|setAccessibilityLabel|setAccessibilityHelp))\((?:zh\()?"((?:[^"\\]|\\.)*)"|(?:\.toolTip = (?:zh\()?|title: |withTitle: )"((?:[^"\\]|\\.)*)"')
missing=[]
for p in sorted((ROOT/'Compositor').rglob('*.swift')):
 if p.name=='UpdateDriver.swift':continue
 for m in pattern.finditer(p.read_text()):
  key=m[1] or m[2] or ""
  if re.search('[A-Za-z]{3}',key) and key not in terms and key not in allowed and '\\(' not in key:
   missing.append({'key':key,'file':str(p.relative_to(ROOT)),'line':p.read_text()[:m.start()].count('\n')+1})
out=ROOT/'localization/audit-report.json';out.write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n')
print(f'{len(missing)} uncovered literal occurrences; report: {out}')
raise SystemExit(bool(missing))
