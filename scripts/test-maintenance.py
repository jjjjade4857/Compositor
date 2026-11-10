"""Regression checks for interrupted upstream sync and translation resource validation."""
import os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class MaintenanceTests(unittest.TestCase):
 def sync(self, *, existing=True, pr='', network_failure=False):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);binpath=root/'bin';binpath.mkdir();(root/'scripts').mkdir()
   for name in ['generate-localization.py','audit-localization.py','review-localization.py']:(root/'scripts'/name).write_text('pass\n')
   mock='''#!/usr/bin/env python3
import os,sys
from pathlib import Path
name=Path(sys.argv[0]).name;args=sys.argv[1:]
with open(os.environ['CALLS'],'a') as f:f.write(name+' '+ ' '.join(args)+'\\n')
if name=='gh':
 if args[0]=='api':print('v1.6.7')
 if args[:2]==['pr','list']:print(os.environ['PR'])
else:
 if args[:2]==['merge-base','--is-ancestor'] and args[-1]=='HEAD' and not Path('checked-out').exists():sys.exit(1)
 if args[0]=='checkout':Path('checked-out').touch()
 if args[0]=='ls-remote':
  if os.environ['NETWORK_FAILURE']=='1':sys.exit(128)
  if os.environ['EXISTING']=='1':print('abc refs/heads/sync/upstream-v1.6.7')
'''
   for name in ['git','gh']:
    p=binpath/name;p.write_text(mock);p.chmod(0o755)
   calls=root/'calls';env=dict(os.environ,PATH=str(binpath)+os.pathsep+os.environ['PATH'],CALLS=str(calls),EXISTING=str(int(existing)),PR=pr,NETWORK_FAILURE=str(int(network_failure)))
   result=subprocess.run(['bash',str(ROOT/'scripts/sync-upstream.sh')],cwd=root,env=env,capture_output=True,text=True)
   return result.returncode,calls.read_text()
 def test_existing_branch_recovers_missing_runs_and_pr(self):
  code,calls=self.sync();self.assertEqual(code,0)
  self.assertIn('gh workflow run chinese.yml',calls);self.assertIn('gh workflow run verify.yml',calls);self.assertIn('gh pr create',calls)
 def test_retry_does_not_duplicate_existing_pr(self):
  code,calls=self.sync(pr='42');self.assertEqual(code,0);self.assertNotIn('gh pr create',calls)
 def test_network_failure_never_pushes(self):
  code,calls=self.sync(network_failure=True);self.assertNotEqual(code,0);self.assertNotIn('git push',calls)
 def test_invalid_translation_placeholders_fail_generation(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'scripts').mkdir();(root/'localization').mkdir()
   script=root/'scripts/generate-localization.py';script.write_bytes((ROOT/'scripts/generate-localization.py').read_bytes())
   (root/'localization/zh-Hans.txt').write_text('File %@ has %d layers|Only %@\n')
   result=subprocess.run(['python3',str(script)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('Placeholder mismatch',result.stderr)

class LocalizationAuditTests(unittest.TestCase):
 def audit(self, source, translations):
  import json
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'scripts').mkdir();(root/'localization').mkdir();(root/'Compositor/UI').mkdir(parents=True)
   for name in ['review-localization.py','swift_strings.py']:(root/'scripts'/name).write_bytes((ROOT/'scripts'/name).read_bytes())
   (root/'Compositor/UI/Fixture.swift').write_text(source)
   (root/'localization/zh-Hans.txt').write_text(translations)
   (root/'localization/reviewed-exceptions.json').write_text('{}')
   result=subprocess.run(['python3',str(root/'scripts/review-localization.py')],capture_output=True,text=True)
   return result.returncode,json.loads((root/'localization/full-audit-report.json').read_text())
 def test_custom_control_parameters_are_not_silently_ignored(self):
  code,report=self.audit('control("Offset", help: "Smooths colored speckles.")','')
  self.assertNotEqual(code,0);self.assertIn('Offset',report['untranslated_literals']);self.assertIn('Smooths colored speckles.',report['untranslated_literals'])
 def test_localized_dictionary_does_not_hide_native_display_bypass(self):
  code,report=self.audit('let label = NSTextField(labelWithString: kind.rawValue)','Gaussian Blur|高斯模糊\n')
  self.assertNotEqual(code,0);self.assertTrue(report['unlocalized_display_boundaries'])
 def test_raw_enum_interpolation_in_button_is_rejected(self):
  code,report=self.audit('Button("\\(kind.rawValue)…") {}','Gaussian Blur|高斯模糊\n')
  self.assertNotEqual(code,0);self.assertTrue(report['unlocalized_display_boundaries'])
 def test_properly_localized_control_passes(self):
  code,report=self.audit('Text(zh("Offset"))','Offset|偏移\n')
  self.assertEqual(code,0);self.assertFalse(report['untranslated_literals'])

class ArchiveTests(unittest.TestCase):
 def test_unicode_names_executable_bits_and_symlinks_survive_archive(self):
  import stat,zipfile
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);app=root/'Compositor 中文版.app';binary=app/'Contents/MacOS/Compositor';binary.parent.mkdir(parents=True)
   binary.write_text('#!/bin/sh\nexit 0\n');binary.chmod(0o755)
   (app/'ExecutableLink').symlink_to('Contents/MacOS/Compositor')
   output=root/'release.zip'
   subprocess.run(['python3',str(ROOT/'scripts/archive-chinese.py'),str(app),str(output)],check=True,capture_output=True)
   with zipfile.ZipFile(output) as archive:
    info=archive.getinfo('Compositor 中文版.app/Contents/MacOS/Compositor')
    self.assertTrue(info.flag_bits & 0x800);self.assertTrue(info.external_attr >> 16 & 0o111)
    link=archive.getinfo('Compositor 中文版.app/ExecutableLink')
    self.assertTrue(stat.S_ISLNK(link.external_attr >> 16));self.assertEqual(archive.read(link),'Contents/MacOS/Compositor'.encode())

if __name__=='__main__':unittest.main()
