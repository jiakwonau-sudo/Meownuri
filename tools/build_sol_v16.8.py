from pathlib import Path
import re,hashlib,json
root=Path('/mnt/data')
wood=(root/'MEOWNURI_SOL_v16.7_WOOD_BITE.html').read_text()
tap=(root/'MEOWNURI_SOL_v16.5_TAP_CINEMA.html').read_text()
match=re.search(r'<script id="solTapCinematicController">[\s\S]*?</script>',tap)
assert match,'missing stand-alone TAP cinematic controller'
assert 'solTapCinematicController' not in wood,'controller already injected'
assert wood.count('</body>')==1 and wood.count('<script type="importmap">')==1
controller=match.group().replace('SOL v16.5 · TAP-TO-ADVANCE','SOL v16.8 · TAP-TO-ADVANCE').replace("version:'SOL v16.5'", "version:'SOL v16.8'")
assert 'if(window.__MEOWNURI_TAP_CONTROLLER__)return;' in controller
changed=wood.replace('WIDE WORLD v16.7 · WOOD BITE · DAY 1–10','WIDE WORLD v16.8 · WOOD BITE + TAP · DAY 1–10')
changed=changed.replace("version:'v16.7'", "version:'v16.8'")
changed=changed.replace('</body>',controller+'\n</body>',1)
assert changed.count('id="solTapCinematicController"')==1
assert changed.count('<script type="importmap">')==1
assert changed.count('__GEMINI_KEY__')==0
out=root/'work_20261011'/'MEOWNURI_SOL_v16.8_TAP_WOOD_BITE.html';out.write_text(changed)
manifest={'build':'SOL v16.8','kind':'preview candidate','base_sha256':hashlib.sha256(wood.encode()).hexdigest(),'tap_sha256':hashlib.sha256(tap.encode()).hexdigest(),'output_sha256':hashlib.sha256(changed.encode()).hexdigest(),'method':'add TAP cinematic controller script from v16.5 to v16.7 without modifying embedded game engines; bump display version','independent_3d_test':'pending','legacy_main':'unchanged'}
(out.parent/'meownuri_v16.8_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'out':str(out),'bytes':out.stat().st_size,'sha256':manifest['output_sha256'],'controller_bytes':len(controller)},ensure_ascii=False))
