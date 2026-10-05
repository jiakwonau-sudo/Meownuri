"""Forward-port three reviewed fixes onto exact Muse 15.2; preserve SILENT content."""
from pathlib import Path
import hashlib, json, re, sys
import apply_v14_19_r1 as save_patch
from apply_v14_19_r2 import build as home_patch
EXPECTED='0297d36aa5de898f217c927843713bffe5850a6fa40e0fdfba589dc2a6411ad7'
BASE_COMMIT='06b56a7300dfdd8eb83a6528ceb78404207a0ea8'
def build(source,destination):
    raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Source changed; refusing blind overwrite'
    save_patch.EXPECTED=EXPECTED
    manifest=home_patch(source,destination)
    target=destination/'index.html'
    html=target.read_text().replace(' · QA r2</title>',' · QA r1</title>')
    target.write_text(html)
    scripts0=re.findall(r'<script[^>]*>(.*?)</script>',raw.decode(),re.S)
    scripts1=re.findall(r'<script[^>]*>(.*?)</script>',html,re.S)
    assert scripts0[:4]==scripts1[:4], 'Core modules or BGM changed'
    assert html.count('// SILENT:')==raw.decode().count('// SILENT:')==5
    for s in ["// SILENT: fish drop", "// SILENT: happy/jump", "// SILENT: wood slide", "// SILENT: was '냐앙", "// SILENT: was '🌅"]:
        assert s in html
    manifest.pop('parent_r1_sha256',None)
    manifest.update(build='MEOWNURI 9.0 / Muse v15.2-r1 QA candidate',
      base_commit=BASE_COMMIT,source_sha256=EXPECTED,
      candidate_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
      lineage='MEOWNURI 9.0 / Meta AI Muse',modifier='GPT-6 Astra Pro',
      patches_reused_from='Muse v14.19-r2, R01/R02/R03 only',
      silent_edits_preserved=5,status='CANDIDATE; requires v15.2-specific runtime checks',
      public_deployment='NOT DEPLOYED; original main unchanged')
    (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return manifest
if __name__=='__main__': print(json.dumps(build(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
