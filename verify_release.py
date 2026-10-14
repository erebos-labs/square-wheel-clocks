# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Erebos Labs
"""Verify the manifest, known outputs and generic publication hygiene."""
from pathlib import Path
import ast,hashlib,json,re

ROOT=Path(__file__).resolve().parent
EXCLUDED={'.git','release','__pycache__'}

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts))

manifest=json.loads((ROOT/'MANIFEST.json').read_text())
listed={item['path']:item for item in manifest['files']}
actual={str(p.relative_to(ROOT)):p for p in files() if p.name!='MANIFEST.json'}
assert set(actual)==set(listed),'Manifest membership differs from package files'
secret_patterns=[
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(rb'AKIA[0-9A-Z]{16}'),
    re.compile(rb'https?://[^\s/:]+:[^\s/@]+@'),
    re.compile(rb'/(?:Users|home)/[^\s\"\']+'),
]
for rel,p in actual.items():
    assert not p.is_symlink(),rel
    raw=p.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==listed[rel]['sha256'],rel
    assert len(raw)==listed[rel]['bytes'],rel
    assert p.suffix.lower() not in ('.pdf','.pyc','.ttf','.otf'),rel
    if p.suffix in ('.py','.md','.json','.csv','.txt') or p.name=='LICENSE':
        assert not any(rx.search(raw) for rx in secret_patterns),'Publication hygiene check failed: '+rel
    if p.suffix=='.py':
        ast.parse(raw.decode(),filename=p.name)
for name in ('checks.json','dynamics-checks.json','animation-model-checks.json'):
    assert json.loads((ROOT/'output'/name).read_text())['status']=='PASS',name
figures=json.loads((ROOT/'output/figure-checks.json').read_text())
assert figures['two-clocks.gif']['frames']==120
assert figures['two-clocks.gif']['total_duration_ms']==7200
for md in ROOT.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
        if '://' not in target and not target.startswith('#'):
            assert (md.parent/target.split('#')[0]).is_file(),(md.name,target)
print(json.dumps({'status':'PASS','manifest_files':len(actual),'numeric_checks':'PASS','gif_frames':120,'gif_duration_ms':7200,'generic_secret_and_home_path_check':'PASS','limits':'Bounded publication hygiene, not a guarantee against every possible secret pattern.'}))
