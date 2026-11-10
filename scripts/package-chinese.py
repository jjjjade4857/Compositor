"""Package one canonical local Chinese edition from the current source and build."""
from pathlib import Path
import argparse,json,plistlib,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--official',type=Path,default=(Path('/Applications/Compositor 中文版.app') if Path('/Applications/Compositor 中文版.app').exists() else Path('/Applications/Compositor.app')));args=a.parse_args()
binary=ROOT/'build/zh-Hans/Compositor'
if not binary.is_file():raise SystemExit('Build the current source first.')
subprocess.run(['python3',str(ROOT/'scripts/generate-localization.py')],check=True)
project=(ROOT/'Compositor.xcodeproj/project.pbxproj').read_text()
version=re.search(r'MARKETING_VERSION = ([^;]+);',project)[1]
build=re.search(r'CURRENT_PROJECT_VERSION = ([^;]+);',project)[1]
app=ROOT/'dist/Compositor 中文版.app'
if app.exists():shutil.rmtree(app)
contents=app/'Contents';resources=contents/'Resources';resources.mkdir(parents=True)
shutil.copytree(args.official/'Contents/Resources',resources,dirs_exist_ok=True)
shutil.copytree(ROOT/'Compositor/Resources',resources,dirs_exist_ok=True)
(contents/'MacOS').mkdir();shutil.copy2(binary,contents/'MacOS/Compositor')
info=plistlib.loads((args.official/'Contents/Info.plist').read_bytes())
for key in list(info):
 if key.startswith(('SU','DT')) or key=='BuildMachineOSBuild':del info[key]
info.update(plistlib.loads((ROOT/'Config/Info.plist').read_bytes()))
for item in info.get('CFBundleDocumentTypes',[]):item['LSHandlerRank']='Alternate'
(contents/'Info.plist').write_bytes(plistlib.dumps(info));(contents/'PkgInfo').write_bytes(b'APPL????')
subprocess.run(['python3',str(ROOT/'scripts/configure-chinese-bundle.py'),str(app)],check=True)
locale=resources/'zh-Hans.lproj';(locale/'InfoPlist.strings').write_text('"CFBundleDisplayName" = "Compositor 中文版";\n"CFBundleName" = "Compositor 中文版";\n')
shutil.copy2(ROOT/'LICENSE',resources/'Compositor-LICENSE.txt')
subprocess.run(['plutil','-lint',str(contents/'Info.plist'),str(locale/'Localizable.strings')],check=True)
subprocess.run(['codesign','--force','--sign','-','--options','runtime','--entitlements',str(ROOT/'Config/Compositor.entitlements'),str(app)],check=True)
subprocess.run(['codesign','--verify','--strict',str(app)],check=True)
print(app)
