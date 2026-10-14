# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Build a deterministic source/illustration ZIP without Git data or caches."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parent
EXCLUDED={'.git','release','__pycache__'}
paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts) and p.name!='MANIFEST.json')
for p in paths:
    assert not p.is_symlink()
items=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
(ROOT/'MANIFEST.json').write_text(json.dumps({'files':items,'manifest_self_hash_excluded':True},indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'verify_release.py')],check=True,cwd=ROOT)
paths.append(ROOT/'MANIFEST.json')
release=ROOT/'release'
release.mkdir(exist_ok=True)
archive=release/'square-wheel-clocks-v1.0.0.zip'
with zipfile.ZipFile(archive,'w') as z:
    for p in sorted(paths):
        info=zipfile.ZipInfo('square-wheel-clocks/'+str(p.relative_to(ROOT)),date_time=(2026,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(paths)
    for p in paths:
        assert z.read('square-wheel-clocks/'+str(p.relative_to(ROOT)))==p.read_bytes()
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
(release/'SHA256SUMS').write_text(sha+'  '+archive.name+'\n')
print(json.dumps({'status':'PASS','archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha,'files':len(paths),'crc_and_member_bytes':'PASS'}))
