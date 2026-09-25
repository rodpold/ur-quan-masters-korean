"""Create an auditable development source bundle; never include game assets."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),*args],cwd=ROOT)

def build(output,allow_dirty=False):
    dirty=bool(git('status','--porcelain').strip())
    if dirty and not allow_dirty:raise ValueError('Commit or preserve pending work before creating a release; --allow-dirty is for local inspection only.')
    revision=git('rev-parse','HEAD').decode().strip()
    tracked=[n for n in git('ls-files','-z').decode().split('\0') if n]
    included={}
    for name in tracked:
        p=Path(name);parts=p.parts
        allowed=(len(parts)==1 and (p.suffix=='.py' or name in {'README.md','THIRD_PARTY.md','LICENSE','requirements.txt'}))
        allowed|=parts[0] in {'translations','tools','tests','docs'} and p.suffix in {'.py','.json','.md'}
        allowed|=parts[0] in {'vendor','LICENSES'}
        if not allowed:continue
        path=ROOT/p
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):raise ValueError('Linked bundle input: '+name)
        if p.suffix.lower() in {'.uqm','.exe','.dll','.ogg','.lpf','.png'} or p.name.startswith('uqmsave'):raise ValueError('Unexpected binary/game payload: '+name)
        included[name]=path.read_bytes()
    for required in ('patcher.py','requirements.txt','LICENSE','THIRD_PARTY.md','vendor/galmuri/OFL.txt','LICENSES/UQM-GPL.txt'):
        if required not in included:raise ValueError('Missing bundle requirement: '+required)
    manifest={'kind':'development_source_not_standalone_executable','source_revision':revision,'dirty_worktree':dirty,'files':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(included.items())},'excluded':['Original game assets','Generated ko-ui.uqm','User saves/settings','Images in developer preview documentation','Python interpreter and installed dependencies']}
    included['SOURCE-BUNDLE.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w') as z:
        for name,data in sorted(included.items()):
            item=ZipInfo('uqm-korean-patcher/'+name,date_time=(2026,1,1,0,0,0));item.compress_type=ZIP_DEFLATED;item.external_attr=0o100644<<16
            z.writestr(item,data)
    with ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('Corrupt source archive')
        for name,expected in manifest['files'].items():
            if hashlib.sha256(z.read('uqm-korean-patcher/'+name)).hexdigest()!=expected:raise ValueError(name)
    return {'archive':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'files':len(included),'source_revision':revision,'dirty_worktree':dirty}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'artifacts/uqm-korean-development-source.zip');p.add_argument('--allow-dirty',action='store_true');a=p.parse_args()
    print(json.dumps(build(a.output,a.allow_dirty),ensure_ascii=False,indent=2))
