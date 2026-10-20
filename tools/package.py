"""MIT licensed data-only validation/packaging utility. Never executes package code."""
from pathlib import Path
import argparse, hashlib, json, re, struct, zipfile
from xml.etree import ElementTree as ET

SCHEMAS=Path(__file__).resolve().parents[1]/"schemas"
def require(ok,message):
    if not ok:raise ValueError(message)
def pairs(items):
    result={}
    for k,v in items:
        require(k.casefold() not in {s.casefold() for s in result},"Duplicate JSON key: "+k);result[k]=v
    return result
def read(path):
    raw=path.read_bytes();require(len(raw)<=16*1024*1024,"JSON file exceeds 16 MiB")
    # Bound nesting before the parser allocates recursive objects.
    depth=0;string=False;escape=False
    for b in raw:
        if string:
            if escape:escape=False
            elif b==92:escape=True
            elif b==34:string=False
        elif b==34:string=True
        elif b in (91,123):depth+=1;require(depth<=32,"JSON depth exceeds 32")
        elif b in (93,125):depth-=1
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError("Non-finite JSON")))
    def inspect(v):
        require(v is not None,"Omit optional members instead of null")
        if isinstance(v,list):require(len(v)<=20000,"Array limit");[inspect(x) for x in v]
        elif isinstance(v,dict):[inspect(x) for x in v.values()]
        elif isinstance(v,str):require(len(v)<=16384,"Text limit")
    inspect(value);return value
def safe(relative):
    require(len(relative)<=180 and "\\" not in relative and ":" not in relative and "%" not in relative,"Unsafe path")
    for p in relative.split("/"):
        require(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*",p) and not p.endswith(".") and not re.fullmatch(r"(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])",p.split(".")[0]),"Unsafe path: "+relative)
def schema_check(value,schema,root=None,path="$"):
    root=root or schema
    if "$ref" in schema:return schema_check(value,root["$defs"][schema["$ref"].split("/")[-1]],root,path)
    for child in schema.get("allOf",[]):schema_check(value,child,root,path)
    if "const" in schema:require(value==schema["const"],path+" constant")
    if "enum" in schema:require(value in schema["enum"],path+" enum")
    typ=schema.get("type")
    types={"object":dict,"array":list,"string":str,"boolean":bool,"integer":int,"number":(int,float)}
    if typ:require(isinstance(value,types[typ]) and not (typ in ("integer","number") and isinstance(value,bool)),path+" type "+typ)
    if isinstance(value,dict):
        require(all(k in value for k in schema.get("required",[])),path+" missing required member")
        for k,v in value.items():
            prop=schema.get("properties",{}).get(k,schema.get("additionalProperties",{}))
            require(prop is not False,path+" unknown member "+k)
            if isinstance(prop,dict):schema_check(v,prop,root,path+"."+k)
    if isinstance(value,list):
        require(schema.get("minItems",0)<=len(value)<=schema.get("maxItems",20000),path+" array count")
        if schema.get("uniqueItems"):require(len({json.dumps(v,sort_keys=True) for v in value})==len(value),path+" duplicate")
        for v in value:schema_check(v,schema.get("items",{}),root,path+"[]")
    if isinstance(value,str):
        require(len(value)<=schema.get("maxLength",16384),path+" text length")
        if "pattern" in schema:require(re.search(schema["pattern"],value),path+" pattern")
def validate(folder):
    folder=folder.resolve();require(folder.is_dir(),"Package source folder missing")
    files=sorted(p for p in folder.rglob("*") if p.is_file() or p.is_symlink())
    require(0<len(files)<=512,"Entry count limit");seen=set();total=0
    for p in files:
        rel=p.relative_to(folder).as_posix();safe(rel)
        require(not p.is_symlink() and p.resolve().is_relative_to(folder),"Links forbidden")
        require(rel.casefold() not in seen,"Case collision");seen.add(rel.casefold())
        require(rel not in ("receipt.json",".package.zip"),"Reserved runtime metadata")
        require(p.suffix.lower() in (".json",".png",".svg"),"Unsupported/executable file")
        size=p.stat().st_size;total+=size;require(size<=16*1024*1024 and total<=128*1024*1024,"Size limit")
        if p.suffix==".json":read(p)
        if p.suffix==".png":
            with p.open("rb") as f:header=f.read(33)
            require(header[:8]==b"\x89PNG\r\n\x1a\n" and header[12:16]==b"IHDR","Invalid PNG")
            w,h=struct.unpack(">II",header[16:24]);require(0<w<=2048 and 0<h<=2048,"PNG dimensions")
        if p.suffix==".svg":
            raw=p.read_bytes();require(len(raw)<=2*1024*1024 and b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(),"Unsafe SVG")
            elements=list(ET.fromstring(raw).iter());require(len(elements)<=10000,"SVG count")
            for e in elements:
                require(e.tag.split("}")[-1] in ("svg","g","path","rect","circle","ellipse","polygon","polyline","line","title","desc"),"Unsupported SVG element")
                for k,v in e.attrib.items():require(not k.split("}")[-1].lower().startswith("on") and k.split("}")[-1] not in ("href","style") and "url(" not in v.lower(),"Unsafe SVG reference")
    m=read(folder/"mod.json");schema_check(m,json.loads((SCHEMAS/"mod.schema.json").read_text()))
    require(m["content"] or m.get("dependencies"),"Empty package")
    require(len(m.get("dependencies",[]))<=64 and len(m.get("conflicts",[]))<=64,"Dependency limit")
    for category,entry in m["content"].items():
        require(category in m["categories"] and category!="modpacks","Undeclared category");safe(entry)
        schema_check(read(folder/entry),json.loads((SCHEMAS/(category+".schema.json")).read_text()))
    if "preview" in m:safe(m["preview"]);require((folder/m["preview"]).is_file(),"Missing preview")
    return m,files
def package(folder,destination):
    m,files=validate(folder);destination.parent.mkdir(parents=True,exist_ok=True)
    require(not destination.exists(),"Destination exists; retain immutable package bytes")
    with zipfile.ZipFile(destination,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:
            info=zipfile.ZipInfo(p.relative_to(folder).as_posix(),(2026,10,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    require(destination.stat().st_size<=64*1024*1024,"Archive exceeds 64 MiB")
    with zipfile.ZipFile(destination) as z:
        require(all(e.file_size<=max(1,e.compress_size)*200 for e in z.infolist()),"Compression ratio exceeds 200:1")
    receipt=dict(id=m["id"],version=m["version"],size=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    destination.with_suffix(destination.suffix+".submission.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return receipt
def main():
    parser=argparse.ArgumentParser();parser.add_argument("source",type=Path);parser.add_argument("destination",type=Path,nargs="?");parser.add_argument("--all",action="store_true")
    args=parser.parse_args()
    if args.all:
        paths=sorted(args.source.rglob("mod.json"));require(paths,"No manifests found")
        for path in paths:validate(path.parent);print("VALID",path)
    elif args.destination:print(json.dumps(package(args.source,args.destination)))
    else:validate(args.source);print("VALID",args.source)
if __name__=="__main__":main()
