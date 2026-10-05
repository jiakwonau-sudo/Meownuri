"""Build a separate, reproducible v14.19-r1 candidate. Never overwrite original."""
from pathlib import Path
import hashlib,json,re,sys
EXPECTED='0269a3fde9f4c1dee0829abf4e8c19ff61b25701765d7e4fa1bcbfc893605161'
SNAPSHOT="""
    // Persist control state, not only the visible quest sentence.
    s.agencyProgress = {
      version: 1,
      friendMeetPhase: this.friendMeetPhase || 0,
      bondJourney: this.bondJourney ? {phase: this.bondJourney.phase || 0} : null,
      homeJourney: this.homeJourney ? {lookAt: 0} : null,
      homeReady: !!this.homeReady,
      sunsetJourney: this.sunsetJourney ? {phase: this.sunsetJourney.phase || 0, lookAt: 0} : null,
      sunsetReady: !!this.sunsetReady,
      clueLead: this.clueLead ? JSON.parse(JSON.stringify(this.clueLead)) : null,
      clueLeadReady: !!this.clueLeadReady,
      day1Complete: !!this.__day1Complete
    };
"""
RESTORE="""
    // Reconstruct existing progression without clearing or renaming save keys.
    // Absolute simulation-time deadlines are deliberately restarted.
    if (this.mode === 'play' && savedState && savedState.line === 'MEOWNURI9' && savedState.schema === 2) {
      var ap = savedState.agencyProgress;
      if (ap && ap.version === 1) {
        if (Number.isInteger(ap.friendMeetPhase) && ap.friendMeetPhase >= 0 && ap.friendMeetPhase <= 3)
          this.friendMeetPhase = ap.friendMeetPhase;
        this.bondJourney = ap.bondJourney ? {phase: ap.bondJourney.phase || 0, lookAt: 0} : null;
        this.homeJourney = ap.homeJourney ? {lookAt: 0} : null;
        this.homeReady = !!ap.homeReady;
        this.sunsetJourney = ap.sunsetJourney ? {phase: ap.sunsetJourney.phase || 0, lookAt: 0} : null;
        this.sunsetReady = !!ap.sunsetReady;
        this.clueLead = ap.clueLead ? Object.assign({}, ap.clueLead, {lookAt: 0}) : null;
        this.clueLeadReady = !!ap.clueLeadReady;
        this.__day1Complete = !!ap.day1Complete;
      } else if (this.stage === 7 && this.dayNumber === 1) {
        // Legacy saves have no journey flags. Resume a safe stage, no rewards granted.
        if (this.storyPhase === 0) this.bondJourney = {phase: 0, lookAt: 0};
        if (this.storyPhase === 1) {
          this.homeReady = Math.hypot(this.friend.x - (this.box.x + 3.5), this.friend.z - (this.box.z + 3.5)) < 0.7;
          this.homeJourney = this.homeReady ? null : {lookAt: 0};
        }
        if (this.storyPhase === 2) {
          var sun = this.storyWorld.sunset;
          this.sunsetReady = Math.hypot(this.friend.x - sun.x, this.friend.z - sun.z) < 0.7;
          this.sunsetJourney = {phase: this.sunsetReady ? 1 : 0, lookAt: 0};
          if (savedQuest && savedQuest.text === '밤의 평화') this.__day1Complete = true;
        }
      }
      if (this.dayNumber === 1 && this.storyPhase === 0 && this.bondJourney) {
        if (this.bondJourney.phase === 0 || this.bondJourney.phase === 1) {
          if (this.giftFish) this.giftFish.visible = false;
          if (this.bondJourney.phase === 1) { var sf = this.ensureStoryFish(); sf.visible = true; }
        } else if (this.ensureGiftFish) { this.ensureGiftFish(); if (this.giftFish) this.giftFish.visible = true; }
      }
      if (this.dayNumber === 1 && this.storyPhase === 2) {
        this.showSunsetTrail(!this.__day1Complete);
        if (this.__day1Complete) { this.sunsetJourney = null; this.sunsetReady = false; showDay2Button(); }
      }
    }
"""
def once(text,old,new):
 assert text.count(old)==1, f'Unsafe patch anchor: {old[:70]!r}: {text.count(old)}'
 return text.replace(old,new,1)
def build(source:Path, destination:Path):
 raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Wrong original: refusing patch'
 html=raw.decode('utf-8');match=re.search(r'<script>\s*/\*\s*=+\s*MEOWNURI v12.*?</script>',html,re.S)
 assert match,'Agency block missing'
 block=match.group(); agency=block[len('<script>'):-len('</script>')]
 agency=once(agency,"    s.quest = { text: this.__questText || '', detail: this.__questDetail || '' };", "    s.quest = { text: this.__questText || '', detail: this.__questDetail || '' };"+SNAPSHOT)
 agency=once(agency,'    var savedQuest = null;', '    var savedQuest = null, savedState = null;')
 agency=once(agency,"      var s = JSON.parse(localStorage.getItem(SAVE_KEY_FIX) || 'null');", "      var s = JSON.parse(localStorage.getItem(SAVE_KEY_FIX) || 'null'); savedState = s;")
 agency=once(agency,'    var r = origRestore();','    var r = origRestore();'+RESTORE)
 agency=once(agency,"origSetQuest(savedQuest.text, savedQuest.detail || '')","this.setQuest(savedQuest.text, savedQuest.detail || '')")
 agency=once(agency,'origSetQuest(lq[0], lq[1])','this.setQuest(lq[0], lq[1])')
 agency=once(agency,"        if (this.storyPhase === 4 && !this.clueLead)","        if (this.storyPhase === 4 && !this.clueLead && !this.clueLeadReady)")
 agency=once(agency,"        } else if (this.storyPhase === 5 && !this.clueLead)","        } else if (this.storyPhase === 5 && !this.clueLead && !this.clueLeadReady)")
 anchor="""  (function initClueWatchdog() {
    setInterval(function () {
      try {
        if (!g || g.mode !== 'play' || g.cut) return;"""
 replacement=anchor.replace("if (!g || g.mode !== 'play' || g.cut) return;", "if (!g || g.mode !== 'play' || g.cut || g.ending || g.bearStarted || g.storyLock || g.modalLocked) return;")
 agency=once(agency,anchor,replacement)
 agency=once(agency,'        if (!arrivedQuest) {','        if (!arrivedQuest && !g.clueLeadReady) {')
 html=html[:match.start()]+'<script>'+agency+'</script>'+html[match.end():]
 html=re.sub(r'(<title>)(.*?)(</title>)',lambda m:m[1]+m[2]+' · QA r1'+m[3],html,count=1,flags=re.S)
 destination.mkdir(parents=True,exist_ok=True);(destination/'index.html').write_text(html)
 (destination/'agency.js').write_text(agency.strip()+'\n')
 imports=re.search(r'<script type="importmap">(.*?)</script>',html,re.S).group(1)
 (destination/'game_original.js').write_text(imports)
 scripts=re.findall(r'<script[^>]*>(.*?)</script>',html,re.S)
 (destination/'bgm.js').write_text(scripts[3].strip()+'\n')
 manifest={'build':'MEOWNURI 9.0 / Muse v14.19-r1 QA candidate','source_sha256':EXPECTED,'candidate_sha256':hashlib.sha256((destination/'index.html').read_bytes()).hexdigest(),'scope':['R01: ending-safe clue watchdog','R02: persisted journeys and legacy save recovery'],'unchanged':['story content','BGM','core importmap modules','save key and schema','public main'],'status':'CANDIDATE UNTIL BROWSER TESTED'}
 (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));return manifest
if __name__=='__main__':
 print(json.dumps(build(Path(sys.argv[1] if len(sys.argv)>1 else 'index.html'),Path(sys.argv[2] if len(sys.argv)>2 else 'qa-r1')),indent=2))
