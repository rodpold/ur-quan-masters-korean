"""Static intro checks; not a substitute for watching the running game."""
import io,json,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inventory_text import classify
from check_localization import check_dialogue_record

def verify_intro(package,source):
    root=Path(__file__).resolve().parents[1]
    spec=json.loads((root/'translations/intro.ko.json').read_text(encoding='utf-8'))
    terms=json.loads((root/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']
    old=classify(spec['source_path'],source.read(spec['source_path']).decode('utf-8'))
    new=classify(spec['source_path'],package.read('ko/cutscene/intro/intro.txt').decode('utf-8'))
    assert len(old)==len(new)
    font='starcon';rows=[]
    for a,b in zip(old,new):
        assert a['id']==b['id'] and a['kind']==b['kind']
        if a.get('command')=='FONT':
            if a['text']=='FONT 0':font='starcon'
            elif a['text']=='FONT 1':font='slides'
            if len(a['text'].split())==3:
                assert b['text'].split()[:2]==a['text'].split()[:2]
                assert b['text'].split()[2]=='addons/uqm-korean-ui-poc/ko/fonts/'+a['text'].split('/')[-1]
            else:assert a==b
        elif a['kind']=='slide_text':
            assert b['text']==spec['records'][a['id']]
            check_dialogue_record(a['text'],b['text'],terms,spec['source_path'],'intro/'+a['id'])
            widths=[]
            for line in b['text'].splitlines():
                width=0
                for char in line:
                    image=Image.open(io.BytesIO(package.read(f'ko/fonts/{font}.fon/{ord(char):05x}.png'))).convert('RGBA')
                    assert set(image.getchannel('A').getdata())<={0,255}
                    width+=image.width+1
                widths.append(width)
            assert max(widths)<=310,(a['id'],widths)
            rows.append(dict(id=a['id'],font=font,widths=widths))
        else:assert a==b,('Control command changed',a['id'])
    assert len(rows)==32
    return dict(status='static_passed_runtime_pending',subtitles=rows)
