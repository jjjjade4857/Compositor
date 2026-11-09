"""Regression checks for interrupted upstream sync and translation resource validation."""
import os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class MaintenanceTests(unittest.TestCase):
 def sync(self, *, existing=True, pr='', network_failure=False):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);binpath=root/'bin';binpath.mkdir();(root/'scripts').mkdir()
   for name in ['generate-localization.py','audit-localization.py']:(root/'scripts'/name).write_text('pass\n')
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

if __name__=='__main__':unittest.main()
