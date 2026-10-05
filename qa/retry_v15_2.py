"""Retry only the two photograph-interrupted routes on identical v15.2-r1 bytes.
Functional assertions and original game clocks are unchanged. Capture failures
are recorded separately, never converted into visual-QA success.
"""
from pathlib import Path
import sys, os, json, hashlib, traceback
TARGET='a5c9665109b5c58e657cc989850736c134a1403c89df73a5a6f9f056703ff2ec'
which=sys.argv[1]
assert which in ('natural','fresh')
loader=Path('qa/check_v15_2.py').read_text().split("exec(compile(source,'qa/complete_v14_19_r2.py','exec'),globals())",1)[0]
exec(compile(loader,'qa/check_v15_2.py','exec'),globals())
definitions=source.split('try:\n time.sleep(1)\n with sync_playwright()',1)[0]
exec(compile(definitions,'qa/complete_v14_19_r2.py','exec'),globals())
assert hashlib.sha256(Path('qa-continuation/candidate_r2/index.html').read_bytes()).hexdigest()==TARGET
R['source_run_id']=os.environ.get('GITHUB_RUN_ID','local')
R['retry_of']='37247951908: four cases passed; these two were interrupted by screenshot timeouts'
R['capture_policy']='Critical frames only; actual renderer; JPEG capture. Failed photographs logged separately from gameplay assertions.'
R['capture_warnings']=[]
def shot(p,name,method):
    s=state(p)
    entry={'name':name,'method':method,'state':s,'capture_status':'STATE_ONLY'}
    R['frames'].append(entry);persist()
    important=any(k in name.lower() for k in ('title','home_arrived','reload','restore','bear_choice','ending'))
    if important:
        try:
            p.evaluate('__qaDraw()')
            p.screenshot(path=str(O/(name+'.jpg')),type='jpeg',quality=75,timeout=12000)
            entry['capture_status']='CAPTURED'
            entry['file']=name+'.jpg'
        except Exception as e:
            entry['capture_status']='CAPTURE_INCOMPLETE'
            R['capture_warnings'].append({'name':name,'error':str(e)})
        persist()
    return s
try:
    time.sleep(1)
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        if which=='natural':
            case('R03 repaired home return through actual ending','same unmodified natural save and furniture; normal input and actual ending; not a fresh start',lambda:repaired_home_and_ending(b))
        else:
            case('v15.2-r1 fresh start through Day2 loss ending','empty storage; original clocks; keyboard and visible pointer; two UI save/reloads; no checkpoint injection or teleport',lambda:continuous(b))
        b.close()
except Exception as e:
    R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
    server.terminate();persist()
    print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'capture_warnings':R['capture_warnings']},ensure_ascii=False),flush=True)
    if R.get('fatal') or len(R['cases'])!=1 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
