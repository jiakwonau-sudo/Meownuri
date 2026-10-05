"""Reuse the prior proven input driver on pinned v15.2, with explicit new-run labels."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'qa/complete_v14_19_r2.py').read_text()
assert hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()=='0297d36aa5de898f217c927843713bffe5850a6fa40e0fdfba589dc2a6411ad7'
assert source.count("'from apply_v14_19_r2 import'")==1
source=source.replace("'from apply_v14_19_r2 import'","'from apply_v15_2_r1 import'")
source=source.replace("R['build_target']='v14.19-r2; original/main untouched'","R['build_target']='Muse v15.2-r1 SILENT; original main unchanged'")
source=source.replace('timeout=100000','timeout=180000')
source=source.replace("  case('R03 original blocked destination reproduced'", "  case('v15.2 original R01/R02 reproduced','seeded checkpoints, real UI save/reload and normal watchdog timer',lambda:baseline(b,False))\n  case('R03 original blocked destination reproduced'")
source=source.replace('natural saved layout, original v14.19','natural saved layout, original v15.2')
source=source.replace("case('r2 fresh start through Day2 loss ending'","case('v15.2-r1 fresh start through Day2 loss ending'")
source=source.replace("case('r2 mobile controls'","case('v15.2-r1 mobile controls'")
exec(compile(source,'qa/complete_v14_19_r2.py','exec'),globals())
