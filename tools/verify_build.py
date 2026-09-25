"""Read-only checks against a locally installed supported game."""
import io,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import patcher

def verify(game):
    data,report=patcher.build(game)
    assert patcher.build(game)[0]==data,'Non-deterministic build'
    with ZipFile(io.BytesIO(data)) as z, ZipFile(Path(game)/patcher.SOURCE) as source:
        assert z.testzip() is None
        names=set(z.namelist())
        for line in z.read('ko-ui.rmp').decode().splitlines():
            path=line.split(':',1)[1]
            prefix='addons/'+patcher.ADDON+'/'
            assert path.startswith(prefix),path
            relative=path.removeprefix(prefix)
            assert relative in names or any(n.startswith(relative+'/') for n in names),relative
        for name in names:
            if name.endswith('.ani'):
                for line in z.read(name).decode().splitlines():
                    fields=line.split();assert len(fields)==5
                    assert str(Path(name).parent/fields[0]).replace('\\','/') in names
        for original,translated in [('base/gamestrings.txt','ko/gamestrings.txt'),('base/ui/setupmenu.txt','ko/setupmenu.txt')]:
            header=lambda b: re.findall(rb'(?m)^#[^\r\n]*',b)
            assert header(source.read(original))==header(z.read(translated))
        for family in ['starcon','tiny','micro','player']:
            for name in source.namelist():
                if name.startswith(f'base/fonts/{family}.fon/'):
                    assert source.read(name)==z.read(name.replace('base/fonts/','ko/fonts/',1))
        for n in names:
            if '/fonts/' in n and 0xAC00 <= int(Path(n).stem,16) <= 0xD7A3:
                im=Image.open(io.BytesIO(z.read(n)))
                assert im.getchannel('A').getbbox(),n
        for n in ['playmenu-060.png','playmenu-061.png','playmenu-062.png','playmenu-063.png']:
            assert Image.open(io.BytesIO(z.read('ko/ui/'+n))).size==Image.open(io.BytesIO(source.read('base/ui/'+n))).size
    print(json.dumps({'checks':'passed',**report},indent=2))

if __name__=='__main__':verify(Path(sys.argv[1]))
