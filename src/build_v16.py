from pathlib import Path
import re,json,base64
P=Path('/mnt/data/meownuri_work')
s=(P/'MEOWNURI_SOL_v15.8_FIX.html').read_text()
story=(P/'story4_10.js').read_text()
# Keep import statements native to the one-file ES module; existing map supplies all imports.
s=s.replace('</body>', '<script type="module" id="solStoryDay04to10">\n'+story+'\n</script>\n</body>',1)
s=s.replace('WIDE WORLD v15.8 · DISPLAY FIX · DAY 3','WIDE WORLD v16.0 · DAY 1–10')
s=s.replace('>v15.8<','>v16.0<')
path=P/'MEOWNURI_SOL_v16.0_DAY01-10.html';path.write_text(s)
print('created',path,path.stat().st_size)
