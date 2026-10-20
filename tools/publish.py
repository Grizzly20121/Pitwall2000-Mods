"""Trusted maintainer utility: publish immutable assets, verify anonymously, then write catalog."""
from pathlib import Path
import argparse, hashlib, json, subprocess, urllib.request
from package import package, read, require

OWNER="Grizzly20121";REPO=f"{OWNER}/Pitwall2000-Mods"
def gh(*args):return subprocess.check_output(["gh",*args],text=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--tag",default="examples-v1");args=parser.parse_args()
    require(__import__("re").fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,80}",args.tag),"Invalid tag")
    root=Path(__file__).resolve().parents[1];packages=root/"packages";packages.mkdir(exist_ok=True)
    try:release=json.loads(gh("release","view",args.tag,"--repo",REPO,"--json","assets"))
    except subprocess.CalledProcessError:
        subprocess.run(["gh","release","create",args.tag,"--repo",REPO,"--title","Original Workshop examples — "+args.tag,"--notes","Original CC0 examples for Mod API 1. See the creator guide and compatibility ranges."],check=True)
        release={"assets":[]}
    entries=[]
    for manifest in sorted((root/"examples").glob("*/*/mod.json")):
        m=read(manifest);name=f'{m["id"]}-{m["version"]}.zip';zip_path=packages/name
        if not zip_path.exists():package(manifest.parent,zip_path)
        raw=zip_path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        existing=next((a for a in release["assets"] if a["name"]==name),None)
        if existing is None:subprocess.run(["gh","release","upload",args.tag,str(zip_path),"--repo",REPO],check=True)
        url=f"https://github.com/{REPO}/releases/download/{args.tag}/{name}"
        # No Authorization header or gh download: exercise the public player path.
        with urllib.request.urlopen(url,timeout=90) as response:
            public=response.read(64*1024*1024+1)
        require(len(public)==len(raw) and hashlib.sha256(public).hexdigest()==digest,"Public asset differs; do not overwrite an existing release asset")
        entries.append(dict(manifest=m,url=url,size=len(raw),sha256=digest,
            previewUrl=f"https://raw.githubusercontent.com/{REPO}/main/{manifest.parent.relative_to(root).as_posix()}/preview.png"))
    catalog_path=root/"catalog.json"
    old=json.loads(catalog_path.read_text()) if catalog_path.exists() else {"packages":[]}
    by_key={(p["manifest"]["id"],p["manifest"]["version"]):p for p in old["packages"]}
    for entry in entries:
        key=(entry["manifest"]["id"],entry["manifest"]["version"])
        require(key not in by_key or by_key[key]["sha256"]==entry["sha256"],"Immutable catalog conflict")
        by_key[key]=entry
    from datetime import datetime,timezone
    catalog=dict(schemaVersion=1,publishedUtc=datetime.now(timezone.utc).isoformat(),packages=[by_key[k] for k in sorted(by_key)])
    temporary=root/"catalog.json.tmp";temporary.write_text(json.dumps(catalog,indent=2)+"\n",encoding="utf-8");temporary.replace(catalog_path)
    print("PUBLIC_ASSETS_VERIFIED",len(entries))
if __name__=="__main__":main()
