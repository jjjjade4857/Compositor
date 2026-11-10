"""Create a UTF-8 ZIP preserving executable bits and framework symlinks."""
from pathlib import Path
import os,stat,sys,zipfile
app=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]);output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for path in [app,*sorted(app.rglob('*'))]:
  relative=str(path.relative_to(app.parent))
  metadata=path.lstat()
  if path.is_symlink():
   info=zipfile.ZipInfo(relative);info.create_system=3;info.external_attr=metadata.st_mode<<16
   archive.writestr(info,os.readlink(path).encode('utf-8'))
  else:archive.write(path,relative+('/' if path.is_dir() else ''))
print(output)
