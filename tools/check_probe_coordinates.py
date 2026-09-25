"""Verify data consumed by the probe's engine-generated coordinate subtitle.

Does not emulate game execution or synthesize/reorder numeric voice clips.
"""
import argparse,json,re,sys
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher

def records(raw):
    parts=re.split(r'(?m)^#\(([^)]*)\)([^\r\n]*)\r?\n',raw.decode('utf-8'))
    return {parts[i]:(parts[i+1],parts[i+2].rstrip('\r\n')) for i in range(1,len(parts),3)}

def verify(game):
    with ZipFile(game/patcher.SOURCE) as source, ZipFile(patcher.addon_dir(game)/'ko-ui.uqm') as installed:
        original=records(source.read('base/comm/probe/probe.txt'))
        translated=records(installed.read('ko/comm/probe/probe.txt'))
        assert original.keys()==translated.keys()
        required={'COORD_PLUS':'+','COORD_MINUS':'-','COORD_POINT':'.','THIS_IS_PROBE_41':',','THIS_IS_PROBE_42':'.'}
        for key,value in required.items():
            assert translated[key]==original[key],key
            assert translated[key][1]==value,key
        prefix=translated['THIS_IS_PROBE_40'][1]
        assert prefix.endswith(': ') and '2418-B' in prefix
        assert translated['THIS_IS_PROBE_40'][0]==original['THIS_IS_PROBE_40'][0]
        numerals=[k for k in original if k.startswith('ENUMERATE_')]
        assert len(numerals)==30
        for key in numerals:
            assert translated[key][0]==original[key][0],key
            assert re.search(r'probe-\d{3}\.ogg',translated[key][0]),key
        mapping=installed.read('ko-ui.rmp').decode().splitlines()
        font=next(line.split(' = FONTRES:',1)[1] for line in mapping if line.startswith('comm.probe.font = FONTRES:'))
        font=font.removeprefix('addons/'+patcher.ADDON+'/')
        for char in '0123456789+-,.':
            filename=f'{ord(char):05x}.png'
            assert installed.read(font+'/'+filename)==source.read('base/fonts/probe.fon/'+filename),char
    return {'status':'installed_coordinate_fragments_and_numeric_glyphs_preserved','numeric_voice_headers':len(numerals),'literal_coordinate_fragments':len(required),'engine_generated_digits':'Arabic numerals per pinned public source; translated numeral words are not composed into the coordinate subtitle.','limitations':['No execution of the installed EXE or validation of audio playback/timing.','Pinned source coordinate basis and subtitle formatting remain runtime verification targets.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--write-report',action='store_true');a=p.parse_args()
    result=verify(a.game)
    if a.write_report:(ROOT/'docs/probe-coordinate-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
