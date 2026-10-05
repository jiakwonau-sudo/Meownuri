"""Apply only R01/R02/R03 to pinned Muse v15.3, preserving new Day3 verbatim."""
from pathlib import Path
import hashlib,json,re,sys
import apply_v14_19_r1 as save_patch
from apply_v14_19_r2 import build as home_patch
EXPECTED='dfcde462fb211fcaa7a4128848f468a7fbd890c84dff72987bb07e2eb4a9ae68'
BASE_COMMIT='08821042a218eefce81b4eb093794b6cc8eaba92'
DAY3='/* ---------- 16. DAY 3: 마지막 아침 ---------- */'
def build(source,destination):
 raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Wrong base; refusing overwrite'
 save_patch.EXPECTED=EXPECTED;m=home_patch(source,destination)
 target=destination/'index.html';s=target.read_text().replace(' · QA r2</title>',' · QA r1</title>');target.write_text(s)
 before=raw.decode();a=re.findall(r'<script[^>]*>(.*?)</script>',before,re.S);b=re.findall(r'<script[^>]*>(.*?)</script>',s,re.S)
 assert a[:4]==b[:4],'Core/BGM changed'
 assert a[-1].split(DAY3,1)[1]==b[-1].split(DAY3,1)[1],'Day3 changed'
 assert s.count('// SILENT:')==before.count('// SILENT:')==5
 m.pop('parent_r1_sha256',None)
 m.update(build='MEOWNURI 9.0 / Muse v15.3-r1 QA candidate',lineage='Meta AI / Muse',modifier='GPT-6 Astra Pro',base_commit=BASE_COMMIT,source_sha256=EXPECTED,candidate_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),day3_verbatim_preserved=True,silent_edits_preserved=5,status='PARTIAL UNTIL TARGETED BROWSER CHECKS',public_deployment='NOT DEPLOYED; public main unchanged by this task')
 (destination/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));return m
if __name__=='__main__':print(json.dumps(build(Path(sys.argv[1]),Path(sys.argv[2])),ensure_ascii=False,indent=2))
