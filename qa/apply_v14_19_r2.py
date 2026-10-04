"""Add a narrow furniture-safe home goal to the unchanged r1 candidate."""
from pathlib import Path
import json,hashlib,re,sys
from apply_v14_19_r1 import build as build_r1
WRAPPER='''
  // R03: placeable furniture may cover a scripted home-arrival coordinate.
  // Resolve only homeward companion destinations, without moving any actor
  // or furniture and without bypassing normal travel/collision/arrival checks.
  var originalHomeTravel = g.travel.bind(g);
  var safeHomeTargets = new WeakMap();
  g.travel = function (actor, target, dt, speed) {
    var homeward = (this.storyPhase === 1 && this.homeJourney) ||
      (this.storyPhase === 5 && this.clueLead && this.clueLead.kind === 'home');
    if (actor === this.friend && homeward && target && !this.bearStarted && !this.ending) {
      var radius = actor.radius + 0.06;
      if (this.ground.blocked(target.x, target.z, radius)) {
        var key = target.x + ':' + target.z + ':' + this.ground.version;
        var cached = safeHomeTargets.get(actor);
        if (!cached || cached.key !== key || this.ground.blocked(cached.goal.x, cached.goal.z, radius)) {
          var freeGoal = this.ground.nearest(target.x, target.z, radius + 0.06, this.otherActors(actor), 4.5);
          cached = freeGoal ? {key: key, goal: freeGoal} : null;
          if (cached) safeHomeTargets.set(actor, cached);
        }
        if (cached) target = cached.goal;
      }
    }
    return originalHomeTravel(actor, target, dt, speed);
  };
'''
def build(source,destination):
 manifest=build_r1(source,destination)
 html=(destination/'index.html').read_text()
 anchor='function install(g) {'
 assert html.count(anchor)==1
 html=html.replace(anchor,anchor+WRAPPER,1).replace(' · QA r1</title>',' · QA r2</title>')
 (destination/'index.html').write_text(html)
 agency=(destination/'agency.js').read_text();assert agency.count(anchor)==1
 (destination/'agency.js').write_text(agency.replace(anchor,anchor+WRAPPER,1))
 manifest.update(build='MEOWNURI 9.0 / Muse v14.19-r2 QA candidate',candidate_sha256=hashlib.sha256((destination/'index.html').read_bytes()).hexdigest(),parent_r1_sha256='f4cde2bb3dcb38ba56fb0de29c0fea3198b2c6be7c8b9953c9cda66b9400f7be')
 manifest['scope'].append('R03: furniture-safe scripted home arrival, normal collision and movement retained')
 manifest['unchanged']=[x for x in manifest['unchanged'] if x!='public main']+['no writes to current main by this review task']
 (destination/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 return manifest
if __name__=='__main__':print(json.dumps(build(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
