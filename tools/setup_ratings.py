"""Maintainer command: create/reuse the public rating issues for reviewed featured content."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];REPO='Grizzly20121/Pitwall2000-Mods'
def gh(*args):return subprocess.check_output(['gh',*args,'--repo',REPO],text=True).strip()
existing=json.loads(gh('issue','list','--state','all','--limit','100','--json','number,title'))
ratings={}
for path in sorted((ROOT/'featured').glob('*/*/mod.json')):
    m=json.loads(path.read_text(encoding='utf8'));title='[Ratings] '+m['name']
    found=next((i for i in existing if i['title']==title),None)
    if found:ratings[m['id']]=found['number'];continue
    body=(f"Project-maintained public rating thread for **{m['name']}** (`{m['id']}`, featured v0.4.5.0 content).\n\n"
          "Use the +1 (thumbs up) or -1 (thumbs down) reaction on this issue to rate the mod. The game reads the actual public reaction counts; local preferences are not global votes.\n\n"
          "The package author **void_58** is a fictional identity created for this release, not an external creator being impersonated. Package sources and immutable downloads are maintained by this project. Bugs and submissions belong in separate issues.\n")
    temp=ROOT/'packages'/'rating-body.txt';temp.write_text(body,encoding='utf8')
    try:url=gh('issue','create','--title',title,'--body-file',str(temp))
    finally:temp.unlink(missing_ok=True)
    ratings[m['id']]=int(url.rsplit('/',1)[-1]);print(m['id'],url,flush=True)
(ROOT/'rating-issues.json').write_text(json.dumps(ratings,indent=2)+'\n',encoding='utf8')
print('PUBLIC_RATING_THREADS_READY',len(ratings))
