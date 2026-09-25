"""Read-only checks against a locally installed supported game."""
import io,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import patcher

def verify(game, ui_font="compact"):
    data,report=patcher.build(game, ui_font)
    assert patcher.build(game, ui_font)[0]==data,'Non-deterministic build'
    with ZipFile(io.BytesIO(data)) as z, ZipFile(Path(game)/patcher.SOURCE) as source:
        assert z.testzip() is None
        names=set(z.namelist())
        if ui_font == 'larger':
            table=z.read('ko/setupmenu.txt').decode('utf-8')
            records=re.split(r'(?m)^#\(([^\r\n]*)\)[^\r\n]*\r?\n',table)
            fields={records[i]:records[i+1].rstrip('\r\n') for i in range(1,len(records),2)}
            assert fields['TITLE']==' ', 'Large setup title must not overlap subtitle'
            assert fields['SUBTITLES'].splitlines()[0]=='UQM 설정'
            assert len(fields['SUBTITLES'].splitlines())==8

        for line in z.read('ko-ui.rmp').decode().splitlines():
            path=line.split(':',1)[1]
            prefix='addons/'+patcher.ADDON+'/'
            assert path.startswith(prefix),path
            relative=path.split(':',1)[0].removeprefix(prefix)
            assert relative in names or any(n.startswith(relative+'/') for n in names),relative
        for name in names:
            if name.endswith('.ani'):
                for line in z.read(name).decode().splitlines():
                    fields=line.split();assert len(fields)==5
                    assert str(Path(name).parent/fields[0]).replace('\\','/') in names
        for original,translated in [('base/gamestrings.txt','ko/gamestrings.txt'),('base/ui/setupmenu.txt','ko/setupmenu.txt')]:
            header=lambda b: re.findall(rb'(?m)^#[^\r\n]*',b)
            assert header(source.read(original))==header(z.read(translated))
        for family in ['starcon','tiny','micro','player','urquan']:
            for name in source.namelist():
                if name.startswith(f'base/fonts/{family}.fon/'):
                    assert source.read(name)==z.read(name.replace('base/fonts/','ko/fonts/',1))
        for n in names:
            if '/fonts/' in n and 0xAC00 <= int(Path(n).stem,16) <= 0xD7A3:
                im=Image.open(io.BytesIO(z.read(n)))
                alpha=im.getchannel('A')
                assert alpha.getbbox(),n
                assert set(alpha.getdata()) <= {0,255},f'Semitransparent Korean glyph: {n}'
        translations=json.loads((patcher.ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
        setup=json.loads((patcher.ROOT/'translations/setup.ko.json').read_text(encoding='utf-8'))
        dialogue = {p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (patcher.ROOT/'translations/dialogue').glob('*.json')}
        required={c for value in [*translations.values(),*setup.values(),*[v for records in dialogue.values() for v in records.values()]] for c in value if ord(c)>127}
        registry=json.loads((patcher.ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
        groups=[row for row in registry['dialogue_fonts'] if row['id']==row['font_group']]
        assert len(groups)==24
        assert len({registry['fonts'][row['candidate_font']]['sha256'] for row in groups})==24
        for row in groups:
            old=row['original_font'].removeprefix('FONTRES:')+'/'
            new=f"ko/fonts/races/{row['id']}.fon/"
            for name in source.namelist():
                if name.startswith(old) and name.endswith('.png'):
                    assert source.read(name)==z.read(new+Path(name).name),f'Original race glyph changed: {name}'
            for char in required:
                assert new+f'{ord(char):05x}.png' in names,f'Missing race glyph: {row["id"]}/{char}'
        for species in sorted(p.name.removesuffix('.ko.json') for p in (patcher.ROOT/'translations/dialogue').glob('*.ko.json')):
            source_species='yehatrebels' if species=='yehat.rebel' else species
            a=source.read(f'base/comm/{source_species}/{source_species}.txt').decode('utf-8')
            b=z.read(f'ko/comm/{species}/{species}.txt').decode('utf-8')
            split=lambda t: re.split(r'(?m)(^#\([^\r\n]*\)[^\r\n]*\r?\n)',t)
            aa,bb=split(a),split(b)
            assert aa[1::2]==bb[1::2], 'Dialogue headers or audio names changed'
            for before,after in zip(aa[2::2],bb[2::2]):
                assert len(before.rstrip('\r\n').splitlines())==len(after.rstrip('\r\n').splitlines()), 'Subtitle segment count changed'
        for fontname,size in [('Galmuri7',8),('Galmuri9',10),('Galmuri11',12)]:
            face=patcher.font(fontname,size)
            missing=bytes(face.getmask(chr(0x10ffff)))
            for char in required:
                mask=bytes(face.getmask(char))
                assert any(mask) and mask!=missing,f'{fontname}: missing glyph U+{ord(char):04X}'
        widths={chr(int(Path(n).stem,16)):Image.open(io.BytesIO(z.read(n))).width+1
                for n in names if n.startswith('ko/fonts/starcon.fon/')}
        for key,value in setup.items():
            for line in value.splitlines():
                width=sum(widths[c] for c in line)
                assert width<=300,f'Setup text wider than safe screen area: {key}: {width}'
        for key in ['starmap','manifest','game','navigate','cargo','devices','roster','save game','load game','quit game','exit menu']:
            assert sum(widths[c] for c in translations[key])<=54,f'Sidebar overflow: {key}'
        for n in ['playmenu-060.png','playmenu-061.png','playmenu-062.png','playmenu-063.png']:
            assert Image.open(io.BytesIO(z.read('ko/ui/'+n))).size==Image.open(io.BytesIO(source.read('base/ui/'+n))).size
    print(json.dumps({'checks':'passed',**report},indent=2))

if __name__=='__main__':verify(Path(sys.argv[1]), sys.argv[2] if len(sys.argv)>2 else "compact")
