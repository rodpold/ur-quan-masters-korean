"""Static intro/ending checks; not a substitute for watching the running game."""
import io,json,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inventory_text import classify
from check_localization import check_dialogue_record

def verify_slides(package,source,spec,expected_count):
    root=Path(__file__).resolve().parents[1]
    terms=json.loads((root/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']
    old=classify(spec['source_path'],source.read(spec['source_path']).decode('utf-8'))
    new=classify(spec['source_path'],package.read(spec['source_path'].replace('base/','ko/',1)).decode('utf-8'))
    assert len(old)==len(new)
    font='starcon';slots={};rows=[]
    for a,b in zip(old,new):
        assert a['id']==b['id'] and a['kind']==b['kind']
        if a.get('command')=='FONT':
            if len(a['text'].split())==3:
                fields=a['text'].split()
                slots[fields[1]]=Path(fields[2]).stem
                font=slots[fields[1]]
                assert b['text'].split()[:2]==a['text'].split()[:2]
                assert b['text'].split()[2]=='addons/uqm-korean-ui-poc/ko/fonts/'+a['text'].split('/')[-1]
            else:
                assert a==b
                font=slots[a['text'].split()[1]]
        elif a['kind']=='slide_text':
            assert b['text']==spec['records'][a['id']]
            assert len(b['text'].encode('utf-8'))<512,('Slide text buffer exceeded',a['id'])
            assert len(b['text'].splitlines())<=15,('Slide line buffer exceeded',a['id'])
            check_dialogue_record(a['text'],b['text'],terms,spec['source_path'],spec['source_path']+'/'+a['id'])
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
    assert len(rows)==expected_count
    return dict(status='static_passed_runtime_pending',subtitles=rows)


def verify_intro(package,source):
    from cutscene_text import load_intro
    return verify_slides(package,source,load_intro(),32)


def verify_ending(package,source):
    from cutscene_text import load_ending,compile_ending_wrapper
    import patcher
    spec=load_ending()
    personas=json.loads((patcher.ROOT/'translations/personas.ko.json').read_text(encoding='utf-8'))['cutscene_profiles']['ending']
    assert personas['source_path']==spec['source_path'] and personas['source_sha256']==spec['source_sha256']
    ids=[key for voice in personas['voices'] for key in voice['record_ids']]
    assert len(ids)==len(set(ids)) and set(ids)==set(spec['records'])
    raw=source.read(spec['wrapper_path'])
    actual=package.read('ko/cutscene/ending/ending.txt')
    assert actual==compile_ending_wrapper(raw,spec,patcher.ADDON)
    assert actual.replace(f'CALL addons/{patcher.ADDON}/ko/cutscene/ending/final.txt'.encode(),
                          b'CALL base/cutscene/ending/final.txt')==raw
    return verify_slides(package,source,spec,42)
