"""Apply identical release metadata to local and CI Chinese bundles before signing."""
from pathlib import Path
import json,plistlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
app=Path(sys.argv[1]);path=app/'Contents/Info.plist'
info=plistlib.loads(path.read_bytes());release=json.loads((ROOT/'localization/release.json').read_text())
project=(ROOT/'Compositor.xcodeproj/project.pbxproj').read_text()
version=re.search(r'MARKETING_VERSION = ([^;]+);',project)[1]
build=re.search(r'CURRENT_PROJECT_VERSION = ([^;]+);',project)[1]
for key in list(info):
 if key.startswith(('SU','DT')) or key=='BuildMachineOSBuild':del info[key]
info.update(CFBundleIdentifier=release['bundle_identifier'],CFBundleName=release['app_name'],CFBundleDisplayName=release['app_name'],CFBundleExecutable='Compositor',CFBundleDevelopmentRegion='zh-Hans',CFBundleLocalizations=['zh-Hans'],CFBundleShortVersionString=version,CFBundleVersion=f"{build}.{release['patch_revision']}",CompositorChinesePatchVersion=release['patch_date'])
for item in info.get('CFBundleDocumentTypes',[]):item['LSHandlerRank']='Alternate'
path.write_bytes(plistlib.dumps(info))
locale=app/'Contents/Resources/zh-Hans.lproj';locale.mkdir(parents=True,exist_ok=True)
q=lambda s:json.dumps(s,ensure_ascii=False)
(locale/'InfoPlist.strings').write_text(f'"CFBundleDisplayName" = {q(release["app_name"])};\n"CFBundleName" = {q(release["app_name"])};\n')
